# /jellyfish/utils/spec_plotter.py

# Plots spectrogram and power spectral density for audio files (single file or directory structure)
# Part of audio information retrieval pipeline for animal vocalizations (formerly psd_kiwi_airpipe.ipynb)
# Initializes with nfft=1024, grabs sample rate automatically from file, and zero-pads files to ensure uniformity. 

import os
import re
import numpy as np
import librosa
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import math
import importlib
from pathlib import Path

from . import jelly_funcs as jelfun

# Import for notebooks
# from jellyfish.utils import jelly_funcs as jelfun


def _load_and_validate_audio(audio_path_obj, fmin=None, fmax=None):
    """Shared audio loading and validation logic."""
    
    # Check if file exists, try .wav extension if needed
    if not audio_path_obj.exists():
        if audio_path_obj.suffix.lower() != '.wav':
            wav_path = audio_path_obj.with_suffix('.wav')
            if wav_path.exists():
                audio_path_obj = wav_path
            else:
                error_msg = f"WAV file not found: {audio_path_obj} or {wav_path}"
                print(f"ERROR: {error_msg}")
                raise FileNotFoundError(error_msg)
        else:
            error_msg = f"WAV file not found: {audio_path_obj}"
            print(f"ERROR: {error_msg}")
            raise FileNotFoundError(error_msg)
    
    # Load audio
    try:
        y, sr = librosa.load(str(audio_path_obj), sr=None)
    except Exception as e:
        error_msg = f"Failed to load audio file {audio_path_obj}: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)
    
    # Validate not empty
    if len(y) == 0:
        error_msg = f"Audio file is empty: {audio_path_obj}"
        print(f"ERROR: {error_msg}")
        raise ValueError(error_msg)
    
    # Apply spectral bandpass filter if bounds specified
    if fmin is not None or fmax is not None:
        Y = np.fft.fft(y)
        freqs = np.fft.fftfreq(len(y), 1/sr)
        abs_freqs = np.abs(freqs)
        
        # Create frequency mask
        mask = np.ones_like(abs_freqs, dtype=bool)
        if fmin is not None:
            mask &= abs_freqs >= fmin
        if fmax is not None:
            mask &= abs_freqs <= fmax
            
        Y_filtered = Y * mask
        y = np.real(np.fft.ifft(Y_filtered))
    
    return y, sr, audio_path_obj

def _compute_dual_resolution(y, sr, psd_n_fft, psd_hop_length, spec_n_fft, 
                           spec_hop_length, use_dual_resolution, verbose):
    """Core dual resolution computation logic."""
    
    if use_dual_resolution:
        # HIGH FREQUENCY RESOLUTION PSD 
        stft_psd = librosa.stft(y, n_fft=psd_n_fft, hop_length=psd_hop_length)
        power_spectrum_psd = np.abs(stft_psd)**2
        psd_mean = np.mean(power_spectrum_psd, axis=1)
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=psd_n_fft)
        
        # HIGH TIME RESOLUTION SPECTROGRAM
        stft_spec = librosa.stft(y, n_fft=spec_n_fft, hop_length=spec_hop_length)
        power_spectrum_spec = np.abs(stft_spec)**2
        times = librosa.frames_to_time(np.arange(power_spectrum_spec.shape[1]), 
                                       sr=sr, hop_length=spec_hop_length)
        spec_frequencies = librosa.fft_frequencies(sr=sr, n_fft=spec_n_fft)
        
        # INTERPOLATE SPECTROGRAM TO MATCH PSD FREQUENCY GRID
        interpolated_spectrogram = np.zeros((len(frequencies), power_spectrum_spec.shape[1]))
        
        if verbose:
            print(f"Interpolating spectrogram from {len(spec_frequencies)} to {len(frequencies)} freq bins")
        
        for time_idx in range(power_spectrum_spec.shape[1]):
            interp_func = interp1d(
                spec_frequencies, 
                power_spectrum_spec[:, time_idx], 
                kind='linear',
                bounds_error=False,
                fill_value=0
            )
            interpolated_spectrogram[:, time_idx] = interp_func(frequencies)
        
        power_spectrum = interpolated_spectrogram
        
    else:
        # SINGLE RESOLUTION
        stft_result = librosa.stft(y, n_fft=psd_n_fft, hop_length=psd_hop_length)
        power_spectrum = np.abs(stft_result)**2
        times = librosa.frames_to_time(np.arange(power_spectrum.shape[1]), 
                                       sr=sr, hop_length=psd_hop_length)
        psd_mean = np.mean(power_spectrum, axis=1)
        frequencies = librosa.fft_frequencies(sr=sr, n_fft=psd_n_fft)

    return frequencies, times, power_spectrum, psd_mean

