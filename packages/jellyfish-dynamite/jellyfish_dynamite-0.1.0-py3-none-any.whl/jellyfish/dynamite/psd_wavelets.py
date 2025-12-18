# /jellyfish/dynamite/psd_wavelets.py

import librosa
import numpy as np
import pywt
from scipy import signal
from scipy.interpolate import interp1d

# ==================== PSD CALCULATION METHODS ====================

def cqt_based_psd(audio_path, bins_per_octave=36, n_bins=144, fmin=20.0, fmax=None, hop_length=128, n_fft=512):
    """Calculate PSD using Constant-Q Transform."""
    y, sr = librosa.load(audio_path, sr=None)
    
    if fmax is None:
        fmax = sr / 2
    if hop_length is None:
        hop_length = n_fft // 8
    
    C = librosa.cqt(y, sr=sr, fmin=fmin, n_bins=n_bins, 
                    bins_per_octave=bins_per_octave, hop_length=hop_length)
    power_spectrum = np.abs(C)**2
    psd_mean = np.mean(power_spectrum, axis=1)
    frequencies = librosa.cqt_frequencies(n_bins=n_bins, fmin=fmin, bins_per_octave=bins_per_octave)
    
    return frequencies, psd_mean

def multi_resolution_psd(audio_path, fft_sizes=[512, 1024, 2048, 4096], n_fft=None, hop_length=None):
    """Calculate PSD using multiple FFT window sizes."""
    y, sr = librosa.load(audio_path, sr=None)
    fft_sizes = sorted(fft_sizes)
    
    if n_fft is None:
        n_fft = max(fft_sizes)
    
    cutoff_freqs = []
    for i in range(len(fft_sizes) - 1):
        cutoff = np.sqrt(sr / fft_sizes[i] * sr / fft_sizes[i+1])
        cutoff_freqs.append(cutoff)
    cutoff_freqs.append(sr/2)
    
    out_frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    out_psd = np.zeros_like(out_frequencies)
    
    for i, curr_n_fft in enumerate(fft_sizes):
        curr_hop_length = hop_length if hop_length else curr_n_fft // 4
        
        stft_result = librosa.stft(y, n_fft=curr_n_fft, hop_length=curr_hop_length)
        power_spectrum = np.abs(stft_result)**2
        curr_psd = np.mean(power_spectrum, axis=1)
        curr_freqs = librosa.fft_frequencies(sr=sr, n_fft=curr_n_fft)
        
        if i == 0:
            freq_mask = (out_frequencies > cutoff_freqs[i])
        elif i == len(fft_sizes) - 1:
            freq_mask = (out_frequencies <= cutoff_freqs[i-1])
        else:
            freq_mask = (out_frequencies > cutoff_freqs[i-1]) & (out_frequencies <= cutoff_freqs[i])
        
        f_interp = interp1d(curr_freqs, curr_psd, kind='linear', 
                           bounds_error=False, fill_value=(curr_psd[0], curr_psd[-1]))
        out_psd[freq_mask] = f_interp(out_frequencies[freq_mask])
        
        if i == len(fft_sizes) - 1:
            zero_mask = (out_psd == 0)
            if np.any(zero_mask):
                out_psd[zero_mask] = f_interp(out_frequencies[zero_mask])
    
    return out_frequencies, out_psd

def chirplet_transform(audio_path, n_chirps=100, min_freq=20, max_freq=5000, n_fft=None):
    """Simplified chirplet transform for adaptive time-frequency analysis."""
    from scipy import signal
    
    y, sr = librosa.load(audio_path, sr=None)
    
    frequencies = np.logspace(np.log10(min_freq), np.log10(max_freq), n_chirps)
    chirp_energies = np.zeros(n_chirps)
    
    for i, freq in enumerate(frequencies):
        t = np.arange(0, len(y)/sr, 1/sr)
        chirp = signal.chirp(t, f0=freq*0.8, f1=freq*1.2, t1=len(y)/sr, method='logarithmic')
        window = signal.windows.hann(len(chirp))
        chirp *= window
        correlation = signal.correlate(y, chirp, mode='same')
        chirp_energies[i] = np.max(np.abs(correlation)**2)
    
    return frequencies, chirp_energies

