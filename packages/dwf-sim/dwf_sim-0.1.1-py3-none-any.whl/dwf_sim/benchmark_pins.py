"""Benchmark private individual variant calls."""

import logging, sys
from pathlib import Path
from typing import Dict, List, Optional, Set
import pandas as pd
from multiprocessing import Pool
from .matrix_context import MatrixContext
from .benchmark import calculate_metrics
from .vcf_utils import intersect_vcfs_vcfeval, call_state_by_type, normalize_all_vcfs, find_private_variants, count_variants

logger = logging.getLogger(__name__)

def _process_individual(args):
    (
        individual_id,
        other_individuals,
        norm_truth,
        norm_caller,
        private_dir,
        comparisons_dir,
        sdf_dir,
        matrix_size,
        coverage,
        filtration_status,
    ) = args

    logger.debug(
        f"Finding private variants for {individual_id} "
        f"(comparing to {len(other_individuals)} others)"
    )

    # Build list of "other" VCFs
    other_vcfs = [norm_truth[oid] for oid in other_individuals]

    # Find private variants for this individual
    private_vcf = find_private_variants(
        individual_id=individual_id,
        individual_vcf=norm_truth[individual_id],
        other_vcfs=other_vcfs,
        output_dir=private_dir,
    )

    truth_variant_count = count_variants(private_vcf)
    caller_variant_count = count_variants(norm_caller[individual_id])

    logger.info(
        f"  {individual_id}: {truth_variant_count} private true variants. "
        f"{caller_variant_count} called variants."
    )
    logger.info(f"Comparing {individual_id}")

    if caller_variant_count == 0 and truth_variant_count == 0:
        counts = {k: {"TP": 0, "FP": 0, "FN": 0} for k in ("snv", "indel", "both")}
    else:
        work_dir = comparisons_dir / individual_id
        work_dir.mkdir(exist_ok=True)

        # Compare variant calls with vcfeval
        comparison = intersect_vcfs_vcfeval(
            a_vcf=norm_caller[individual_id],
            b_vcf=private_vcf,
            sdf_dir=sdf_dir,
            out_prefix=work_dir / "vcfeval",
        )

        # Get counts by variant type
        counts = call_state_by_type(
            tp=comparison["both"],
            fp=comparison["a_only"],
            fn=comparison["b_only"],
        )

    results = []

    for vartype, stats in counts.items():
        tp, fp, fn = stats["TP"], stats["FP"], stats["FN"]
        metrics = calculate_metrics(tp, fp, fn)

        logger.info(
            f"  {vartype.upper():6} -> "
            f"TP: {tp:6d}, FP: {fp:6d}, FN: {fn:6d}, "
            f"Sens: {metrics['sensitivity']:.4f}, "
            f"F1: {metrics['F1_score']:.4f}"
        )

        result = {
            "individual_id": individual_id,
            "variant_type": vartype.upper(),
            "total_variant_calls": metrics["total_variant_calls"],
            "total_variants_in_truthset": metrics["total_variants_in_truthset"],
            "TP": tp,
            "FP": fp,
            "FN": fn,
            "sensitivity": metrics["sensitivity"],
            "precision": metrics["precision"],
            "F1_score": metrics["F1_score"],
            "FDR": metrics["FDR"],
        }
        
        # Add optional metadata columns if provided
        if matrix_size is not None:
            result["matrix_size"] = matrix_size
        if coverage is not None:
            result["coverage"] = coverage
        if filtration_status is not None:
            result["filtration_status"] = filtration_status

        results.append(result)

    return results

