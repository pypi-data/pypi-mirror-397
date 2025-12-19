"""Epoch extraction for Statistical Learning paradigms.

This module handles the complex epoching logic for SL experiments:
- Detects syllable onsets from event codes
- Identifies jitter points (gaps between blocks)
- Creates epochs at word boundaries
- Separates structured vs random conditions
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mne
import numpy as np

from .config import SLConfig, get_preset


@dataclass
class EpochingResult:
    """Result of epoch extraction."""

    structured_epochs: mne.Epochs
    random_epochs: mne.Epochs
    n_structured: int
    n_random: int
    jitter_indices: list[int]
    word_onset_indices: list[int]
    syllable_latencies_ms: np.ndarray
    sfreq: float

    def summary(self) -> str:
        """Return a summary string."""
        return (
            f"Epoching Result:\n"
            f"  Structured epochs: {self.n_structured}\n"
            f"  Random epochs: {self.n_random}\n"
            f"  Jitter points: {len(self.jitter_indices)}\n"
            f"  Word onsets detected: {len(self.word_onset_indices)}\n"
            f"  Sampling rate: {self.sfreq} Hz"
        )


def load_raw_with_events(
    filepath: str | Path,
    verbose: bool = False,
) -> tuple[mne.io.Raw, np.ndarray]:
    """Load raw EEG data with events from a .set file.

    Args:
        filepath: Path to .set file.
        verbose: Whether to print progress.

    Returns:
        Tuple of (raw data, events array).
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if filepath.suffix.lower() != ".set":
        raise ValueError(f"Expected .set file, got: {filepath.suffix}")

    # Load raw data
    raw = mne.io.read_raw_eeglab(str(filepath), preload=True, verbose=verbose)

    # Extract events from annotations
    events, event_id = mne.events_from_annotations(raw, verbose=verbose)

    return raw, events


