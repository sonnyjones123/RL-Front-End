"""
This file is meant to extract steps from multiple EMG channels using the heel strike to heel strike distances
from the XSensor pressure insole.

Written by Grange Simpson
Version: 2024.06.12

Usage: Run the file.
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy import interpolate
from math import factorial


class Step_Extraction_Stats:
    def __init__(self, windowSize):
        self.peakSpacing = 1000

        # Variables to use for testing
        self.upSampleData = 0
        self.upSampledPressDataSlope = 0
        self.pressDataInfl = 0

        self.smoothWindowSize = windowSize
    
    """
    Savitzky golay algorithm is used to smooth out the very spiky upsampled data using a running average
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    """
    def savitzky_golay(self, y, window_size, order, deriv=0, rate=1):

        try:
            window_size = np.abs(int(window_size))
            order = np.abs(int(order))

        except ValueError as msg:
            raise ValueError("window_size and order have to be of type int")
        
        if window_size % 2 != 1 or window_size < 1:
            raise TypeError("window_size size must be a positive odd number")
        
        if window_size < order + 2:
            raise TypeError("window_size is too small for the polynomials order")
        
        order_range = range(order+1)
        half_window = (window_size -1) // 2
        # Precompute coefficients
        b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
        m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
        # Pad the signal at the extremes with
        # Values taken from the signal itself
        firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
        lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        
        return np.convolve( m[::-1], y, mode='valid')

    """
    Upsample the heel data from 10 Hz to ~1926 Hz by filling the lower sampled data with NaNs 
    then interpolating those NaNs to fill in the signal
    """
    def upsample_data(self, inputData, upsampleFactor):

        # Calculate length of the upsampled signal
        upsampledLength = len(inputData) * upsampleFactor - (upsampleFactor - 1)

        # Create upsampled signal with NaNs
        upsampledSignal = np.full(upsampledLength, np.nan)
        upsampledSignal[::upsampleFactor] = inputData

        # Interpolate NaNs
        originalIndices = np.arange(0, upsampledLength, upsampleFactor)
        interpolationFunction = interpolate.interp1d(
            originalIndices, 
            inputData, 
            kind='linear', 
            fill_value="extrapolate"
        )

        # Get the interpolated signal
        upSampHeelData = interpolationFunction(np.arange(upsampledLength))

        return upSampHeelData

    """"""
    def find_slopes(self, inputData): 
        #heelSlope = np.zeros(len(inputData))

        heelSlope = np.diff(inputData)

        return heelSlope

    """"""
    def find_bin_peaks(self, inputData):
        peakMinPosVal = np.mean(inputData[inputData > 0])
        # TODO: update self.peakSpacing to be based upon the mean peak distance
        peaks, _ = find_peaks(inputData, height = peakMinPosVal, distance = self.peakSpacing)

        return peaks
    
    def find_bin_inflections(self, inputSlope):  

        slopeData = np.array(inputSlope)

        slopeData = self.savitzky_golay(slopeData, self.smoothWindowSize, 3)

        # Removing unloading events from the data
        slopeData[slopeData < 0] = 0
        # Removing small loading noise from the data
        # TODO: check with Kylee what a better number would be for removing small loading noise than meanPeakHeight / 15
        # Finding peaks to get the average peak height, will likely need to adjust for higher sampling rate
        pressDataPeakInds = self.find_bin_peaks(inputSlope)
        meanPeakHeight = np.mean(inputSlope[pressDataPeakInds])

        slopeData[slopeData < meanPeakHeight / 15] = 0 


        indexArr = []
        # Only save the indexs of inflection points where the difference in slope is small for the current point then large for the next point
        # indicating an inflection point
        for x in range(len(slopeData) - 2):
            if (slopeData[x] == 0 and slopeData[x + 1] > 0):
                indexArr.append(x)

        meanStepLength = np.mean(np.diff(indexArr))

        # Removing all possible false steps that are less than 1/2 the mean length of all steps
        indexArrCop = indexArr.copy()
        deleteIter = 0
        for x in range(len(indexArr) - 2):
            #print(x)
            if (indexArr[x + 1] - indexArr[x] < meanStepLength / 1.5):
                
                #print(len(indexArrCop))
                #print(len(indexArr))
                del indexArrCop[(x) - deleteIter]
                deleteIter += 1

        return indexArrCop

    """
    This function downsamples the emg steps to make them all the same length.
    """
    def downsample_signal(self, signal, targetLength):
        originalIndices = np.linspace(0, len(signal) - 1, num=len(signal))
        targetIndices = np.linspace(0, len(signal) - 1, num=targetLength)
        
        interpolation_function = interpolate.interp1d(
            originalIndices, 
            signal, 
            kind='linear'  
        )
        
        downsampled_signal = interpolation_function(targetIndices)
        return downsampled_signal


    """
    This function takes binned XSensor data and uses the heel data to segment out the steps from the EMG
    Only does left or right data, not both at the same time
    """
    def extract_steps(self, pressureStepsDf, EMGStepsDf, binToParseOn):

        emgCols = EMGStepsDf.columns

        # Upsampling the XSensor data for now since it's at 10 Hz and the EMG is at 1926 Hz
        upsampleFactor = np.round((len(EMGStepsDf[emgCols[0]]) / len(pressureStepsDf[binToParseOn]))).astype(int)

        # Normalizing the input pressure data
        # Taking the mean of the top 50 minimums to remove most of the baseline shift.
        pressData = pressureStepsDf[binToParseOn]
        meanMinSortedPressData = np.mean(np.sort(pressData)[0:50])

        pressData = pressData - meanMinSortedPressData

        pressData = pressData / np.max(pressData)

        upSampledHeelData = self.upsample_data(pressData, upsampleFactor)
        self.upSampleData = upSampledHeelData

        # Turning the upsampled data into slopes by taking the difference in between each point
        pressDataSlope = self.find_slopes(upSampledHeelData)
        
        self.upSampledPressDataSlope = pressDataSlope

        # Finding the peaks 
        #pressDataPeakInds = self.find_bin_peaks(pressDataSlope)

        # Finding the inflection points right before a step
        pressDataInflInds = self.find_bin_inflections(pressDataSlope)
        self.pressDataInfl = pressDataInflInds

        # Iterating through only the left or right EMG data based upon the input bin
        stepsDict = {}
        minLenArr = np.inf
        for i in range(len(emgCols)):

            # Checking if the column is from the left or right leg
            binLastLetter = emgCols[i][len(emgCols[i]) - 1:len(emgCols[i])]
            if (binLastLetter == binToParseOn[len(binToParseOn) - 1: len(binToParseOn)]):
                dataToParse = EMGStepsDf[emgCols[i]].to_numpy()

                # Extracting steps from the EMG data using the heel strike peak indices
                stepsDict[emgCols[i]] = []
                for j in range(len(pressDataInflInds) - 1):
                    extractedStep = dataToParse[pressDataInflInds[j]:pressDataInflInds[j + 1]]
                    stepsDict[emgCols[i]].append(extractedStep)
                    
                    # Saving the minimum length to use in cutting all steps down to the same size
                    if (len(extractedStep) < minLenArr):
                        minLenArr = len(extractedStep)

        # Downsampling all of the data to the smallest step size
        stepsDictKeys = list(stepsDict.keys())
        for i in range(len(stepsDictKeys)):
            signals = stepsDict[stepsDictKeys[i]]

            stepsDict[stepsDictKeys[i]] = [self.downsample_signal(signal, minLenArr) for signal in signals]

        outDf = pd.DataFrame.from_dict(stepsDict)

        return outDf