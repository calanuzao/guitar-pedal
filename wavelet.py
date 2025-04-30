import numpy as np
import pywt
from typing import List, Union

class WaveletEffect:
    def __init__(self, 
                 wavelet: str = 'db4', 
                 level: int = 4,
                 wah_freq_min: float = 300.0,
                 wah_freq_max: float = 1200.0,
                 resonance: float = 2.0):
        self.wavelet = wavelet
        self.level = level
        self.wah_freq_min = wah_freq_min
        self.wah_freq_max = wah_freq_max
        self.resonance = resonance

    def process(self, audio: np.ndarray) -> np.ndarray:
        # wavelet decomposition
        coeffs = pywt.wavedec(audio, self.wavelet, level=self.level)
        
        # processing each level that corresponds to wah frequencies
        for i in range(3, min(6, len(coeffs))):
            coeff_len = len(coeffs[i])
            t = np.linspace(0, len(audio)/44100, coeff_len)
            
            # envelope and modulation of matching sizes
            envelope = np.abs(coeffs[i])
            mod_freq = 2.0  # 2 Hz modulation
            modulation = 1 + self.resonance * np.sin(2 * np.pi * mod_freq * t)
            
            # modulation and envelope
            coeffs[i] = coeffs[i] * modulation * (envelope ** 0.5)
        
        # attenuate frequencies outside wah-wah range (similar to speech and my hearing aids)
        coeffs[0] *= 0.1  # Reduce bass
        coeffs[1] *= 0.2  # Reduce high frequencies
        coeffs[2] *= 0.5  # Partially reduce upper-mids
      
        processed = pywt.waverec(coeffs, self.wavelet)
        processed = processed / np.max(np.abs(processed))
        
        return processed