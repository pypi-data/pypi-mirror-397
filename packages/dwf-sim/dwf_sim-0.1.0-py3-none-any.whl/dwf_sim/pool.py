"""Pool combination logic for FASTQs, BAMs, and VCFs."""

import logging
import subprocess
from multiprocessing import Pool
from .vcf_utils import merge_vcfs, convert_ngsngs_tsv_to_vcf
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

def rename_fastq(
    input_fastq: Path,
    output_fastq: Path,
    prefix: str,
) -> None:
    """
    Rename read IDs in a gzipped FASTQ using gunzip | awk | gzip.

    - Expects input_fastq to be gzipped
    - Produces gzipped output_fastq
    - Only changes the header line (NR % 4 == 1)
    - Only rewrites the first field ($1), preserving anything after the first space

    Equivalent AWK logic:
        gunzip -c in.fq.gz |
          awk -v p=PREFIX 'NR%4==1 { sub(/^@/, "@" p "_", $1) } { print }' |
          gzip -c > out.fq.gz
    """
    logger.debug(
        f"Renaming FASTQ {input_fastq.name} -> {output_fastq.name} with prefix '{prefix}'"
    )

    # gunzip -c input.fastq.gz
    p_gunzip = subprocess.Popen(
        ["gunzip", "-c", str(input_fastq)],
        stdout=subprocess.PIPE,
    )
    # awk -v p=prefix 'NR%4==1 { sub(/^@/, "@" p "_", $1) } { print }'
    awk_script = (
        r'NR%4==1 { c++; '
        r'sub(/^@/, "@" p "_" c "_", $1) } '
        r'{ print }'
    )
    p_awk = subprocess.Popen(
        ["awk", "-v", f"p={prefix}", awk_script],
        stdin=p_gunzip.stdout,
        stdout=subprocess.PIPE,
    )

    p_gunzip.stdout.close()  # allow gunzip to get SIGPIPE if awk exits

    # gzip -c > output_fastq
    with output_fastq.open("wb") as out_fh:
        p_gzip = subprocess.Popen(
            ["gzip", "-c"],
            stdin=p_awk.stdout,
            stdout=out_fh,
        )
        p_awk.stdout.close()  # allow awk to get SIGPIPE if gzip exits

        # Run the pipeline
        p_gzip.communicate()

    # Wait for upstream processes
    ret_gzip = p_gzip.returncode
    ret_awk = p_awk.wait()
    ret_gunzip = p_gunzip.wait()

    if any(rc != 0 for rc in (ret_gunzip, ret_awk, ret_gzip)):
        logger.error(
            "FASTQ renaming pipeline failed: "
            f"gunzip={ret_gunzip}, awk={ret_awk}, gzip={ret_gzip}"
        )
        raise subprocess.CalledProcessError(
            ret_gzip, "gzip (gunzip|awk|gzip pipeline)"
        )
    return output_fastq

def combine_fastqs(
    input_files: List[Path],
    output_file: Path,
) -> None:
    """
    Combine multiple FASTQ files into one (gzipped).
    
    Args:
        input_files: List of input FASTQ paths
        output_file: Output combined FASTQ path
    """
    logger.debug(f"Combining {len(input_files)} FASTQs -> {output_file.name}")
    
    with output_file.open("wb") as out_fh:
        for fq_path in input_files:
            with fq_path.open("rb") as in_fh:
                out_fh.write(in_fh.read())

