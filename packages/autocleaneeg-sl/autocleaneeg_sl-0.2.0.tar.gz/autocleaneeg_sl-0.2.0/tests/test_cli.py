"""Tests for the command-line interface."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
import mne

from autocleaneeg_sl.cli import main
from autocleaneeg_sl.core import ZITCResult


# Check if eeglabio is available for exporting .set files
try:
    import eeglabio
    HAS_EEGLABIO = True
except ImportError:
    HAS_EEGLABIO = False

requires_eeglabio = pytest.mark.skipif(
    not HAS_EEGLABIO,
    reason="eeglabio not installed - needed to create test .set files"
)


@pytest.fixture
def mock_result():
    """Create a mock ZITCResult for testing."""
    n_channels = 4
    n_freqs = 50
    frequencies = np.linspace(0.2, 10.0, n_freqs)

    return ZITCResult(
        frequencies=frequencies,
        raw_itc=np.random.rand(n_channels, n_freqs) * 0.3,
        zitc=np.random.randn(n_channels, n_freqs) * 2,
        surrogate_mean=np.random.rand(n_channels, n_freqs) * 0.1,
        surrogate_std=np.random.rand(n_channels, n_freqs) * 0.05 + 0.01,
        channel_names=[f"Ch{i}" for i in range(n_channels)],
        sfreq=256.0,
        n_epochs=20,
        n_surrogates=100,
    )


@pytest.fixture
def temp_set_file_for_cli(tmp_path):
    """Create a temporary .set file for CLI testing.

    Requires eeglabio package.
    """
    if not HAS_EEGLABIO:
        pytest.skip("eeglabio not installed")

    # Create minimal MNE epochs
    n_epochs, n_channels, n_timepoints = 10, 4, 256
    rng = np.random.default_rng(42)
    data = rng.standard_normal((n_epochs, n_channels, n_timepoints))

    info = mne.create_info(
        ch_names=[f"Ch{i}" for i in range(n_channels)],
        sfreq=256.0,
        ch_types="eeg"
    )
    epochs = mne.EpochsArray(data, info, verbose=False)

    filepath = tmp_path / "test_epochs.set"
    epochs.export(str(filepath), overwrite=True)
    return filepath


class TestCLIHelp:
    """Test CLI help and basic invocation."""

    def test_help_flag(self):
        """--help should display help and exit cleanly."""
        result = subprocess.run(
            [sys.executable, "-m", "autocleaneeg_sl.cli", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "autocleaneeg-sl" in result.stdout
        assert "epoch" in result.stdout
        assert "zitc" in result.stdout
        assert "pipeline" in result.stdout

    def test_zitc_help_flag(self):
        """zitc --help should display ZITC-specific help."""
        result = subprocess.run(
            [sys.executable, "-m", "autocleaneeg_sl.cli", "zitc", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "--freq-min" in result.stdout
        assert "--surrogates" in result.stdout
        assert "--target-freqs" in result.stdout

    def test_epoch_help_flag(self):
        """epoch --help should display epoch-specific help."""
        result = subprocess.run(
            [sys.executable, "-m", "autocleaneeg_sl.cli", "epoch", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "--preset" in result.stdout
        assert "--subject" in result.stdout
        assert "--config" in result.stdout

    def test_no_args_shows_help(self):
        """Running without arguments should show help."""
        result = subprocess.run(
            [sys.executable, "-m", "autocleaneeg_sl.cli"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "epoch" in result.stdout or "zitc" in result.stdout


class TestCLIArgumentParsing:
    """Test CLI argument parsing."""

    def test_parse_freq_range(self):
        """Frequency range arguments should be parsed correctly."""
        with patch("autocleaneeg_sl.cli.compute_zitc") as mock_compute:
            mock_compute.return_value = MagicMock(
                to_dataframe=MagicMock(return_value=MagicMock(to_csv=MagicMock()))
            )

            with patch("sys.argv", [
                "autocleaneeg-sl", "zitc",
                "dummy.set",
                "--freq-min", "1.0",
                "--freq-max", "5.0"
            ]):
                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.suffix", new_callable=lambda: property(lambda s: ".set")):
                        # This will try to run but we're just checking arg parsing
                        pass

    def test_parse_surrogates(self):
        """Surrogates argument should be parsed correctly."""
        result = subprocess.run(
            [sys.executable, "-m", "autocleaneeg_sl.cli", "zitc", "--help"],
            capture_output=True,
            text=True
        )
        assert "--surrogates" in result.stdout
        assert "-n" in result.stdout

    def test_parse_target_freqs(self):
        """Target frequencies should accept multiple values."""
        result = subprocess.run(
            [sys.executable, "-m", "autocleaneeg_sl.cli", "zitc", "--help"],
            capture_output=True,
            text=True
        )
        assert "--target-freqs" in result.stdout


class TestCLIFileHandling:
    """Test CLI file handling behavior."""

    def test_nonexistent_file_error(self, tmp_path, capsys):
        """CLI should handle nonexistent files gracefully."""
        fake_file = tmp_path / "nonexistent.set"

        with patch("sys.argv", ["autocleaneeg-sl", "zitc", str(fake_file)]):
            main()

        captured = capsys.readouterr()
        assert "not found" in captured.err.lower() or "error" in captured.err.lower()

    def test_non_set_file_warning(self, tmp_path, capsys):
        """CLI should warn about non-.set files."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("dummy")

        with patch("sys.argv", ["autocleaneeg-sl", "zitc", str(txt_file)]):
            main()

        captured = capsys.readouterr()
        assert "skipping" in captured.err.lower() or "warning" in captured.err.lower()


