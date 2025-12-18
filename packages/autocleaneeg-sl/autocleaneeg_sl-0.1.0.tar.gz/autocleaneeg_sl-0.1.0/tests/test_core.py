"""Tests for core ZITC computation functions."""

import numpy as np
import pytest
import mne
from pathlib import Path

from autocleaneeg_sl.core import (
    compute_zitc,
    load_epochs,
    _compute_plv,
    _generate_surrogate,
    ZITCResult,
)


class TestComputePLV:
    """Tests for the _compute_plv function."""

    def test_plv_shape(self, random_epochs_data):
        """PLV output should have shape (n_channels, n_timepoints)."""
        n_channels, n_timepoints, n_epochs = random_epochs_data.shape
        plv = _compute_plv(random_epochs_data)

        assert plv.shape == (n_channels, n_timepoints)

    def test_plv_range(self, random_epochs_data):
        """PLV values should be between 0 and 1."""
        plv = _compute_plv(random_epochs_data)

        assert np.all(plv >= 0)
        assert np.all(plv <= 1)

    def test_plv_perfect_phase_lock(self, n_channels, n_timepoints):
        """Identical signals across epochs should give PLV = 1."""
        n_epochs = 10
        # Same signal repeated across all epochs
        signal = np.sin(np.linspace(0, 4 * np.pi, n_timepoints))
        data = np.zeros((n_channels, n_timepoints, n_epochs))
        for ch in range(n_channels):
            for ep in range(n_epochs):
                data[ch, :, ep] = signal

        plv = _compute_plv(data)

        # All PLV values should be 1 (perfect phase-locking)
        np.testing.assert_array_almost_equal(plv, np.ones_like(plv), decimal=10)

    def test_plv_high_for_phase_locked_signal(self, phase_locked_data, sample_rate):
        """Phase-locked signal should have high PLV at target frequency."""
        data, target_freq = phase_locked_data
        n_timepoints = data.shape[1]

        plv = _compute_plv(data)

        # Find the frequency bin closest to target
        freqs = np.fft.fftfreq(n_timepoints, 1.0 / sample_rate)
        target_bin = np.argmin(np.abs(freqs - target_freq))

        # PLV at target frequency should be high (> 0.7)
        assert np.mean(plv[:, target_bin]) > 0.7

    def test_plv_low_for_random_phase(self, random_phase_data, sample_rate):
        """Random phase signal should have lower PLV at target frequency."""
        data, target_freq = random_phase_data
        n_timepoints = data.shape[1]

        plv = _compute_plv(data)

        # Find the frequency bin closest to target
        freqs = np.fft.fftfreq(n_timepoints, 1.0 / sample_rate)
        target_bin = np.argmin(np.abs(freqs - target_freq))

        # PLV at target frequency should be lower (< 0.5)
        assert np.mean(plv[:, target_bin]) < 0.5


