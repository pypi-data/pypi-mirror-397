import argparse
import sys
from pathlib import Path
from .main import process_simulation
from .benchmark import benchmark_caller
from .benchmark_pins import benchmark_private_variants
from .sample_1kg import sample_1kg
from .utils import setup_logging
from .data_files import get_data_file

def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="dwf-sim: Simulate two-dimensional overlapped pool sequencing data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Simulate command
    sim_parser = subparsers.add_parser('simulate', help='Run simulation')
    # Required arguments
    sim_parser.add_argument("--matrix-size", type=int, required=True, help="Matrix dimension (N x N)")
    sim_parser.add_argument("--reference", type=Path, required=True, help="Reference genome FASTA")
    sim_parser.add_argument("--output-dir", type=Path, required=True, help="Output directory")

    # Sequencing parameters
    sim_parser.add_argument("--coverage", type=int, default=30, help="Read coverage per individual")
    sim_parser.add_argument("--read-length", type=int, default=150, help="Read length (bp)")
    sim_parser.add_argument("--fragment-mean", type=int, default=450, help="Mean fragment size (outer distance)")
    sim_parser.add_argument("--fragment-stdev", type=int, default=75, help="Fragment size std dev")
    sim_parser.add_argument("--read-mode", type=str, choices=["fixed", "poisson", "uniform"], 
                       default="fixed", help="Read distribution mode for pooling")
    # Variant parameters
    sim_parser.add_argument("--vcf-dir", type=Path, default=None, help="Per-individual VCF directory (optional)")
    sim_parser.add_argument("--mutation-rate", type=float, default=0.001, help="Mutation rate if no VCFs")
    sim_parser.add_argument("--targeted-bed", type=Path, default=None, help="BED file for targeted regions (optional)")
    sim_parser.add_argument("--ignore-missing-vcfs", action="store_true", default=False, help="Ignore missing VCF files and use mutation rate")

    # Other parameters
    sim_parser.add_argument("--pool-prefix", type=str, default="P", help="Pool ID prefix")
    sim_parser.add_argument("--random-seed", type=int, default=None, help="Random seed for reproducibility")
    sim_parser.add_argument("--threads", type=int, default=1, help="Number of threads for simulation")
    sim_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    # Benchmark command
    bench_parser = subparsers.add_parser('benchmark', help='Benchmark variant calls')
    bench_parser.add_argument('--matrix-context', type=Path, required=True,
                             help='Path to matrix_context.json from simulation')
    bench_parser.add_argument('--gold-standard-dir', type=Path, required=True,
                             help='Directory with gold standard pool VCFs')
    bench_parser.add_argument('--caller-dir', type=Path, required=True,
                             help='Directory with caller VCFs to benchmark')
    bench_parser.add_argument('--caller-name', type=str, required=True,
                             help='Name of the variant caller')
    bench_parser.add_argument('--filtration-status', type=str, default=None,
                                help='Filtration status of the VCFs being benchmarked')
    bench_parser.add_argument('--coverage', type=int, default=None,
                            help='Sequencing coverage used in simulation')
    bench_parser.add_argument('--matrix-size', type=int, default=None,
                            help='Matrix size used in simulation')
    bench_parser.add_argument('--output-dir', type=Path, required=True)
    bench_parser.add_argument('--reference', type=Path, required=True)
    bench_parser.add_argument('--sdf-dir', type=Path, required=True,
                             help='RTG SDF directory')
    bench_parser.add_argument('--bed', type=Path, default=None)
    bench_parser.add_argument('--caller-suffix', type=str, default='vcf.gz')
    bench_parser.add_argument('--output-filename', type=str, default=None,
                             help='Output filename (default: pool_results.tsv)')
    bench_parser.add_argument('--verbose', action='store_true')

    pins_parser = subparsers.add_parser('benchmark-pins', help='Benchmark private individual variants')
    pins_parser.add_argument('--matrix-context', type=Path, required=True,
                            help='Path to matrix_context.json from simulation')
    pins_parser.add_argument('--gold-standard-dir', type=Path, required=True,
                            help='Directory with gold standard VCFs for individuals')
    pins_parser.add_argument('--caller-dir', type=Path, required=True,
                            help='Directory with caller VCFs for individuals')
    pins_parser.add_argument('--filtration-status', type=str, default=None,
                                help='Filtration status of the VCFs being benchmarked')
    pins_parser.add_argument('--coverage', type=int, default=None,
                            help='Sequencing coverage used in simulation')
    pins_parser.add_argument('--matrix-size', type=int, default=None,
                            help='Matrix size used in simulation')
    pins_parser.add_argument('--output-dir', type=Path, required=True)
    pins_parser.add_argument('--reference', type=Path, required=True)
    pins_parser.add_argument('--sdf-dir', type=Path, required=True,
                            help='RTG SDF directory')
    pins_parser.add_argument('--bed', type=Path, default=None)
    pins_parser.add_argument('--caller-suffix', type=str, default='vcf.gz')
    pins_parser.add_argument('--output-filename', type=str, default=None,
                             help='Output filename (default: pins_results.tsv)')
    pins_parser.add_argument('--verbose', action='store_true')
    pins_parser.add_argument("--threads", type=int, default=1, 
                             help="Number of threads for benchmarking private individual variants")

    sample_parser = subparsers.add_parser('sample-1kg', help='Sample individuals from 1000 Genomes')
    sample_parser.add_argument('--vcf', type=Path, required=True,
                            help='Multisample 1000 Genomes VCF')
    sample_parser.add_argument('--sample-table', type=Path, required=True,
                            help='sample_population_codes.tsv')
    sample_parser.add_argument('--pedigree', type=Path, required=True,
                            help='Pedigree file')
    sample_parser.add_argument('--matrix-size', type=int, required=True,
                            help='Matrix dimension (N x N)')
    sample_parser.add_argument('--output-dir', type=Path, required=True,
                            help='Output directory')
    sample_parser.add_argument('--non-eur-fraction', type=float, default=0.02,
                            help='Fraction of non-EUR individuals (default: 0.02)')
    sample_parser.add_argument('--reference', type=Path, required=True)
    sample_parser.add_argument('--seed', type=int, default=42,
                            help='Random seed')
    sample_parser.add_argument('--verbose', action='store_true')

    sim_parser = subparsers.add_parser('test', help='Run simulation test with minimal dataset')

    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose if hasattr(args, 'verbose') else False)
    
    if args.command == 'simulate':
        if not args.reference.exists():
            print(f"Error: Reference file not found: {args.reference}", file=sys.stderr)
            sys.exit(1)
        
        if args.vcf_dir and not args.vcf_dir.exists():
            print(f"Error: VCF directory not found: {args.vcf_dir}", file=sys.stderr)
            sys.exit(1)
        
        if args.targeted_bed and not args.targeted_bed.exists():
            print(f"Error: BED file not found: {args.targeted_bed}", file=sys.stderr)
            sys.exit(1)

        process_simulation(
            matrix_size=args.matrix_size,
            reference=args.reference,
            output_dir=args.output_dir,
            coverage=args.coverage,
            read_length=args.read_length,
            vcf_dir=args.vcf_dir,
            mutation_rate=args.mutation_rate,
            targeted_bed=args.targeted_bed,
            ignore_missing_vcfs=args.ignore_missing_vcfs,
            read_mode=args.read_mode,
            pool_prefix=args.pool_prefix,
            fragment_mean=args.fragment_mean,
            fragment_stdev=args.fragment_stdev,
            threads=args.threads
        )
    elif args.command == 'benchmark':
        
        setup_logging(args.verbose)

        benchmark_caller(
            matrix_context_path=args.matrix_context,
            gold_standard_dir=args.gold_standard_dir,
            caller_dir=args.caller_dir,
            caller_name=args.caller_name,
            output_dir=args.output_dir,
            reference=args.reference,
            sdf_dir=args.sdf_dir,
            bed=args.bed,
            caller_suffix=args.caller_suffix,
            filtration_status=args.filtration_status,
            coverage=args.coverage,
            matrix_size=args.matrix_size,
            output_filename=args.output_filename,
        )
    elif args.command == 'benchmark-pins':
        
        setup_logging(args.verbose)

        benchmark_private_variants(
            matrix_context_path=args.matrix_context,
            gold_standard_dir=args.gold_standard_dir,
            caller_dir=args.caller_dir,
            output_dir=args.output_dir,
            reference=args.reference,
            sdf_dir=args.sdf_dir,
            bed=args.bed,
            caller_suffix=args.caller_suffix,
            filtration_status=args.filtration_status,
            coverage=args.coverage,
            matrix_size=args.matrix_size,
            threads=args.threads,
            output_filename=args.output_filename,
        )

    elif args.command == 'sample-1kg':
        setup_logging(args.verbose)
        
        sample_1kg(
            vcf_path=args.vcf,
            sample_table=args.sample_table,
            pedigree=args.pedigree,
            reference=args.reference,
            output_dir=args.output_dir,
            matrix_size=args.matrix_size,
            non_eur_fraction=args.non_eur_fraction,
            seed=args.seed,
        )

    elif args.command == 'test':
        process_simulation(
            matrix_size=2,
            reference=get_data_file("small_reference.fna"),
            output_dir=Path('dwf'),
            coverage=10,
            read_length=100,
            mutation_rate=0.01,
            targeted_bed=get_data_file("target_calling.bed"),
            pool_prefix='pool',
            fragment_mean=200,
            fragment_stdev=20,
            threads=1
        )

    elif args.command == '--help':
        parser.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()