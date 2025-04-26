"""
Wah-wah effect implementation using envelope-controlled bandpass filter
"""

import numpy as np
from scipy import signal

class EnvelopeFollower:
    def __init__(self, cutoff: float, sr: float = 44100):
        self.sr = sr
        self.cutoff = cutoff
        self.b, self.a = signal.butter(3, cutoff, fs=sr)
        self.reset()

    def reset(self):
        self.z = signal.lfilter_zi(self.b, self.a).astype(np.float32)

    def process(self, x: np.ndarray) -> np.ndarray:
        x_abs = np.abs(x).astype(np.float32)
        y, self.z = signal.lfilter(self.b, self.a, x_abs, zi=self.z)
        return y

class VariableBPF:
    """
    State-variable filter for real-time frequency modulation.
    """
    def __init__(self, sr: float = 44100):
        self.sr = sr
        self.fc = 1000.0  # Center frequency
        self.q = 0.7      # Q factor (1/damping)
        self.low = 0.0
        self.band = 0.0
        self.high = 0.0

    def update_params(self, fc: float, q: float):
        self.fc = np.clip(fc, 20.0, self.sr/2 * 0.9)
        self.q = np.clip(q, 0.1, 10.0)
        self.f = 2 * np.sin(np.pi * self.fc / self.sr)

    def process_sample(self, x: float) -> float:
        self.high = x - (1/self.q) * self.band - self.low
        self.band += self.f * self.high
        self.low += self.f * self.band
        return self.band  # Bandpass output

class WahWah:
    """
    Wah-wah effect processor that can operate in either envelope-following or pedal-controlled mode.
    
    Parameters:
        sr (float): Sample rate in Hz (default: 44100)
        min_freq (float): Minimum cutoff frequency in Hz (default: 200.0)
        max_freq (float): Maximum cutoff frequency in Hz (default: 2000.0)
        q (float): Q factor for resonance control (default: 2.0)
        env_cutoff (float): Envelope follower cutoff frequency in Hz (default: 10.0)
    """
    def __init__(self, 
                 sr: float = 44100,
                 min_freq: float = 200.0,
                 max_freq: float = 2000.0,
                 q: float = 2.0,
                 env_cutoff: float = 10.0):
        
        self.sr = sr
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.q = q
        
        # components
        self.env_follower = EnvelopeFollower(env_cutoff, sr)
        self.bpf = VariableBPF(sr)
        self.bpf.update_params(min_freq, q)
        
        # DC blocking
        self.dc_b = np.array([1.0, -1.0], dtype=np.float32)
        self.dc_a = np.array([1.0, -0.995], dtype=np.float32)
        self.dc_z = signal.lfilter_zi(self.dc_b, self.dc_a)

        # guitar pedal
        self.pedal = None

    def set_pedal(self, pedal) -> None:
        """
        Attach a pedal controller to the wah effect
        
        Parameters:
            pedal: WahPedal object for controlling the effect
        """
        self.pedal = pedal
    
    def process(self, input_buffer: np.ndarray) -> np.ndarray:
        """
        Process audio through the wah-wah effect
        
        Parameters:
            input_buffer (np.ndarray): Input audio samples
            
        Returns:
            np.ndarray: Processed audio samples with wah effect applied
        """
        if self.pedal:
            # use pedal position instead of envelope
            pedal_positions = self.pedal.get_position(len(input_buffer))
            output = np.zeros_like(input_buffer)

            for i in range(len(input_buffer)):
                # mapping pedal position to frequency range
                freq = self.min_freq + pedal_positions[i] * (self.max_freq - self.min_freq)
                self.bpf.update_params(freq, self.q)
                output[i] = self.bpf.process_sample(input_buffer[i])
        else:
            # tracking amplitude envelope
            envelope = self.env_follower.process(input_buffer)
            
            # normalize envelope to [0, 1] range
            env_min = np.min(envelope)
            env_max = np.max(envelope)
            envelope = (envelope - env_min) / (env_max - env_min + 1e-7)
            
            # process samples with modulated filter
            output = np.zeros_like(input_buffer)
            for i in range(len(input_buffer)):
                # Map envelope to frequency range
                freq = self.min_freq + envelope[i] * (self.max_freq - self.min_freq)
                self.bpf.update_params(freq, self.q)
                output[i] = self.bpf.process_sample(input_buffer[i])

        # removes DC offset
        output, self.dc_z = signal.lfilter(
            self.dc_b, self.dc_a, output, zi=self.dc_z
        )
        
        return output * 2.0  # Compensation gain