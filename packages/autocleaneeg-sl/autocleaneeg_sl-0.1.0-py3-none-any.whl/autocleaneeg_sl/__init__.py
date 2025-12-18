"""
autocleaneeg-sl - Statistical Learning analysis for EEG data.

Computes Z-scored Inter-Trial Coherence (ZITC) from EEGLAB .set files.
"""

from .core import compute_zitc, load_epochs, ZITCResult

__version__ = "0.1.0"
__all__ = ["compute_zitc", "load_epochs", "ZITCResult"]
