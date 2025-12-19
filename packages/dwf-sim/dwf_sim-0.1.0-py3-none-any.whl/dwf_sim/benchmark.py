import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from .matrix_context import MatrixContext
from .vcf_utils import normalize_vcf, intersect_vcfs_vcfeval, call_state_by_type, count_variants

logger = logging.getLogger(__name__)

"""Benchmarking variant calls against gold standard VCFs."""

def calculate_metrics(tp: int, fp: int, fn: int) -> Dict[str, float]:
    """
    Calculate performance metrics from TP, FP, FN counts.
    
    Args:
        tp: True positives
        fp: False positives
        fn: False negatives
    
    Returns:
        Dictionary with sensitivity, precision, F1, FDR, and total variants
    """
    metrics = {}
    metrics['sensitivity'] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    metrics['precision'] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    metrics['F1_score'] = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
    metrics['FDR'] = fp / (fp + tp) if (fp + tp) > 0 else 0.0
    metrics['total_variant_calls'] = tp + fp
    metrics['total_variants_in_truthset'] = tp + fn
    
    return metrics

def benchmark_caller(
    matrix_context_path: Path,
    gold_standard_dir: Path,
    caller_dir: Path,
    caller_name: str,
    output_dir: Path,
    reference: Path,
    sdf_dir: Path,
    filtration_status: Optional[str] = None,
    coverage: Optional[int] = None,
    matrix_size: Optional[int] = None,
    bed: Optional[Path] = None,
    caller_suffix: str = "vcf.gz",
    output_filename: Optional[str] = None,
) -> pd.DataFrame:
    """
    Benchmark variant caller against gold standard pool VCFs.
    
    Args:
        matrix_context_path: Path to matrix_context.json
        gold_standard_dir: Directory with gold standard pool VCFs (from simulation)
        caller_dir: Directory with caller VCFs to benchmark
        caller_name: Name of the caller (for output)
        output_dir: Output directory for results
        reference: Reference genome FASTA
        sdf_dir: RTG SDF directory
        bed: Optional BED file for targeted regions
        caller_suffix: Suffix for caller VCF files (default: "vcf.gz")
    
    Returns:
        DataFrame with benchmarking results
    """
    logger.info(f"Benchmarking {caller_name} against gold standard")
    
    # Load matrix context
    mc = MatrixContext.load(matrix_context_path)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    gold_standard_dir = Path(gold_standard_dir)
    caller_dir = Path(caller_dir)
    
    results = []
    
    # Benchmark each pool
    for pool_id in mc.all_pools:
        logger.info(f"Processing pool: {pool_id}")
        
        # Gold standard VCF path (from simulation)
        gold_vcf = gold_standard_dir / f"{pool_id}.vcf.gz"
        if not gold_vcf.exists():
            logger.error(f"Gold standard VCF not found: {gold_vcf}")
            raise FileNotFoundError
        
        # Caller VCF path
        caller_vcf = caller_dir / f"{pool_id}.{caller_name}.{caller_suffix}"
        if not caller_vcf.exists():
            logger.error(f"Caller VCF not found: {caller_vcf}")
            raise FileNotFoundError
        
        # Normalize caller VCF
        work_dir = output_dir / f"tmp_{pool_id}"
        work_dir.mkdir(exist_ok=True)
        
        caller_norm = normalize_vcf(
            caller_vcf,
            work_dir / "caller_norm.vcf.gz",
            reference,
            target_bed=bed
        )

        # Normalize gold standard VCF
        gold_norm = normalize_vcf(
            gold_vcf,
            work_dir / "gold_norm.vcf.gz",
            reference,
            target_bed=bed
        )
        
        # Compare with vcfeval
        logger.info(f"Running vcfeval for {pool_id}...")
        comparison = intersect_vcfs_vcfeval(
            a_vcf=caller_norm,
            b_vcf=gold_norm,
            sdf_dir=sdf_dir,
            out_prefix=work_dir / "comparison"
        )
        
        # Get counts by variant type
        counts = call_state_by_type(
            tp=comparison['both'],
            fp=comparison['a_only'],
            fn=comparison['b_only']
        )
        
        # Calculate metrics
        for vartype, stats in counts.items():
            tp, fp, fn = stats['TP'], stats['FP'], stats['FN']
            metrics = calculate_metrics(tp, fp, fn)
            
            logger.info(
                f"  {pool_id} {vartype.upper():6} -> "
                f"TP: {tp:6d}, FP: {fp:6d}, FN: {fn:6d}, "
                f"Sens: {metrics['sensitivity']:.4f}, F1: {metrics['F1_score']:.4f}"
            )
            
            result = {
                'pool_id': pool_id,
                'caller': caller_name,
                'variant_type': vartype.upper(),
                'total_variant_calls': metrics['total_variant_calls'],
                'total_variants_in_truthset': metrics['total_variants_in_truthset'],
                'TP': tp,
                'FP': fp,
                'FN': fn,
                'sensitivity': metrics['sensitivity'],
                'precision': metrics['precision'],
                'F1_score': metrics['F1_score'],
                'FDR': metrics['FDR']
            }
            
            # Add optional metadata columns if provided
            if matrix_size is not None:
                result['matrix_size'] = matrix_size
            if coverage is not None:
                result['coverage'] = coverage
            if filtration_status is not None:
                result['filtration_status'] = filtration_status
            
            results.append(result)
    
    # Create DataFrame and save
    df = pd.DataFrame(results)
    
    if output_filename is None:
        output_filename = "pool_results.tsv"
    
    output_file = output_dir / output_filename
    df.to_csv(output_file, sep='\t', index=False, float_format='%.6f')
    
    logger.info(f"Benchmark results written to: {output_file}")
    logger.info(f"Total comparisons: {len(df)}")
    
    return df