def calculate_stft_dual(input_path, fmin=None, fmax=None, # Simple bandpass
                        psd_n_fft=512, psd_hop_length=None, # PSD parameters (frequency-optimized)
                        spec_n_fft=512, spec_hop_length=None, # Spectrogram parameters (time-optimized)
                        use_dual_resolution=False, verbose=False, max_files=None): # Control flags
    """Calculate PSD and spectrogram with dual resolution for single files or directories."""
    
    path_obj = Path(input_path)
    
    # Get list of files to process
    if path_obj.is_file():
        wav_files = [path_obj]
        is_directory = False
    elif path_obj.is_dir():
        wav_files = list(path_obj.glob("*.wav"))
        if not wav_files:
            error_msg = f"No .wav files found in {path_obj}"
            print(f"ERROR: {error_msg}")
            raise ValueError(error_msg)
        
        # Limit files if specified
        if max_files and len(wav_files) > max_files:
            wav_files = wav_files[:max_files]
            print(f"Processing {max_files} of {len(list(path_obj.glob('*.wav')))} files")
        else:
            print(f"Processing {len(wav_files)} audio files")
        is_directory = True
    else:
        raise FileNotFoundError(f"Path not found or invalid: {input_path}")
    
    # Set hop lengths
    if psd_hop_length is None:
        psd_hop_length = psd_n_fft // 16
    if spec_hop_length is None:
        spec_hop_length = spec_n_fft // 16
    
    # Pre-processing: determine max length and common sample rate (for directories only)
    if is_directory:
        print("Analyzing files...")
        max_length = 0
        original_srs = []
        valid_files = []
        
        for wav_file in wav_files:
            try:
                y, sr, _ = _load_and_validate_audio(wav_file, fmin=fmin, fmax=fmax)
                max_length = max(max_length, len(y))
                original_srs.append(sr)
                valid_files.append(wav_file)
            except Exception as e:
                print(f"ERROR: Skipping {wav_file.name}: {e}")
                continue
        
        if not valid_files:
            error_msg = "No files could be loaded successfully"
            print(f"ERROR: {error_msg}")
            raise RuntimeError(error_msg)
        
        # Use most common sample rate
        most_common_sr = max(set(original_srs), key=original_srs.count)
        wav_files = valid_files  # Use only valid files
        print(f"Using sample rate: {most_common_sr} Hz")
        print(f"Max file length: {max_length} samples ({max_length/most_common_sr:.2f}s)")
        print("Computing psd and spectrograms...")
    else:
        # Single file - skip pre-processing
        max_length = None
        most_common_sr = None
    
    # Process files
    psd = []
    spectrograms = []
    file_info = []
    successful_count = 0
    failed_files = []
    
    for wav_file in wav_files:
        try:
            y, sr, validated_path = _load_and_validate_audio(wav_file, fmin=fmin, fmax=fmax)

            # Store original file metadata before processing
            original_duration = len(y) / sr
            original_length = len(y)
            original_sr = sr
            original_max_amp = np.max(np.abs(y))
            
            # For directories: resample and zero-pad
            if is_directory:
                # Resample if needed
                if sr != most_common_sr:
                    y = librosa.resample(y, orig_sr=sr, target_sr=most_common_sr)
                    sr = most_common_sr
                
                # Zero-pad to max length
                if len(y) < max_length:
                    y = np.pad(y, (0, max_length - len(y)), mode='constant', constant_values=0)
                
                # Remove DC
                y = y - np.mean(y)
            
            if verbose:
                print(f"Processing: {validated_path.name}")
                if not is_directory:  # Only print details for single file
                    print(f"PSD: {psd_n_fft}-point FFT, {psd_hop_length} hop")
                    print(f"Spectrogram: {spec_n_fft}-point FFT, {spec_hop_length} hop")
            
            # Compute dual resolution
            frequencies, times, power_spectrum, psd_mean = _compute_dual_resolution(
                y, sr, psd_n_fft, psd_hop_length, spec_n_fft, spec_hop_length,
                use_dual_resolution, verbose and not is_directory)
            
            psd.append(psd_mean)
            spectrograms.append(power_spectrum)
            
            # Calculate final duration after processing
            final_length = len(y)
            final_duration = len(y) / sr
            max_amp = np.max(np.abs(y))

            # Store comprehensive file metadata
            file_info.append({
                'filename': validated_path.name,
                'original_duration': original_duration,           # Uses original len(y) and original sr
                'final_duration': len(y) / sr,                   # Uses modified len(y) and potentially modified sr
                'original_length_samples': original_length,       # Original sample count
                'final_length_samples': len(y),                  # After padding
                'original_sample_rate': original_sr,             # Before resampling
                'final_sample_rate': sr,                         # After resampling
                'original_max_amplitude': original_max_amp,
                'final_max_amplitude': np.max(np.abs(y)),
                'was_resampled': sr != original_sr,
                'was_zero_padded': is_directory and len(y) > original_length,
                'padding_samples_added': len(y) - original_length if is_directory else 0,
                # Legacy field names for backward compatibility
                'duration': original_duration,
                'max_amplitude': original_max_amp
            })
            
            successful_count += 1
            
        except Exception as e:
            error_msg = f"Error processing {wav_file.name}: {e}"
            print(f"ERROR: {error_msg}")
            failed_files.append(wav_file.name)
            continue
    
    if is_directory:
        print(f"Completed processing: {successful_count}/{len(wav_files)} files successfully processed")
        if failed_files:
            print(f"Failed files: {failed_files}")
    
    if not psd:
        error_msg = "No psd computed successfully"
        print(f"ERROR: {error_msg}")
        raise RuntimeError(error_msg)
    
    # Convert to arrays and compute statistics
    psd_array = np.array(psd)
    mean_psd = np.mean(psd_array, axis=0)
    std_psd = np.std(psd_array, axis=0) if is_directory else np.zeros_like(psd_array[0])
    
    # Find peak frequency (excluding DC component)
    peak_freq_idx = np.argmax(mean_psd[1:]) + 1
    peak_freq = frequencies[peak_freq_idx]
    
    # Determine final sample rate
    if is_directory:
        final_sr = most_common_sr
    else:
        final_sr = sr  # For single files, sr is still the original file's sample rate
            
    return {
        'psd': psd_array,
        'mean_psd': mean_psd,
        'std_psd': std_psd,
        'spectrograms': spectrograms if is_directory else spectrograms[0],
        'frequencies': frequencies,
        'times': times,
        'sample_rate': final_sr,
        'file_info': pd.DataFrame(file_info),
        'directory_name': path_obj.name if is_directory else path_obj.parent.name,
        'psd_n_fft': psd_n_fft,
        'spec_n_fft': spec_n_fft,
        'max_length': max_length,
        'peak_frequency': peak_freq,
        'dual_resolution': use_dual_resolution,
        'failed_files': failed_files if failed_files else None,
        # Legacy field names for backward compatibility
        'nfft': psd_n_fft
    }

