"""VCF manipulation utilities using bcftools."""

import logging
import subprocess
import shutil
import pysam
from .matrix_context import column_label_from_index
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

Interval = Tuple[int, int, str, int]  # (start1, end1, panel_name, length)

def count_variants(vcf_path: Path) -> int:
    cmd = ["bcftools", "view", "-H", str(vcf_path)]
    count_lines = subprocess.run(cmd, capture_output=True, text=True)
    variant_count = len(count_lines.stdout.strip().split('\n')) if count_lines.stdout.strip() else 0
    return variant_count

def read_vcf_samples(vcf_path: Path) -> List[str]:
    """Extract sample list from VCF using bcftools."""
    logger.info("Extracting sample list from VCF...")
    cmd = ["bcftools", "query", "-l", str(vcf_path)]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    samples = [line.strip() for line in result.stdout.split('\n') if line.strip()]
    logger.info(f"VCF contains {len(samples)} samples")
    return samples

def tabix_index(vcf_path: Path) -> None:
    """Index a bgzipped VCF with tabix."""
    vcf_path = Path(vcf_path)
    cmd = ["tabix", "-p", "vcf", str(vcf_path)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"tabix failed for {vcf_path}")
        logger.error(f"Command: {' '.join(cmd)}")
        logger.error(f"stderr: {e.stderr}")
        raise

def bgzip_vcf(input_vcf: Path, output_vcf: Path) -> Path:
    """
    Bgzip a VCF file.
    
    Args:
        input_vcf: uncompressed VCF
        output_vcf: output .vcf.gz path
    
    Returns:
        Path to bgzipped VCF
    """
    cmd = ["bgzip", "-c", str(input_vcf)]
    try:
        with open(output_vcf, "wb") as out:
            subprocess.run(cmd, stdout=out, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"bgzip failed for {input_vcf}")
        logger.error(f"Command: {' '.join(cmd)}")
        logger.error(f"stderr: {e.stderr}")
        raise
    return output_vcf


def index_reference(reference: Path) -> None:
    """
    Index reference FASTA with samtools faidx if not already indexed.
    
    Args:
        reference: Path to reference FASTA
    """
    reference = Path(reference)
    fai_path = reference.with_suffix(reference.suffix + ".fai")
    
    if fai_path.exists():
        logger.debug(f"Reference index exists: {fai_path}")
        return
    
    logger.info(f"Indexing reference: {reference}")
    cmd = ["samtools", "faidx", str(reference)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"samtools faidx failed for {reference}")
        logger.error(f"Command: {' '.join(cmd)}")
        logger.error(f"stderr: {e.stderr}")
        raise

def bgzip_vcf(input_vcf: Path, output_vcf: Path) -> Path:
    """
    Bgzip a VCF file.
    
    Args:
        input_vcf: uncompressed VCF
        output_vcf: output .vcf.gz path
    
    Returns:
        Path to bgzipped VCF
    """
    cmd = ["bgzip", "-c", str(input_vcf)]
    try:
        with open(output_vcf, "wb") as out:
            subprocess.run(cmd, stdout=out, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"bgzip failed for {input_vcf}")
        logger.error(f"Command: {' '.join(cmd)}")
        logger.error(f"stderr: {e.stderr}")
        raise
    return output_vcf

