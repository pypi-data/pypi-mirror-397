"""Command-line interface for autocleaneeg-sl."""

import argparse
import sys
from pathlib import Path

from .core import compute_zitc


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="autocleaneeg-sl",
        description="Compute Z-scored Inter-Trial Coherence (ZITC) from EEGLAB .set files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - process a single file
  autocleaneeg-sl subject01_epochs.set

  # Process multiple files
  autocleaneeg-sl subject01.set subject02.set subject03.set

  # Custom frequency range and more surrogates
  autocleaneeg-sl subject01.set --freq-min 0.5 --freq-max 5.0 --surrogates 200

  # Extract specific target frequencies
  autocleaneeg-sl subject01.set --target-freqs 1.111 3.333

  # Output to specific directory
  autocleaneeg-sl subject01.set --output-dir ./results/
""",
    )

    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="One or more .set files to process",
    )
    parser.add_argument(
        "--freq-min",
        type=float,
        default=0.2,
        help="Minimum frequency in Hz (default: 0.2)",
    )
    parser.add_argument(
        "--freq-max",
        type=float,
        default=10.0,
        help="Maximum frequency in Hz (default: 10.0)",
    )
    parser.add_argument(
        "--surrogates",
        "-n",
        type=int,
        default=100,
        help="Number of surrogate datasets (default: 100)",
    )
    parser.add_argument(
        "--target-freqs",
        "-t",
        type=float,
        nargs="+",
        help="Target frequencies to extract (e.g., 1.111 3.333)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=None,
        help="Output directory (default: same as input file)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print progress messages",
    )
    parser.add_argument(
        "--full-spectrum",
        action="store_true",
        help="Output full spectrum CSV (default: only summary)",
    )

    args = parser.parse_args()

    # Process each file
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
        if args.output_dir:
            output_dir = args.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = filepath.parent

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

        # Always output at least one file - default summary if no target freqs
        if not args.target_freqs and not args.full_spectrum:
            spectrum_df = result.to_dataframe(average_channels=True)
            spectrum_path = output_dir / f"{stem}_zitc.csv"
            spectrum_df.to_csv(spectrum_path, index=False)
            print(f"  Output: {spectrum_path}")

    print("Done.")


if __name__ == "__main__":
    main()
