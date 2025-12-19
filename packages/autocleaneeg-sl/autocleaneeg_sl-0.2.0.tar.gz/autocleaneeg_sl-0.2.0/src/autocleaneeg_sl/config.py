"""Configuration schema and parser for Statistical Learning paradigms."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class LanguageConfig:
    """Configuration for a counterbalanced language stream."""
    word_onset_codes: list[int]
    words: list[str] = field(default_factory=list)


@dataclass
class SubjectConfig:
    """Per-subject configuration."""
    language: str  # "stream1" or "stream2"
    structured_first: bool = True


@dataclass
class ParadigmConfig:
    """Core paradigm timing parameters."""
    name: str = "statistical-learning"
    syllable_soa_ms: float = 300.0
    syllables_per_epoch: int = 36
    jitter_threshold_ms: float = 320.0

    @property
    def epoch_length_sec(self) -> float:
        """Epoch length in seconds."""
        return self.syllables_per_epoch * (self.syllable_soa_ms / 1000.0)

    @property
    def syllable_rate_hz(self) -> float:
        """Syllable presentation rate in Hz."""
        return 1000.0 / self.syllable_soa_ms

    @property
    def word_rate_hz(self) -> float:
        """Word presentation rate in Hz (assuming 3 syllables per word)."""
        return self.syllable_rate_hz / 3.0


@dataclass
class AnalysisConfig:
    """ZITC analysis parameters."""
    freq_range: tuple[float, float] = (0.2, 10.0)
    target_freqs: dict[str, float] = field(default_factory=lambda: {
        "word": 1.111,
        "syllable": 3.333
    })
    n_surrogates: int = 100
    channels: Optional[str] = None  # e.g., "1:64" or None for all
    random_seed: Optional[int] = None


@dataclass
class SLConfig:
    """Complete Statistical Learning configuration."""
    paradigm: ParadigmConfig
    syllable_codes: list[int]
    languages: dict[str, LanguageConfig]
    subjects: dict[str, SubjectConfig] = field(default_factory=dict)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)

    def get_word_onset_codes(self, subject_id: str) -> list[int]:
        """Get word onset codes for a specific subject."""
        if subject_id not in self.subjects:
            raise ValueError(f"Subject {subject_id} not found in config")

        language_name = self.subjects[subject_id].language
        if language_name not in self.languages:
            raise ValueError(f"Language {language_name} not found in config")

        return self.languages[language_name].word_onset_codes

    def get_subject_language(self, subject_id: str) -> str:
        """Get language stream name for a subject."""
        if subject_id not in self.subjects:
            raise ValueError(f"Subject {subject_id} not found in config")
        return self.subjects[subject_id].language


def load_config(config_path: str | Path) -> SLConfig:
    """Load configuration from a YAML file.

    Args:
        config_path: Path to YAML config file.

    Returns:
        SLConfig object.
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    # Parse paradigm
    paradigm_data = data.get("paradigm", {})
    paradigm = ParadigmConfig(
        name=paradigm_data.get("name", "statistical-learning"),
        syllable_soa_ms=paradigm_data.get("syllable_soa_ms", 300.0),
        syllables_per_epoch=paradigm_data.get("syllables_per_epoch", 36),
        jitter_threshold_ms=paradigm_data.get("jitter_threshold_ms", 320.0),
    )

    # Parse languages
    languages = {}
    for lang_name, lang_data in data.get("languages", {}).items():
        languages[lang_name] = LanguageConfig(
            word_onset_codes=lang_data.get("word_onset_codes", []),
            words=lang_data.get("words", []),
        )

    # Parse subjects
    subjects = {}
    for subj_id, subj_data in data.get("subjects", {}).items():
        subjects[str(subj_id)] = SubjectConfig(
            language=subj_data.get("language", "stream1"),
            structured_first=subj_data.get("structured_first", True),
        )

    # Parse analysis
    analysis_data = data.get("analysis", {})
    freq_range = analysis_data.get("freq_range", [0.2, 10.0])
    analysis = AnalysisConfig(
        freq_range=tuple(freq_range),
        target_freqs=analysis_data.get("target_freqs", {"word": 1.111, "syllable": 3.333}),
        n_surrogates=analysis_data.get("n_surrogates", 100),
        channels=analysis_data.get("channels"),
        random_seed=analysis_data.get("random_seed"),
    )

    return SLConfig(
        paradigm=paradigm,
        syllable_codes=data.get("syllable_codes", list(range(1, 13))),
        languages=languages,
        subjects=subjects,
        analysis=analysis,
    )


