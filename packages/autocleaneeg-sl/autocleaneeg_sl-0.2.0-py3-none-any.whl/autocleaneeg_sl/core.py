"""Core ZITC computation functions."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import mne


@dataclass
class ZITCResult:
    """Result container for ZITC computation."""

    frequencies: np.ndarray  # Frequency bins (Hz)
    raw_itc: np.ndarray      # Raw PLV/ITC values (n_channels, n_freqs)
    zitc: np.ndarray         # Z-scored ITC (n_channels, n_freqs)
    surrogate_mean: np.ndarray
    surrogate_std: np.ndarray
    channel_names: list[str]
    sfreq: float
    n_epochs: int
    n_surrogates: int

    def to_dataframe(self, average_channels: bool = True) -> pd.DataFrame:
        """Convert results to a DataFrame.

        Args:
            average_channels: If True, average across channels. If False,
                include per-channel values.

        Returns:
            DataFrame with frequency, raw_itc, zitc columns.
        """
        if average_channels:
            return pd.DataFrame({
                "frequency_hz": self.frequencies,
                "raw_itc": self.raw_itc.mean(axis=0),
                "surrogate_mean": self.surrogate_mean.mean(axis=0),
                "surrogate_std": self.surrogate_std.mean(axis=0),
                "zitc": self.zitc.mean(axis=0),
            })
        else:
            rows = []
            for ch_idx, ch_name in enumerate(self.channel_names):
                for f_idx, freq in enumerate(self.frequencies):
                    rows.append({
                        "channel": ch_name,
                        "frequency_hz": freq,
                        "raw_itc": self.raw_itc[ch_idx, f_idx],
                        "surrogate_mean": self.surrogate_mean[ch_idx, f_idx],
                        "surrogate_std": self.surrogate_std[ch_idx, f_idx],
                        "zitc": self.zitc[ch_idx, f_idx],
                    })
            return pd.DataFrame(rows)

    def get_zitc_at_freq(self, target_freq: float, average_channels: bool = True) -> dict:
        """Get ZITC value at a specific frequency.

        Args:
            target_freq: Target frequency in Hz.
            average_channels: If True, return channel-averaged value.

        Returns:
            Dict with matched frequency and ZITC value(s).
        """
        freq_idx = np.argmin(np.abs(self.frequencies - target_freq))
        matched_freq = self.frequencies[freq_idx]

        if average_channels:
            return {
                "target_freq_hz": target_freq,
                "matched_freq_hz": matched_freq,
                "raw_itc": float(self.raw_itc[:, freq_idx].mean()),
                "zitc": float(self.zitc[:, freq_idx].mean()),
            }
        else:
            return {
                "target_freq_hz": target_freq,
                "matched_freq_hz": matched_freq,
                "raw_itc": self.raw_itc[:, freq_idx],
                "zitc": self.zitc[:, freq_idx],
                "channels": self.channel_names,
            }


def load_epochs(filepath: str | Path) -> mne.io.Raw | mne.Epochs:
    """Load EEG epochs from an EEGLAB .set file.

    Args:
        filepath: Path to .set file.

    Returns:
        MNE Epochs object.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if filepath.suffix.lower() != ".set":
        raise ValueError(f"Expected .set file, got: {filepath.suffix}")

    # Load with MNE
    epochs = mne.io.read_epochs_eeglab(str(filepath), verbose=False)
    return epochs


def _compute_plv(data: np.ndarray) -> np.ndarray:
    """Compute Phase-Locking Value (PLV) from epoched data.

    Args:
        data: Array of shape (n_channels, n_timepoints, n_epochs).

    Returns:
        PLV array of shape (n_channels, n_freqs).
    """
    # FFT along time dimension
    fft_data = np.fft.fft(data, axis=1)

    # Get phase angles
    phase = np.angle(fft_data)

    # PLV = |mean(exp(i*phase))| across epochs
    plv = np.abs(np.mean(np.exp(1j * phase), axis=2))

    return plv


