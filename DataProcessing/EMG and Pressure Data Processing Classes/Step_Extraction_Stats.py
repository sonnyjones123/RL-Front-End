"""
This file is meant to extract steps from multiple EMG channels using the heel strike to heel strike distances
from the XSensor pressure insole.

Written by Grange Simpson
Version: 2024.05.21

Usage: Run the file.
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from scipy import interpolate


class Step_Extraction_Stats:
    def __init__(self):
        self.peakSpacing = 2000

        # Variables to use for testing
        self.upSampleData = 0
        self.upSampledPressDataSlope = 0
        self.pressDataInfl = 0
    

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
        # Removing unloading events from the data
        slopeData[slopeData < 0] = 0

        # Removing small loading noise from the data
        # TODO: check with Kylee what a better number would be for removing small loading noise than meanPeakHeight / 15
        # Finding peaks to get the average peak height, will likely need to adjust for higher sampling rate
        pressDataPeakInds = self.find_bin_peaks(inputSlope)
        meanPeakHeight = np.mean(inputSlope[pressDataPeakInds])

        slopeData[slopeData < meanPeakHeight / 20] = 0 

        indexArr = []
        # Only save the indexs of inflection points where the difference in slope is small for the current point then large for the next point
        # indicating an inflection point
        for x in range(len(slopeData) - 2):
            if (slopeData[x] == 0 and slopeData[x + 1] > 0):
                indexArr.append(x + 1)

        meanStepLength = np.mean(np.diff(indexArr))

        # Removing all possible false steps that are less than 1/2 the mean length of all steps
        indexArrCop = indexArr.copy()
        deleteIter = 0
        for x in range(len(indexArr) - 2):
            #print(x)
            if (indexArr[x + 1] - indexArr[x] < meanStepLength / 1.5):
                
                #print(len(indexArrCop))
                #print(len(indexArr))
                del indexArrCop[(x + 1) - deleteIter]
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

        upSampledHeelData = self.upsample_data(pressureStepsDf[binToParseOn], upsampleFactor)
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
    

if __name__ == "__main__":
    stepExtr = Step_Extraction_Stats()

