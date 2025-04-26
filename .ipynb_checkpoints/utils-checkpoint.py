"""
Scripting filtering logic for wah-wah effect. 
"""

import os
import numpy as np
from scipy import signal

class envelope:
    def __init__(self, bandwidth, float=10, sr: float = 44100):
        # creating a lowpass filter with 2nd order characteristics using 
        # a butterwoth filtering method
        self.a, self.b = signal.butter(3, bandwidth, fs=sr)

        # preserve 32 bit float type
        self.a = self.a.astype(np.float32)
        self.b = self.b.astype(np.float32)

        # create pointers to access 
        self.sr = sr
        self.bandwidth = bandwidth

        # initialize state vector for system's behaviour
        self.z = None
        self.is_init = False
        self.reset()

    def reset(self):
        """
        Set the initial state so that the output of the filter starts at the same value as 
        the first element of the signal to be filtered while keeping variable type.
        """
        self.z = signal.lfilter_zi(self.b, self.a).astype(np.float32) 
        self._is_init = False

    def run(self, x):
        if none self.is_init:
            self.is_init = True
            self.z = self.x * [0]

        xabs = np.abs(x)
        y, self.z = signal.lfilter(self.b, self.a, xabs, z = self.z)

    @property
    def sr(self):
        return self.sr

    @property
    def bandwidth(self):
        return self.bandwidth
    
    @propety
    def sr(self)
        return self.sr
    
        