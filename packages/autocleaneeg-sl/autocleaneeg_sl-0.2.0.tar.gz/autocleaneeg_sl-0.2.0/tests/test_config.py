"""Tests for the configuration module."""

import tempfile
from pathlib import Path

import pytest

from autocleaneeg_sl.config import (
    SLConfig,
    ParadigmConfig,
    AnalysisConfig,
    LanguageConfig,
    SubjectConfig,
    load_config,
    get_preset,
    list_presets,
    PRESETS,
)


class TestPresets:
    """Test built-in presets."""

    def test_list_presets_not_empty(self):
        """Should have at least one preset."""
        presets = list_presets()
        assert len(presets) >= 1

    def test_adult_sl_2017_preset_exists(self):
        """Adult SL 2017 preset should exist."""
        assert "adult-sl-2017" in list_presets()

    def test_infant_sl_preset_exists(self):
        """Infant SL preset should exist."""
        assert "infant-sl" in list_presets()

    def test_get_preset_returns_slconfig(self):
        """get_preset should return SLConfig."""
        config = get_preset("adult-sl-2017")
        assert isinstance(config, SLConfig)

    def test_get_preset_unknown_raises(self):
        """Unknown preset should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown preset"):
            get_preset("nonexistent-preset")


class TestAdultSL2017Preset:
    """Test the adult-sl-2017 preset specifically."""

    @pytest.fixture
    def config(self):
        return get_preset("adult-sl-2017")

    def test_paradigm_name(self, config):
        """Paradigm should be named correctly."""
        assert config.paradigm.name == "adult-sl-2017"

    def test_syllable_soa(self, config):
        """SOA should be 300ms."""
        assert config.paradigm.syllable_soa_ms == 300.0

    def test_syllables_per_epoch(self, config):
        """Should have 36 syllables per epoch."""
        assert config.paradigm.syllables_per_epoch == 36

    def test_epoch_length(self, config):
        """Epoch should be 10.8 seconds."""
        assert config.paradigm.epoch_length_sec == pytest.approx(10.8)

    def test_syllable_rate(self, config):
        """Syllable rate should be ~3.333 Hz."""
        assert config.paradigm.syllable_rate_hz == pytest.approx(3.333, rel=0.01)

    def test_word_rate(self, config):
        """Word rate should be ~1.111 Hz."""
        assert config.paradigm.word_rate_hz == pytest.approx(1.111, rel=0.01)

    def test_jitter_threshold(self, config):
        """Jitter threshold should be 320ms."""
        assert config.paradigm.jitter_threshold_ms == 320.0

    def test_syllable_codes(self, config):
        """Should have 12 syllable codes (1-12)."""
        assert config.syllable_codes == list(range(1, 13))

    def test_has_two_languages(self, config):
        """Should have stream1 and stream2."""
        assert "stream1" in config.languages
        assert "stream2" in config.languages

    def test_stream1_word_onsets(self, config):
        """Stream1 should have correct word onset codes."""
        assert config.languages["stream1"].word_onset_codes == [1, 5, 8, 12]

    def test_stream2_word_onsets(self, config):
        """Stream2 should have correct word onset codes."""
        assert config.languages["stream2"].word_onset_codes == [5, 10, 11, 12]

    def test_has_subjects(self, config):
        """Should have subjects defined."""
        assert len(config.subjects) > 0

    def test_subject_001re_is_stream1(self, config):
        """Subject 001re should be stream1."""
        assert config.subjects["001re"].language == "stream1"

    def test_subject_002sm_is_stream2(self, config):
        """Subject 002sm should be stream2."""
        assert config.subjects["002sm"].language == "stream2"

    def test_get_word_onset_codes(self, config):
        """get_word_onset_codes should return correct codes."""
        codes = config.get_word_onset_codes("001re")
        assert codes == [1, 5, 8, 12]

        codes = config.get_word_onset_codes("002sm")
        assert codes == [5, 10, 11, 12]

    def test_get_word_onset_codes_unknown_subject(self, config):
        """Unknown subject should raise ValueError."""
        with pytest.raises(ValueError, match="Subject .* not found"):
            config.get_word_onset_codes("unknown_subject")

    def test_analysis_config(self, config):
        """Analysis config should have correct defaults."""
        assert config.analysis.freq_range == (0.2, 10.0)
        assert config.analysis.n_surrogates == 100
        assert config.analysis.channels == "1:64"


class TestLoadConfig:
    """Test YAML config loading."""

    def test_load_minimal_config(self, tmp_path):
        """Should load a minimal config file."""
        config_content = """