class TestGenerateSurrogate:
    """Tests for the _generate_surrogate function."""

    def test_surrogate_shape(self, random_epochs_data):
        """Surrogate should have same shape as input."""
        rng = np.random.default_rng(42)
        surrogate = _generate_surrogate(random_epochs_data, rng)

        assert surrogate.shape == random_epochs_data.shape

    def test_surrogate_preserves_values(self, random_epochs_data):
        """Surrogate should contain same values (just shifted)."""
        rng = np.random.default_rng(42)
        surrogate = _generate_surrogate(random_epochs_data, rng)

        # Each epoch should have the same set of values
        for ep in range(random_epochs_data.shape[2]):
            for ch in range(random_epochs_data.shape[0]):
                original_sorted = np.sort(random_epochs_data[ch, :, ep])
                surrogate_sorted = np.sort(surrogate[ch, :, ep])
                np.testing.assert_array_almost_equal(original_sorted, surrogate_sorted)

    def test_surrogate_different_from_original(self, random_epochs_data):
        """Surrogate should be different from original (shifted)."""
        rng = np.random.default_rng(42)
        surrogate = _generate_surrogate(random_epochs_data, rng)

        # At least some epochs should be different
        differences = 0
        for ep in range(random_epochs_data.shape[2]):
            if not np.allclose(random_epochs_data[:, :, ep], surrogate[:, :, ep]):
                differences += 1

        # Most epochs should be different (unlikely all shifts are 0 or n_timepoints)
        assert differences > random_epochs_data.shape[2] * 0.5

    def test_surrogate_reproducible(self, random_epochs_data):
        """Same seed should produce same surrogate."""
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)

        surrogate1 = _generate_surrogate(random_epochs_data, rng1)
        surrogate2 = _generate_surrogate(random_epochs_data, rng2)

        np.testing.assert_array_equal(surrogate1, surrogate2)

    def test_surrogate_destroys_phase_lock(self, phase_locked_data, sample_rate):
        """Surrogate should reduce PLV of phase-locked signal."""
        data, target_freq = phase_locked_data
        n_timepoints = data.shape[1]

        # Compute PLV for original
        plv_original = _compute_plv(data)

        # Compute PLV for multiple surrogates and average
        rng = np.random.default_rng(42)
        surrogate_plvs = []
        for _ in range(20):
            surrogate = _generate_surrogate(data, rng)
            surrogate_plvs.append(_compute_plv(surrogate))

        plv_surrogate = np.mean(surrogate_plvs, axis=0)

        # Find target frequency bin
        freqs = np.fft.fftfreq(n_timepoints, 1.0 / sample_rate)
        target_bin = np.argmin(np.abs(freqs - target_freq))

        # Surrogate PLV at target should be lower
        assert np.mean(plv_surrogate[:, target_bin]) < np.mean(plv_original[:, target_bin])


class TestComputeZITC:
    """Tests for the main compute_zitc function."""

    def test_zitc_returns_result_object(self, mne_epochs):
        """compute_zitc should return ZITCResult object."""
        result = compute_zitc(mne_epochs, n_surrogates=10)

        assert isinstance(result, ZITCResult)

    def test_zitc_result_shapes(self, mne_epochs, n_channels):
        """Result arrays should have correct shapes."""
        result = compute_zitc(mne_epochs, n_surrogates=10, freq_range=(0.5, 10.0))

        n_freqs = len(result.frequencies)

        assert result.raw_itc.shape == (n_channels, n_freqs)
        assert result.zitc.shape == (n_channels, n_freqs)
        assert result.surrogate_mean.shape == (n_channels, n_freqs)
        assert result.surrogate_std.shape == (n_channels, n_freqs)
        assert len(result.channel_names) == n_channels

    def test_zitc_metadata(self, mne_epochs, sample_rate, n_epochs):
        """Result should contain correct metadata."""
        result = compute_zitc(mne_epochs, n_surrogates=15)

        assert result.sfreq == sample_rate
        assert result.n_epochs == n_epochs
        assert result.n_surrogates == 15

    def test_zitc_frequency_range(self, mne_epochs):
        """Frequencies should be within specified range."""
        freq_range = (1.0, 8.0)
        result = compute_zitc(mne_epochs, n_surrogates=10, freq_range=freq_range)

        assert np.all(result.frequencies >= freq_range[0])
        assert np.all(result.frequencies <= freq_range[1])

    def test_zitc_reproducible_with_seed(self, mne_epochs):
        """Same seed should produce same results."""
        result1 = compute_zitc(mne_epochs, n_surrogates=10, random_seed=42)
        result2 = compute_zitc(mne_epochs, n_surrogates=10, random_seed=42)

        np.testing.assert_array_equal(result1.zitc, result2.zitc)
        np.testing.assert_array_equal(result1.surrogate_mean, result2.surrogate_mean)

    def test_zitc_different_without_seed(self, mne_epochs):
        """Different runs without seed should produce different surrogate stats."""
        result1 = compute_zitc(mne_epochs, n_surrogates=10, random_seed=42)
        result2 = compute_zitc(mne_epochs, n_surrogates=10, random_seed=99)

        # Surrogate statistics should differ
        assert not np.allclose(result1.surrogate_mean, result2.surrogate_mean)

    def test_zitc_high_for_phase_locked(self, mne_epochs_phase_locked):
        """Phase-locked signal should have high ZITC at target frequency."""
        epochs, target_freq = mne_epochs_phase_locked
        result = compute_zitc(epochs, n_surrogates=50, random_seed=42)

        # Find closest frequency
        freq_idx = np.argmin(np.abs(result.frequencies - target_freq))

        # Mean ZITC at target frequency should be significantly positive
        mean_zitc = result.zitc[:, freq_idx].mean()
        assert mean_zitc > 2.0  # At least 2 standard deviations above surrogate mean

    def test_zitc_channel_selection(self, mne_epochs, channel_names):
        """Channel selection should work correctly."""
        selected_channels = channel_names[:2]
        result = compute_zitc(mne_epochs, n_surrogates=10, channels=selected_channels)

        assert len(result.channel_names) == 2
        assert result.channel_names == selected_channels
        assert result.raw_itc.shape[0] == 2

    def test_zitc_with_invalid_channels(self, mne_epochs):
        """Invalid channel names should be ignored."""
        result = compute_zitc(
            mne_epochs,
            n_surrogates=10,
            channels=["Ch1", "InvalidChannel", "Ch2"]
        )

        # Only valid channels should be included
        assert "InvalidChannel" not in result.channel_names

    def test_zitc_formula_correctness(self, mne_epochs):
        """ZITC should equal (raw - surrogate_mean) / surrogate_std."""
        result = compute_zitc(mne_epochs, n_surrogates=10, random_seed=42)

        # Manually compute ZITC from components
        expected_zitc = (result.raw_itc - result.surrogate_mean) / result.surrogate_std

        np.testing.assert_array_almost_equal(result.zitc, expected_zitc)


