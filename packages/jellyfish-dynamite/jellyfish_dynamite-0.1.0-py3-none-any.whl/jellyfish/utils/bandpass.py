def bandpass(audio_file, lowcut, highcut, order=4):
    """
    Apply a bandpass filter to an audio file and return the filtered audio array.
    
    Args:
        audio_file: Path to audio file
        lowcut: Low frequency cutoff in Hz
        highcut: High frequency cutoff in Hz  
        order: Filter order (higher = steeper rolloff)
        
    Returns:
        numpy.ndarray: Filtered audio data (not a tuple)
    """
    import librosa
    import numpy as np
    from scipy import signal
    
    # Load audio
    audio, sr = librosa.load(audio_file, sr=None)
    
    # Design Butterworth bandpass filter
    nyquist = sr / 2
    low = lowcut / nyquist
    high = highcut / nyquist
    
    # Ensure frequencies are within valid range
    low = max(0.01, min(low, 0.99))
    high = max(low + 0.01, min(high, 0.99))
    
    # Create filter coefficients
    b, a = signal.butter(order, [low, high], btype='band')
    
    # Apply filter
    filtered_audio = signal.filtfilt(b, a, audio)
    
    return filtered_audio  # Return only the filtered audio array