def normalize_vcf(
    input_vcf: Path,
    output_vcf: Path,
    reference: Path,
    target_bed: Optional[Path] = None,
) -> Path:
    """
    Normalize a VCF: split multi-allelic sites and remove duplicates.
    
    Args:
        input_vcf: input bgzipped VCF
        output_vcf: normalized bgzipped VCF
        reference: reference genome FASTA
    
    Returns:
        Path to normalized, bgzipped, and tabix-indexed VCF
    """
    input_vcf = Path(input_vcf)
    output_vcf = Path(output_vcf)
    reference = Path(reference)
    
    # Ensure reference is indexed
    index_reference(reference)
    
    # Ensure input VCF is bgzipped
    if input_vcf.suffix != ".gz":
        temp_bgzipped = input_vcf.parent / f"{input_vcf.stem}.vcf.gz"
        bgzip_vcf(input_vcf, temp_bgzipped)
        input_vcf = temp_bgzipped

    # Ensure input VCF is indexed
    if not Path(f"{input_vcf}.tbi").exists():
        tabix_index(input_vcf)
    
    cmd = [
        "bcftools", "norm",
        "-m", "-both",
        "-d", "exact",
        "-f", str(reference),
        "--force",
        "-Oz",
        "-o", str(output_vcf)
    ]

    if target_bed:
        cmd.extend(["-R", str(target_bed)])
    
    cmd.append(str(input_vcf))
    
    logger.debug(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stderr:
            logger.debug(f"bcftools norm stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"bcftools norm failed")
        logger.error(f"Command: {' '.join(cmd)}")
        logger.error(f"stderr: {e.stderr}")
        logger.error(f"stdout: {e.stdout}")
        raise
    
    tabix_index(output_vcf)
    return output_vcf


def merge_vcfs(
    input_vcfs: List[Path],
    output_vcf: Path,
    reference: Path,
) -> Path:
    """
    Merge VCF files and keep unique variation.
    
    SIMPLIFIED: Takes list of VCF paths directly (not sample_ids + directory).
    
    Args:
        input_vcfs: list of VCF paths (will be bgzipped if needed)
        output_vcf: final merged VCF.gz path
        reference: reference genome FASTA
    
    Returns:
        Path to merged, normalized VCF
    """
    output_vcf = Path(output_vcf)
    tmp_dir = output_vcf.parent / ".tmp_vcf_merge"
    tmp_dir.mkdir(exist_ok=True)
    
    logger.debug(f"Merging {len(input_vcfs)} VCFs")
    
    # Ensure all VCFs are bgzipped and indexed
    bgzipped_vcfs = []
    for i, vcf in enumerate(input_vcfs):
        vcf = Path(vcf)
        if vcf.suffix == ".gz":
            bgzipped = vcf
        else:
            bgzipped = tmp_dir / f"tmp_{i}.vcf.gz"
            bgzip_vcf(vcf, bgzipped)
        
        if not Path(f"{bgzipped}.tbi").exists():
            tabix_index(bgzipped)
        
        bgzipped_vcfs.append(bgzipped)
    
    # Merge
    tmp_merged = tmp_dir / "merged.tmp.vcf.gz"
    merge_cmd = [
        "bcftools", "merge",
        "-m", "none",
        "--force-samples",
        "-Oz",
        "-o", str(tmp_merged),
    ] + [str(v) for v in bgzipped_vcfs]
    
    logger.debug(f"Running: {' '.join(merge_cmd)}")
    try:
        result = subprocess.run(merge_cmd, check=True, capture_output=True, text=True)
        if result.stderr:
            logger.debug(f"bcftools merge stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"bcftools merge failed")
        logger.error(f"Command: {' '.join(merge_cmd)}")
        logger.error(f"stderr: {e.stderr}")
        logger.error(f"stdout: {e.stdout}")
        raise
    
    # Normalize
    normalize_vcf(tmp_merged, output_vcf, reference)
    
    # Cleanup
    shutil.rmtree(tmp_dir, ignore_errors=True)
    
    return output_vcf

def call_state_by_type(tp: Path, fp: Path, fn: Path) -> Dict[str, Dict[str, int]]:
    """
    Count TP/FP/FN by variant type via bcftools.
    
    Args:
        tp: True positive VCF
        fp: False positive VCF
        fn: False negative VCF
    
    Returns:
        Dictionary: {'snv': {'TP':..,'FP':..,'FN':..}, 'indel': {...}, 'both': {...}}
    """
    tp_c = count_variant_types_bcftools(tp)
    fp_c = count_variant_types_bcftools(fp)
    fn_c = count_variant_types_bcftools(fn)
    
    out = {}
    for k in ("snv", "indel", "both"):
        out[k] = {"TP": tp_c[k], "FP": fp_c[k], "FN": fn_c[k]}
    return out


def count_variant_types_bcftools(vcf: Path) -> Dict[str, int]:
    """
    Count variants by type using bcftools.
    
    Args:
        vcf: VCF file to count
    
    Returns:
        Dictionary: {'snv': N, 'indel': N, 'both': N}
    """
    vcf = Path(vcf)
    snv   = _wc_l(["bcftools", "view", "-H", "-v", "snps", str(vcf)])
    indel = _wc_l(["bcftools", "view", "-H", "-v", "indels", str(vcf)])
    both  = _wc_l(["bcftools", "view", "-H", str(vcf)])
    return {"snv": snv, "indel": indel, "both": both}


def _wc_l(cmd: List[str]) -> int:
    """Count lines from a command output."""
    import subprocess
    p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=False)
    p2 = subprocess.Popen(
        ["wc", "-l"],
        stdin=p1.stdout,
        stdout=subprocess.PIPE,
        text=True
    )
    p1.stdout.close()
    out, _ = p2.communicate()
    return int(out.strip()) if out and out.strip() else 0


def intersect_vcfs_vcfeval(
    a_vcf: Path,
    b_vcf: Path,
    sdf_dir: Path,
    out_prefix: Path,
    threads: int = 4,
    mem_gb: int = 8
) -> Dict[str, Path]:
    """
    Intersect two VCFs using RTG vcfeval.
    
    Args:
        a_vcf: first VCF(.gz)
        b_vcf: second VCF(.gz) - gold standard
        sdf_dir: RTG SDF directory for the reference
        out_prefix: path prefix for output files
        singularity_img: optional path to rtgtools .sif
        threads: vcfeval --threads
        mem_gb: Java heap for rtg (-Xmx)
    
    Returns:
        Dictionary: {'both': tp.vcf.gz, 'a_only': fp.vcf.gz, 'b_only': fn.vcf.gz}
    """
    import tempfile
    import shutil
    import subprocess
    
    calls = Path(a_vcf).resolve()
    background = Path(b_vcf).resolve()
    sdf_dir = Path(sdf_dir)
    out_prefix = Path(out_prefix)
    
    with tempfile.TemporaryDirectory(prefix="vcfeval_tmp_") as tmp_root:
        tmp_root = Path(tmp_root)
        outdir = tmp_root / "vcfeval_out"
        
        cmd = [
            "rtg", f"RTG_MEM={mem_gb}G", "vcfeval",
            "-t", str(sdf_dir),
            "-b", str(background),
            "-c", str(calls),
            "--squash-ploidy", "--sample", "ALT,ALT",
            "--threads", str(threads),
            "--output-mode", "split",
            "-o", str(outdir),
        ]
        

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("RTG vcfeval failed")
            print("Return code:", e.returncode)
            print("STDOUT:", e.stdout.decode() if e.stdout else "")
            print("STDERR:", e.stderr.decode() if e.stderr else "")
        
        # Copy outputs
        tp_o = out_prefix.with_suffix(".tp.vcf.gz")
        fp_o = out_prefix.with_suffix(".fp.vcf.gz")
        fn_o = out_prefix.with_suffix(".fn.vcf.gz")
        
        shutil.copyfile(outdir / "tp.vcf.gz", tp_o)
        tabix_index(tp_o)
        shutil.copyfile(outdir / "fp.vcf.gz", fp_o)
        tabix_index(fp_o)
        shutil.copyfile(outdir / "fn.vcf.gz", fn_o)
        tabix_index(fn_o)
    
    return {'both': tp_o, 'a_only': fp_o, 'b_only': fn_o}

def normalize_all_vcfs(
    vcf_dict: Dict[str, Path],
    output_dir: Path,
    reference: Path,
    bed: Optional[Path] = None,
    label: str = "vcf",
) -> Dict[str, Path]:
    """
    Normalize all VCFs in a dictionary.
    
    Args:
        vcf_dict: Dictionary mapping ID -> VCF path
        output_dir: Directory for normalized VCFs
        reference: Reference genome
        bed: Optional BED file
        label: Label for output files
    
    Returns:
        Dictionary mapping ID -> normalized VCF path
    """
    logger.info(f"Normalizing {len(vcf_dict)} {label} VCFs...")
    
    norm_dir = output_dir / f"normalized_{label}"
    norm_dir.mkdir(parents=True, exist_ok=True)
    
    normalized = {}
    for vcf_id, vcf_path in vcf_dict.items():
        logger.debug(f"  Normalizing {vcf_id}")
        norm_vcf = normalize_vcf(
            vcf_path,
            norm_dir / f"{vcf_id}_norm.vcf.gz",
            reference,
            target_bed=bed
        )
        normalized[vcf_id] = norm_vcf
    
    logger.info(f"Normalized {len(normalized)} {label} VCFs")
    return normalized

def find_private_variants(
    individual_id: str,
    individual_vcf: Path,
    other_vcfs: List[Path],
    output_dir: Path,
) -> Path:
    """
    Find variants private to an individual using bcftools isec.
    
    Assumes all VCFs are already normalized.
    
    Args:
        individual_id: ID of the individual
        individual_vcf: Normalized VCF for the individual
        other_vcfs: Normalized VCFs for all other individuals in their pools
        output_dir: Working directory
    
    Returns:
        Path to VCF with private variants
    """
    logger.debug(f"Finding private variants for {individual_id}")
    
    # Use bcftools isec to find variants unique to individual
    isec_dir = output_dir / individual_id
    isec_dir.mkdir(exist_ok=True)
    
    cmd = [
        "bcftools", "isec",
        "-n=1",  # Present in exactly 1 file
        "-w", "1",  # Write the first file's unique variants
        "-c", "none",
        "-p", str(isec_dir),
        "-Oz",
        "-W=tbi",
        str(individual_vcf)
    ] + [str(v) for v in other_vcfs]
    
    logger.debug(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"bcftools isec failed for {individual_id}")
        logger.error(f"stderr: {e.stderr}")
        raise
    
    # Output is in 0000.vcf.gz (first file's unique variants)
    private_vcf = isec_dir / "0000.vcf.gz"
    
    if not private_vcf.exists():
        logger.error(f"Private variants VCF not created: {private_vcf}")
        raise FileNotFoundError(f"bcftools isec did not create {private_vcf}")

    return private_vcf

def convert_vcf_to_dwgsim_format(
    input_vcf: Path,
    output_vcf: Path,
    reference: Path,
    sample_id: str,
) -> Path:
    """
    Convert 1000 Genomes VCF to dwgsim format.
    
    Handles overlapping variants by keeping only non-overlapping ones.
    """
    
    logger.debug(f"Converting {input_vcf.name} to dwgsim format")
    
    # Read reference to get contig info
    fasta = pysam.FastaFile(str(reference))
    
    # Open input VCF
    vcf_in = pysam.VariantFile(str(input_vcf))
    
    # Create output VCF with dwgsim headers
    header = pysam.VariantHeader()
    
    # Add contigs from reference
    for contig in fasta.references:
        length = fasta.get_reference_length(contig)
        header.add_line(f'##contig=<ID={contig},length={length}>')
    
    # Add INFO fields
    header.add_line('##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">')
    header.add_line('##INFO=<ID=pl,Number=1,Type=Integer,Description="Phasing: 1=HET contig1, 2=HET contig2, 3=HOM both">')
    header.add_line('##INFO=<ID=mt,Number=1,Type=String,Description="Mutation Type: SUBSTITUTE/INSERT/DELETE">')
    
    # Write uncompressed VCF
    vcf_out = pysam.VariantFile(str(output_vcf), 'w', header=header)
    
    converted = 0
    skipped = 0
    overlaps = 0
    
    # Track last end position per chromosome to detect overlaps
    last_end = {}  # chrom -> end_position
    
    for record in vcf_in:
        # Skip if not biallelic
        if len(record.alts) != 1:
            skipped += 1
            continue
        
        # Get genotype for this sample
        gt = record.samples[sample_id]['GT']
        
        # Skip if no call or homozygous reference
        if None in gt or gt == (0, 0):
            skipped += 1
            continue
        
        # Calculate variant span
        ref_len = len(record.ref)
        variant_start = record.pos
        variant_end = record.pos + ref_len
        
        # Check for overlap with previous variant on same chromosome
        if record.contig in last_end:
            if variant_start < last_end[record.contig]:
                overlaps += 1
                continue
        
        # Create new record
        new_record = vcf_out.new_record(
            contig=record.contig,
            start=record.start,
            stop=record.stop,
            alleles=record.alleles,
            id=record.id,
            qual=100,
            filter='PASS'
        )
        
        # Determine pl based on genotype
        if gt == (0, 1):
            pl = 1
            af = 0.5
        elif gt == (1, 0):
            pl = 2
            af = 0.5
        elif gt == (1, 1):
            pl = 3
            af = 1.0
        else:
            skipped += 1
            continue
        
        # Determine mutation type
        alt_len = len(record.alts[0])
        
        if ref_len == alt_len:
            mt = "SUBSTITUTE"
        elif ref_len < alt_len:
            mt = "INSERT"
        else:
            mt = "DELETE"
        
        # Add INFO fields
        new_record.info['AF'] = af
        new_record.info['pl'] = pl
        new_record.info['mt'] = mt
        
        vcf_out.write(new_record)
        
        # Update last end position for this chromosome
        last_end[record.contig] = variant_end
        converted += 1
    
    vcf_in.close()
    vcf_out.close()
    fasta.close()
    
    logger.debug(f"Converted {converted} variants, skipped {skipped}, filtered {overlaps} overlaps")
    
    return output_vcf

def convert_vcf_to_ngsngs_format(
    input_vcf: Path,
    output_vcf: Path,
    reference: Path,
    sample_id: str,
) -> Path:
    """
    Convert 1000 Genomes VCF to ngsngs format. Removes overlapping variants.
    """
    
    logger.debug(f"Converting {input_vcf.name} to ngsngs format")
    
    # Read reference to get contig info
    fasta = pysam.FastaFile(str(reference))
    
    # Open input VCF
    vcf_in = pysam.VariantFile(str(input_vcf))
    
    # Create output VCF with ngsngs headers
    header = pysam.VariantHeader()
    
    # Add contigs from reference
    ref_info = {}
    for contig in fasta.references:
        ref_info[contig] = fasta.get_reference_length(contig)
        length = fasta.get_reference_length(contig)
    
    # Add contigs from input VCF (in case any are missing)
    for contig in vcf_in.header.contigs:
        length = vcf_in.header.contigs[contig].length
        if contig not in ref_info or ref_info[contig] != length:
            raise ValueError(f"Contig {contig} in VCF not found in reference FASTA, or length mismatch. {ref_info.get(contig, 'N/A')} vs {length}")
        header.add_line(f'##contig=<ID={contig},length={length}>')
    
    # Add INFO fields
    header.add_meta('INFO', items=[('ID', 'AF'), ('Number', 'A'), ('Type', 'Float'), ('Description', 'Allele Frequency')])
    header.add_meta('INFO', items=[('ID', 'pl'), ('Number', '1'), ('Type', 'Integer'), ('Description', 'Phasing: 1=HET contig1, 2=HET contig2, 3=HOM both')])
    header.add_meta('INFO', items=[('ID', 'mt'), ('Number', '1'), ('Type', 'String'), ('Description', 'Mutation Type: SUBSTITUTE/INSERT/DELETE')])
    
    # Add FORMAT field
    header.add_meta('FORMAT', items=[('ID', 'GT'), ('Number', '1'), ('Type', 'String'), ('Description', 'Genotype')])

    # Add sample to header
    header.add_sample(sample_id)

    # Write uncompressed VCF
    vcf_out = pysam.VariantFile(str(output_vcf), 'w', header=header)
    
    converted = 0
    skipped = 0
    overlaps = 0
    
    # Track last end position per chromosome to detect overlaps
    last_end = {}  # chrom -> end_position
    
    for record in vcf_in:

        if len(record.alts) != 1:
            skipped += 1
            continue
        
        # Get genotype for this sample
        gt = record.samples[sample_id]['GT']
        
        # Skip if no call or homozygous reference
        if None in gt or gt == (0, 0):
            skipped += 1
            continue

        # Calculate variant span
        ref_len = len(record.ref)
        variant_start = record.pos
        variant_end = record.pos + ref_len
        
        # Check for overlap with previous variant on same chromosome
        if record.contig in last_end:
            if variant_start < last_end[record.contig]:
                overlaps += 1
                continue
        
        # Create new record
        new_record = vcf_out.new_record(
            contig=record.contig,
            start=record.start,
            stop=record.stop,
            alleles=record.alleles,
            id=record.id,
            qual=100,
            filter='PASS'
        )
        
        # Determine pl based on genotype
        if gt == (0, 1):
            pl = 1
            af = 0.5
        elif gt == (1, 0):
            pl = 2
            af = 0.5
        elif gt == (1, 1):
            pl = 3
            af = 1.0
        else:
            skipped += 1
            continue
        
        # Add genotype to sample
        new_record.samples[sample_id]['GT'] = record.samples[sample_id]['GT']
        #new_record.samples[sample_id].phased = record.samples[sample_id].phased

        # Determine mutation type
        alt_len = len(record.alts[0])
        
        if ref_len == alt_len:
            mt = "SUBSTITUTE"
        elif ref_len < alt_len:
            mt = "INSERT"
        else:
            mt = "DELETE"
        
        # Add INFO fields
        new_record.info['AF'] = af
        new_record.info['pl'] = pl
        new_record.info['mt'] = mt
        
        vcf_out.write(new_record)
        
        # Update last end position for this chromosome
        last_end[record.contig] = variant_end
        converted += 1
    
    vcf_in.close()
    vcf_out.close()
    fasta.close()
    
    logger.debug(f"Converted {converted} variants, skipped {skipped}, filtered {overlaps} overlaps")
    
    return output_vcf

def convert_ngsngs_tsv_to_vcf(
    input_tsv: Path,
    output_vcf: Path,
    reference: Path,
    sample_id: str,
) -> Path:
    """
    Convert NGSNGS mutations file TSV to VCF format.
    """
    
    logger.debug(f"Converting {input_tsv.name} to VCF format")
    
    # Read reference to get contig info
    fasta = pysam.FastaFile(str(reference))
    # Create output VCF with headers
    header = pysam.VariantHeader()
    
    # Add INFO fields
    header.add_meta('INFO', items=[('ID', 'AF'), ('Number', 'A'), ('Type', 'Float'), ('Description', 'Allele Frequency')])
    header.add_meta('INFO', items=[('ID', 'pl'), ('Number', '1'), ('Type', 'Integer'), ('Description', 'Phasing: 1=HET contig1, 2=HET contig2, 3=HOM both')])
    header.add_meta('INFO', items=[('ID', 'mt'), ('Number', '1'), ('Type', 'String'), ('Description', 'Mutation Type: SUBSTITUTE/INSERT/DELETE')])
    
    # Add FORMAT field
    header.add_meta('FORMAT', items=[('ID', 'GT'), ('Number', '1'), ('Type', 'String'), ('Description', 'Genotype')])

    # Add sample to header
    header.add_sample(sample_id)

    # Write uncompressed VCF
    vcf_out = pysam.VariantFile(str(output_vcf), 'w', header=header)
    
    skipped = 0
    # Create dict of TSV records and sort by contig and position:
    records = []
    with open(input_tsv, 'r') as tsv_file:
        for line in tsv_file:
            fields = line.strip().split('\t')
            contig, interval = fields[0].split(':')
            int_start, int_end = interval.split('-')
            pos = int(fields[1]) + int(int_start)  # Convert to 1-based position
            ref = fields[2]
            alt = fields[3]
            gt_str='1/1' # Currently NGSNGS only supports homozygous mutations
            records.append((contig, pos, ref, alt, gt_str))

    records.sort(key=lambda x: (x[0], x[1]))

    for contig, pos, ref, alt, gt_str in records:
            
            gt = tuple(int(x) for x in gt_str.split('/'))
            
            if None in gt or gt == (0, 0):
                skipped += 1
                continue
            
            # Add contig to header if missing
            if contig not in vcf_out.header.contigs:
                length = fasta.get_reference_length(contig)
                vcf_out.header.add_line(f'##contig=<ID={contig},length={length}>')

            # Determine variant span
            ref_len = len(ref)
            alt_len = len(alt)

            # Create new record
            new_record = vcf_out.new_record(
                contig=contig,
                start=pos - 1,
                stop=pos - 1 + ref_len,
                alleles=(ref, alt),
                id='.',
                qual=100,
                filter='PASS'
            )
            
            # Determine pl based on genotype
            if gt == (0, 1):
                pl = 1
                af = 0.5
            elif gt == (1, 0):
                pl = 2
                af = 0.5
            elif gt == (1, 1):
                pl = 3
                af = 1.0
            else:
                skipped += 1
                continue
            
            # Add genotype to sample
            new_record.samples[sample_id]['GT'] = gt
            
            if ref_len == alt_len:
                mt = "SUBSTITUTE"
            elif ref_len < alt_len:
                mt = "INSERT"
            else:
                mt = "DELETE"
            
            # Add INFO fields
            new_record.info['AF'] = af
            new_record.info['pl'] = pl
            new_record.info['mt'] = mt
            vcf_out.write(new_record)

    vcf_out.close()
    fasta.close()
    
    logger.debug(f"Skipped {skipped}")
    
    return output_vcf

def extract_individual_vcfs(
    input_vcf: Path,
    samples: List[str],
    output_dir: Path,
    matrix_size: int,
    reference: Path,
    ) -> Dict[str, Path]:
    """
    Extract per-individual VCFs and convert to dwgsim format.
    
    Args:
        input_vcf: Input multisample VCF
        samples: List of sample IDs to extract
        output_dir: Output directory for VCFs
        matrix_size: Matrix size (for cell alias generation)
        reference: Reference genome (for contig headers)
    
    Returns:
        Dictionary mapping cell_alias -> VCF path
    """
    logger.info(f"Extracting {len(samples)} individual VCFs...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cell_aliases = []
    for row in range(matrix_size):
        for col in range(matrix_size):
            row_label = str(row + 1)
            col_label = column_label_from_index(col + 1)
            cell_aliases.append(f"{col_label}{row_label}")
    
    # Map samples to cell aliases
    sample_to_alias = {}
    for i, sample_id in enumerate(samples[:len(cell_aliases)]):
        sample_to_alias[sample_id] = cell_aliases[i]
    
    # Create temp directory for intermediate files
    dwgsim_dir = output_dir / "dwgsim"
    dwgsim_dir.mkdir(exist_ok=True)
    ngsngs_dir = output_dir / "ngsngs"
    ngsngs_dir.mkdir(exist_ok=True)

    # Extract each individual
    extracted = {}
    for sample_id, alias in sample_to_alias.items():
        logger.debug(f"Processing {sample_id} -> {alias}")
        
        extracted_vcf = output_dir / f"{alias}.vcf.gz"
        
        cmd = [
            "bcftools", "view",
            "-s", sample_id,
            "-c", "1",
            "-O", "z",
            "-W=tbi",
            "-o", str(extracted_vcf),
            str(input_vcf)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        convert_vcf_to_dwgsim_format(extracted_vcf, dwgsim_dir / f"{alias}.vcf", reference, sample_id)
        convert_vcf_to_ngsngs_format(extracted_vcf, ngsngs_dir / f"{alias}.vcf", reference, sample_id)
        
        extracted[alias] = Path(str(ngsngs_dir / f"{alias}.vcf"))
    
    # shutil.rmtree(temp_dir)
    
    logger.info(f"Extracted and converted {len(extracted)} individual VCFs")
    
    return extracted