def benchmark_private_variants(
    matrix_context_path: Path,
    gold_standard_dir: Path,
    caller_dir: Path,
    output_dir: Path,
    reference: Path,
    sdf_dir: Path,
    bed: Optional[Path] = None,
    caller_suffix: str = "vcf.gz",
    threads: int = 4,
    output_filename: Optional[str] = None,
    filtration_status: Optional[str] = None,
    coverage: Optional[int] = None,
    matrix_size: Optional[int] = None
) -> pd.DataFrame:
    """
    Benchmark private individual variant calls.
    
    For each individual:
    1. Find their private variants (variants not in other pool members)
    2. Compare against caller's predictions for this individual
    3. Calculate metrics
    
    Args:
        matrix_context_path: Path to matrix_context.json
        gold_standard_dir: Directory with gold standard VCFs for individuals (from simulation)
        caller_dir: Directory with caller VCFs for individuals
        output_dir: Output directory for results
        reference: Reference genome FASTA
        sdf_dir: RTG SDF directory
        bed: Optional BED file for targeted regions
        caller_suffix: Suffix for caller VCF files
    
    Returns:
        DataFrame with benchmarking results
    """
    logger.info(f"Benchmarking private variants")
    
    # Load matrix context
    mc = MatrixContext.load(matrix_context_path)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    gold_standard_dir = Path(gold_standard_dir)
    caller_dir = Path(caller_dir)
    
    # Collect all truth VCF paths
    truth_vcfs = {}
    for cell in mc._ctx["matrix"]["cells"]:
        individual_id = cell["alias"]
        truth_vcfs[individual_id] = gold_standard_dir / f"{individual_id}.vcf"
        if not truth_vcfs[individual_id].exists():
            logger.error(f"Truth VCF not found: {truth_vcfs[individual_id]}")
            raise FileNotFoundError
    
    logger.info(f"Found {len(truth_vcfs)} truth VCFs")

    # Collect all caller VCF paths
    caller_vcfs = {}
    for individual_id in truth_vcfs.keys():
        caller_vcf = caller_dir / f"{individual_id}{caller_suffix}"
        if caller_vcf.exists():
            caller_vcfs[individual_id] = caller_vcf
        else:
            logger.warning(f"Caller VCF not found for {individual_id}: {caller_vcf}")
    
    logger.info(f"Found {len(caller_vcfs)} caller VCFs")

    # Find common individuals
    common_individuals = set(truth_vcfs.keys()) & set(caller_vcfs.keys())
    if not common_individuals:
        logger.error("No matching truth and caller VCFs found")
        raise ValueError("No VCF pairs to compare")
    
    logger.info(f"Found {len(common_individuals)} individuals to benchmark")
    
    norm_truth = normalize_all_vcfs(
        {iid: truth_vcfs[iid] for iid in common_individuals},
        output_dir,
        reference,
        bed=bed,
        label="truth"
    )
    
    norm_caller = normalize_all_vcfs(
        {iid: caller_vcfs[iid] for iid in common_individuals},
        output_dir,
        reference,
        bed=bed,
        label="caller"
    )

    logger.info("Finding private variants for all individuals...")
    
    results = []
    comparisons_dir = output_dir / "comparisons"
    comparisons_dir.mkdir(exist_ok=True)
    private_dir = output_dir / "private_variants"
    private_dir.mkdir(exist_ok=True)
    
    cells = mc._ctx["matrix"]["cells"]

    work = []
    for cell in cells:
        individual_id = cell["alias"]
        
        if individual_id not in common_individuals:
            logger.error(f"No matching truth VCF for {individual_id}")
            raise ValueError(f"No VCF pairs to compare for {individual_id}")

        other_individuals = [
            c["alias"] for c in cells
            if c["alias"] != individual_id
            and c["alias"] in norm_truth
        ]

        if not other_individuals:
            logger.error(f"No other individuals found in pools for {individual_id}")
            raise ValueError(f"Mismatch in individuals for {individual_id}")
        
        work.append(
            (
                individual_id,
                other_individuals,
                norm_truth,
                norm_caller,
                private_dir,
                comparisons_dir,
                sdf_dir,
                matrix_size,
                coverage,
                filtration_status,
            )
        )
    results: List[Dict] = []
    with Pool(processes=threads) as pool:
        for indiv_results in pool.imap_unordered(_process_individual, work):
            results.extend(indiv_results)
    
    # Create DataFrame and save
    df = pd.DataFrame(results)
    
    if output_filename is None:
        output_filename = "pins_results.tsv"
    
    output_file = output_dir / output_filename
    df.to_csv(output_file, sep='\t', index=False, float_format='%.6f')
    
    logger.info(f"PIN benchmark results written to: {output_file}")
    logger.info(f"Total individuals processed: {len(df['individual_id'].unique())}")
    
    return df