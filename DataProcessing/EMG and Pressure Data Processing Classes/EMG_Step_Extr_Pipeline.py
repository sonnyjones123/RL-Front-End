#import h5py
import numpy as np
import scipy as sp
import pandas as pd
from scipy.signal import find_peaks
from operator import itemgetter
from EMGProcessingV2 import EMGProcessor
    

class EMGStepExtraction:
    def __init__(self):
        self.EMGSampFreq = 1925.925
        self.EMGProcessor = EMGProcessor(self.EMGSampFreq)


    def filter_and_smooth(self, inputDf):
        smoothedFlat1Dict = {}

        extrCols = inputDf.columns

        # Iterating through all raw EMG data from each dataframe filtering and smoothing it
        for x in range(len(inputDf.columns)):
            rawEMG = inputDf[extrCols[x]].to_numpy()

            filteredEMG = self.EMGProcessor.filter_high_pass(rawEMG, cutoff_frequency=0.1)
            rectifyEMG = self.EMGProcessor.rectify(filteredEMG)
            smoothedEMG = self.EMGProcessor.moving_window_average(rectifyEMG, window_size=0.1)

            smoothedFlat1Dict[extrCols[x]] = smoothedEMG

        #print(smoothedFlat1Dict)
        outputDf = pd.DataFrame.from_dict(smoothedFlat1Dict, orient='columns')

        return outputDf
    

    def step_extraction(self, inputDf):
        DataSaveDict = {}
        cols = inputDf.columns
        # Extracting all the peaks and saving them to a dataframe
        for x in range(len(cols)):
            smoothedData = inputDf[cols[x]]
            #print(smoothedData)
            intermDict = {}
            # Invert the signal to find indexes around peaks
            extractPeaks, _ = find_peaks(-smoothedData, distance = 2000)
            if (len(extractPeaks) > 0):
                for y in range(len(extractPeaks) + 1):
                    # Extracing peaks at the start, for now skip it
                    if (y == 0):
                        continue
                        #intermDict[y] = np.array(smoothedData[0:extractPeaks[y]])

                    # Extracting peaks at the end, for now skip it
                    elif (y > len(extractPeaks) - 1):
                        continue
                        #intermDict[y] = np.array(smoothedData[extractPeaks[y - 1]:len(smoothedData)])

                    # Extracting all other peaks
                    else:
                        intermDict[y] = np.array(smoothedData[extractPeaks[y - 1]:extractPeaks[y]])

            DataSaveDict[cols[x]] = intermDict

        return DataSaveDict
    

    def uniform_tail_removal(self, inputDict):
        UniformSizeDataDict = {}

        cols = list(inputDict.keys())

        for x in range(len(inputDict.keys())):
            EMGDict = inputDict[cols[x]]
            intermDict = {}

            for y in range(len(EMGDict.keys())):
                if (y in list(EMGDict.keys())):
                    stepData = EMGDict[y]
                    peaks, _ = find_peaks(stepData, distance=1000)

                    # Extract peak vals to find the maximum value
                    peakVals = list(itemgetter(*peaks)(stepData))

                    maxInd = np.where(stepData == max(peakVals))[0]

                    # Making all steps to be 2000 values long, since the sampling rate is 1925 and a normal step should take about a second.
                    if (len(stepData) > 2000):
                        # Trimming steps down on the right or left depending on the location of the tails
                        lengthDiff = len(stepData) - maxInd

                        # Trimming the data tails on the left
                        if (lengthDiff < maxInd):
                            # Removing tails on the left
                            removeLeft = len(stepData) - 2000
                            intermDict[y] = stepData[removeLeft:len(stepData)]
                            
                        # Trimming data tails on the right:
                        else:
                            removeRight = len(stepData) - 2000
                            intermDict[y] = stepData[0:len(stepData)-removeRight]
                    
                    # TODO: Unsure if we need to bother with steps less than a second for now
                    else:
                        addOnArr = np.zeros(3)
                        """
                        stepData = EMGDict[y]
                        peaks, _ = find_peaks(stepData, distance=1000)

                        # Extract peak vals to find the maximum value
                        peakVals = list(itemgetter(*peaks)(stepData))

                        maxInd = np.where(stepData == max(peakVals))[0]

                        # Making all steps to be 2000 values long, since the sampling rate is 1925 and a normal step should take about a second.
                        if (len(stepData) > 2000):
                            # Trimming steps down on the right or left depending on the location of the tails
                            lengthDiff = len(stepData) - maxInd

                            # Trimming the data tails on the left
                            if (lengthDiff < maxInd):
                                # Removing tails on the left
                                removeLeft = len(stepData) - 2000
                                intermDict[y] = stepData[removeLeft:len(stepData)]
                                
                            # Trimming data tails on the right:
                            else:
                                removeRight = len(stepData) - 2000
                                intermDict[y] = stepData[0:len(stepData)-removeRight]
                        """       

            UniformSizeDataDict[cols[x]] = intermDict

        return UniformSizeDataDict

