import numpy as np
import scipy.signal

def enveloping(signal, sampleRate, windowSize: int, edges: list[float] = [5, 500]):
    """
    Computes the EMG envelope of an EMG signal.
    Args:
        signal: Raw EMG Signal.
        sampleRate: Sample Rate of the input signal.
        windowSize (int): Size of the moving average window.
        edges list[float]: List of size 2 containing lower and upper Hz bounds. 
    Returns:
        np.array: Enveloped EMG Signal.
    """
    # Filter Design
    sos = scipy.signal.butter(6, edges, 'bandpass', fs = sampleRate, output = 'sos')

    # Bandpass Filtering Data
    filteredSignal = scipy.signal.sosfiltfilt(sos, signal)

    # Returning MAV with windowSize
    return np.convolve(np.abs(filteredSignal), np.ones(windowSize)/windowSize, mode = 'same')

def movingAverage(signal, windowSize: int):
    """
    Computes the moving average of an EMG signal.
    Args:
        signal: Raw EMG Signal.
        windowSize (int): Size of the moving average window.
    Returns:
        np.array: Smoothed EMG signal.
    """
    # Returning MAV with windowSize
    return np.convolve(signal, np.ones(windowSize)/windowSize, mode = 'same')

def MAV(signal, n: int):
    ret = np.cumsum(signal, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n