def _generate_surrogate(data: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Generate surrogate data by circular shifting each epoch.

    Args:
        data: Array of shape (n_channels, n_timepoints, n_epochs).
        rng: NumPy random generator.

    Returns:
        Surrogate data with same shape.
    """
    n_channels, n_timepoints, n_epochs = data.shape
    surrogate = np.zeros_like(data)

    for epoch_idx in range(n_epochs):
        shift = rng.integers(1, n_timepoints + 1)
        surrogate[:, :, epoch_idx] = np.roll(data[:, :, epoch_idx], shift, axis=1)

    return surrogate


def compute_zitc(
    epochs: mne.Epochs | str | Path,
    freq_range: tuple[float, float] = (0.2, 10.0),
    n_surrogates: int = 100,
    channels: Optional[list[str]] = None,
    random_seed: Optional[int] = None,
    verbose: bool = False,
) -> ZITCResult:
    """Compute Z-scored Inter-Trial Coherence (ZITC).

    ZITC = (True PLV - Surrogate Mean) / Surrogate Std

    Surrogate data is generated by circular shifting each epoch by a random
    amount, which preserves the spectral content but destroys phase relationships.

    Args:
        epochs: MNE Epochs object, or path to .set file.
        freq_range: Tuple of (min_freq, max_freq) in Hz. Default (0.2, 10.0).
        n_surrogates: Number of surrogate datasets to generate. Default 100.
        channels: List of channel names to include. If None, uses all channels.
        random_seed: Random seed for reproducibility.
        verbose: If True, print progress messages.

    Returns:
        ZITCResult object containing raw ITC, ZITC, and metadata.

    Example:
        >>> result = compute_zitc("subject01_epochs.set")
        >>> result.get_zitc_at_freq(1.111)  # Word rate
        {'target_freq_hz': 1.111, 'matched_freq_hz': 1.11, 'raw_itc': 0.13, 'zitc': 0.39}
    """
    # Load data if path provided
    if isinstance(epochs, (str, Path)):
        if verbose:
            print(f"Loading {epochs}...")
        epochs = load_epochs(epochs)

    # Get data as (n_channels, n_timepoints, n_epochs)
    data = epochs.get_data()  # (n_epochs, n_channels, n_timepoints)
    data = data.transpose(1, 2, 0)  # -> (n_channels, n_timepoints, n_epochs)

    channel_names = epochs.ch_names
    sfreq = epochs.info["sfreq"]
    n_channels, n_timepoints, n_epochs = data.shape

    # Channel selection
    if channels is not None:
        ch_indices = [channel_names.index(ch) for ch in channels if ch in channel_names]
        data = data[ch_indices, :, :]
        channel_names = [channel_names[i] for i in ch_indices]
        n_channels = len(ch_indices)

    if verbose:
        print(f"Data shape: {n_channels} channels x {n_timepoints} timepoints x {n_epochs} epochs")
        print(f"Sampling rate: {sfreq} Hz")

    # Compute frequency bins
    freqs = np.fft.fftfreq(n_timepoints, 1.0 / sfreq)
    freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
    freqs_out = freqs[freq_mask]

    if verbose:
        print(f"Frequency range: {freqs_out[0]:.3f} - {freqs_out[-1]:.3f} Hz ({len(freqs_out)} bins)")

    # Compute true PLV
    if verbose:
        print("Computing true PLV...")
    true_plv_full = _compute_plv(data)
    true_plv = true_plv_full[:, freq_mask]

    # Generate surrogates and compute PLV for each
    rng = np.random.default_rng(random_seed)
    surrogate_plvs = np.zeros((n_surrogates, n_channels, len(freqs_out)))

    if verbose:
        print(f"Computing {n_surrogates} surrogates...")

    for i in range(n_surrogates):
        if verbose and (i + 1) % 20 == 0:
            print(f"  Surrogate {i + 1}/{n_surrogates}")

        surrogate_data = _generate_surrogate(data, rng)
        surrogate_plv_full = _compute_plv(surrogate_data)
        surrogate_plvs[i] = surrogate_plv_full[:, freq_mask]

    # Compute surrogate statistics
    surrogate_mean = surrogate_plvs.mean(axis=0)
    surrogate_std = surrogate_plvs.std(axis=0, ddof=0)  # Match MATLAB default

    # Compute ZITC
    zitc = (true_plv - surrogate_mean) / surrogate_std

    if verbose:
        print("Done.")

    return ZITCResult(
        frequencies=freqs_out,
        raw_itc=true_plv,
        zitc=zitc,
        surrogate_mean=surrogate_mean,
        surrogate_std=surrogate_std,
        channel_names=list(channel_names),
        sfreq=sfreq,
        n_epochs=n_epochs,
        n_surrogates=n_surrogates,
    )
