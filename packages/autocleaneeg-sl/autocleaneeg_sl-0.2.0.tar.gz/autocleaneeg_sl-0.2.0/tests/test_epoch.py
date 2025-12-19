"""Tests for the epoch extraction module."""

import numpy as np
import pytest
import mne

from autocleaneeg_sl.epoch import (
    find_syllable_onsets,
    detect_jitter_points,
    find_word_onsets,
    EpochingResult,
)


class TestFindSyllableOnsets:
    """Test syllable onset detection."""

    def test_basic_detection(self):
        """Should find syllables with matching codes."""
        # Events: [sample, 0, event_code]
        events = np.array([
            [100, 0, 1],
            [200, 0, 2],
            [300, 0, 99],  # Not a syllable
            [400, 0, 3],
            [500, 0, 1],
        ])

        syllable_codes = [1, 2, 3]
        samples, codes = find_syllable_onsets(events, syllable_codes, sfreq=1000.0)

        assert len(samples) == 4
        assert list(samples) == [100, 200, 400, 500]
        assert list(codes) == [1, 2, 3, 1]

    def test_no_matching_codes(self):
        """Should return empty arrays if no matches."""
        events = np.array([
            [100, 0, 99],
            [200, 0, 100],
        ])

        samples, codes = find_syllable_onsets(events, [1, 2, 3], sfreq=1000.0)

        assert len(samples) == 0
        assert len(codes) == 0

    def test_all_matching_codes(self):
        """Should find all when all match."""
        events = np.array([
            [100, 0, 1],
            [200, 0, 2],
            [300, 0, 3],
        ])

        samples, codes = find_syllable_onsets(events, [1, 2, 3], sfreq=1000.0)

        assert len(samples) == 3


class TestDetectJitterPoints:
    """Test jitter point detection."""

    def test_no_jitter(self):
        """Regular intervals should produce no jitter."""
        # 300ms intervals at 1000 Hz = 300 samples apart
        samples = np.array([0, 300, 600, 900, 1200])
        sfreq = 1000.0
        threshold_ms = 320.0

        jitter = detect_jitter_points(samples, sfreq, threshold_ms)

        assert len(jitter) == 0

    def test_single_jitter(self):
        """Single large gap should be detected."""
        # Gap between index 2 and 3 is 500ms
        samples = np.array([0, 300, 600, 1100, 1400])
        sfreq = 1000.0
        threshold_ms = 320.0

        jitter = detect_jitter_points(samples, sfreq, threshold_ms)

        assert jitter == [3]  # Jitter before syllable at index 3

    def test_multiple_jitters(self):
        """Multiple large gaps should all be detected."""
        # Gaps at indices 2 and 4
        samples = np.array([0, 300, 800, 1100, 1700, 2000])
        sfreq = 1000.0
        threshold_ms = 320.0

        jitter = detect_jitter_points(samples, sfreq, threshold_ms)

        assert jitter == [2, 4]

    def test_threshold_boundary(self):
        """Gaps exactly at threshold should not trigger."""
        # 320ms gap exactly at threshold
        samples = np.array([0, 300, 620, 920])
        sfreq = 1000.0
        threshold_ms = 320.0

        jitter = detect_jitter_points(samples, sfreq, threshold_ms)

        assert len(jitter) == 0

    def test_empty_samples(self):
        """Empty input should return empty list."""
        jitter = detect_jitter_points(np.array([]), 1000.0, 320.0)
        assert jitter == []

    def test_single_sample(self):
        """Single sample should return empty list."""
        jitter = detect_jitter_points(np.array([100]), 1000.0, 320.0)
        assert jitter == []


class TestFindWordOnsets:
    """Test word onset detection."""

    def test_basic_detection(self):
        """Should find word-initial syllables."""
        syllable_codes = np.array([1, 2, 3, 5, 6, 7, 1, 8, 9])
        word_onset_codes = [1, 5, 8]

        indices = find_word_onsets(syllable_codes, word_onset_codes)

        assert indices == [0, 3, 6, 7]

    def test_no_word_onsets(self):
        """Should return empty if no word onsets found."""
        syllable_codes = np.array([2, 3, 4, 6, 7])
        word_onset_codes = [1, 5, 8]

        indices = find_word_onsets(syllable_codes, word_onset_codes)

        assert indices == []

    def test_all_word_onsets(self):
        """Should find all if all are word onsets."""
        syllable_codes = np.array([1, 1, 1])
        word_onset_codes = [1]

        indices = find_word_onsets(syllable_codes, word_onset_codes)

        assert indices == [0, 1, 2]


class TestEpochingResult:
    """Test EpochingResult dataclass."""

    @pytest.fixture
    def mock_epochs(self):
        """Create minimal MNE epochs for testing."""
        n_epochs, n_channels, n_times = 5, 2, 100
        data = np.random.randn(n_epochs, n_channels, n_times)
        info = mne.create_info(["Ch1", "Ch2"], sfreq=100.0, ch_types="eeg")
        return mne.EpochsArray(data, info, verbose=False)

    def test_summary_output(self, mock_epochs):
        """Summary should contain key information."""
        result = EpochingResult(
            structured_epochs=mock_epochs,
            random_epochs=mock_epochs,
            n_structured=5,
            n_random=5,
            jitter_indices=[100, 200],
            word_onset_indices=[0, 10, 20],
            syllable_latencies_ms=np.array([0, 300, 600]),
            sfreq=100.0,
        )

        summary = result.summary()

        assert "Structured epochs: 5" in summary
        assert "Random epochs: 5" in summary
        assert "Jitter points: 2" in summary


class TestIntegration:
    """Integration tests for epoch extraction."""

    def test_sl_paradigm_typical_values(self):
        """Test with typical SL paradigm values."""
        # Simulate 2 minutes of syllables at 300ms SOA
        sfreq = 1000.0
        soa_samples = 300  # 300ms at 1000 Hz
        n_syllables = 400  # About 2 minutes

        # Create syllable samples
        syllable_samples = np.arange(n_syllables) * soa_samples

        # Add a jitter point (simulating block boundary)
        # Insert 500ms gap after syllable 200
        syllable_samples[200:] += 200  # Add extra 200ms to exceed 320ms threshold

        jitter = detect_jitter_points(syllable_samples, sfreq, 320.0)

        assert len(jitter) == 1
        assert jitter[0] == 200

    def test_word_onset_frequency(self):
        """Word onsets should occur at expected frequency."""
        # In SL paradigm, words are 3 syllables
        # So every 3rd syllable is a word onset
        n_syllables = 36
        syllable_codes = np.tile([1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 4, 11], 3)

        # Word onsets for stream1: 1, 5, 8, 12
        word_onset_codes = [1, 5, 8, 12]

        word_indices = find_word_onsets(syllable_codes[:n_syllables], word_onset_codes)

        # Should have 12 word onsets (36 syllables / 3 per word)
        assert len(word_indices) == 12
