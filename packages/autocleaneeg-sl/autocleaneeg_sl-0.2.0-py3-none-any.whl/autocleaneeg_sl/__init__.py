"""
autocleaneeg-sl - Statistical Learning analysis for EEG data.

Provides tools for:
- Epoch extraction from continuous EEG with SL paradigm markers
- Z-scored Inter-Trial Coherence (ZITC) computation
- Built-in presets for common SL experiments
"""

from .core import compute_zitc, load_epochs, ZITCResult
from .config import (
    SLConfig,
    ParadigmConfig,
    AnalysisConfig,
    LanguageConfig,
    SubjectConfig,
    load_config,
    get_preset,
    list_presets,
)
from .epoch import extract_sl_epochs, EpochingResult, save_epochs

__version__ = "0.2.0"
__all__ = [
    # Core ZITC computation
    "compute_zitc",
    "load_epochs",
    "ZITCResult",
    # Configuration
    "SLConfig",
    "ParadigmConfig",
    "AnalysisConfig",
    "LanguageConfig",
    "SubjectConfig",
    "load_config",
    "get_preset",
    "list_presets",
    # Epoch extraction
    "extract_sl_epochs",
    "EpochingResult",
    "save_epochs",
]