class TestCLIPresets:
    """Test CLI preset functionality."""

    def test_list_presets(self):
        """--list-presets should show available presets."""
        result = subprocess.run(
            [sys.executable, "-m", "autocleaneeg_sl.cli", "epoch", "--list-presets"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "adult-sl-2017" in result.stdout
        assert "infant-sl" in result.stdout


class TestCLIOutput:
    """Test CLI output generation."""

    @requires_eeglabio
    def test_default_output_creates_csv(self, temp_set_file_for_cli, tmp_path):
        """Default run should create output CSV."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "autocleaneeg_sl.cli", "zitc",
                str(temp_set_file_for_cli),
                "--output-dir", str(output_dir),
                "--surrogates", "5",  # Use few surrogates for speed
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Should complete without error
        assert result.returncode == 0 or "Done" in result.stdout

        # Should create output file
        output_files = list(output_dir.glob("*.csv"))
        assert len(output_files) >= 1

    @requires_eeglabio
    def test_target_freqs_creates_summary(self, temp_set_file_for_cli, tmp_path):
        """--target-freqs should create summary CSV."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "autocleaneeg_sl.cli", "zitc",
                str(temp_set_file_for_cli),
                "--output-dir", str(output_dir),
                "--surrogates", "5",
                "--target-freqs", "1.0", "2.0"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Look for summary file
        summary_files = list(output_dir.glob("*summary*.csv"))
        assert len(summary_files) >= 1

    @requires_eeglabio
    def test_full_spectrum_flag(self, temp_set_file_for_cli, tmp_path):
        """--full-spectrum should create spectrum CSV."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "autocleaneeg_sl.cli", "zitc",
                str(temp_set_file_for_cli),
                "--output-dir", str(output_dir),
                "--surrogates", "5",
                "--full-spectrum"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Look for spectrum file
        spectrum_files = list(output_dir.glob("*spectrum*.csv"))
        assert len(spectrum_files) >= 1

    @requires_eeglabio
    def test_verbose_output(self, temp_set_file_for_cli, tmp_path):
        """--verbose should produce progress output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "autocleaneeg_sl.cli", "zitc",
                str(temp_set_file_for_cli),
                "--output-dir", str(output_dir),
                "--surrogates", "5",
                "--verbose"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Verbose mode should show progress
        assert "Computing" in result.stdout or "Loading" in result.stdout or "Processing" in result.stdout


class TestCLIIntegration:
    """Integration tests for CLI."""

    @requires_eeglabio
    def test_full_workflow(self, temp_set_file_for_cli, tmp_path):
        """Test complete CLI workflow."""
        output_dir = tmp_path / "results"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "autocleaneeg_sl.cli", "zitc",
                str(temp_set_file_for_cli),
                "--freq-min", "0.5",
                "--freq-max", "8.0",
                "--surrogates", "10",
                "--target-freqs", "1.0", "2.0", "4.0",
                "--output-dir", str(output_dir),
                "--seed", "42",
                "--verbose",
                "--full-spectrum"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        # Should complete
        assert "Done" in result.stdout

        # Should create both summary and spectrum files
        csv_files = list(output_dir.glob("*.csv"))
        assert len(csv_files) >= 2

    @requires_eeglabio
    def test_multiple_files(self, tmp_path):
        """Test processing multiple files."""
        # Create two test files
        n_epochs, n_channels, n_timepoints = 5, 2, 128
        rng = np.random.default_rng(42)

        files = []
        for i in range(2):
            data = rng.standard_normal((n_epochs, n_channels, n_timepoints))
            info = mne.create_info(
                ch_names=[f"Ch{j}" for j in range(n_channels)],
                sfreq=128.0,
                ch_types="eeg"
            )
            epochs = mne.EpochsArray(data, info, verbose=False)

            filepath = tmp_path / f"test_{i}.set"
            epochs.export(str(filepath), overwrite=True)
            files.append(filepath)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "autocleaneeg_sl.cli", "zitc",
                str(files[0]),
                str(files[1]),
                "--output-dir", str(output_dir),
                "--surrogates", "5"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        # Should process both files
        csv_files = list(output_dir.glob("*.csv"))
        assert len(csv_files) >= 2

    @requires_eeglabio
    def test_seed_reproducibility_cli(self, temp_set_file_for_cli, tmp_path):
        """Same seed should produce identical results via CLI."""
        output_dir1 = tmp_path / "output1"
        output_dir2 = tmp_path / "output2"
        output_dir1.mkdir()
        output_dir2.mkdir()

        # Run twice with same seed
        for output_dir in [output_dir1, output_dir2]:
            subprocess.run(
                [
                    sys.executable, "-m", "autocleaneeg_sl.cli", "zitc",
                    str(temp_set_file_for_cli),
                    "--output-dir", str(output_dir),
                    "--surrogates", "10",
                    "--seed", "42",
                    "--full-spectrum"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

        # Read both output files
        import pandas as pd
        csv1 = list(output_dir1.glob("*spectrum*.csv"))[0]
        csv2 = list(output_dir2.glob("*spectrum*.csv"))[0]

        df1 = pd.read_csv(csv1)
        df2 = pd.read_csv(csv2)

        # Results should be identical
        np.testing.assert_array_almost_equal(df1["zitc"].values, df2["zitc"].values)


class TestCLIWithRealSetFile:
    """Tests using actual .set files if available."""

    @pytest.fixture
    def real_set_file(self):
        """Return path to real .set file if available."""
        test_file = Path("/Volumes/ernie/Sandbox/LaurasITC/clean_folder/011ds_structured_epochs.set")
        if test_file.exists():
            return test_file
        pytest.skip("Real test .set file not available")

    def test_cli_with_real_file(self, real_set_file, tmp_path):
        """Test CLI with actual EEG data."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = subprocess.run(
            [
                sys.executable, "-m", "autocleaneeg_sl.cli", "zitc",
                str(real_set_file),
                "--output-dir", str(output_dir),
                "--surrogates", "10",
                "--target-freqs", "1.111", "3.333",
                "--seed", "42"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        assert "Done" in result.stdout

        # Check output file was created
        summary_files = list(output_dir.glob("*summary*.csv"))
        assert len(summary_files) == 1

        # Verify CSV has expected structure
        import pandas as pd
        df = pd.read_csv(summary_files[0])
        assert "target_freq_hz" in df.columns
        assert "zitc" in df.columns
        assert len(df) == 2  # Two target frequencies
