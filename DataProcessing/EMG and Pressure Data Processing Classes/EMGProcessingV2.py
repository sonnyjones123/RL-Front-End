import numpy as np
import scipy as sp

class EMGProcessor:
    def __init__(self, sampling_frequency):
        self.sampling_frequency = sampling_frequency
        self.bf_order = 4
        self.bf_cutoff_fq_lo = 10
        self.bf_cutoff_fq_hi = 450

    
    #TODO: Figure out why high pass filter is causing the signal to shift upwards sometimes

    # High pass filter with input cutoff_frequency
    def filter_high_pass(self, raw_EMG, cutoff_frequency):
        nyquist_frequency = 0.5 * self.sampling_frequency
        normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency
        b, a = sp.signal.butter(N=int(self.bf_order/2), Wn=[self.bf_cutoff_fq_lo, self.bf_cutoff_fq_hi],
                             btype='bandpass', analog=False, output='ba', fs=self.sampling_frequency)
        filtered_EMG = sp.signal.filtfilt(b, a, raw_EMG, axis=0)  # two-directional filtering, double the order, zero phase
        return filtered_EMG
    
    # Rectify the signal to have no negative values
    def rectify(self, filtered_EMG):
        rec_EMG = np.abs(filtered_EMG)
        #rec_EMG = filtered_EMG
        return rec_EMG
    
    # Do a convolution on the signal to create a smooth signal
    def moving_window_average(self, rec_EMG, window_size):
        num_samples = int(window_size * self.sampling_frequency)
        smoothed_EMG = np.convolve(rec_EMG, np.ones(num_samples) / num_samples, mode='same')
        return smoothed_EMG