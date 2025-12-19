"""Command-line interface for autocleaneeg-sl."""

import argparse
import sys
from pathlib import Path

from .core import compute_zitc
from .config import load_config, get_preset, list_presets
from .epoch import extract_sl_epochs, save_epochs


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="autocleaneeg-sl",
        description="Statistical Learning EEG analysis - epoch extraction and ZITC computation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.2.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ============ EPOCH subcommand ============
    epoch_parser = subparsers.add_parser(
        "epoch",
        help="Extract epochs from continuous EEG",
        description="Extract epochs from continuous EEG files using SL paradigm markers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using a built-in preset
  autocleaneeg-sl epoch raw_data.set --preset adult-sl-2017 --subject 001re

  # Using a custom config file
  autocleaneeg-sl epoch raw_data.set --config my_study.yaml --subject sub01

  # List available presets
  autocleaneeg-sl epoch --list-presets
""",
    )

    epoch_parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Continuous EEG .set file to epoch",
    )
    epoch_parser.add_argument(
        "--preset",
        "-p",
        type=str,
        default=None,
        help="Built-in preset name (e.g., adult-sl-2017, infant-sl)",
    )
    epoch_parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=None,
        help="Custom YAML config file",
    )
    epoch_parser.add_argument(
        "--subject",
        "-s",
        type=str,
        default=None,
        help="Subject ID for counterbalancing lookup",
    )
    epoch_parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Output directory (default: same as input)",
    )
    epoch_parser.add_argument(
        "--structured-first",
        action="store_true",
        default=None,
        help="Override: structured condition comes first",
    )
    epoch_parser.add_argument(
        "--random-first",
        action="store_true",
        help="Override: random condition comes first",
    )
    epoch_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages",
    )
    epoch_parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available presets and exit",
    )

    # ============ ZITC subcommand ============
    zitc_parser = subparsers.add_parser(
        "zitc",
        help="Compute ZITC from epoched EEG",
        description="Compute Z-scored Inter-Trial Coherence from epoched .set files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  autocleaneeg-sl zitc subject01_epochs.set

  # With target frequencies for SL analysis
  autocleaneeg-sl zitc subject01_epochs.set --target-freqs 1.111 3.333

  # Custom frequency range and more surrogates
  autocleaneeg-sl zitc subject01.set --freq-min 0.5 --freq-max 5.0 --surrogates 200

  # Process multiple files
  autocleaneeg-sl zitc subject01.set subject02.set subject03.set
""",
    )

    zitc_parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="One or more epoched .set files to process",
    )
    zitc_parser.add_argument(
        "--freq-min",
        type=float,
        default=0.2,
        help="Minimum frequency in Hz (default: 0.2)",
    )
    zitc_parser.add_argument(
        "--freq-max",
        type=float,
        default=10.0,
        help="Maximum frequency in Hz (default: 10.0)",
    )
    zitc_parser.add_argument(
        "--surrogates",
        "-n",
        type=int,
        default=100,
        help="Number of surrogate datasets (default: 100)",
    )
    zitc_parser.add_argument(
        "--target-freqs",
        "-t",
        type=float,
        nargs="+",
        help="Target frequencies to extract (e.g., 1.111 3.333)",
    )
    zitc_parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Output directory (default: same as input file)",
    )
    zitc_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    zitc_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages",
    )
    zitc_parser.add_argument(
        "--full-spectrum",
        action="store_true",
        help="Output full spectrum CSV (default: only summary)",
    )

    # ============ PIPELINE subcommand ============
    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Full workflow: epoch + ZITC",
        description="Run complete SL analysis pipeline: epoch extraction followed by ZITC computation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline with preset
  autocleaneeg-sl pipeline raw_data.set --preset adult-sl-2017 --subject 001re

  # With custom config
  autocleaneeg-sl pipeline raw_data.set --config study.yaml --subject sub01 \\
      --target-freqs 1.111 3.333 --surrogates 200
