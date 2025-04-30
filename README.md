# Guitar Pedal Wah-Wah Effect Implementation

This project implements a digital wah-wah effect for guitar processing using both traditional signal processing techniques and wavelet-based approaches. The implementation combines envelope following, bandpass filtering, and wavelet decomposition to create a rich, dynamic wah effect.

## Overview

The wah-wah effect is implemented through two main approaches:

1. **Traditional Signal Processing Pipeline**
   - Envelope following
   - Variable bandpass filtering
   - DC offset removal

2. **Wavelet-Based Processing**
   - Multi-level wavelet decomposition
   - Frequency band modulation
   - Dynamic envelope control

## Mathematical Foundations

### 1. Envelope Following

The envelope follower uses a Butterworth lowpass filter to track the signal's amplitude:

```math
H(s) = \frac{1}{(s/\omega_c)^n + 1}
```

where:
- $\omega_c$ is the cutoff frequency
- $n$ is the filter order (3rd order in our implementation)

### 2. Variable Bandpass Filter

The state-variable filter implementation uses the following difference equations:

```math
\begin{align}
y_{high}[n] &= x[n] - \frac{1}{Q}y_{band}[n] - y_{low}[n] \\
y_{band}[n] &= y_{band}[n-1] + f \cdot y_{high}[n] \\
y_{low}[n] &= y_{low}[n-1] + f \cdot y_{band}[n]
\end{align}
```

where:
- $f = 2\sin(\pi f_c/f_s)$ is the frequency coefficient
- $Q$ is the quality factor
- $f_c$ is the center frequency
- $f_s$ is the sampling rate

### 3. Wavelet Processing

The wavelet-based approach uses the discrete wavelet transform (DWT):

```math
W_{\psi}[j,k] = \frac{1}{\sqrt{a_0^j}} \sum_{n} x[n] \psi\left(\frac{n - k b_0 a_0^j}{a_0^j}\right)
```

where:
- $\psi$ is the mother wavelet (db4 in our implementation)
- $j$ is the scale level
- $k$ is the translation parameter
- $a_0$ and $b_0$ are the dilation and translation steps

## Filter Analysis and Wah-Wah Effect

### State-Variable Filter Analysis

The state-variable filter implementation is crucial for the wah-wah effect as it provides:
1. Precise frequency control
2. Independent control of resonance
3. Stable operation across the entire frequency range

#### Transfer Function Analysis

The state-variable filter can be represented in the z-domain:

```math
H_{band}(z) = \frac{fz^{-1}}{1 - (2 - f^2)z^{-1} + (1 - f)z^{-2}}
```

where:
- $f$ is the frequency coefficient
- $z^{-1}$ represents a unit delay

This transfer function shows that the filter is a second-order system with:
- Two poles that determine the resonance characteristics
- One zero at DC that provides the bandpass response

#### Frequency Response

The magnitude response of the bandpass filter is given by:

```math
|H_{band}(e^{j\omega})| = \frac{f}{\sqrt{(1 - (2 - f^2)\cos\omega + (1 - f)\cos2\omega)^2 + ((2 - f^2)\sin\omega - (1 - f)\sin2\omega)^2}}
```

where $\omega = 2\pi f_c/f_s$ is the normalized frequency.

#### Wah-Wah Effect Implementation

The wah-wah effect is achieved through:

1. **Frequency Modulation**
   - The center frequency $f_c$ is modulated by the envelope or pedal position
   - This creates the characteristic "wah" sound as the filter sweeps through frequencies
   - The modulation range (200Hz - 2000Hz) is chosen to match the guitar's midrange frequencies

2. **Resonance Control**
   - The Q factor controls the filter's resonance
   - Higher Q values (2.0 in our implementation) create a more pronounced wah effect
   - The resonance emphasizes the current center frequency, creating the "peak" in the wah sound

3. **State Variable Implementation**
   - The difference equations provide a stable implementation
   - The state variables (low, band, high) allow for precise control
   - The implementation is efficient and suitable for real-time processing

#### Stability Analysis

The filter's stability is ensured by:
1. Proper coefficient scaling
2. Bounded frequency range
3. Careful Q factor control

The stability condition is:

```math
0 < f < 2
```

which is always satisfied in our implementation since $f = 2\sin(\pi f_c/f_s)$ and $f_c < f_s/2$.

#### Real-Time Considerations

The state-variable implementation is particularly suitable for wah-wah effects because:
1. It allows for smooth frequency transitions
2. It maintains phase coherence during modulation
3. It provides independent control of frequency and resonance
4. It's computationally efficient for real-time processing

## Implementation Details

### Core Components

1. **WahPedal Class**
   - Controls the wah effect position
   - Supports both automatic and manual modes
   - Generates smooth pedal motion using sine wave modulation

2. **WaveletEffect Class**
   - Implements multi-level wavelet decomposition
   - Processes specific frequency bands for wah effect
   - Applies dynamic modulation and envelope control

3. **WahWah Class**
   - Combines envelope following and bandpass filtering
   - Supports both pedal-controlled and envelope-following modes
   - Implements DC offset removal

### Signal Processing Pipeline

1. **Input Processing**
   - Audio signal is normalized
   - DC offset is removed
   - Signal is prepared for processing

2. **Effect Application**
   - In traditional mode:
     - Envelope is extracted
     - Bandpass filter frequency is modulated
     - Signal is processed through the filter
   - In wavelet mode:
     - Signal is decomposed into frequency bands
     - Selected bands are modulated
     - Signal is reconstructed

3. **Output Processing**
   - Signal is normalized
   - DC offset is removed
   - Output is scaled appropriately

## Usage

```python
from pedal import WahPedal
from wavelet import WaveletEffect
from utils import WahWah

# Create a wah-wah effect instance
wah = WahWah(sr=44100, min_freq=200.0, max_freq=2000.0, q=2.0)

# Option 1: Use with pedal control (my favorite)
pedal = WahPedal(pedal_rate=2.0, mode='auto')
wah.set_pedal(pedal)

# Option 2: Use wavelet-based processing
wavelet_effect = WaveletEffect(wavelet='db4', level=4)

# Process audio
processed_audio = wah.process(input_audio)
```

## Technical Specifications

- Sampling Rate: 44.1 kHz
- Frequency Range: 200 Hz - 2000 Hz (adjustable)
- Wavelet: Daubechies 4 (db4)
- Decomposition Levels: 4
- Envelope Follower Cutoff: 10 Hz
- Quality Factor (Q): 2.0 (adjustable)

## Dependencies

- NumPy
- SciPy
- PyWavelets
- Matplotlib
- SoundFile (for audio I/O)

## References

1. Smith, J.O. (2010). *Physical Audio Signal Processing*
2. Mallat, S. (2009). *A Wavelet Tour of Signal Processing*
3. Zölzer, U. (2011). *DAFX: Digital Audio Effects*

## License

This project is licensed under the MIT License - see the LICENSE file for details. 