# PSD PLOTTING FUNCTIONS 

def plot_psd_grid(audio_data, grid_cols=4, freq_range=None, save_plot=True, save_dir="../psd_plots"):
    """
    Plot grid of individual psd (peak detection removed).
    """
    if audio_data is None:
        return
    
    # Create save directory
    if save_plot:
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
    
    # Extract data - handle both single file and directory results
    psd_array = audio_data['psd']
    freqs = audio_data['frequencies']
    file_info = audio_data['file_info']
    
    # Set frequency range
    if freq_range is None:
        freq_range = (0, audio_data['sample_rate'] // 2)
    
    freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
    freqs_plot = freqs[freq_mask]
    
    # Calculate grid dimensions
    n_files = len(psd_array)
    grid_rows = math.ceil(n_files / grid_cols)
    
    # Create figure
    fig, axes = plt.subplots(grid_rows, grid_cols, figsize=(4*grid_cols, 3*grid_rows))
    
    # Handle single subplot case
    if n_files == 1:
        axes = np.array([axes])
    
    # Handle single row/column cases
    if grid_rows == 1 and n_files > 1:
        axes = axes.reshape(1, -1)
    elif grid_cols == 1 and n_files > 1:
        axes = axes.reshape(-1, 1)
    
    # Ensure axes is always iterable for consistent indexing
    axes_flat = axes.flatten() if hasattr(axes, 'flatten') else [axes]
    
    # Plot each individual PSD
    for i in range(n_files):
        ax = axes_flat[i]
        
        # Plot PSD
        ax.semilogy(freqs_plot, psd_array[i][freq_mask], 'b-', linewidth=1)
        
        # Formatting - handle both old and new field names
        filename = file_info.iloc[i]['filename']
        duration = file_info.iloc[i].get('original_duration', file_info.iloc[i].get('duration', 0))
        max_amp = file_info.iloc[i].get('original_max_amplitude', file_info.iloc[i].get('max_amplitude', 0))
        
        # Truncate filename if too long
        display_name = filename if len(filename) <= 20 else filename[:17] + "..."
        ax.set_title(f"{display_name}\n{duration:.2f}s, amp={max_amp:.3f}", fontsize=8)
        ax.set_xlabel('Frequency (Hz)', fontsize=8)
        ax.set_ylabel('PSD', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=7)
    
    # Hide unused subplots
    for i in range(n_files, len(axes_flat)):
        axes_flat[i].set_visible(False)
    
    # Handle title with available fields
    nfft_info = audio_data.get('psd_n_fft', audio_data.get('nfft', 'unknown'))
    dual_res_info = " (Dual-Res)" if audio_data.get('dual_resolution', False) else ""
    
    plt.suptitle(f'Unified PSD Grid - {audio_data["directory_name"]} ({n_files} files){dual_res_info}', fontsize=14)
    plt.tight_layout()
    
    if save_plot:
        filepath = save_path / f"psd_grid_{audio_data['directory_name']}_{nfft_info}fft.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Unified PSD Grid plot saved as: {filepath.resolve()}")
    
    plt.show()