paradigm:
  name: test-paradigm
  syllable_soa_ms: 300.0

syllable_codes: [1, 2, 3, 4]

languages:
  stream1:
    word_onset_codes: [1, 3]
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(config_content)

        config = load_config(config_file)

        assert config.paradigm.name == "test-paradigm"
        assert config.paradigm.syllable_soa_ms == 300.0
        assert config.syllable_codes == [1, 2, 3, 4]
        assert config.languages["stream1"].word_onset_codes == [1, 3]

    def test_load_full_config(self, tmp_path):
        """Should load a complete config file."""
        config_content = """
paradigm:
  name: full-test
  syllable_soa_ms: 250.0
  syllables_per_epoch: 48
  jitter_threshold_ms: 300.0

syllable_codes: [1, 2, 3, 4, 5, 6]

languages:
  lang_a:
    word_onset_codes: [1, 4]
    words: ["1-2-3", "4-5-6"]
  lang_b:
    word_onset_codes: [2, 5]
    words: ["2-3-1", "5-6-4"]

subjects:
  sub01:
    language: lang_a
    structured_first: true
  sub02:
    language: lang_b
    structured_first: false

analysis:
  freq_range: [0.5, 8.0]
  n_surrogates: 50
  channels: "1:32"
  random_seed: 42
"""
        config_file = tmp_path / "full_config.yaml"
        config_file.write_text(config_content)

        config = load_config(config_file)

        assert config.paradigm.name == "full-test"
        assert config.paradigm.syllable_soa_ms == 250.0
        assert config.paradigm.syllables_per_epoch == 48
        assert config.paradigm.jitter_threshold_ms == 300.0

        assert len(config.languages) == 2
        assert config.languages["lang_a"].words == ["1-2-3", "4-5-6"]

        assert len(config.subjects) == 2
        assert config.subjects["sub01"].language == "lang_a"
        assert config.subjects["sub02"].structured_first is False

        assert config.analysis.freq_range == (0.5, 8.0)
        assert config.analysis.n_surrogates == 50
        assert config.analysis.random_seed == 42

    def test_load_nonexistent_raises(self):
        """Loading nonexistent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_load_config_with_defaults(self, tmp_path):
        """Missing values should use defaults."""
        config_content = """
languages:
  stream1:
    word_onset_codes: [1]
"""
        config_file = tmp_path / "minimal.yaml"
        config_file.write_text(config_content)

        config = load_config(config_file)

        # Check defaults
        assert config.paradigm.name == "statistical-learning"
        assert config.paradigm.syllable_soa_ms == 300.0
        assert config.analysis.n_surrogates == 100


class TestParadigmConfig:
    """Test ParadigmConfig properties."""

    def test_epoch_length_calculation(self):
        """Epoch length should be calculated correctly."""
        config = ParadigmConfig(
            syllable_soa_ms=300.0,
            syllables_per_epoch=36,
        )
        assert config.epoch_length_sec == pytest.approx(10.8)

    def test_syllable_rate_calculation(self):
        """Syllable rate should be calculated correctly."""
        config = ParadigmConfig(syllable_soa_ms=300.0)
        assert config.syllable_rate_hz == pytest.approx(3.333, rel=0.01)

    def test_word_rate_calculation(self):
        """Word rate should be syllable rate / 3."""
        config = ParadigmConfig(syllable_soa_ms=300.0)
        assert config.word_rate_hz == pytest.approx(1.111, rel=0.01)

    def test_custom_soa(self):
        """Custom SOA should affect rates."""
        config = ParadigmConfig(syllable_soa_ms=250.0)
        assert config.syllable_rate_hz == pytest.approx(4.0)
        assert config.word_rate_hz == pytest.approx(4.0 / 3.0)
