"""Pytest fixtures for autocleaneeg-sl tests."""

import numpy as np
import pytest
import mne


@pytest.fixture
def sample_rate():
    """Standard sample rate for tests."""
    return 256.0


@pytest.fixture
def n_channels():
    """Number of channels for tests."""
    return 4


@pytest.fixture
def n_epochs():
    """Number of epochs for tests."""
    return 20


@pytest.fixture
def n_timepoints():
    """Number of timepoints per epoch (1 second at 256 Hz)."""
    return 256


@pytest.fixture
def channel_names(n_channels):
    """Channel names for tests."""
    return [f"Ch{i+1}" for i in range(n_channels)]


@pytest.fixture
def random_epochs_data(n_channels, n_timepoints, n_epochs):
    """Generate random epoched data (n_channels, n_timepoints, n_epochs)."""
    rng = np.random.default_rng(42)
    return rng.standard_normal((n_channels, n_timepoints, n_epochs))


@pytest.fixture
def phase_locked_data(n_channels, n_timepoints, n_epochs, sample_rate):
    """Generate data with strong phase-locking at 2 Hz.

    This creates epochs where a 2 Hz signal is phase-locked across epochs,
    which should produce high ITC at 2 Hz.
    """
    rng = np.random.default_rng(42)
    t = np.arange(n_timepoints) / sample_rate

    # Create phase-locked 2 Hz signal + noise
    data = np.zeros((n_channels, n_timepoints, n_epochs))
    target_freq = 2.0

    for ch in range(n_channels):
        for epoch in range(n_epochs):
            # Phase-locked signal (same phase across epochs)
            signal = np.sin(2 * np.pi * target_freq * t)
            # Add some noise
            noise = 0.3 * rng.standard_normal(n_timepoints)
            data[ch, :, epoch] = signal + noise

    return data, target_freq


@pytest.fixture
def random_phase_data(n_channels, n_timepoints, n_epochs, sample_rate):
    """Generate data with random phase at 2 Hz (no phase-locking).

    This creates epochs where a 2 Hz signal has random phase across epochs,
    which should produce low ITC at 2 Hz.
    """
    rng = np.random.default_rng(42)
    t = np.arange(n_timepoints) / sample_rate

    data = np.zeros((n_channels, n_timepoints, n_epochs))
    target_freq = 2.0

    for ch in range(n_channels):
        for epoch in range(n_epochs):
            # Random phase for each epoch
            random_phase = rng.uniform(0, 2 * np.pi)
            signal = np.sin(2 * np.pi * target_freq * t + random_phase)
            noise = 0.3 * rng.standard_normal(n_timepoints)
            data[ch, :, epoch] = signal + noise

    return data, target_freq


@pytest.fixture
def mne_epochs(n_channels, n_timepoints, n_epochs, sample_rate, channel_names):
    """Create an MNE Epochs object for testing."""
    rng = np.random.default_rng(42)

    # MNE expects (n_epochs, n_channels, n_timepoints)
    data = rng.standard_normal((n_epochs, n_channels, n_timepoints))

    # Create info
    info = mne.create_info(
        ch_names=channel_names,
        sfreq=sample_rate,
        ch_types="eeg"
    )

    # Create epochs
    epochs = mne.EpochsArray(data, info, verbose=False)

    return epochs


@pytest.fixture
def mne_epochs_phase_locked(n_channels, n_timepoints, n_epochs, sample_rate, channel_names):
    """Create MNE Epochs with phase-locked signal at 2 Hz."""
    rng = np.random.default_rng(42)
    t = np.arange(n_timepoints) / sample_rate
    target_freq = 2.0

    # MNE expects (n_epochs, n_channels, n_timepoints)
    data = np.zeros((n_epochs, n_channels, n_timepoints))

    for epoch in range(n_epochs):
        for ch in range(n_channels):
            signal = np.sin(2 * np.pi * target_freq * t)
            noise = 0.2 * rng.standard_normal(n_timepoints)
            data[epoch, ch, :] = signal + noise

    info = mne.create_info(
        ch_names=channel_names,
        sfreq=sample_rate,
        ch_types="eeg"
    )

    epochs = mne.EpochsArray(data, info, verbose=False)

    return epochs, target_freq


@pytest.fixture
def temp_set_file(tmp_path, mne_epochs):
    """Create a temporary .set file for testing file loading.

    Note: This creates a minimal EEGLAB-compatible file using MNE's export.
    """
    # MNE can export to EEGLAB format
    filepath = tmp_path / "test_epochs.set"
    mne_epochs.export(str(filepath), overwrite=True)
    return filepath