def plot_mean_log_psd(audio_data, freq_range=None, save_plot=True, save_dir="../psd_plots"):
    """
    Plot mean PSD with individual psd overlay (peak detection removed).
    """
    if audio_data is None:
        return

    # Create save directory
    if save_plot:
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)

    # Extract data
    psd_array = audio_data['psd']
    mean_psd = audio_data['mean_psd']
    std_psd = audio_data['std_psd']
    freqs = audio_data['frequencies']

    # Set frequency range
    if freq_range is None:
        freq_range = (0, audio_data['sample_rate'] // 2)
    
    freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
    freqs_plot = freqs[freq_mask]
    
    # Create plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    
    # Plot individual psd using LINEAR scale
    if len(psd_array) <= 50:
        for psd in psd_array:
            ax.plot(freqs_plot, psd[freq_mask], alpha=0.2, color='lightblue', linewidth=0.5)
    
    # Plot mean PSD - LOGARITHMIC SCALE
    ax.semilogy(freqs_plot, mean_psd[freq_mask], 'b-', linewidth=2, label=f'Mean PSD (n={len(psd_array)})')

    # Plot confidence interval
    upper = mean_psd[freq_mask] + std_psd[freq_mask]
    lower = np.maximum(mean_psd[freq_mask] - std_psd[freq_mask], 1e-10)  # No negative values
    ax.fill_between(freqs_plot, lower, upper, alpha=0.3, color='blue', label='±1 std')

    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Power Spectral Density (Log PSD, log plot)')
    ax.set_title(f'Mean PSD Analysis - {audio_data["directory_name"]}\n'
                f'{len(psd_array)} files, {audio_data.get("psd_n_fft", audio_data.get("nfft", "unknown"))}-point FFT')

    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_plot:
        nfft_info = audio_data.get('psd_n_fft', audio_data.get('nfft', 'unknown'))
        filepath = save_path / f"psd_mean_{audio_data['directory_name']}_{nfft_info}fft.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Mean PSD plot saved as: {filepath.resolve()}")
    
    plt.show()

