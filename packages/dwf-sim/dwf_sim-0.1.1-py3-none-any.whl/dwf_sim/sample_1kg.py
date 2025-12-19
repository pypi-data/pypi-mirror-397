import logging
import random
from .vcf_utils import read_vcf_samples, extract_individual_vcfs
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import deque
import pandas as pd

logger = logging.getLogger(__name__)

def identify_families(
    vcf_samples: List[str],
    pedigree_path: Path
) -> Dict[str, str]:
    """
    Identify family relationships from pedigree file.
    
    Args:
        vcf_samples: List of samples in VCF
        pedigree_path: Path to pedigree file
    
    Returns:
        Dictionary mapping sample_id -> family_id (only for samples with relatives)
    """
    logger.info("Identifying family relationships...")
    
    vcf_set = set(vcf_samples)
    
    # Read pedigree
    ped = pd.read_csv(pedigree_path, sep=r'\s+', dtype=str)
    
    # Build adjacency list of relationships
    adj = {s: set() for s in vcf_set}
    
    for row in ped.itertuples(index=False):
        child = row.sampleID
        if child not in vcf_set:
            continue
        for parent in (row.fatherID, row.motherID):
            if parent != "0" and parent in vcf_set:
                adj[child].add(parent)
                adj[parent].add(child)
    
    # Find connected components (families)
    sample_to_family = {}
    visited = set()
    family_index = 1
    
    for s in vcf_samples:  # Keep deterministic order
        if s in visited:
            continue
        
        # BFS to find component
        comp = []
        queue = deque([s])
        visited.add(s)
        
        while queue:
            cur = queue.popleft()
            comp.append(cur)
            for nb in adj.get(cur, []):
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
        
        # If component size > 1, assign family ID
        if len(comp) > 1:
            fam_id = f"FAM{family_index}"
            family_index += 1
            for member in comp:
                sample_to_family[member] = fam_id
    
    logger.info(f"Identified {family_index - 1} families with >1 member")
    logger.info(f"{len(sample_to_family)} individuals have close relatives in VCF")
    
    return sample_to_family


def sample_without_family_overlap(
    pool: List[str],
    n: int,
    sample_to_family: Dict[str, str],
    seed: int = 42
) -> List[str]:
    """
    Sample n individuals from pool, avoiding family overlap.
    
    Args:
        pool: List of sample IDs to sample from
        n: Number of samples to pick
        sample_to_family: Dictionary mapping sample_id -> family_id
        seed: Random seed
    
    Returns:
        List of sampled sample IDs
    """
    rng = random.Random(seed)
    pool = pool[:]
    rng.shuffle(pool)
    
    picked = []
    used_families = set()
    
    for s in pool:
        if len(picked) == n:
            break
        
        fam = sample_to_family.get(s)
        if fam and fam in used_families:
            continue
        
        picked.append(s)
        if fam:
            used_families.add(fam)
    
    if len(picked) < n:
        logger.warning(f"Only found {len(picked)}/{n} unrelated samples in pool")
    
    return picked


def sample_individuals(
    vcf_samples: List[str],
    sample_table_path: Path,
    pedigree_path: Path,
    n_total: int,
    non_eur_fraction: float = 0.02,
    seed: int = 42
) -> List[str]:
    """
    Sample individuals from 1000 Genomes, avoiding family overlap.
    
    Args:
        vcf_samples: List of all samples in VCF
        sample_table_path: Path to sample population codes TSV
        pedigree_path: Path to pedigree file
        n_total: Total number of individuals to sample
        non_eur_fraction: Fraction of non-EUR individuals (default 0.02 = 2%)
        seed: Random seed
    
    Returns:
        List of sampled sample IDs
    """
    logger.info(f"Sampling {n_total} individuals (non-EUR fraction: {non_eur_fraction})")
    
    vcf_set = set(vcf_samples)
    
    # Read sample population codes
    samples = pd.read_csv(sample_table_path, sep='\t', dtype=str)
    samples = samples[samples["sample_id"].isin(vcf_set)].copy()
    
    # Split into EUR (non-FIN) and non-EUR
    eur_nonfin = samples[
        (samples["super_pop_code"] == "EUR") &
        (samples["pop_code"] != "FIN")
    ]["sample_id"].tolist()
    
    eur_nonfin_set = set(eur_nonfin)
    non_eur = [s for s in vcf_samples if s not in eur_nonfin_set]
    
    logger.info(f"Available: {len(eur_nonfin)} EUR (non-FIN), {len(non_eur)} non-EUR")
    
    # Calculate splits
    n_non_eur = int(n_total * non_eur_fraction)
    n_eur = n_total - n_non_eur
    
    logger.info(f"Target: {n_eur} EUR, {n_non_eur} non-EUR")
    
    # Identify families
    sample_to_family = identify_families(vcf_samples, pedigree_path)
    
    # Sample without family overlap
    picked_eur = sample_without_family_overlap(eur_nonfin, n_eur, sample_to_family, seed)
    picked_non_eur = sample_without_family_overlap(non_eur, n_non_eur, sample_to_family, seed + 1)
    
    picked = picked_eur + picked_non_eur
    
    logger.info(f"Sampled {len(picked)} unique individuals")
    logger.info(f"  EUR: {len(picked_eur)}, non-EUR: {len(picked_non_eur)}")
    
    if len(picked) < n_total:
        logger.warning(f"Only sampled {len(picked)}/{n_total} individuals")
    
    return picked


def sample_1kg(
    vcf_path: Path,
    sample_table: Path,
    pedigree: Path,
    reference: Path,
    output_dir: Path,
    matrix_size: int,
    non_eur_fraction: float = 0.02,
    seed: int = 42,
) -> Dict[str, Path]:
    """
    Sample individuals from 1000 Genomes VCF and extract to per-individual VCFs.
    
    Args:
        vcf_path: Path to multisample 1000 Genomes VCF
        sample_table: Path to sample_population_codes.tsv
        pedigree: Path to pedigree file
        output_dir: Output directory
        matrix_size: Matrix dimension (N x N)
        non_eur_fraction: Fraction of non-EUR individuals
        seed: Random seed
    
    Returns:
        Dictionary mapping cell_alias -> VCF path
    """
    logger.info("=" * 60)
    logger.info("1000 Genomes Sampling")
    logger.info("=" * 60)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Calculate total samples needed
    n_total = matrix_size * matrix_size
    
    # Get samples from VCF
    vcf_samples = read_vcf_samples(vcf_path)
    
    # Sample individuals
    selected = sample_individuals(
        vcf_samples=vcf_samples,
        sample_table_path=sample_table,
        pedigree_path=pedigree,
        n_total=n_total,
        non_eur_fraction=non_eur_fraction,
        seed=seed,
    )
    
    # Write sample list
    sample_list_file = output_dir / "sampled_individuals.txt"
    with open(sample_list_file, 'w') as f:
        for sample_id in selected:
            f.write(f"{sample_id}\n")
    logger.info(f"Sample list written to {sample_list_file}")
    
    # Extract VCFs
    vcf_dir = output_dir / "vcfs"
    extracted = extract_individual_vcfs(
        input_vcf=vcf_path,
        samples=selected,
        output_dir=vcf_dir,
        matrix_size=matrix_size,
        reference=reference
    )
    
    logger.info("=" * 60)
    logger.info(f"Sampled {len(extracted)} individuals")
    logger.info(f"VCFs: {vcf_dir}")
    logger.info("=" * 60)
    
    return extracted