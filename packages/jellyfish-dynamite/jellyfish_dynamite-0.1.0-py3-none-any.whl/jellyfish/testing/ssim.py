import numpy as np
import matplotlib.pyplot as plt
import librosa.display
from skimage.metrics import structural_similarity as ssim
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import cv2
from itertools import combinations

def spectrogram_to_image(signal, sr, target_size=(64, 64)):
    """Convert signal to standardized spectrogram image"""
    D = librosa.amplitude_to_db(np.abs(librosa.stft(signal, n_fft=512, hop_length=256)))
    
    # Normalize to 0-255 range
    D_norm = ((D - D.min()) / (D.max() - D.min()) * 255).astype(np.uint8)
    
    # Resize to standard size for comparison
    D_resized = cv2.resize(D_norm, target_size)
    
    return D_resized

def compute_similarity_metrics(original_img, reconstruction_img):
    """Compute multiple similarity metrics between spectrograms"""
    
    # Structural Similarity Index
    ssim_score = ssim(original_img, reconstruction_img)
    
    # Mean Squared Error
    mse = np.mean((original_img.astype(float) - reconstruction_img.astype(float)) ** 2)
    
    # Normalized Cross Correlation
    ncc = np.corrcoef(original_img.flatten(), reconstruction_img.flatten())[0,1]
    
    # Histogram correlation
    hist1 = cv2.calcHist([original_img], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([reconstruction_img], [0], None, [256], [0, 256])
    hist_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    
    return {
        'ssim': ssim_score,
        'mse': mse,
        'ncc': ncc if not np.isnan(ncc) else 0,
        'hist_corr': hist_corr
    }