def plot_low_freq_detail(audio_data, low_freq_limit=1000, save_plot=True, save_dir="../psd_plots"):
    """
    Plot linear scale view of low frequencies.
    
    Args:
        audio_data: Dictionary returned from calculate_psd_spectro
        low_freq_limit: Upper frequency limit for detail view (Hz)
        save_plot: Whether to save the plot
        save_dir: Directory to save plots
    """
    if audio_data is None:
        return
    
    # Create save directory
    if save_plot:
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
    
    # Extract data
    mean_psd = audio_data['mean_psd']
    std_psd = audio_data['std_psd']
    freqs = audio_data['frequencies']
    
    # Focus on low frequencies
    low_freq_mask = freqs <= low_freq_limit
    freqs_low = freqs[low_freq_mask]
    mean_psd_low = mean_psd[low_freq_mask]
    std_psd_low = std_psd[low_freq_mask]
    
    # Create plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    
    # Plot mean PSD
    ax.plot(freqs_low, mean_psd_low, 'b-', linewidth=2, label='Mean PSD')
    
    # Plot confidence interval
    upper = mean_psd_low + std_psd_low
    lower = np.maximum(mean_psd_low - std_psd_low, 0)  # No negative values on linear scale
    ax.fill_between(freqs_low, lower, upper, alpha=0.3, color='blue', label='±1 std')
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Power Spectral Density (Linear)')
    ax.set_title(f'Low Frequency Detail - {audio_data["directory_name"]} (0-{low_freq_limit} Hz)\n'
                f'Peak frequency: {audio_data["peak_frequency"]:.1f} Hz')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_plot:
        nfft_info = audio_data.get('psd_n_fft', audio_data.get('nfft', 'unknown'))
        filepath = save_path / f"psd_lowfreq_{audio_data['directory_name']}_{nfft_info}fft.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Low frequency plot saved as: {filepath.resolve()}")
    
    plt.show()

# SPECTROGRAM PLOTTING FUNCTIONS (unchanged from paste 1)

