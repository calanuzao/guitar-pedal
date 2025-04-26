import numpy as np

class WahPedal:
    def __init__(self, 
                 pedal_rate: float = 2.0,  # Hz - how fast the pedal moves
                 sr: float = 44100,
                 mode: str = 'auto'):      # 'auto' or 'manual'
        self.sr = sr
        self.pedal_rate = pedal_rate
        self.mode = mode
        self.phase = 0
        self.current_position = 0.0  # 0 (heel) to 1 (toe)
        
    def get_position(self, n_samples: int) -> np.ndarray:
        """
        Returns pedal position over time
        0 = heel position (lowest frequency)
        1 = toe position (highest frequency)
        """
        if self.mode == 'auto':
            # Generate smooth pedal motion using sine wave
            t = np.arange(n_samples) / self.sr
            positions = 0.5 + 0.5 * np.sin(2 * np.pi * self.pedal_rate * t + self.phase)
            self.phase += 2 * np.pi * self.pedal_rate * (n_samples / self.sr)
            self.phase %= 2 * np.pi
            return positions
        else:
            # For manual mode, return constant current position
            return np.full(n_samples, self.current_position)
    
    def set_position(self, position: float):
        """For manual control - set pedal position between 0 and 1"""
        self.current_position = np.clip(position, 0, 1)