def chirplet_transform_zero_padding(audio_path, n_chirps=100, min_freq=20, max_freq=5000, n_fft=2048):
    """Simplified chirplet transform with zero-padding."""
    from scipy import signal
    
    y, sr = librosa.load(audio_path, sr=None)
    
    if len(y) < n_fft:
        y = np.pad(y, (0, n_fft - len(y)), 'constant')
    
    frequencies = np.logspace(np.log10(min_freq), np.log10(max_freq), n_chirps)
    chirp_energies = np.zeros(n_chirps)
    
    for i, freq in enumerate(frequencies):
        t = np.arange(0, len(y)/sr, 1/sr)
        chirp = signal.chirp(t, f0=freq*0.8, f1=freq*1.2, t1=len(y)/sr, method='logarithmic')
        window = signal.windows.hann(len(chirp))
        chirp *= window
        correlation = signal.correlate(y, chirp, mode='same')
        chirp_energies[i] = np.max(np.abs(correlation)**2)
    
    return frequencies, chirp_energies

def wavelet_packet_psd(audio_path, wavelet='sym8', max_level=8, hop_length=None, n_fft=2048):
    """Calculate PSD using Wavelet Packet Decomposition."""
    import pywt
    
    y, sr = librosa.load(audio_path, sr=None)
    print(f"Original Wavelet - Signal length: {len(y)}, Sample rate: {sr}")
    
    # Calculate padded length for better frequency resolution
    pad_length = 2**int(np.ceil(np.log2(len(y))))
    y_padded = np.pad(y, (0, pad_length - len(y)), 'constant')
    
    # Calculate optimal level based on the amount of data and desired frequency resolution
    optimal_level = min(int(np.log2(n_fft)), int(np.log2(len(y_padded))) - 2)
    
    if max_level > optimal_level:
        print(f"WARNING: Adjusting max_level from {max_level} to {optimal_level} for better accuracy")
        max_level = optimal_level
    
    if hop_length is None:
        hop_length = n_fft // 4
    
    segment_size = n_fft
    
    if len(y) < segment_size:
        y = np.pad(y, (0, segment_size - len(y)), 'constant')
    
    # Remove the try-except that was silently failing
    wp = pywt.WaveletPacket(data=y, wavelet=wavelet, mode='symmetric', maxlevel=max_level)
    nodes = [node for node in wp.get_level(max_level, 'natural')]
    powers = [np.mean(np.abs(node.data)**2) for node in nodes]
    powers = [max(p, 1e-10) for p in powers]
    
    # Define correction factors to fix frequency shift issue
    correction_factors = {
        'db4': 1.15,
        'db8': 1.12,
        'sym8': 1.05,
        'coif5': 1.03
    }
    correction = correction_factors.get(wavelet, 1.0)
    
    freqs = []
    nyquist = sr / 2
    bands = 2**max_level
    for i in range(bands):
        low = i * nyquist / bands * correction
        high = (i + 1) * nyquist / bands * correction
        center = (low + high) / 2
        freqs.append(center)
    
    if sum(powers) > 0:
        powers = [p / sum(powers) for p in powers]
    else:
        raise ValueError(f"All wavelet powers are zero for file {audio_path}. This indicates a problem with the input signal or wavelet decomposition.")
        
    print(f"Original Wavelet - Success. PSD range: {min(powers):.2e} to {max(powers):.2e}")
    return np.array(freqs), np.array(powers)