def plot_beautiful_spectrogram(audio_data, file_index=0, 
                              freq_range=None, time_range=None,
                              colormap='magma', figsize=(8, 4),
                              db_range=(-80, 0), interpolation='bilinear',
                              save_plot=True, save_dir="../spectro_plots"):
    """Create a beautiful spectrogram like Audacity/Sonic Visualiser."""
    
    # Get spectrogram data
    if len(audio_data['file_info']) == 1:
        spec = audio_data['spectrograms']
        filename = audio_data['file_info'].iloc[0]['filename']
    else:
        spec = audio_data['spectrograms'][file_index]
        filename = audio_data['file_info'].iloc[file_index]['filename']
    
    frequencies = audio_data['frequencies']
    times = audio_data['times']
    
    # Convert to dB with proper dynamic range
    spec_db = 10 * np.log10(spec + 1e-10)  # Add small epsilon to avoid log(0)
    
    # Apply frequency range if specified
    if freq_range:
        freq_mask = (frequencies >= freq_range[0]) & (frequencies <= freq_range[1])
        if not np.any(freq_mask):
            print(f"Warning: No frequencies found in range {freq_range}")
            freq_mask = np.ones(len(frequencies), dtype=bool)
        frequencies = frequencies[freq_mask]
        spec_db = spec_db[freq_mask, :]
    
    # Apply time range if specified
    if time_range:
        time_mask = (times >= time_range[0]) & (times <= time_range[1])
        if not np.any(time_mask):
            print(f"Warning: No time points found in range {time_range}. Audio duration: {times[-1]:.2f}s")
            time_mask = np.ones(len(times), dtype=bool)
        times = times[time_mask]
        spec_db = spec_db[:, time_mask]
    
    # Check if we have data to plot
    if len(times) == 0 or len(frequencies) == 0:
        print("Error: No data to plot after filtering")
        return
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize, facecolor='black')
    ax.set_facecolor('black')
    
    # Main spectrogram
    im = ax.imshow(spec_db, 
                   aspect='auto', 
                   origin='lower',
                   extent=[times[0], times[-1], frequencies[0], frequencies[-1]],
                   vmin=db_range[0], vmax=db_range[1],
                   cmap=colormap,
                   interpolation=interpolation)
    
    # Professional styling
    ax.set_xlabel('Time (s)', fontsize=14, color='white')
    ax.set_ylabel('Frequency (Hz)', fontsize=14, color='white')
    ax.set_title(f'Spectrogram: {filename}', fontsize=16, color='white', pad=20)
    
    # Style the axes
    ax.tick_params(colors='white', labelsize=12)
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white') 
    ax.spines['right'].set_color('white')
    ax.spines['left'].set_color('white')
    
    # Beautiful colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cbar.set_label('Power (dB)', fontsize=14, color='white')
    cbar.ax.tick_params(colors='white', labelsize=12)
    cbar.outline.set_edgecolor('white')
    
    # Frequency axis formatting (like professional software)
    if frequencies[-1] > 10000:
        # Add secondary kHz labels for high frequencies
        ax2 = ax.twinx()
        ax2.set_ylim(frequencies[0]/1000, frequencies[-1]/1000)
        ax2.set_ylabel('Frequency (kHz)', fontsize=14, color='white')
        ax2.tick_params(colors='white', labelsize=12)
        ax2.spines['right'].set_color('white')
    
    plt.tight_layout()

    if save_plot:
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        filename = audio_data['file_info'].iloc[file_index]['filename'] if len(audio_data['file_info']) > 1 else audio_data['file_info'].iloc[0]['filename']
        filepath = save_path / f"spectro_beautiful_{filename[:-4]}.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='black')
        print(f"Beautiful spectrogram saved as: {filepath.resolve()}")

    plt.show()

# Professional style functions for spectrograms
def plot_sonic_visualizer_style(audio_data, file_index=0, **kwargs):
    """Sonic Visualiser inspired spectrogram."""
    plot_beautiful_spectrogram(audio_data, file_index, 
                              colormap='plasma', 
                              db_range=(-100, -20),
                              **kwargs)

def plot_audacity_style(audio_data, file_index=0, **kwargs):
    """Audacity inspired spectrogram."""
    plot_beautiful_spectrogram(audio_data, file_index,
                              colormap='hot',
                              db_range=(-80, 0),
                              **kwargs)

def plot_prism_style(audio_data, file_index=0, **kwargs):
    """High-contrast scientific style."""
    plot_beautiful_spectrogram(audio_data, file_index,
                              colormap='viridis',
                              db_range=(-60, 0),
                              interpolation='gaussian',
                              **kwargs)

