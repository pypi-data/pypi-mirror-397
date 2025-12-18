# /jellyfish/dynamite/ridge.py

import numpy as np
import matplotlib.pyplot as plt

# ==================== SPECTRAL RIDGE DETECTION ====================

def find_max_energy_ridge(spectrogram, frequencies, times, fmin=None, fmax=None):
    """Find the frequency of maximum energy at each time slice, with optional frequency limits."""
    spec_db = 10 * np.log10(np.maximum(spectrogram, 1e-10))

    # Create a frequency mask
    mask = np.ones_like(frequencies, dtype=bool)
    if fmin is not None:
        mask &= frequencies >= fmin
    if fmax is not None:
        mask &= frequencies <= fmax

    # Apply mask by setting out-of-range values to -inf
    spec_db_masked = spec_db.copy()
    spec_db_masked[~mask, :] = -np.inf

    max_freq_indices = np.argmax(spec_db_masked, axis=0)
    ridge_freqs = frequencies[max_freq_indices]
    return times, ridge_freqs


# Original plotting
# def plot_spectrogram_with_ridge(frequencies, times, spectrogram, show_ridge=True):
#     """Plot spectrogram with optional energy ridge overlay."""
#     fig, ax = plt.subplots(figsize=(12, 6))
    
#     # Plot spectrogram
#     spec_db = 10 * np.log10(np.maximum(spectrogram, 1e-10))
#     im = ax.imshow(spec_db.T, aspect='auto', origin='lower',
#                    extent=[frequencies[0], frequencies[-1], times[0], times[-1]],
#                    cmap='magma')
    
#     # Add ridge if requested
#     if show_ridge:
#         ridge_times, ridge_freqs = find_max_energy_ridge(spectrogram, frequencies, times, fmin=500, fmax=8000)
#         ax.plot(ridge_freqs, ridge_times, 'w--', linewidth=2, alpha=0.8, label='Max Energy Ridge')
#         ax.legend()
    
#     ax.set_xlabel('Frequency (Hz)')
#     ax.set_ylabel('Time (s)')
#     ax.set_title(f'Spectrogram {"with Energy Ridge" if show_ridge else ""}')
#     plt.colorbar(im, ax=ax, label='Power (dB)')
    
#     return fig, ax

# Plotting with rotation options
def plot_spectrogram_with_ridge(frequencies, times, spectrogram,
                                show_ridge=True, fmin=None, fmax=None,
                                rotation=0, show_derivative=False):
    """
    Plot spectrogram with optional energy ridge overlay.
    
    Parameters:
        rotation: 0 (default) = normal, 90 = rotate spectrogram 90° clockwise
        fmin/fmax: optional frequency limits for ridge detection
        show_derivative: if True, also compute and return ridge derivative
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    spec_db = 10 * np.log10(np.maximum(spectrogram, 1e-10))

    # Determine plotting extent
    if rotation == 0:
        extent = [frequencies[0], frequencies[-1], times[0], times[-1]]
        ax.imshow(spec_db.T, aspect='auto', origin='lower', extent=extent, cmap='magma')
    elif rotation == 90:
        extent = [times[0], times[-1], frequencies[0], frequencies[-1]]
        ax.imshow(spec_db, aspect='auto', origin='lower', extent=extent, cmap='magma')
    else:
        raise ValueError("rotation must be 0 or 90")
    
    ridge_times, ridge_freqs = None, None
    ridge_derivative = None

    if show_ridge:
        ridge_times, ridge_freqs = find_max_energy_ridge(spectrogram, frequencies, times, fmin=fmin, fmax=fmax)
        if rotation == 0:
            ax.plot(ridge_freqs, ridge_times, 'w--', linewidth=2, alpha=0.8, label='Max Energy Ridge')
        elif rotation == 90:
            ax.plot(ridge_times, ridge_freqs, 'w--', linewidth=2, alpha=0.8, label='Max Energy Ridge')
        ax.legend()

        if show_derivative:
            ridge_derivative = np.gradient(ridge_freqs, ridge_times)  # df/dt
            # You could plot this on a secondary axis
            ax2 = ax.twinx()
            ax2.plot(ridge_times, ridge_derivative, color='red', alpha=0.6, linewidth=1.5, label='Ridge derivative')
            ax2.set_ylabel("Freq change (Hz/s)")
            ax2.legend(loc='upper right')

    ax.set_xlabel('Frequency (Hz)' if rotation == 0 else 'Time (s)')
    ax.set_ylabel('Time (s)' if rotation == 0 else 'Frequency (Hz)')
    ax.set_title(f'Spectrogram {"with Energy Ridge" if show_ridge else ""}')
    plt.colorbar(ax.images[0], ax=ax, label='Power (dB)')
    
    return fig, ax, ridge_times, ridge_freqs, ridge_derivative
