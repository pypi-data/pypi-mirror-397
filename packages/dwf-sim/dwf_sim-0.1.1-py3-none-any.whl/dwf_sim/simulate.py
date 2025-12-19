import logging
import subprocess
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, Optional, Tuple
from .data_files import get_data_file, get_ngsngs_binary

logger = logging.getLogger(__name__)

def run_ngsngs(
    individual_id: str,
    reference: Path,
    output_dir: Path,
    coverage: int,
    read_length: int,
    fragment_mean: int = 450,
    fragment_stdev: int = 75,
    mutation_rate: float = 0.001,
    vcf_path: Optional[Path] = None,
    bed_path: Optional[Path] = None,
    random_seed: Optional[int] = None,
) -> Dict[str, Path]:
    """
    Run NGSNGS for one individual.

    Args:
        individual_id: Unique identifier (cell alias like A01)
        reference: Path to reference genome FASTA
        output_dir: Directory for NGSNGS output
        coverage: Read coverage
        read_length: Read length
        fragment_mean: Mean fragment size (mapped to length distribution)
        fragment_stdev: Fragment size standard deviation (mapped similarly)
        mutation_rate: Mutation rate (used if no VCF)
        vcf_path: Optional VCF file for this individual
        bed_path: Optional BED file for targeted regions
        random_seed: Optional random seed for reproducibility

    Returns:
        Dictionary with paths to generated files
    """
    logger.info(f"Running NGSNGS for individual {individual_id}")

    output_prefix = output_dir / individual_id
    ngsngs = get_ngsngs_binary()

    cmd = [
        str(ngsngs),                                     # platform-specific binary
        "--input", str(reference),                        # input reference
        "--output", str(output_prefix),                    # output prefix (NGSNGS may take output prefix)
        "--format", "fastq.gz",                             # output format
        "-q1", str(get_data_file("AccFreqL150R1.txt")),   # quality encoding
        "-q2", str(get_data_file("AccFreqL150R2.txt")),   # quality encoding
        "-seq", "PE",                                  # assuming paired end
        "--reads", str(coverage),                   # coverage
        "--lengthdist", f"norm,{fragment_mean},{fragment_stdev}",  # fragment length distribution
    ]

    # random seed
    if random_seed is not None:
        cmd.extend(["--seed", str(random_seed)])

    # VCF or mutation rate
    if vcf_path:
        logger.info(f"Using input VCF: {vcf_path}")
        cmd.extend(["-vcf", str(vcf_path), "-id", "0"])
        cmd.extend(["--mutationrate", str(0.0)])
        cmd.extend(["--vcf-applied", f"{output_prefix}_mutations.txt"])
        cmd.extend(["-fl", "300"]) # Flanking region
        # cmd.extend(["--noerror"])
        # cmd.extend(["-indel", "0.05,0.1,0.1,0.2"])
    else:
        logger.info(f"Using mutation rate: {mutation_rate}")
        cmd.extend(["--mutationrate", str(mutation_rate)])
        cmd.extend(["-DumpVar", f"{output_prefix}_mutations"])
        # cmd.extend(["-fl", "300"]) # Flanking region
        # cmd.extend(["--noerror"])
        # cmd.extend(["-indel", "0.05,0.1,0.1,0.2"])
        # cmd.extend(["--model", "Illumina,0.024,0.36,0.68,0.0097"])
        # cmd.extend(["--mutationrate", str(mutation_rate)])

    # BED targeted regions
    if bed_path:
        logger.info(f"Using targeted regions BED: {bed_path}")
        cmd.extend(["--include", str(bed_path)])

    logger.debug(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=False
        )
        if result.stderr:
            try:
                stderr_text = result.stderr.decode('utf-8', errors='replace')
                logger.debug(f"NGSNGS stderr: {stderr_text}")
            except Exception:
                logger.debug("NGSNGS produced binary stderr output")
    except subprocess.CalledProcessError as e:
        logger.error(f"NGSNGS failed for {individual_id}")
        logger.error(f"Command: {' '.join(cmd)}")
        try:
            stderr_text = e.stderr.decode('utf-8', errors='replace') if e.stderr else "N/A"
            stdout_text = e.stdout.decode('utf-8', errors='replace') if e.stdout else "N/A"
            logger.error(f"stderr: {stderr_text}")
            logger.error(f"stdout: {stdout_text}")
        except Exception:
            logger.error("Could not decode error output (binary data)")
        raise

    files = {
        "fastq1": Path(f"{output_prefix}_R1.fq.gz"),
        "fastq2": Path(f"{output_prefix}_R2.fq.gz"),
        "vcf": vcf_path if vcf_path or mutation_rate else None,
        "mutations_txt": Path(f"{output_prefix}_mutations.txt"),
    }

    # Verify FASTQ outputs
    for key in ("fastq1", "fastq2"):
        path = files[key]
        if not path.exists():
            logger.error(f"Expected output file not found: {path}")
            raise FileNotFoundError(f"NGSNGS did not create {path}")

    logger.info(f"NGSNGS completed for {individual_id}")
    return files

