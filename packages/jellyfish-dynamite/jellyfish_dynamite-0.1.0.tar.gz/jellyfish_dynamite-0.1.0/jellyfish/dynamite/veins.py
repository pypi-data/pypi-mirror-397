# dynamite/veins.py

import matplotlib.pyplot as plt
import numpy as np

from .ridge import find_max_energy_ridge

# ==================== SPECTRAL VEINS DETECTION ====================

def find_spectral_veins(spectrogram, frequencies, times, num_veins=6, freq_window=50):
    """Find veins by tracking bright regions in specific frequency bands."""
    spec_db = 10 * np.log10(np.maximum(spectrogram, 1e-10))
    
    # Find strongest frequency regions across all time
    overall_energy = np.mean(spec_db, axis=1)
    
    # Find peak frequency regions
    from scipy.signal import find_peaks
    peak_indices, _ = find_peaks(overall_energy, prominence=np.std(overall_energy)*0.3)
    
    # Sort by strength and take top num_veins
    if len(peak_indices) > 0:
        peak_strengths = overall_energy[peak_indices]
        top_peak_indices = peak_indices[np.argsort(peak_strengths)[-num_veins:]][::-1]
    else:
        # Fallback: just use strongest frequencies
        top_peak_indices = np.argsort(overall_energy)[-num_veins:][::-1]
    
    veins = []
    
    for i, center_freq_idx in enumerate(top_peak_indices):
        center_freq = frequencies[center_freq_idx]
        
        # Define frequency window around this peak
        freq_range = slice(max(0, center_freq_idx - freq_window//2), 
                          min(len(frequencies), center_freq_idx + freq_window//2))
        
        vein_times = []
        vein_freqs = []
        
        # For each time slice, find max energy within this frequency window
        for t_idx in range(spec_db.shape[1]):
            window_slice = spec_db[freq_range, t_idx]
            if len(window_slice) > 0:
                local_max_idx = np.argmax(window_slice)
                global_freq_idx = freq_range.start + local_max_idx
                
                vein_times.append(times[t_idx])
                vein_freqs.append(frequencies[global_freq_idx])
        
        veins.append({
            'times': np.array(vein_times),
            'freqs': np.array(vein_freqs),
            'center_freq': center_freq,
            'rank': i + 1
        })
    
    return veins

def plot_spectrogram_with_veins(frequencies, times, spectrogram, show_max_ridge=True, show_multi_veins=True, num_veins=5):
    """Plot spectrogram with optional vein overlays."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot spectrogram
    spec_db = 10 * np.log10(np.maximum(spectrogram, 1e-10))
    im = ax.imshow(spec_db.T, aspect='auto', origin='lower',
                   extent=[frequencies[0], frequencies[-1], times[0], times[-1]],
                   cmap='magma')
    
    # Add max energy RIDGE (SOLID CYAN LINE)
    if show_max_ridge: 
        ridge_times, ridge_freqs = find_max_energy_ridge(spectrogram, frequencies, times) 
        ax.plot(ridge_freqs, ridge_times, 'c-', linewidth=2.2, alpha=0.9)
        
        # Calculate visual slope (time vs frequency)
        visual_slope, _ = np.polyfit(ridge_freqs, ridge_times, 1)
        print(f"Max Energy Ridge visual slope: {visual_slope:.6f} s/Hz")
    
    # Add multiple spectral VEINS (DASHED COLORED LINES)
    if show_multi_veins:
        # veins = find_spectral_veins(spectrogram, frequencies, times, num_veins)
        # veins = find_spectral_veins_coherent(spectrogram, frequencies, times, num_veins, smoothing_window=8, coherence_threshold=0.4)
        veins = find_spectral_veins_flexible(spectrogram, frequencies, times, num_veins)



        vein_colors = ['coral', 'yellow', 'magenta', 'lime', 'orange', 'teal', 'green', 'plum', 'orchid']
            
        for i, vein in enumerate(veins[:len(vein_colors)]):
            if len(vein['freqs']) > 0:
                # Draw the dashed line
                ax.plot(vein['freqs'], vein['times'], '--', 
                    color=vein_colors[i], linewidth=1.8, alpha=0.7)
                
                # Find point of maximum energy along this vein
                vein_energies = []
                for freq, time in zip(vein['freqs'], vein['times']):
                    freq_idx = np.argmin(np.abs(frequencies - freq))
                    time_idx = np.argmin(np.abs(times - time))
                    energy = spectrogram[freq_idx, time_idx]
                    vein_energies.append(energy)
                
                if vein_energies:
                    max_energy_idx = np.argmax(vein_energies)
                    max_freq = vein['freqs'][max_energy_idx]
                    max_time = vein['times'][max_energy_idx]
                    
                    # Add a dot at the maximum energy point
                    ax.plot(max_freq, max_time, 'o', 
                        color=vein_colors[i], markersize=6, 
                        markeredgecolor='white', markeredgewidth=1)
                
                visual_slope, _ = np.polyfit(vein['freqs'], vein['times'], 1)
                print(f"Spectral Vein {vein['rank']} visual slope: {visual_slope:.6f} s/Hz")
                
    
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Time (s)')
    plt.colorbar(im, ax=ax, label='Power (dB)')
    return fig, ax






def find_spectral_veins_flexible(spectrogram, frequencies, times, num_veins=6):
    """
    Find flexible spectral veins that can handle direction changes and longer tracks.
    """
    from scipy import ndimage
    from scipy.signal import find_peaks
    
    spec_db = 10 * np.log10(np.maximum(spectrogram, 1e-10))
    
    # Light smoothing to preserve detail while reducing noise
    spec_smooth = ndimage.gaussian_filter(spec_db, sigma=[2, 2])
    
    # Find all significant peaks across the entire spectrogram
    all_peaks = []
    for t_idx in range(spec_smooth.shape[1]):
        freq_slice = spec_smooth[:, t_idx]
        peaks, properties = find_peaks(freq_slice, 
                                     prominence=np.std(freq_slice) * 0.3,
                                     distance=10)
        
        for peak_idx in peaks:
            all_peaks.append({
                'freq_idx': peak_idx,
                'time_idx': t_idx,
                'strength': freq_slice[peak_idx],
                'freq': frequencies[peak_idx],
                'time': times[t_idx]
            })
    
    # Build tracks using dynamic programming approach
    tracks = build_flexible_tracks(all_peaks, max_time_gap=3, adaptive_freq_jump=True)
    
    # Convert to vein format
    veins = []
    for i, track in enumerate(tracks[:num_veins]):
        if len(track) >= 5:  # Minimum length
            track_times = [pt['time'] for pt in track]
            track_freqs = [pt['freq'] for pt in track]
            
            veins.append({
                'times': np.array(track_times),
                'freqs': np.array(track_freqs),
                'strength': np.mean([pt['strength'] for pt in track]),
                'rank': i + 1
            })
    
    return veins

def build_flexible_tracks(peaks, max_time_gap=3, adaptive_freq_jump=True):
    """Build tracks that can handle direction changes and long continuous paths."""
    
    # Sort peaks by time, then by strength
    peaks.sort(key=lambda x: (x['time_idx'], -x['strength']))
    
    tracks = []
    used_peaks = set()
    
    for seed_peak in peaks:
        if id(seed_peak) in used_peaks:
            continue
            
        # Start new track
        track = [seed_peak]
        used_peaks.add(id(seed_peak))
        
        # Extend track forward through time
        current_peak = seed_peak
        
        while True:
            next_peak = find_best_continuation(current_peak, peaks, used_peaks, 
                                             max_time_gap, adaptive_freq_jump)
            if next_peak is None:
                break
                
            track.append(next_peak)
            used_peaks.add(id(next_peak))
            current_peak = next_peak
        
        if len(track) >= 5:  # Only keep substantial tracks
            tracks.append(track)
    
    # Sort tracks by total strength and length
    tracks.sort(key=lambda t: (-len(t) * np.mean([p['strength'] for p in t])))
    
    return tracks

def find_best_continuation(current_peak, all_peaks, used_peaks, max_time_gap, adaptive_freq_jump):
    """Find the best next peak to continue a track, allowing for direction changes."""
    
    candidates = []
    
    for peak in all_peaks:
        if id(peak) in used_peaks:
            continue
            
        time_diff = peak['time_idx'] - current_peak['time_idx']
        
        # Must be forward in time but within gap limit
        if time_diff <= 0 or time_diff > max_time_gap:
            continue
            
        freq_diff = abs(peak['freq_idx'] - current_peak['freq_idx'])
        
        # Adaptive frequency jump based on time gap
        if adaptive_freq_jump:
            max_freq_jump = 20 + (time_diff * 10)  # Allow larger jumps for larger time gaps
        else:
            max_freq_jump = 25
            
        if freq_diff <= max_freq_jump:
            # Score based on strength, proximity, and continuity
            proximity_score = 1.0 / (1 + freq_diff + time_diff * 2)
            strength_score = peak['strength'] / 100.0  # Normalize strength
            
            total_score = proximity_score + strength_score
            
            candidates.append((peak, total_score))
    
    if not candidates:
        return None
        
    # Return the best candidate
    candidates.sort(key=lambda x: -x[1])
    return candidates[0][0]