def find_syllable_onsets(
    events: np.ndarray,
    syllable_codes: list[int],
    sfreq: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Find syllable onset times from events.

    Args:
        events: MNE events array (n_events, 3).
        syllable_codes: List of event codes that represent syllables.
        sfreq: Sampling frequency.

    Returns:
        Tuple of (syllable_samples, syllable_codes_found).
    """
    # Events array: column 0 = sample, column 2 = event code
    mask = np.isin(events[:, 2], syllable_codes)
    syllable_events = events[mask]

    samples = syllable_events[:, 0]
    codes = syllable_events[:, 2]

    return samples, codes


def detect_jitter_points(
    syllable_samples: np.ndarray,
    sfreq: float,
    jitter_threshold_ms: float = 320.0,
) -> list[int]:
    """Detect jitter points (gaps between syllables exceeding threshold).

    Jitter points indicate block boundaries in the SL paradigm.

    Args:
        syllable_samples: Sample indices of syllable onsets.
        sfreq: Sampling frequency.
        jitter_threshold_ms: Threshold in ms for detecting gaps.

    Returns:
        List of indices where jitter was detected (i.e., syllable i has
        gap > threshold before it).
    """
    if len(syllable_samples) < 2:
        return []

    # Calculate inter-syllable intervals in ms
    intervals_samples = np.diff(syllable_samples)
    intervals_ms = (intervals_samples / sfreq) * 1000.0

    # Find where interval exceeds threshold
    # Note: index i in intervals corresponds to gap BEFORE syllable i+1
    jitter_mask = intervals_ms > jitter_threshold_ms
    jitter_indices = np.where(jitter_mask)[0] + 1  # +1 because diff shifts by 1

    return jitter_indices.tolist()


def find_word_onsets(
    syllable_codes: np.ndarray,
    word_onset_codes: list[int],
) -> list[int]:
    """Find indices where word-initial syllables occur.

    Args:
        syllable_codes: Array of syllable event codes.
        word_onset_codes: Codes that mark word-initial syllables.

    Returns:
        List of indices into syllable_codes where words begin.
    """
    mask = np.isin(syllable_codes, word_onset_codes)
    return np.where(mask)[0].tolist()


def create_epochs_at_word_boundaries(
    raw: mne.io.Raw,
    syllable_samples: np.ndarray,
    word_onset_indices: list[int],
    syllables_per_epoch: int = 36,
    syllable_soa_ms: float = 300.0,
    verbose: bool = False,
) -> mne.Epochs:
    """Create epochs starting at word boundaries.

    Args:
        raw: Raw EEG data.
        syllable_samples: Sample indices of all syllables.
        word_onset_indices: Indices into syllable_samples where words start.
        syllables_per_epoch: Number of syllables per epoch.
        syllable_soa_ms: Stimulus onset asynchrony in ms.
        verbose: Whether to print progress.

    Returns:
        MNE Epochs object.
    """
    sfreq = raw.info["sfreq"]
    epoch_duration_sec = syllables_per_epoch * (syllable_soa_ms / 1000.0)

    # Filter word onsets that can form complete epochs
    valid_word_onsets = []
    for idx in word_onset_indices:
        # Check if we have enough syllables after this word onset
        if idx + syllables_per_epoch <= len(syllable_samples):
            valid_word_onsets.append(idx)

    if not valid_word_onsets:
        raise ValueError("No valid word onset positions for epoching")

    # Create events array for MNE
    # Each event: [sample, 0, event_id]
    epoch_events = np.zeros((len(valid_word_onsets), 3), dtype=int)
    for i, idx in enumerate(valid_word_onsets):
        epoch_events[i, 0] = syllable_samples[idx]
        epoch_events[i, 2] = 1  # Event ID

    # Create epochs
    epochs = mne.Epochs(
        raw,
        epoch_events,
        event_id={"epoch": 1},
        tmin=0.0,
        tmax=epoch_duration_sec,
        baseline=None,
        preload=True,
        verbose=verbose,
    )

    return epochs


def separate_conditions(
    epochs: mne.Epochs,
    jitter_indices: list[int],
    word_onset_indices: list[int],
    structured_first: bool = True,
) -> tuple[mne.Epochs, mne.Epochs]:
    """Separate epochs into structured and random conditions.

    The SL paradigm alternates between structured (statistical regularities)
    and random (no regularities) conditions, separated by jitter points.

    Args:
        epochs: All epochs.
        jitter_indices: Syllable indices where jitter occurs.
        word_onset_indices: Syllable indices of epoch start points.
        structured_first: Whether structured condition comes first.

    Returns:
        Tuple of (structured_epochs, random_epochs).
    """
    if len(jitter_indices) == 0:
        # No jitter detected - return all as structured (or split in half)
        n_epochs = len(epochs)
        mid = n_epochs // 2
        if structured_first:
            return epochs[:mid], epochs[mid:]
        else:
            return epochs[mid:], epochs[:mid]

    # Determine which epochs belong to which condition
    # Each epoch corresponds to a word onset index
    structured_mask = []
    random_mask = []

    # Sort jitter indices
    jitter_set = set(jitter_indices)

    # Track current condition (alternates at each jitter)
    in_structured = structured_first

    for i, word_idx in enumerate(word_onset_indices):
        if i >= len(epochs):
            break

        # Check if we've passed a jitter point
        # (jitter point comes BEFORE this word onset)
        if word_idx in jitter_set:
            in_structured = not in_structured

        if in_structured:
            structured_mask.append(i)
        else:
            random_mask.append(i)

    # Extract epochs for each condition
    if structured_mask:
        structured_epochs = epochs[structured_mask]
    else:
        structured_epochs = epochs[[]]  # Empty

    if random_mask:
        random_epochs = epochs[random_mask]
    else:
        random_epochs = epochs[[]]  # Empty

    return structured_epochs, random_epochs


def extract_sl_epochs(
    filepath: str | Path,
    config: Optional[SLConfig] = None,
    preset: Optional[str] = None,
    subject_id: Optional[str] = None,
    structured_first: Optional[bool] = None,
    verbose: bool = False,
) -> EpochingResult:
    """Extract epochs from continuous EEG for Statistical Learning analysis.

    This is the main entry point for epoch extraction. It:
    1. Loads raw EEG with events
    2. Finds syllable onsets
    3. Detects jitter points (block boundaries)
    4. Creates epochs at word boundaries
    5. Separates structured vs random conditions

    Args:
        filepath: Path to .set file with continuous EEG.
        config: SLConfig object with paradigm parameters.
        preset: Name of built-in preset (alternative to config).
        subject_id: Subject ID for looking up counterbalancing info.
        structured_first: Override for condition order.
        verbose: Whether to print progress.

    Returns:
        EpochingResult with separated epochs and metadata.

    Example:
        >>> result = extract_sl_epochs(
        ...     "subject01_raw.set",
        ...     preset="adult-sl-2017",
        ...     subject_id="001re"
        ... )
        >>> print(result.summary())
    """
    # Get configuration
    if config is None:
        if preset is not None:
            config = get_preset(preset)
        else:
            # Default to adult-sl-2017
            config = get_preset("adult-sl-2017")

    # Get subject-specific settings
    if subject_id is not None and subject_id in config.subjects:
        subj_config = config.subjects[subject_id]
        word_onset_codes = config.get_word_onset_codes(subject_id)
        if structured_first is None:
            structured_first = subj_config.structured_first
    else:
        # Use stream1 as default
        word_onset_codes = config.languages["stream1"].word_onset_codes
        if structured_first is None:
            structured_first = True

    # Load data
    if verbose:
        print(f"Loading {filepath}...")
    raw, events = load_raw_with_events(filepath, verbose=verbose)
    sfreq = raw.info["sfreq"]

    # Find syllable onsets
    if verbose:
        print("Finding syllable onsets...")
    syllable_samples, syllable_codes = find_syllable_onsets(
        events, config.syllable_codes, sfreq
    )

    if len(syllable_samples) == 0:
        raise ValueError(
            f"No syllable events found. Expected codes: {config.syllable_codes}"
        )

    if verbose:
        print(f"  Found {len(syllable_samples)} syllables")

    # Detect jitter points
    jitter_indices = detect_jitter_points(
        syllable_samples, sfreq, config.paradigm.jitter_threshold_ms
    )

    if verbose:
        print(f"  Detected {len(jitter_indices)} jitter points")

    # Find word onsets
    word_onset_indices = find_word_onsets(syllable_codes, word_onset_codes)

    if verbose:
        print(f"  Found {len(word_onset_indices)} word onsets")

    # Create epochs
    if verbose:
        print("Creating epochs...")
    all_epochs = create_epochs_at_word_boundaries(
        raw,
        syllable_samples,
        word_onset_indices,
        syllables_per_epoch=config.paradigm.syllables_per_epoch,
        syllable_soa_ms=config.paradigm.syllable_soa_ms,
        verbose=verbose,
    )

    if verbose:
        print(f"  Created {len(all_epochs)} epochs")

    # Separate conditions
    if verbose:
        print("Separating conditions...")
    structured_epochs, random_epochs = separate_conditions(
        all_epochs,
        jitter_indices,
        word_onset_indices[:len(all_epochs)],
        structured_first=structured_first,
    )

    if verbose:
        print(f"  Structured: {len(structured_epochs)}, Random: {len(random_epochs)}")

    # Calculate syllable latencies in ms
    syllable_latencies_ms = (syllable_samples / sfreq) * 1000.0

    return EpochingResult(
        structured_epochs=structured_epochs,
        random_epochs=random_epochs,
        n_structured=len(structured_epochs),
        n_random=len(random_epochs),
        jitter_indices=jitter_indices,
        word_onset_indices=word_onset_indices,
        syllable_latencies_ms=syllable_latencies_ms,
        sfreq=sfreq,
    )


def save_epochs(
    epochs: mne.Epochs,
    filepath: str | Path,
    overwrite: bool = True,
) -> Path:
    """Save epochs to a .set file.

    Args:
        epochs: MNE Epochs to save.
        filepath: Output path (.set extension).
        overwrite: Whether to overwrite existing file.

    Returns:
        Path to saved file.
    """
    filepath = Path(filepath)

    # Ensure .set extension
    if filepath.suffix.lower() != ".set":
        filepath = filepath.with_suffix(".set")

    epochs.export(str(filepath), overwrite=overwrite)
    return filepath