class TestLoadEpochs:
    """Tests for the load_epochs function."""

    def test_load_nonexistent_file(self):
        """Loading nonexistent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_epochs("/nonexistent/path/file.set")

    def test_load_wrong_extension(self, tmp_path):
        """Loading non-.set file should raise ValueError."""
        # Create a dummy file with wrong extension
        wrong_file = tmp_path / "test.txt"
        wrong_file.write_text("dummy content")

        with pytest.raises(ValueError, match="Expected .set file"):
            load_epochs(wrong_file)

    def test_load_accepts_path_object(self, tmp_path):
        """load_epochs should accept Path objects."""
        # This will fail because file doesn't exist, but tests the Path handling
        fake_path = Path(tmp_path) / "fake.set"
        with pytest.raises(FileNotFoundError):
            load_epochs(fake_path)

    def test_load_accepts_string(self, tmp_path):
        """load_epochs should accept string paths."""
        fake_path = str(tmp_path / "fake.set")
        with pytest.raises(FileNotFoundError):
            load_epochs(fake_path)


class TestZITCResultMethods:
    """Tests for ZITCResult class methods."""

    @pytest.fixture
    def sample_result(self):
        """Create a sample ZITCResult for testing."""
        n_channels = 3
        n_freqs = 10
        frequencies = np.linspace(0.5, 5.0, n_freqs)

        return ZITCResult(
            frequencies=frequencies,
            raw_itc=np.random.rand(n_channels, n_freqs),
            zitc=np.random.randn(n_channels, n_freqs),
            surrogate_mean=np.random.rand(n_channels, n_freqs) * 0.1,
            surrogate_std=np.random.rand(n_channels, n_freqs) * 0.05 + 0.01,
            channel_names=["Fz", "Cz", "Pz"],
            sfreq=256.0,
            n_epochs=20,
            n_surrogates=100,
        )

    def test_to_dataframe_averaged(self, sample_result):
        """to_dataframe with averaging should return correct shape."""
        df = sample_result.to_dataframe(average_channels=True)

        assert len(df) == len(sample_result.frequencies)
        assert "frequency_hz" in df.columns
        assert "raw_itc" in df.columns
        assert "zitc" in df.columns
        assert "surrogate_mean" in df.columns
        assert "surrogate_std" in df.columns

    def test_to_dataframe_per_channel(self, sample_result):
        """to_dataframe without averaging should include all channels."""
        df = sample_result.to_dataframe(average_channels=False)

        n_expected = len(sample_result.frequencies) * len(sample_result.channel_names)
        assert len(df) == n_expected
        assert "channel" in df.columns
        assert set(df["channel"].unique()) == set(sample_result.channel_names)

    def test_get_zitc_at_freq_averaged(self, sample_result):
        """get_zitc_at_freq should return dict with averaged values."""
        target = 2.5
        result = sample_result.get_zitc_at_freq(target, average_channels=True)

        assert "target_freq_hz" in result
        assert "matched_freq_hz" in result
        assert "raw_itc" in result
        assert "zitc" in result
        assert result["target_freq_hz"] == target
        assert isinstance(result["raw_itc"], float)
        assert isinstance(result["zitc"], float)

    def test_get_zitc_at_freq_per_channel(self, sample_result):
        """get_zitc_at_freq without averaging should return per-channel arrays."""
        target = 2.5
        result = sample_result.get_zitc_at_freq(target, average_channels=False)

        assert "channels" in result
        assert len(result["raw_itc"]) == len(sample_result.channel_names)
        assert len(result["zitc"]) == len(sample_result.channel_names)

    def test_get_zitc_at_freq_finds_closest(self, sample_result):
        """get_zitc_at_freq should find the closest frequency bin."""
        # Request frequency not exactly in array
        target = 2.3
        result = sample_result.get_zitc_at_freq(target)

        # Should find closest frequency
        expected_idx = np.argmin(np.abs(sample_result.frequencies - target))
        expected_freq = sample_result.frequencies[expected_idx]

        assert result["matched_freq_hz"] == expected_freq

    def test_to_dataframe_values_correct(self, sample_result):
        """DataFrame values should match result arrays."""
        df = sample_result.to_dataframe(average_channels=True)

        # Check that averaged values match
        np.testing.assert_array_almost_equal(
            df["raw_itc"].values,
            sample_result.raw_itc.mean(axis=0)
        )
        np.testing.assert_array_almost_equal(
            df["zitc"].values,
            sample_result.zitc.mean(axis=0)
        )


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_pipeline_with_mne_epochs(self, mne_epochs):
        """Test complete pipeline from MNE epochs to results."""
        result = compute_zitc(
            mne_epochs,
            freq_range=(0.5, 10.0),
            n_surrogates=20,
            random_seed=42,
            verbose=False
        )

        # Should produce valid results
        assert not np.any(np.isnan(result.zitc))
        assert not np.any(np.isinf(result.zitc))

        # Should be able to export to DataFrame
        df = result.to_dataframe()
        assert len(df) > 0

        # Should be able to query specific frequencies
        info = result.get_zitc_at_freq(2.0)
        assert "zitc" in info

    def test_increasing_surrogates_reduces_variance(self, mne_epochs):
        """More surrogates should produce more stable estimates."""
        # Run with few surrogates multiple times
        low_surr_results = []
        for seed in range(5):
            result = compute_zitc(mne_epochs, n_surrogates=5, random_seed=seed)
            low_surr_results.append(result.zitc.mean())

        # Run with more surrogates multiple times
        high_surr_results = []
        for seed in range(5):
            result = compute_zitc(mne_epochs, n_surrogates=50, random_seed=seed)
            high_surr_results.append(result.zitc.mean())

        # Variance should be lower with more surrogates
        low_var = np.var(low_surr_results)
        high_var = np.var(high_surr_results)

        # This isn't guaranteed but should generally hold
        # Using a weak assertion to avoid flaky tests
        assert high_var <= low_var * 2  # High surr variance shouldn't be much worse