""",
    )

    pipeline_parser.add_argument(
        "file",
        type=Path,
        help="Continuous EEG .set file",
    )
    pipeline_parser.add_argument(
        "--preset",
        "-p",
        type=str,
        default=None,
        help="Built-in preset name",
    )
    pipeline_parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=None,
        help="Custom YAML config file",
    )
    pipeline_parser.add_argument(
        "--subject",
        "-s",
        type=str,
        default=None,
        help="Subject ID for counterbalancing",
    )
    pipeline_parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Output directory",
    )
    pipeline_parser.add_argument(
        "--surrogates",
        "-n",
        type=int,
        default=100,
        help="Number of surrogates (default: 100)",
    )
    pipeline_parser.add_argument(
        "--target-freqs",
        "-t",
        type=float,
        nargs="+",
        default=[1.111, 3.333],
        help="Target frequencies (default: 1.111 3.333)",
    )
    pipeline_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed",
    )
    pipeline_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages",
    )
    pipeline_parser.add_argument(
        "--keep-epochs",
        action="store_true",
        help="Save intermediate epoch files",
    )

    return parser


def cmd_epoch(args) -> int:
    """Handle the epoch subcommand."""
    # List presets
    if args.list_presets:
        print("Available presets:")
        for name in list_presets():
            preset = get_preset(name)
            print(f"  {name}: {preset.paradigm.name}")
            print(f"    - Syllable SOA: {preset.paradigm.syllable_soa_ms} ms")
            print(f"    - Syllables per epoch: {preset.paradigm.syllables_per_epoch}")
            print(f"    - Languages: {', '.join(preset.languages.keys())}")
            print(f"    - Subjects: {len(preset.subjects)}")
        return 0

    if args.file is None:
        print("Error: file argument required (or use --list-presets)", file=sys.stderr)
        return 1

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # Load config
    config = None
    if args.config:
        config = load_config(args.config)
    elif args.preset:
        config = get_preset(args.preset)

    # Determine structured_first
    structured_first = None
    if args.structured_first:
        structured_first = True
    elif args.random_first:
        structured_first = False

    try:
        result = extract_sl_epochs(
            args.file,
            config=config,
            subject_id=args.subject,
            structured_first=structured_first,
            verbose=args.verbose,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Determine output directory
    output_dir = args.output_dir or args.file.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = args.file.stem

    # Save epochs
    structured_path = output_dir / f"{stem}_structured_epochs.set"
    random_path = output_dir / f"{stem}_random_epochs.set"

    save_epochs(result.structured_epochs, structured_path)
    print(f"Structured epochs ({result.n_structured}): {structured_path}")

    save_epochs(result.random_epochs, random_path)
    print(f"Random epochs ({result.n_random}): {random_path}")

    print(result.summary())
    return 0


def cmd_zitc(args) -> int:
    """Handle the zitc subcommand."""
    for filepath in args.files:
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            continue

        if filepath.suffix.lower() != ".set":
            print(f"Warning: Skipping non-.set file: {filepath}", file=sys.stderr)
            continue

        print(f"Processing: {filepath.name}")

        try:
            result = compute_zitc(
                filepath,
                freq_range=(args.freq_min, args.freq_max),
                n_surrogates=args.surrogates,
                random_seed=args.seed,
                verbose=args.verbose,
            )
        except Exception as e:
            print(f"Error processing {filepath.name}: {e}", file=sys.stderr)
            continue

        # Determine output directory
        output_dir = args.output_dir or filepath.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        stem = filepath.stem

        # Generate summary CSV for target frequencies
        if args.target_freqs:
            summary_rows = []
            for target_freq in args.target_freqs:
                info = result.get_zitc_at_freq(target_freq)
                summary_rows.append({
                    "target_freq_hz": info["target_freq_hz"],
                    "matched_freq_hz": info["matched_freq_hz"],
                    "raw_itc": info["raw_itc"],
                    "zitc": info["zitc"],
                })
                if args.verbose:
                    print(f"  {target_freq:.3f} Hz -> ZITC = {info['zitc']:.4f}")

            import pandas as pd
            summary_df = pd.DataFrame(summary_rows)
            summary_path = output_dir / f"{stem}_zitc_summary.csv"
            summary_df.to_csv(summary_path, index=False)
            print(f"  Summary: {summary_path}")

        # Generate full spectrum CSV if requested
        if args.full_spectrum:
            spectrum_df = result.to_dataframe(average_channels=True)
            spectrum_path = output_dir / f"{stem}_zitc_spectrum.csv"
            spectrum_df.to_csv(spectrum_path, index=False)
            print(f"  Spectrum: {spectrum_path}")

        # Always output at least one file
        if not args.target_freqs and not args.full_spectrum:
            spectrum_df = result.to_dataframe(average_channels=True)
            spectrum_path = output_dir / f"{stem}_zitc.csv"
            spectrum_df.to_csv(spectrum_path, index=False)
            print(f"  Output: {spectrum_path}")

    print("Done.")
    return 0


def cmd_pipeline(args) -> int:
    """Handle the pipeline subcommand."""
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # Load config
    config = None
    if args.config:
        config = load_config(args.config)
    elif args.preset:
        config = get_preset(args.preset)

    output_dir = args.output_dir or args.file.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = args.file.stem

    # Step 1: Extract epochs
    print(f"=== Extracting epochs from {args.file.name} ===")
    try:
        epoch_result = extract_sl_epochs(
            args.file,
            config=config,
            subject_id=args.subject,
            verbose=args.verbose,
        )
    except Exception as e:
        print(f"Error during epoching: {e}", file=sys.stderr)
        return 1

    print(epoch_result.summary())

    # Save epochs if requested
    if args.keep_epochs:
        structured_path = output_dir / f"{stem}_structured_epochs.set"
        random_path = output_dir / f"{stem}_random_epochs.set"
        save_epochs(epoch_result.structured_epochs, structured_path)
        save_epochs(epoch_result.random_epochs, random_path)
        print(f"Saved: {structured_path}, {random_path}")

    # Step 2: Compute ZITC for both conditions
    import pandas as pd

    for condition, epochs in [
        ("structured", epoch_result.structured_epochs),
        ("random", epoch_result.random_epochs),
    ]:
        if len(epochs) == 0:
            print(f"Warning: No {condition} epochs, skipping ZITC")
            continue

        print(f"\n=== Computing ZITC for {condition} condition ===")

        try:
            zitc_result = compute_zitc(
                epochs,
                freq_range=(0.2, 10.0),
                n_surrogates=args.surrogates,
                random_seed=args.seed,
                verbose=args.verbose,
            )
        except Exception as e:
            print(f"Error computing ZITC for {condition}: {e}", file=sys.stderr)
            continue

        # Summary for target frequencies
        summary_rows = []
        for target_freq in args.target_freqs:
            info = zitc_result.get_zitc_at_freq(target_freq)
            summary_rows.append({
                "condition": condition,
                "target_freq_hz": info["target_freq_hz"],
                "matched_freq_hz": info["matched_freq_hz"],
                "raw_itc": info["raw_itc"],
                "zitc": info["zitc"],
            })
            print(f"  {target_freq:.3f} Hz -> ZITC = {info['zitc']:.4f}")

        summary_df = pd.DataFrame(summary_rows)
        summary_path = output_dir / f"{stem}_{condition}_zitc_summary.csv"
        summary_df.to_csv(summary_path, index=False)
        print(f"  Output: {summary_path}")

    print("\nPipeline complete.")
    return 0


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        # No subcommand - check for legacy usage (positional files)
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            # Likely legacy usage, redirect to zitc
            print("Note: Consider using 'autocleaneeg-sl zitc' for explicit command", file=sys.stderr)
            sys.argv.insert(1, "zitc")
            args = parser.parse_args()
        else:
            parser.print_help()
            return 0

    if args.command == "epoch":
        return cmd_epoch(args)
    elif args.command == "zitc":
        return cmd_zitc(args)
    elif args.command == "pipeline":
        return cmd_pipeline(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
