"""
This file is meant to segment and bin hdf5 files from the RLFrontEnd.py file used for collecting EMG, IMU, Goniometer, and Foot Pressure data.

Written by Grange Simpson
Version: 2024.05.16

Usage: Run the file.

"""

import h5py
import numpy as np
import scipy as sp
from scipy import signal
import pandas as pd

class Data_Segmentor:
    def __init__(self):
        self.EMGSampRate = None
        self.IMUSampRate = None
        self.GonSampRate = None
        self.XSensorSampRate = None

        self.rawEMGData = pd.DataFrame()
        self.rawGonData = pd.DataFrame()
        self.rawXSensorData = pd.DataFrame()
        self.rawIMUData = pd.DataFrame()
        
        self.smoothedEMGData = pd.DataFrame()
        self.binnedPressData = pd.DataFrame()

        self.defaultSensorConnections = ['TAL', 'TAR', 'LGL', 'LGR', 'VLL', 'VLR', 'BFL', 'BFR','None', 'None', 'None', 'None', 'None', 'LK', 'RK']


    """
    Section for parsing a h5py file into individual pandas dataframes.
    """
    def parseData(self, inputFile):
        # TODO: file type checking to make sure the input file is a h5py file

        # Extract all data from the input h5py file
        fileKeysList = list(inputFile.keys())

        # Dictionaries to store each datatype in
        emgDict = {}
        gonDict = {}
        pressDict = {}
        imuDict = {}

        # Iterating through all sensor signals stored in the h5py file
        for i in range(len(fileKeysList)):
            # Parsing out EMG and IMU data from the h5py file
            if ("Sensor " in fileKeysList[i]):
                # Sensor 14 and 15 are the goniometer and IMU data
                if ("Sensor 14" in fileKeysList[i] or "Sensor 15" in fileKeysList[i]):
                    sensorKeysList = inputFile[fileKeysList[i]].keys()

                    # Only saving analog 1 channel data for now
                    gonDict[inputFile[fileKeysList[i]].attrs["Attachment"]] = inputFile[fileKeysList[i] + "/Analog 1"][()]

                    # Saving the Goniometer sampling rate
                    if (self.GonSampRate is None):
                        self.GonSampRate = round(inputFile[fileKeysList[i] + "/Analog 1"].attrs["SampleRate"], 2)

                # All other sensors are EMG and IMU data
                else:
                    # Accessing the EMG and IMU data under each sensor
                    sensorKeysList = list(inputFile[fileKeysList[i]].keys())

                    for j in range(len(sensorKeysList)):
                        if ("EMG" in sensorKeysList[j]):
                            # Assigning the muscle attachment name to the EMG data
                            emgDict[inputFile[fileKeysList[i]].attrs["Attachment"]] = inputFile[fileKeysList[i] + "/" + sensorKeysList[j]][()]

                            # Saving the EMG sampling rate
                            if (self.EMGSampRate is None):
                                self.EMGSampRate = round(inputFile[fileKeysList[i] + "/" + sensorKeysList[j]].attrs["SampleRate"], 2)

                        elif ("GYRO" in sensorKeysList[j]):
                            # Assigning the muscle attachment plus GYRO X, Y, or Z
                            imuDict[inputFile[fileKeysList[i]].attrs["Attachment"] + "_" + sensorKeysList[j]] = inputFile[fileKeysList[i] + "/" + sensorKeysList[j]][()]

                            # Saving the IMU sampling rate
                            if (self.IMUSampRate is None):
                                self.IMUSampRate = round(inputFile[fileKeysList[i] + "/" + sensorKeysList[j]].attrs["SampleRate"], 2)
                    
            
            # Parsing out the XSensor pressure data
            elif ("Foot " in fileKeysList[i]):
                footPlacement = inputFile[fileKeysList[i]].attrs["Foot"]
                pressDict[footPlacement] = inputFile[fileKeysList[i]+"/"+"Pressure"][()]

                # Saving the IMU sampling rate
                if (self.XSensorSampRate is None):
                    self.XSensorSampRate = round(inputFile[fileKeysList[i]+"/"+"Pressure"].attrs["SampleRate"], 2)


        # Converting the dictionaries into dataframes
        self.rawEMGData = pd.DataFrame.from_dict(emgDict)
        self.rawGonData = pd.DataFrame.from_dict(gonDict)
        self.rawXSensorData = pd.DataFrame.from_dict(pressDict)
        self.rawIMUData = pd.DataFrame.from_dict(imuDict)

    # Getter for EMG df                    
    def getEMGData(self):
        return self.rawEMGData
    
    # Getter for the EMG sampling rate
    def getEMGSampRate(self):
        return self.EMGSampRate
    
    # Getter for Goniometer df
    def getGonData(self):
        return self.rawGonData
    
    # Getter for the Goniometer sampling rate
    def getGonSampRate(self):
        return self.GonSampRate
    
    # Getter for XSensor Pressure df
    def getXSensorData(self):
        return self.rawXSensorData
    
    # Getter for the XSensor sampling rate
    def getXSensorSampRate(self):
        return self.XSensorSampRate
    
    # Getter for IMU df, only from the EMG sensors
    def getIMUData(self):
        return self.rawIMUData
    
    # Getter for the IMU sampling rate
    def getIMUSampRate(self):
        return self.IMUSampRate


    """
    Section for filtering, rectifying, and doing a moving window average on the EMG data
    """
    # High pass filter with input cutoff_frequency
    def filter_high_pass_emg(self, raw_EMG, cutoff_frequency):
        bf_order = 4
        bf_cutoff_fq_lo = 10
        bf_cutoff_fq_hi = 450

        #nyquist_frequency = 0.5 * self.EMGSampRate
        #normalized_cutoff_frequency = cutoff_frequency / nyquist_frequency
        b, a = signal.butter(N=int(bf_order/2), Wn=[bf_cutoff_fq_lo, bf_cutoff_fq_hi],
                             btype='bandpass', analog=False, output='ba', fs=self.EMGSampRate)
        filtered_EMG = signal.filtfilt(b, a, raw_EMG, axis=0)  # two-directional filtering, double the order, zero phase
        return filtered_EMG
    
    # Rectify the signal to have no negative values
    def rectify_emg(self, filtered_EMG):
        rec_EMG = np.abs(filtered_EMG)
        #rec_EMG = filtered_EMG
        return rec_EMG
    
    # Do a convolution on the signal to create a smooth signal
    def moving_window_average_emg(self, rec_EMG, window_size):
        num_samples = int(window_size * self.EMGSampRate)
        smoothed_EMG = np.convolve(rec_EMG, np.ones(num_samples) / num_samples, mode='same')
        return smoothed_EMG

    # Perform all three methods on all columns in the raw EMG data
    def filt_rect_smooth_EMG(self):
        EMG_df_cols = self.rawEMGData.columns
        intermEMGDict = {}

        # Iterate through all columns in the raw EMG dataframe
        for i in range(len(EMG_df_cols)):
            rawEMG = self.rawEMGData[EMG_df_cols[i]].to_numpy()

            filteredEMG = self.filter_high_pass_emg(rawEMG, cutoff_frequency=0.1)
            rectifyEMG = self.rectify_emg(filteredEMG)
            smoothedEMG = self.moving_window_average_emg(rectifyEMG, window_size=0.1)

            intermEMGDict[EMG_df_cols[i]] = smoothedEMG

        self.smoothedEMGData = pd.DataFrame.from_dict(intermEMGDict)

    def get_filt_rect_smooth_emg(self):
        return self.smoothedEMGData
    
    """
    Section for binning the pressure insole data
    """

    # Data is binned into hallux, lateral toes, forefoot, midfoot, rearfoot.
    def bin_pressure_data(self):
        # Read existing data from the dataset
        existing_data_right = self.rawXSensorData["Right"].to_numpy()
        existing_data_left = self.rawXSensorData["Left"].to_numpy()

        # Each step within the whole data array is 341 values long, so the 1D array is reshaped into a 2D array to access each step
        footsteps_data_right = existing_data_right.reshape(int(len(existing_data_right) / 341), 341)
        footsteps_data_left = existing_data_left.reshape(int(len(existing_data_right) / 341), 341)

        binNamesArr = ["HalluxL", "HalluxR", "LateralToesL", "LateralToesR", "ForefootL","ForefootR", "MedialfootL", "MedialfootR", "RearfootL", "RearfootR"]
        arrDict = {}

        for i in range(len(binNamesArr)):
            arrDict[binNamesArr[i]] = np.array([])

        for i in range(int(len(existing_data_right) / 341)):
            current_step_left = footsteps_data_left[i]
            current_step_right = footsteps_data_right[i]
            # Change data to 2D shape, and remove non-sensors
            current_step_left.shape = (31, 11)
            current_step_left[current_step_left==-1]=np.nan
            current_step_right.shape = (31, 11)
            current_step_right[current_step_right==-1]=np.nan

            # Take the mean for each bin
            hallux_L = current_step_left[0:6, 7:12]
            arrDict["HalluxL"] = np.append(arrDict["HalluxL"], np.nanmean(hallux_L))
            hallux_R = current_step_right[0:6, 0:4]
            arrDict["HalluxR"] = np.append(arrDict["HalluxR"], np.nanmean(hallux_R))

            lateralToesL = current_step_left[0:6, 0:7]
            arrDict["LateralToesL"] = np.append(arrDict["LateralToesL"], np.nanmean(lateralToesL))
            lateralToesR = current_step_right[0:6, 4:12]
            arrDict["LateralToesR"] = np.append(arrDict["LateralToesR"], np.nanmean(lateralToesR))

            foreFootL = current_step_left[6:15, 0:12]
            arrDict["ForefootL"] = np.append(arrDict["ForefootL"], np.nanmean(foreFootL))
            foreFootR = current_step_right[6:15, 0:12]
            arrDict["ForefootR"] = np.append(arrDict["ForefootR"], np.nanmean(foreFootR))
            
            medialFootL = current_step_left[15:22, 0:12]
            arrDict["MedialfootL"] = np.append(arrDict["MedialfootL"], np.nanmean(medialFootL))
            medialFootR = current_step_right[15:22, 0:12]
            arrDict["MedialfootR"] = np.append(arrDict["MedialfootR"], np.nanmean(medialFootR))

            rearFootL = current_step_left[22:32, 0:12]
            arrDict["RearfootL"] = np.append(arrDict["RearfootL"], np.nanmean(rearFootL))
            rearFootR = current_step_right[22:32, 0:12]
            arrDict["RearfootR"] = np.append(arrDict["RearfootR"], np.nanmean(rearFootR))

        self.binnedPressData = pd.DataFrame.from_dict(arrDict)

    def get_binned_pressure_data(self):
        return self.binnedPressData

"""
Example of parsing data
"""
if __name__ == "__main__":
    Trial4File = h5py.File("Trial 4.h5")
    dataSegm = Data_Segmentor(1925.925, 1925.925, 100, 10)

    dataSegm.parseData(Trial4File)

    dataSegm.filt_rect_smooth_EMG()
    dataSegm.bin_pressure_data()

