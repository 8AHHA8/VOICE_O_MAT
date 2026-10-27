import numpy as np
import pygame

def generate_click_sound():
    """Generuje dźwięk mechanicznego kliknięcia."""
    duration = 0.5
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    signal = np.zeros_like(t)

    idx1 = 0
    len1 = int(0.12 * sample_rate)
    env1 = np.exp(-np.linspace(0, 10, len1))
    sig1 = 0.6 * np.sin(2 * np.pi * 60 * t[idx1:idx1+len1]) + 0.4 * np.sin(2 * np.pi * 45 * t[idx1:idx1+len1])
    signal[idx1:idx1+len1] += sig1 * env1

    idx2 = int(0.20 * sample_rate)
    len2 = int(0.12 * sample_rate)
    env2 = np.exp(-np.linspace(0, 10, len2))
    sig2 = 0.5 * np.sin(2 * np.pi * 110 * t[idx2:idx2+len2]) + 0.3 * np.sin(2 * np.pi * 90 * t[idx2:idx2+len2])
    signal[idx2:idx2+len2] += sig2 * env2
    
    signal = np.convolve(signal, np.ones(80)/80, mode='same')
    
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val 
        
    signal = signal[::-1]
        
    audio_int16 = (signal * 32767).astype(np.int16)
    stereo_audio = np.column_stack((audio_int16, audio_int16))
    
    return pygame.sndarray.make_sound(stereo_audio)