def create_pools(
    matrix_context: dict,
    individual_files: Dict[str, Dict[str, Path]],
    output_dir: Path,
    reference: Path,
    threads: int = 1,
) -> None:
    """
    Create pooled FASTQs, BAMs, and VCFs from individual data.
    
    Uses the predefined paths from the matrix context (pooltable.tsv).
    
    Args:
        matrix_context: Matrix context dictionary
        individual_files: Dict mapping individual_id -> {fastq1, fastq2, bam, vcf}
        output_dir: Output directory for pools
        reference: Reference genome path
    """
    logger.info("Creating pooled data files")
    
    pools_dir = output_dir / "pools"
    individuals_dir = output_dir / "individuals"
    pools_dir.mkdir(parents=True, exist_ok=True)
    individuals_dir.mkdir(parents=True, exist_ok=True)
    
    # Process row pools
    for row_pool in matrix_context["pools"]["rows"]:
        pool_id = row_pool["pool_id"]
        logger.info(f"Creating row pool: {pool_id}")
        
        # Find all individuals in this row
        cells_in_pool = [
            c for c in matrix_context["matrix"]["cells"]
            if c["row_pool_id"] == pool_id
        ]
        individual_ids = [c["alias"] for c in cells_in_pool]
        
        # Add unique prefixes to FASTQ read names to avoid collisions
        rename_jobs = []
        for ind_id in individual_ids:
            fq1_in = individual_files[ind_id]["fastq1"]
            fq2_in = individual_files[ind_id]["fastq2"]
            fq1_out = pools_dir / f"{ind_id}_R1.fq.gz"
            fq2_out = pools_dir / f"{ind_id}_R2.fq.gz"

            rename_jobs.append((fq1_in, fq1_out, ind_id))
            rename_jobs.append((fq2_in, fq2_out, ind_id))

        # Run all rename_fastq() calls in parallel
        with Pool(processes=threads) as pool:   # choose number of processes
            pool.starmap(rename_fastq, rename_jobs)

        # Update paths after all renaming finishes
        for ind_id in individual_ids:
            individual_files[ind_id]["fastq1"] = pools_dir / f"{ind_id}_R1.fq.gz"
            individual_files[ind_id]["fastq2"] = pools_dir / f"{ind_id}_R2.fq.gz"

        # Combine FASTQs
        fq1_files = [individual_files[ind]["fastq1"] for ind in individual_ids]
        fq2_files = [individual_files[ind]["fastq2"] for ind in individual_ids]
        
        logger.debug(f"Row pool {pool_id} individuals: {individual_ids}")

        pool_fq1 = pools_dir / f"{pool_id}_1.fq.gz"
        pool_fq2 = pools_dir / f"{pool_id}_2.fq.gz"
        
        combine_fastqs(fq1_files, pool_fq1)
        combine_fastqs(fq2_files, pool_fq2)
        
        # Convert mutations dump to VCF
        for ind_id in individual_ids:
            vcf_path = individual_files[ind_id]["vcf"]
            if not vcf_path:
                individual_files[ind_id]["vcf"] = individuals_dir / f"{ind_id}.vcf.gz"
                convert_ngsngs_tsv_to_vcf(
                    input_tsv=individual_files[ind_id]["mutations_txt"],
                    output_vcf=individual_files[ind_id]["vcf"],
                    reference=reference,
                    sample_id=ind_id,
                )

        vcf_files = [individual_files[ind]["vcf"] for ind in individual_ids]
        pool_vcf = pools_dir / f"{pool_id}.vcf.gz"
        merge_vcfs(vcf_files, pool_vcf, reference)
        logger.info(f"Merged {len(vcf_files)} VCFs -> {pool_vcf.name}")
    
    # Process column pools
    for col_pool in matrix_context["pools"]["columns"]:
        pool_id = col_pool["pool_id"]
        logger.info(f"Creating column pool: {pool_id}")
        
        cells_in_pool = [
            c for c in matrix_context["matrix"]["cells"]
            if c["col_pool_id"] == pool_id
        ]
        individual_ids = [c["alias"] for c in cells_in_pool]
        
        logger.debug(f"Column pool {pool_id} individuals: {individual_ids}")

        # Combine FASTQs
        fq1_files = [individual_files[ind]["fastq1"] for ind in individual_ids]
        fq2_files = [individual_files[ind]["fastq2"] for ind in individual_ids]
        
        pool_fq1 = pools_dir / f"{pool_id}_1.fq.gz"
        pool_fq2 = pools_dir / f"{pool_id}_2.fq.gz"
        
        combine_fastqs(fq1_files, pool_fq1)
        combine_fastqs(fq2_files, pool_fq2)
        
        # Combine VCFs
        vcf_files = [individual_files[ind]["vcf"] for ind in individual_ids]
        pool_vcf = pools_dir / f"{pool_id}.vcf.gz"
        merge_vcfs(vcf_files, pool_vcf, reference)
        logger.info(f"Merged {len(vcf_files)} VCFs -> {pool_vcf.name}")
    
    logger.info("All pools created successfully")