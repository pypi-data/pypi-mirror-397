"""Main orchestration for DWF-Sim simulation."""

import logging
from pathlib import Path
from typing import Optional

from .matrix_context import create_matrix_context
from .simulate import simulate_individuals
from .pool import create_pools
from .utils import ensure_dir

logger = logging.getLogger(__name__)

def process_simulation(
    matrix_size: int,
    reference: Path,
    output_dir: Path,
    coverage: int = 30,
    read_length: int = 150,
    vcf_dir: Optional[Path] = None,
    mutation_rate: float = 0.001,
    targeted_bed: Optional[Path] = None,
    ignore_missing_vcfs: bool = False,
    read_mode: str = "fixed",
    pool_prefix: str = "P",
    fragment_mean: int = 450,
    fragment_stdev: int = 75,
    threads: int = 1
) -> None:
    """
    Run complete dwf-sim simulation pipeline.
    
    Steps:
        1. Create matrix context and tables
        2. Simulate read data for each individual with dwgsim
        3. Combine individuals into pools
    
    Args:
        matrix_size: Dimension of square matrix (N x N)
        reference: Path to reference genome FASTA
        output_dir: Output directory for all results
        coverage: Read coverage per individual
        read_length: Read length in bp
        vcf_dir: Optional directory with per-individual VCF files
        mutation_rate: Mutation rate if no VCFs provided
        targeted_bed: Optional BED file for targeted regions
        read_mode: Read distribution mode (fixed|poisson|uniform)
        pool_prefix: Prefix for pool IDs
        fragment_mean: Mean fragment size
        fragment_stdev: Fragment size standard deviation
    """
    logger.info("=" * 60)
    logger.info("dwf-sim simulation pipeline")
    logger.info("=" * 60)

    output_dir = ensure_dir(output_dir)
    
    # Step 1: Create matrix context
    logger.info("Step 1: Creating matrix context")
    matrix_context = create_matrix_context(
        matrix_size=matrix_size,
        output_dir=output_dir,
        pool_prefix=pool_prefix,
        pad_width=0
    )
    logger.info(f"Matrix: {matrix_size}x{matrix_size} = {len(matrix_context['matrix']['cells'])} individuals")

    # Step 2: Simulate individuals
    logger.info("Step 2: Simulating individuals with dwgsim")
    individual_files = simulate_individuals(
        matrix_context=matrix_context,
        reference=reference,
        output_dir=output_dir,
        coverage=coverage,
        read_length=read_length,
        vcf_dir=vcf_dir,
        mutation_rate=mutation_rate,
        targeted_bed=targeted_bed,
        ignore_missing_vcfs=ignore_missing_vcfs,
        threads=threads
    )

    # Step 3: Create pools
    logger.info("Step 3: Creating pooled data")
    create_pools(
        matrix_context=matrix_context,
        individual_files=individual_files,
        output_dir=output_dir,
        reference=reference,
        threads=threads
    )
    
    logger.info("=" * 60)
    logger.info("Simulation complete!")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"  - Matrix context: matrix_context.json/tsv")
    logger.info(f"  - Pool table: pooltable.tsv")
    logger.info(f"  - Decode table: decodetable.tsv")
    logger.info(f"  - Individual data: individuals/")
    logger.info(f"  - Pooled data: pools/")
    logger.info("=" * 60)