def _run_ngsngs_worker(args: Tuple) -> Tuple[str, Dict[str, Path]]:
    individual_id, kwargs = args
    files = run_ngsngs(**kwargs)
    return individual_id, files

def simulate_individuals(
    matrix_context: dict,
    reference: Path,
    output_dir: Path,
    coverage: int,
    read_length: int,
    mutation_rate: float = 0.001,
    fragment_mean: int = 450,
    fragment_stdev: int = 75,
    vcf_dir: Optional[Path] = None,
    targeted_bed: Optional[Path] = None,
    ignore_missing_vcfs: bool = False,
    random_seed: Optional[int] = None,
    threads: int = 1,
) -> Dict[str, Dict[str, Path]]:
    logger.info("Starting individual simulations with NGSNGS")

    individuals_dir = output_dir / "individuals"
    individuals_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    cells = matrix_context["matrix"]["cells"]

    tasks = []
    for idx, cell in enumerate(cells):
        individual_id = cell["alias"]

        vcf_path = None
        if vcf_dir:
            for ext in [".vcf"]:
                candidate = vcf_dir / f"{individual_id}{ext}"
                if candidate.exists():
                    vcf_path = candidate
                    break
            if not vcf_path and not ignore_missing_vcfs:
                raise FileNotFoundError(f"VCF not found for {individual_id} in {vcf_dir}")
            if not vcf_path:
                logger.info(f"VCF not found for {individual_id}, using mutation rate")

        # determine seed
        ind_seed = (len(cells) + idx)
        logger.debug(f"Using random seed {ind_seed} for individual {individual_id}")
        kwargs = {
            "individual_id": individual_id,
            "reference": reference,
            "output_dir": individuals_dir,
            "coverage": coverage,
            "read_length": read_length,
            "fragment_mean": fragment_mean,
            "fragment_stdev": fragment_stdev,
            "mutation_rate": mutation_rate,
            "vcf_path": vcf_path,
            "bed_path": targeted_bed,
            "random_seed": ind_seed,
        }
        tasks.append((individual_id, kwargs))

    if threads == 1:
        for idx, (individual_id, kwargs) in enumerate(tasks):
            logger.info(f"Simulating individual {individual_id} ({idx+1}/{len(tasks)})")
            files = run_ngsngs(**kwargs)
            results[individual_id] = files
            logger.info(f"Completed simulation for {individual_id} ({idx+1}/{len(tasks)})")
    else:
        logger.info(f"Simulating individuals in parallel using {threads} threads")
        with Pool(processes=threads) as pool:
            for individual_id, files in pool.imap_unordered(_run_ngsngs_worker, tasks):
                results[individual_id] = files
                logger.info(f"Completed simulation for {individual_id}")
    logger.info(f"All {len(results)} individuals simulated")
    return results