# UNIFIED GRID
def plot_spectro_grid(audio_data, grid_cols=4, freq_range=None, time_range=None, 
                                colormap='magma', db_range=(-80, 0), save_plot=True, save_dir="../spectro_plots"):
    """Plot grid of individual spectrograms."""
    if audio_data is None:
        return
    
    # Create save directory
    if save_plot:
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
    
    # Extract data - handle both single file and directory results
    if len(audio_data['file_info']) == 1:
        spectrograms = [audio_data['spectrograms']]  # Single file
    else:
        spectrograms = audio_data['spectrograms']   # Directory
    
    frequencies = audio_data['frequencies']
    times = audio_data['times']
    file_info = audio_data['file_info']
    
    # Apply frequency range filtering
    if freq_range is None:
        freq_range = (frequencies[0], frequencies[-1])
    
    freq_mask = (frequencies >= freq_range[0]) & (frequencies <= freq_range[1])
    if not np.any(freq_mask):
        print(f"Warning: No frequencies found in range {freq_range}")
        freq_mask = np.ones(len(frequencies), dtype=bool)
    freqs_plot = frequencies[freq_mask]
    
    # Apply time range filtering
    if time_range is None:
        time_range = (times[0], times[-1])
    
    time_mask = (times >= time_range[0]) & (times <= time_range[1])
    if not np.any(time_mask):
        print(f"Warning: No time points found in range {time_range}")
        time_mask = np.ones(len(times), dtype=bool)
    times_plot = times[time_mask]
    
    # Calculate grid dimensions
    n_files = len(spectrograms)
    grid_rows = math.ceil(n_files / grid_cols)
    
    # Create figure with larger subplots for spectrograms
    fig, axes = plt.subplots(grid_rows, grid_cols, figsize=(5*grid_cols, 4*grid_rows))
    
    # Handle single subplot case
    if n_files == 1:
        axes = np.array([axes])
    
    # Handle single row/column cases
    if grid_rows == 1 and n_files > 1:
        axes = axes.reshape(1, -1)
    elif grid_cols == 1 and n_files > 1:
        axes = axes.reshape(-1, 1)
    
    # Ensure axes is always iterable for consistent indexing
    axes_flat = axes.flatten() if hasattr(axes, 'flatten') else [axes]
    
    # Plot each individual spectrogram
    for i in range(n_files):
        ax = axes_flat[i]
        
        # Get spectrogram and apply filters
        spec = spectrograms[i]
        spec_filtered = spec[freq_mask, :][:, time_mask]
        
        # Convert to dB
        spec_db = 10 * np.log10(spec_filtered + 1e-10)
        
        # Plot spectrogram
        im = ax.imshow(spec_db, 
                      aspect='auto', 
                      origin='lower',
                      extent=[times_plot[0], times_plot[-1], freqs_plot[0], freqs_plot[-1]],
                      vmin=db_range[0], vmax=db_range[1],
                      cmap=colormap,
                      interpolation='bilinear')
        
        # Formatting - handle both old and new field names
        filename = file_info.iloc[i]['filename']
        duration = file_info.iloc[i].get('original_duration', file_info.iloc[i].get('duration', 0))
        max_amp = file_info.iloc[i].get('original_max_amplitude', file_info.iloc[i].get('max_amplitude', 0))
        
        # Truncate filename if too long
        display_name = filename if len(filename) <= 20 else filename[:17] + "..."
        ax.set_title(f"{display_name}\n{duration:.2f}s, amp={max_amp:.3f}", fontsize=10)
        ax.set_xlabel('Time (s)', fontsize=8)
        ax.set_ylabel('Frequency (Hz)', fontsize=8)
        ax.tick_params(labelsize=7)
        
        # Add colorbar to each subplot
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
        cbar.set_label('Power (dB)', fontsize=8)
        cbar.ax.tick_params(labelsize=6)
    
    # Hide unused subplots
    for i in range(n_files, len(axes_flat)):
        axes_flat[i].set_visible(False)
    
    # Handle title with available fields
    nfft_info = audio_data.get('spec_n_fft', audio_data.get('nfft', 'unknown'))
    dual_res_info = " (Dual-Res)" if audio_data.get('dual_resolution', False) else ""
    
    plt.suptitle(f'Unified Grid Spectrograms - {audio_data["directory_name"]} ({n_files} files){dual_res_info}', fontsize=14)
    plt.tight_layout()
    
    if save_plot:
        filepath = save_path / f"spectro_grid_{audio_data['directory_name']}_{nfft_info}fft.png"
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"Unified spectrogram grid plot saved as: {filepath.resolve()}")
    
    plt.show()


