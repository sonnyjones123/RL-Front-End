import numpy as np
import h5py
import os
from datetime import datetime

class DataFileHandler():
    """
    This is a Data File Handler Class that is used to save data live to files during experiments. Utilizes
    numpy and h5py files formats to saving.

    Author: Sonny Jones & Grange Simpson
    Version: 2024.01.17 
    """

    def __init__(self, filePath = None):
        # Initialiting filePath
        self.filePath = filePath

        # Initiating num channels
        self.numChannels = 0        

    #-----------------------------------------------------------------------------------
    # ---- File Handler Functions

    def createFile(self, fileName):
        if self.filePath is not None:
            # Checking filePath 
            if not os.path.exists(self.filePath):
                # Creating folder if doesn't exists
                os.makedirs(self.filePath)

            # Formatting FileName
            self.fileName = f"{fileName}.h5"

            # Complete path
            completePath = os.path.join(self.filePath, self.fileName)

            # Creating h5py file with fileName
            self.hdf5File = h5py.File(completePath, 'a')

            # Adding some metadata variables
            self.hdf5File.attrs['Created Date'] = str(datetime.date)
        else:
            # Formatting FileName
            self.fileName = f"{fileName}.h5"

            # Creating h5py file with fileName
            self.hdf5File = h5py.File(self.fileName, 'a')

            # Adding some metadata variables
            self.hdf5File.attrs['Created Date'] = str(datetime.date)

    # Incoming Sensor File Format
    # Key : 'Sensor Name' -> Values: 'Channel Names' : List of Names ; 'Sample Rates' : List of Sample Rates 
    def formatFile(self, sensorDictDelsys: dict = None, sensorDictXSensor: dict = None) -> None:
        # Adding additional metadata
        if sensorDictDelsys and sensorDictXSensor:
            self.hdf5File.attrs['Sensors'] = list(sensorDictDelsys.keys()) + list(sensorDictXSensor.keys())

            # Formatting File for Delsys and XSensor Data
            self.formatDelsysInfo(sensorDictDelsys)
            self.formatXsensorInfo(sensorDictXSensor)

        elif sensorDictDelsys:
            self.hdf5File.attrs['Sensors'] = list(sensorDictDelsys.keys())

            # Formatting File for Delsys
            self.formatDelsysInfo(sensorDictDelsys)

        elif sensorDictXSensor:
            self.hdf5File.attrs['Sensors'] = list(sensorDictXSensor.keys())

            # Formatting File for XSensor Data
            self.formatDelsysInfo(sensorDictXSensor)

        else:
            print("No Formatting Data Provided")

    # Formatting File for Delsys
    def formatDelsysInfo(self, sensorDictDelsys: dict) -> None:
        # Formatting file for the Delsys data structure
        for group, datasets in sensorDictDelsys.items():
            print(group, datasets)
            # Setting internal attributes
            self.DelsysFileStructure = sensorDictDelsys

            # Creating groups then datasets for each connected sensor
            try:
                self.createGroup(group, metaData = {'Attachment' : datasets['Attachment']})
                
                # Checking channel and samplerate attributes are of the same length
                if len(datasets['Channels']) != len(datasets['SampleRates']):
                    print('Channels and SampleRates are not the same length')
                    pass

                # Creating datasets for each channel, 
                for i in range(len(datasets['Channels'])):
                    print(datasets['Channels'][i])
                    # Creating channels and adding sample rates for EMG GYROX, GYROY, GYROZ
                    self.createChannel(group, datasets['Channels'][i], {'SampleRate' : datasets['SampleRates'][i]})

            except Exception as e:
                print("Error in making group or datasets for Delsys.")
                print(e)

    # Formatting File for XSensor
    def formatXsensorInfo(self, sensorDictXSensor: dict) -> None:
        # Formatting file for the XSensor data structure
        for group, datasets in sensorDictXSensor.items():
            print(group, datasets)
            # Setting internal attributes
            self.XSensorFileStructure = sensorDictXSensor

            # Creating groups then datasets for each connected sensor
            try:
                self.createGroup(group, metaData = {'Foot' : datasets['Foot']})

                # Checking channel and samplerate attributes are of the same length
                if len(datasets['Channels']) != len(datasets['SampleRates']):
                    print('Channels and SampleRates are not the same length')
                    pass

                # Creating datasets for each channel
                for i in range(len(datasets['Channels'])):
                    print(datasets['Channels'][i])
                    self.createChannel(group, datasets['Channels'][i], {'SampleRate' : datasets['SampleRates'][i]})

            except Exception as e:
                print("Error in making group or datasets for XSensor.")
                print(e)
    
    """
    First step when creating the hdf5 file is to create a group which will have datasets stored under them
    """
    def createGroup(self, groupName: str, metaData: dict = None) -> None:
        try:
            # Creating group in file
            group = self.hdf5File.create_group(groupName)

            # Adding metadata to group
            if metaData is not None:
                for key, value in metaData.items():
                    group.attrs[key] = value

        except Exception as e:
            print(e)
            print("Group already exists")

    """
    Second step is to create data sets and put them under the right group
    """
    def createChannel(self, groupName: str, channelName: str, metaData: dict = None) -> None:
        # Locating Group in file
        try:
            # Accessing group in file
            group = self.hdf5File[groupName]
            # Adding dataset to group
            maxDataSize = (None,)

            group.create_dataset(channelName, shape = (0,), maxshape = maxDataSize)

            # Adding metadata if available
            if metaData is not None:
                # Adding metadata
                for key, value in metaData.items():
                    group[channelName].attrs[key] = value

            # Adding to channel number
            self.numChannels += 1

        except Exception as e:
            print(e)
            print("Group doesnt exist. Creating standalone channel")
            # Creating dataset in file
            # maxDataSize = (None,)
            # self.hdf5File.create_dataset(channelName, shape = (0,), maxshape = maxDataSize) 

    def openFile(self, fileName):
        # Opens file if not already open
        if self.hdf5File == None:
            self.createFile(fileName)

    def addStartTime(self, startTime):
        # Adding start time as an attribute
        self.hdf5File.attrs['startTime'] = startTime

    def addStopTime(self, stopTime):
        # Adding stop time as an attribute
        self.hdf5File.attrs['stopTime'] = stopTime

    def closeFile(self):
        # Checking to see if file exists
        if self.hdf5File is not None:
            # Closing file
            self.hdf5File.close()
            self.hdf5File = None

    def saveDelsysData(self, data):
        # Checking data length
        if len(data) == 0:
            pass
        else:
            # Indexing param
            index = 0

            # Looping through sensors
            for sensor in list(self.DelsysFileStructure.keys()):
                if ("Sensor" in sensor):
                    for channel in self.DelsysFileStructure[sensor]['Channels']:
                        try:                  
                            # Adding data to sensor channel
                            dataset = self.hdf5File[f'{sensor}/{channel}']
                            
                            # Getting current size and reindexing
                            current_size = dataset.shape[0]
                            dataset.resize(current_size + len(data[0][index]), axis = 0)
                            
                            # Setting new data
                            dataset[current_size:current_size + len(data[0][index])] = list(data[0][index])

                        except Exception as e:
                            print(e)
                            print(f"Unable to add data to {sensor} : {channel}")
                    
                        # Incrementing index
                        index += 1

    def saveXSensorData(self, data):
        # Saving XSensor Data, since data structure is similar, but different
        if len(data) == 0:
            pass
        else:
            # Indexing param
            index = 0

            # Looping through sensors
            for sensor in list(self.XSensorFileStructure.keys()):
                for channel in self.XSensorFileStructure[sensor]['Channels']:
                    try:
                        dataset = self.hdf5File[f'{sensor}/{channel}']
                        # Getting current data from xsensor, saving full array for now
                        current_size = dataset.shape[0]
                        dataset.resize(current_size + len(data[index]), axis = 0)

                        # Setting new data
                        dataset[current_size:current_size + len(data[index])] = data[index]

                    except Exception as e:
                        print(e)
                        print(f"Unable to add data to {sensor} : {channel}")

                    # Increment index
                    index += 1

    def update(self, delsysData = None, XSensorData = None):
        # Updating information in file
        if delsysData:
            self.saveDelsysData(delsysData)
        if XSensorData:
            self.saveXSensorData(XSensorData)

    #-----------------------------------------------------------------------------------
    # ---- Archived

    def addMetaData(self, dictMetaData: dict) -> None:
        """
        This function adds metadata to the overall h5py data file. Useful if you want to add general information
        regarding general data for the file eg: experiment information, etc.
        Input:
            dictMetaData: metaData in dictionary formay.

        Example:
            dictMetaData =  {
                                'Sampling_rate': '100 Hz',
                                'Description': 'Electromyography data'
                            }
        """
        # Checking if hdf5 file exists
        if self.hdf5File is not None:
            # Appending metaData
            for key, value in dictMetaData.items():
                self.hdf5File.attrs[key] = value

    def addChannelMetaData(self, channelName: list, dictMetaData: dict) -> None:
        """
        This function adds metadata to the channels in h5py data file. Useful if you want to add information
        for a specific channel, eg: which sensor, etc
        Input:
            dictMetaData: metaData in dictionary formay.

        Example:
            dictMetaData =  {
                                'Sampling_rate': '100 Hz',
                                'Description': 'Electromyography data'
                            }
        """
        if channelName in self.hdf5File:
            # Grabbing dataset
            dataset = self.hdf5File[channelName]
            
            # Adding metadata
            for key, value in dictMetaData.items():
                dataset.attrs[key] = value