# jellyfish/tracer/trace.py
# Interactive Spectrogram Tracer Tool
# Builds on dynamo.py for spectrogram visualization with curve tracing capabilities

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.widgets import Button
import librosa
from scipy.interpolate import CubicSpline, make_interp_spline, UnivariateSpline, splrep, splev
from scipy.optimize import curve_fit
import json
from pathlib import Path
import os
import time
from datetime import datetime
import warnings

# Import from existing code within the anvo package
from ..utils import jelly_funcs as jelfun

# Call before importing pyplot
# jelfun.setup_matplotlib_backend()

# Suppresses the warning from librosa
warnings.filterwarnings("ignore", message="n_fft=.* is too large for input signal of length=.*")


class InteractiveSpectrogramTracer:
    def __init__(self, audio_path, n_fft=2048, hop_length=512, 
                 fmin=20, fmax=8000, max_points=20):
        """
        Interactive spectrogram tracer for curve reconstruction.
        
        Args:
            audio_path: Path to audio file
            n_fft: FFT window size (preserving your existing parameters)
            hop_length: Hop length for STFT
            fmin, fmax: Frequency range for display
            max_points: Maximum number of points to allow
        """
        self.audio_path = audio_path
        self.filename = os.path.basename(audio_path)
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.fmin = fmin
        self.fmax = fmax
        self.max_points = max_points
        
        # Load audio with native sample rate (preserving your sr=None approach)
        self.y, self.sr = librosa.load(audio_path, sr=None)
        
        # Apply zero-padding if needed (preserving your approach)
        if len(self.y) < n_fft:
            self.y = np.pad(self.y, (0, n_fft - len(self.y)), 'constant')
        
        # Calculate spectrogram
        self.stft = librosa.stft(self.y, n_fft=n_fft, hop_length=hop_length)
        self.spectrogram = np.abs(self.stft)**2
        self.spectrogram_db = librosa.power_to_db(self.spectrogram)
        
        # Get frequency and time axes
        self.frequencies = librosa.fft_frequencies(sr=self.sr, n_fft=n_fft)
        self.times = librosa.times_like(self.stft, sr=self.sr, hop_length=hop_length)
        
        # Filter frequency range
        self.freq_mask = (self.frequencies >= fmin) & (self.frequencies <= fmax)
        self.frequencies_display = self.frequencies[self.freq_mask]
        self.spectrogram_display = self.spectrogram_db[self.freq_mask, :]
        
        # Initialize point storage
        self.clicked_points = []  # List of (time, frequency) tuples
        self.curve_functions = []  # List of fitted curve functions
        self.curve_params = []  # List of curve parameters/equations
        
        # Curve fitting options
        self.curve_types = {
            'linear': self._fit_linear,
            'cubic_spline': self._fit_cubic_spline,
            'polynomial': self._fit_polynomial,
            'exponential': self._fit_exponential,
            'logarithmic': self._fit_logarithmic,
            'sinusoidal': self._fit_sinusoidal,
            'smoothing_spline': self._fit_smoothing_spline
        }
        self.current_curve_type = 'cubic_spline'
        
        # Display elements
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.point_markers = []
        self.curve_lines = []
        
        self._setup_plot()
        self._setup_interactions()
        
    def _setup_plot(self):
        """Setup the initial spectrogram plot"""
        # Plot spectrogram
        self.im = self.ax.imshow(
            self.spectrogram_display, 
            aspect='auto', 
            origin='lower',
            extent=[self.times[0], self.times[-1], 
                   self.frequencies_display[0], self.frequencies_display[-1]],
            cmap='magma',
            alpha=0.8
        )
        
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Frequency (Hz)')
        self.ax.set_title(f'Interactive Spectrogram Tracer - {self.filename}')
        
        # Add colorbar
        plt.colorbar(self.im, ax=self.ax, label='Power (dB)')
        
        # Add instruction text
        instruction_text = (
            'LEFT-CLICK: Add point\n'
            'RIGHT-CLICK: Remove nearest point\n'
            'MIDDLE-CLICK: Fit curve\n'
            'C: Clear all points\n'
            'S: Save results\n'
            'T: Toggle curve type'
        )
        
        self.ax.text(0.02, 0.98, instruction_text, 
                    transform=self.ax.transAxes,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                    fontsize=9)
        
        # Add curve type indicator
        self.curve_type_text = self.ax.text(0.02, 0.02, 
                                          f'Curve type: {self.current_curve_type}',
                                          transform=self.ax.transAxes,
                                          bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

    def _setup_interactions(self):
        """Setup mouse and keyboard interactions"""
        self.cid_click = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_key = self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # Add save button
        save_ax = self.fig.add_axes([0.85, 0.01, 0.1, 0.05])
        self.save_button = Button(save_ax, 'Save')
        self.save_button.on_clicked(self.save_results)

    def on_click(self, event):
        """Handle mouse clicks"""
        if event.inaxes != self.ax:
            return
            
        if event.button == 1:  # Left click - add point
            self.add_point(event.xdata, event.ydata)
        elif event.button == 3:  # Right click - remove nearest point
            self.remove_nearest_point(event.xdata, event.ydata)
        elif event.button == 2:  # Middle click - fit curve
            self.fit_curve()

    def on_key(self, event):
        """Handle key presses"""
        if event.key == 'c':
            self.clear_points()
        elif event.key == 's':
            self.save_results(None)
        elif event.key == 't':
            self.toggle_curve_type()

    def add_point(self, time, frequency):
        """Add a point at the clicked location"""
        if len(self.clicked_points) >= self.max_points:
            print(f"Maximum number of points ({self.max_points}) reached")
            return
            
        # Add point to storage
        self.clicked_points.append((time, frequency))
        
        # Add visual marker
        marker, = self.ax.plot(time, frequency, 'ro', markersize=8, 
                              markeredgecolor='white', markeredgewidth=2)
        self.point_markers.append(marker)
        
        # Add point label
        label = self.ax.text(time, frequency + 50, f'{len(self.clicked_points)}',
                           ha='center', va='bottom', color='white', 
                           fontweight='bold', fontsize=10)
        self.point_markers.append(label)
        
        print(f"Added point {len(self.clicked_points)}: ({time:.3f}s, {frequency:.1f}Hz)")
        self.fig.canvas.draw_idle()

    def remove_nearest_point(self, time, frequency):
        """Remove the nearest point to the clicked location"""
        if not self.clicked_points:
            return
            
        # Find nearest point
        distances = [np.sqrt((t - time)**2 + (f - frequency)**2) 
                    for t, f in self.clicked_points]
        nearest_idx = np.argmin(distances)
        
        # Remove from storage
        removed_point = self.clicked_points.pop(nearest_idx)
        
        # Remove visual elements (point and label)
        marker_idx = nearest_idx * 2  # Each point has marker + label
        if marker_idx < len(self.point_markers):
            self.point_markers[marker_idx].remove()
            if marker_idx + 1 < len(self.point_markers):
                self.point_markers[marker_idx + 1].remove()
            # Remove from list
            del self.point_markers[marker_idx:marker_idx + 2]
        
        # Update remaining point labels
        self._update_point_labels()
        
        print(f"Removed point: ({removed_point[0]:.3f}s, {removed_point[1]:.1f}Hz)")
        self.fig.canvas.draw_idle()

    def _update_point_labels(self):
        """Update point labels after removal"""
        # Remove all current markers
        for marker in self.point_markers:
            if hasattr(marker, 'remove'):
                marker.remove()
        self.point_markers = []
        
        # Re-add all points with correct labels
        for i, (time, frequency) in enumerate(self.clicked_points):
            marker, = self.ax.plot(time, frequency, 'ro', markersize=8,
                                  markeredgecolor='white', markeredgewidth=2)
            self.point_markers.append(marker)
            
            label = self.ax.text(time, frequency + 50, f'{i+1}',
                               ha='center', va='bottom', color='white',
                               fontweight='bold', fontsize=10)
            self.point_markers.append(label)

    def clear_points(self):
        """Clear all points and curves"""
        # Clear points
        self.clicked_points = []
        
        # Remove visual elements
        for marker in self.point_markers:
            if hasattr(marker, 'remove'):
                marker.remove()
        self.point_markers = []
        
        for line in self.curve_lines:
            if hasattr(line, 'remove'):
                line.remove()
        self.curve_lines = []
        
        # Clear curve data
        self.curve_functions = []
        self.curve_params = []
        
        print("Cleared all points and curves")
        self.fig.canvas.draw_idle()

    def toggle_curve_type(self):
        """Toggle between different curve fitting types"""
        curve_types = list(self.curve_types.keys())
        current_idx = curve_types.index(self.current_curve_type)
        next_idx = (current_idx + 1) % len(curve_types)
        self.current_curve_type = curve_types[next_idx]
        
        # Update display
        self.curve_type_text.set_text(f'Curve type: {self.current_curve_type}')
        print(f"Switched to curve type: {self.current_curve_type}")
        self.fig.canvas.draw_idle()

    def fit_curve(self):
        """Fit a curve to the clicked points"""
        if len(self.clicked_points) < 2:
            print("Need at least 2 points to fit a curve")
            return
            
        # Sort points by time
        sorted_points = sorted(self.clicked_points, key=lambda p: p[0])
        times = np.array([p[0] for p in sorted_points])
        frequencies = np.array([p[1] for p in sorted_points])
        
        # Fit curve using selected method
        try:
            curve_func, params = self.curve_types[self.current_curve_type](times, frequencies)
            
            # Generate smooth curve for display
            t_smooth = np.linspace(times.min(), times.max(), 200)
            f_smooth = curve_func(t_smooth)
            
            # Remove previous curve
            for line in self.curve_lines:
                if hasattr(line, 'remove'):
                    line.remove()
            self.curve_lines = []
            
            # Plot new curve
            line, = self.ax.plot(t_smooth, f_smooth, 'cyan', linewidth=3, 
                               alpha=0.8, label=f'{self.current_curve_type} fit')
            self.curve_lines.append(line)
            
            # Store curve data
            self.curve_functions = [curve_func]
            self.curve_params = [params]
            
            print(f"Fitted {self.current_curve_type} curve:")
            print(f"Parameters: {params}")
            
            self.fig.canvas.draw_idle()
            
        except Exception as e:
            print(f"Error fitting curve: {e}")

    def _fit_linear(self, times, frequencies):
        """Fit linear function: y = mx + b"""
        coeffs = np.polyfit(times, frequencies, 1)
        m, b = coeffs
        
        def linear_func(t):
            return m * t + b
            
        params = {'equation': f'y = {m:.3f}*x + {b:.3f}', 'm': m, 'b': b}
        return linear_func, params

    def _fit_cubic_spline(self, times, frequencies):
        """Fit cubic spline"""
        spline = CubicSpline(times, frequencies, bc_type='natural')
        
        def spline_func(t):
            return spline(t)
            
        # Get spline coefficients for each segment
        coeffs = []
        for i in range(len(spline.c[0])):
            segment_coeffs = [spline.c[j, i] for j in range(4)]
            coeffs.append(segment_coeffs)
        
        params = {
            'equation': 'Piecewise cubic spline',
            'knots': times.tolist(),
            'coefficients': coeffs,
            'note': 'Each segment: a*(x-xi)³ + b*(x-xi)² + c*(x-xi) + d'
        }
        return spline_func, params

    def _fit_polynomial(self, times, frequencies):
        """Fit polynomial (degree based on number of points)"""
        degree = min(len(times) - 1, 5)  # Max degree 5
        coeffs = np.polyfit(times, frequencies, degree)
        
        def poly_func(t):
            return np.polyval(coeffs, t)
        
        # Create equation string
        eq_parts = []
        for i, coeff in enumerate(coeffs):
            power = degree - i
            if power == 0:
                eq_parts.append(f"{coeff:.3f}")
            elif power == 1:
                eq_parts.append(f"{coeff:.3f}*x")
            else:
                eq_parts.append(f"{coeff:.3f}*x^{power}")
        
        equation = "y = " + " + ".join(eq_parts)
        params = {'equation': equation, 'coefficients': coeffs.tolist(), 'degree': degree}
        return poly_func, params

    def _fit_exponential(self, times, frequencies):
        """Fit exponential function: y = a * exp(b*x) + c"""
        def exp_func(x, a, b, c):
            return a * np.exp(b * x) + c
        
        # Initial guess
        p0 = [frequencies[0], 0.1, frequencies.min()]
        
        try:
            popt, _ = curve_fit(exp_func, times, frequencies, p0=p0)
            a, b, c = popt
            
            def fitted_exp(t):
                return exp_func(t, a, b, c)
            
            params = {
                'equation': f'y = {a:.3f} * exp({b:.3f}*x) + {c:.3f}',
                'a': a, 'b': b, 'c': c
            }
            return fitted_exp, params
            
        except:
            # Fallback to simple exponential
            return self._fit_polynomial(times, frequencies)

    def _fit_logarithmic(self, times, frequencies):
        """Fit logarithmic function: y = a * log(x + b) + c"""
        def log_func(x, a, b, c):
            return a * np.log(x + b) + c
        
        # Ensure all x values are positive for log
        if times.min() <= 0:
            times_shifted = times - times.min() + 0.1
        else:
            times_shifted = times
        
        p0 = [1, 1, frequencies.mean()]
        
        try:
            popt, _ = curve_fit(log_func, times_shifted, frequencies, p0=p0)
            a, b, c = popt
            
            def fitted_log(t):
                t_shifted = t - times.min() + 0.1 if times.min() <= 0 else t
                return log_func(t_shifted, a, b, c)
            
            params = {
                'equation': f'y = {a:.3f} * log(x + {b:.3f}) + {c:.3f}',
                'a': a, 'b': b, 'c': c
            }
            return fitted_log, params
            
        except:
            return self._fit_polynomial(times, frequencies)

    def _fit_sinusoidal(self, times, frequencies):
        """Fit sinusoidal function: y = a * sin(b*x + c) + d"""
        def sin_func(x, a, b, c, d):
            return a * np.sin(b * x + c) + d
        
        # Initial guess
        amp_guess = (frequencies.max() - frequencies.min()) / 2
        offset_guess = frequencies.mean()
        freq_guess = 2 * np.pi / (times.max() - times.min())
        
        p0 = [amp_guess, freq_guess, 0, offset_guess]
        
        try:
            popt, _ = curve_fit(sin_func, times, frequencies, p0=p0)
            a, b, c, d = popt
            
            def fitted_sin(t):
                return sin_func(t, a, b, c, d)
            
            params = {
                'equation': f'y = {a:.3f} * sin({b:.3f}*x + {c:.3f}) + {d:.3f}',
                'amplitude': a, 'frequency': b, 'phase': c, 'offset': d
            }
            return fitted_sin, params
            
        except:
            return self._fit_polynomial(times, frequencies)

    def _fit_smoothing_spline(self, times, frequencies):
        """Fit smoothing spline with automatic smoothing"""
        # Use scipy's UnivariateSpline for automatic smoothing
        spline = UnivariateSpline(times, frequencies, s=None)  # Auto-select smoothing
        
        def spline_func(t):
            return spline(t)
        
        params = {
            'equation': 'Smoothing spline (auto-smoothed)',
            'knots': times.tolist(),
            'smoothing_factor': spline.get_residual()
        }
        return spline_func, params

    def save_results(self, event):
        """Save the traced curve results"""
        if not self.clicked_points:
            print("No points to save")
            return
        
        # Create output directory
        daily_dir = jelfun.make_daily_directory()
        output_dir = os.path.join(daily_dir, "jellyfish_tracer_results")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save figure
        timestamp = jelfun.get_timestamp()
        base_name = os.path.splitext(self.filename)[0]
        fig_filename = f"{base_name}_traced_{timestamp}.png"
        fig_path = os.path.join(output_dir, fig_filename)
        
        self.fig.savefig(fig_path, dpi=300, bbox_inches='tight')
        
        # Save data
        data_filename = f"{base_name}_trace_data_{timestamp}.json"
        data_path = os.path.join(output_dir, data_filename)
        
        # Prepare data for JSON export
        export_data = {
            'filename': self.filename,
            'audio_path': str(self.audio_path),
            'parameters': {
                'n_fft': self.n_fft,
                'hop_length': self.hop_length,
                'fmin': self.fmin,
                'fmax': self.fmax,
                'sample_rate': self.sr
            },
            'clicked_points': [{'time': float(t), 'frequency': float(f)} 
                             for t, f in self.clicked_points],
            'curve_type': self.current_curve_type,
            'curve_parameters': self.curve_params,
            'timestamp': timestamp
        }
        
        with open(data_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Results saved:")
        print(f"  Figure: {fig_path}")
        print(f"  Data: {data_path}")

    def reconstruct_spectrogram(self):
        """Reconstruct spectrogram from fitted curve (future enhancement)"""
        # This is a placeholder for reconstructing the spectrogram
        # based on the fitted curve parameters
        if not self.curve_functions:
            print("No curve fitted yet")
            return None
        
        # Future implementation would:
        # 1. Use curve function to generate frequency trajectory
        # 2. Create synthetic spectrogram with energy along the curve
        # 3. Display comparison with original
        
        print("Spectrogram reconstruction feature coming soon...")
        return None

def analyze_audio_file(audio_path, **kwargs):
    """
    Analyze a single audio file with the interactive tracer.
    
    Args:
        audio_path: Path to audio file
        **kwargs: Additional parameters for SpectrogramTracer
    """
    tracer = InteractiveSpectrogramTracer(audio_path, **kwargs)
    plt.show()
    return tracer

def batch_trace_analysis(audio_directory, selected_files=None, **kwargs):
    """
    Run interactive tracing on multiple files.
    
    Args:
        audio_directory: Directory containing audio files
        selected_files: List of specific files to analyze
        **kwargs: Parameters for tracer
    """
    if selected_files is None:
        selected_files = select_audio_files(audio_directory, limit=5)
    
    tracers = []
    for filename in selected_files:
        file_path = os.path.join(audio_directory, filename)
        print(f"\nAnalyzing: {filename}")
        tracer = analyze_audio_file(file_path, **kwargs)
        tracers.append(tracer)
    
    return tracers

def main_tracer():
    """Main function for interactive spectrogram tracing"""
    print("🎵 Jellyfish Spectrogram Tracer")
    print("=" * 40)
    
    # Import from jellyfish_dynamo
    from jellyfish_dynamo import all_slicedirs
    
    # Select directory
    main_slicedir = all_slicedirs[57]  # Adjust index as needed
    
    # Select files
    selected_files = select_audio_files(
        main_slicedir,
        range_start=0,
        range_end=2,  # Start with 3 files
        verbose=True
    )
    
    if not selected_files:
        print("No audio files found")
        return
    
    # Parameters (preserving your existing approach)
    tracer_params = {
        'n_fft': 2048,
        'hop_length': 512,
        'fmin': 100,
        'fmax': 6000,
        'max_points': 15
    }
    
    print(f"\nStarting interactive analysis...")
    print("Instructions:")
    print("- Left-click to add points")
    print("- Right-click to remove nearest point") 
    print("- Middle-click to fit curve")
    print("- Press 'c' to clear all")
    print("- Press 't' to toggle curve type")
    print("- Press 's' to save results")
    
    # Run batch analysis
    tracers = batch_trace_analysis(
        main_slicedir,
        selected_files=selected_files,
        **tracer_params
    )
    
    return tracers

if __name__ == "__main__":
    main_tracer()