# PSD and spectrograms for directory of directories
def psd_spectro_dir_of_dirs(main_slice_dir, fmin=300):
    """
    Analyze PSD and spectrograms for audio slicesfrom within double-nested dir structure.
    
    Parameters:
    -----------
    main_slice_dir : str
        Path to directory containing voice subdirectories (e.g., '../tranche/slices/v2_2020')
    kiwi_cutoff : int, optional
        Frequency cutoff for analysis (default: 300 Hz)
    
    Returns:
    --------
    dict
        Summary statistics of processed files per voice directory
    """
    import os
    
    # Get all subdirectories (each voice recording)
    voice_dirs = jelfun.get_subdir_pathlist(main_slice_dir)
    
    processing_summary = {}
    
    for voice_dir in voice_dirs:
        voice_name = os.path.basename(voice_dir)
        print(f"Processing voice directory: {voice_name}")
        
        # Get all audio files in this voice directory
        slicedir_pathlist = jelfun.get_subdir_pathlist(voice_dir)
        
        if len(slicedir_pathlist) == 0:
            print(f"  No audio files found in {voice_name}")
            processing_summary[voice_name] = 0
            continue
        
        print(f"  Found {len(slicedir_pathlist)} audio files")
        
        # Process all slices for this voice
        processed_count = 0
        for path in slicedir_pathlist:
            try:
                audio_data = calculate_psd_spectro(path, fmin)
                plot_psd_grid(audio_data)
                plot_spectro_grid(audio_data)
                processed_count += 1
            except Exception as e:
                print(f"  Error processing {os.path.basename(path)}: {e}")
        
        processing_summary[voice_name] = processed_count
        print(f"  Completed analysis for {voice_name}: {processed_count} files")
        print("-" * 50)
    
    return processing_summary




# ============================================= # =============================================
# Setup paths
# ============================================= # =============================================

# Example directory of slices
# slice_dir = r'D:\anvo\kiwi\tranche\slices\both'

# Get list of paths from directory
# allpaths = jelfun.get_subdir_pathlist(slice_dir)

# print(f"Number of directories found: {len(allpaths)}")
# print(f"First directory path: {single_dir}")
# print(f"First wav file: {single_wav}")



# ============================================= # =============================================
# Single USAGI
# ============================================= # =============================================

# # Path to a single kiwi syllable
# path='../tranche/slices/v2_2020/vox_14_41_27/slice_6.wav'

# # Calculate psd and spectrogram for single file, with a lowcut filter of 500 Hz
# audio_data = calculate_psd_spectro(path, fmin=500)

# # Plot psd and spectrogram
# plot_psd_grid(audio_data)
# plot_spectro_grid(audio_data)


# # Plotting stats and metrics
# plot_mean_log_psd(audio_data)
# plot_low_freq_detail(audio_data)
# # Unified psd grid
# plot_psd_grid(audio_data)

# # Spectrograms
# # Single spectro plots
# plot_beautiful_spectrogram(audio_data)
# plot_sonic_visualizer_style(audio_data)
# plot_audacity_style(audio_data)
# plot_prism_style(audio_data)
# # Unified spectro grid
# plot_spectro_grid(audio_data)



# ============================================= # =============================================
# Batch USAGI
# ============================================= # =============================================

# # Path to a directory of kiwi syllables
# slice_dir='../tranche/slices/v2_2020/vox_14_41_27'

# slicedir_pathlist = jelfun.get_subdir_pathlist(slice_dir)

# for path in slicedir_pathlist:
#     audio_data = calculate_psd_spectro(path, fmin=500)
#     plot_psd_grid(audio_data)
#     plot_spectro_grid(audio_data)


# ============================================= # =============================================
# Directory of directories
# ============================================= # =============================================

# main_slice_dir = '../tranche/slices/v2_2020'
# summary = psd_spectro_dir_of_dirs(main_slice_dir, fmin=500)

# print(f"\nProcessing complete. Total voices analyzed: {len(summary)}")
# print(f"Total files processed: {sum(summary.values())}")