# Built-in presets
PRESETS: dict[str, SLConfig] = {}


def _create_adult_sl_2017_preset() -> SLConfig:
    """Create the Adult SL 2017 dataset preset."""
    return SLConfig(
        paradigm=ParadigmConfig(
            name="adult-sl-2017",
            syllable_soa_ms=300.0,
            syllables_per_epoch=36,
            jitter_threshold_ms=320.0,
        ),
        syllable_codes=list(range(1, 13)),
        languages={
            "stream1": LanguageConfig(
                word_onset_codes=[1, 5, 8, 12],
                words=["12-9-10", "1-3-6", "5-7-2", "8-4-11"],
            ),
            "stream2": LanguageConfig(
                word_onset_codes=[5, 10, 11, 12],
                words=["5-4-2", "11-1-8", "10-3-6", "12-7-9"],
            ),
        },
        subjects={
            # Stream 1 subjects
            "001re": SubjectConfig(language="stream1", structured_first=True),
            "003mi": SubjectConfig(language="stream1", structured_first=True),
            "005sl": SubjectConfig(language="stream1", structured_first=True),
            "010lc": SubjectConfig(language="stream1", structured_first=True),
            "013mg": SubjectConfig(language="stream1", structured_first=True),
            "014mk": SubjectConfig(language="stream1", structured_first=True),
            "017yp": SubjectConfig(language="stream1", structured_first=True),
            "018sy": SubjectConfig(language="stream1", structured_first=True),
            # Stream 2 subjects
            "002sm": SubjectConfig(language="stream2", structured_first=True),
            "004tt": SubjectConfig(language="stream2", structured_first=True),
            "006ld": SubjectConfig(language="stream2", structured_first=True),
            "007mm": SubjectConfig(language="stream2", structured_first=True),
            "008cs": SubjectConfig(language="stream2", structured_first=False),
            "009kx": SubjectConfig(language="stream2", structured_first=False),
            "011ds": SubjectConfig(language="stream2", structured_first=False),
            "012an": SubjectConfig(language="stream2", structured_first=False),
            "015lc": SubjectConfig(language="stream2", structured_first=True),
            "016km": SubjectConfig(language="stream2", structured_first=False),
            "019as": SubjectConfig(language="stream2", structured_first=True),
            "020ez": SubjectConfig(language="stream2", structured_first=True),
            "021ec": SubjectConfig(language="stream2", structured_first=True),
            "022ay": SubjectConfig(language="stream2", structured_first=True),
        },
        analysis=AnalysisConfig(
            freq_range=(0.2, 10.0),
            target_freqs={"word": 1.111, "syllable": 3.333},
            n_surrogates=100,
            channels="1:64",
        ),
    )


def _create_infant_sl_preset() -> SLConfig:
    """Create an Infant SL preset (same structure, may have different subjects)."""
    config = _create_adult_sl_2017_preset()
    config.paradigm.name = "infant-sl"
    config.subjects = {}  # Clear adult subjects
    return config


# Register presets
PRESETS["adult-sl-2017"] = _create_adult_sl_2017_preset()
PRESETS["infant-sl"] = _create_infant_sl_preset()


def get_preset(name: str) -> SLConfig:
    """Get a built-in preset configuration.

    Args:
        name: Preset name (e.g., "adult-sl-2017", "infant-sl").

    Returns:
        SLConfig for the preset.

    Raises:
        ValueError: If preset not found.
    """
    if name not in PRESETS:
        available = ", ".join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")

    return PRESETS[name]


def list_presets() -> list[str]:
    """List available preset names."""
    return list(PRESETS.keys())