def improved_wavelet_packet_psd(audio_path, wavelet='sym8', max_level=8, hop_length=None, n_fft=2048):
    """Improved version of wavelet packet PSD with better frequency resolution."""
    import pywt
    
    y, sr = librosa.load(audio_path, sr=None)
    print(f"Improved Wavelet - Signal length: {len(y)}, Sample rate: {sr}")
    
    pow2_length = 2**int(np.ceil(np.log2(len(y))))
    if len(y) < pow2_length:
        y = np.pad(y, (0, pow2_length - len(y)), 'constant')
    
    optimal_level = min(int(np.log2(n_fft)), int(np.log2(len(y))) - 2)
    if max_level > optimal_level:
        print(f"WARNING: Adjusting max_level from {max_level} to {optimal_level} for better accuracy")
        max_level = optimal_level
    
    out_freqs = np.linspace(20, sr/2, n_fft//2)
    out_psd = np.zeros_like(out_freqs)
    
    wp = pywt.WaveletPacket(data=y, wavelet=wavelet, mode='symmetric', maxlevel=max_level)
    nodes = [node for node in wp.get_level(max_level, 'natural')]
    
    if not nodes:
        raise ValueError(f"No nodes found in wavelet packet decomposition for file {audio_path}. Check input signal and parameters.")
    
    energies = []
    for node in nodes:
        energy = np.sum(np.abs(node.data)**2)
        energies.append(max(energy, 1e-20))
    
    total_energy = sum(energies)
    if total_energy == 0:
        raise ValueError(f"Total energy is zero for file {audio_path}. This indicates a problem with the input signal.")
    
    # Calculate actual frequency bands without any "correction"
    bands = 2**max_level
    band_width = sr / (2 * bands)
    band_centers = np.array([(i * band_width + band_width/2) for i in range(bands)])
    powers = np.array(energies) / total_energy
    
    from scipy import interpolate
    if len(band_centers) > 1:
        interp_func = interpolate.interp1d(
            band_centers, powers, 
            kind='linear',
            bounds_error=False, 
            fill_value=(powers[0], powers[-1])
        )
        out_psd = interp_func(out_freqs)
    else:
        out_psd = np.ones_like(out_freqs) * powers[0]
    
    from scipy.signal import savgol_filter
    window_length = min(21, len(out_psd) // 5 * 2 + 1)
    if window_length > 3 and window_length % 2 == 1:
        out_psd = savgol_filter(out_psd, window_length, 2)
    
    out_psd = np.maximum(out_psd, 1e-10)
    
    print(f"Improved Wavelet - Success. PSD range: {np.min(out_psd):.2e} to {np.max(out_psd):.2e}")
    return out_freqs, out_psd

def stationary_wavelet_psd(audio_path, wavelet='sym8', max_level=6, n_fft=2048):
    """Calculate PSD using Stationary Wavelet Transform (shift-invariant)."""
    import pywt
    
    y, sr = librosa.load(audio_path, sr=None)
    print(f"Stationary Wavelet - Signal length: {len(y)}, Sample rate: {sr}")
    
    target_length = int(2**np.ceil(np.log2(len(y))))
    y_padded = np.pad(y, (0, target_length - len(y)), 'constant')
    
    optimal_level = min(int(np.log2(n_fft)), int(np.log2(len(y_padded))) - 3)
    
    if max_level > optimal_level:
        print(f"WARNING: Adjusting max_level from {max_level} to {optimal_level}")
        max_level = max(1, optimal_level)
    
    out_freqs = np.linspace(20, sr/2, n_fft//2)
    out_psd = np.zeros_like(out_freqs)
    
    # Check if level is too high for the signal length
    if max_level >= int(np.log2(len(y_padded))):
        raise ValueError(f"max_level {max_level} is too high for signal length {len(y_padded)}. "
                        f"Maximum possible level is {int(np.log2(len(y_padded))) - 1}")
    
    coeffs = pywt.swt(y_padded, wavelet, level=max_level)
    
    level_powers = []
    level_freqs = []
    
    for i, (cA, cD) in enumerate(coeffs):
        level = max_level - i
        power = np.mean(np.abs(cD)**2)
        
        # Calculate actual frequency bands without any "correction"
        band_width = sr / (2**(level+1))
        low_freq = band_width
        high_freq = 2 * band_width
        center_freq = (low_freq + high_freq) / 2
        
        level_powers.append(power)
        level_freqs.append(center_freq)
    
    power = np.mean(np.abs(coeffs[-1][0])**2)
    center_freq = sr / (2**(max_level+1)) / 2
    level_powers.append(power)
    level_freqs.append(center_freq)
    
    total_power = sum(level_powers)
    if total_power > 0:
        level_powers = [p / total_power for p in level_powers]
    else:
        raise ValueError(f"Total power is zero for file {audio_path} using stationary wavelet transform. Check input signal.")
    
    for i, (freq, power) in enumerate(zip(level_freqs, level_powers)):
        idx = np.abs(out_freqs - freq).argmin()
        out_psd[idx] = power
    
    from scipy.interpolate import interp1d
    valid_indices = np.where(out_psd > 0)[0]
    if len(valid_indices) > 1:
        f_interp = interp1d(
            out_freqs[valid_indices], 
            out_psd[valid_indices],
            kind='linear', 
            bounds_error=False, 
            fill_value=(out_psd[valid_indices[0]], out_psd[valid_indices[-1]])
        )
        out_psd = f_interp(out_freqs)
    
    from scipy.signal import savgol_filter
    window_length = min(21, len(out_psd) // 5 * 2 + 1)
    if window_length > 3:
        out_psd = savgol_filter(out_psd, window_length, 2)
    
    out_psd = np.maximum(out_psd, 1e-10)
    
    print(f"Stationary Wavelet - Success. PSD range: {np.min(out_psd):.2e} to {np.max(out_psd):.2e}")
    return out_freqs, out_psd