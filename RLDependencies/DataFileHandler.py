import numpy as np
import h5py
import os
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from IPython.display import display, clear_output
import tkinter as tk
import json
import threading
import queue
from pylsl import StreamInlet, resolve_stream, LostError

class DataFileHandler():
    """
    This is a Data File Handler Class that is used to save data live to files during experiments. Utilizes
    numpy and h5py files formats to saving.

    Author: Sonny Jones & Grange Simpson
    Version: 2024.06.10
    """

    def __init__(self, filePath = None):
        # Initialiting filePath
        self.filePath = filePath

        # Initiating num channels
        self.numChannels = 0

        # Initializing File Saving Structures
        self.DelsysFileStructure = None
        self.XSensorFileStructure = None        

    #-----------------------------------------------------------------------------------
    # ---- File Handler Functions

    def setFilePath(self, filePath):
        # Setting File Path
        self.filePath = filePath

    def createFile(self, fileName):
        if self.filePath is not None:
            # Checking filePath 
            if not os.path.exists(self.filePath):
                # Creating folder if doesn't exists
                os.makedirs(self.filePath)

            # Formatting FileName
            self.trialName = fileName
            self.fileName = f"{fileName}.h5"

            # Complete path
            completePath = os.path.join(self.filePath, self.fileName)

            # Creating h5py file with fileName
            self.hdf5File = h5py.File(completePath, 'a')

            # Adding some metadata variables
            self.hdf5File.attrs['Created Date'] = str(date.today())
            self.hdf5File.attrs['Created Time'] = str(datetime.now().strftime("%H:%M:%S"))
        else:
            # Formatting FileName
            self.fileName = f"{fileName}.h5"

            # Creating h5py file with fileName
            self.hdf5File = h5py.File(self.fileName, 'a')

            # Adding some metadata variables
            self.hdf5File.attrs['Created Date'] = str(date.today())
            self.hdf5File.attrs['Created Time'] = str(datetime.now().strftime("%H:%M:%S"))

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
            self.formatXsensorInfo(sensorDictXSensor)

        else:
            print("No Formatting Data Provided")

    # Formatting File for Delsys
    def formatDelsysInfo(self, sensorDictDelsys: dict) -> None:
        # Formatting file for the Delsys data structure
        for group, datasets in sensorDictDelsys.items():
            # Setting internal attributes
            self.DelsysFileStructure = sensorDictDelsys

            # Creating groups then datasets for each connected sensor
            try:
                self.createGroup(group, metaData = {'Attachment' : datasets['Attachment']})
                
                # Checking channel and samplerate attributes are of the same length
                if len(datasets['Channels']) != len(datasets['SampleRates']):
                    print('Channels and SampleRates are not the same length')
                    pass

                # Creating Element if Needing to Add Additional Channels
                self.extra = 1

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
            # Setting internal attributes
            self.XSensorFileStructure = sensorDictXSensor

            # Creating groups then datasets for each connected sensor
            try:
                self.createGroup(group, metaData = {'Foot' : datasets['Foot'], 'SensorSize' : datasets['SensorSize']})

                # Checking channel and samplerate attributes are of the same length
                if len(datasets['Channels']) != len(datasets['SampleRates']):
                    print('Channels and SampleRates are not the same length')
                    pass

                # Creating datasets for each channel
                for i in range(len(datasets['Channels'])):
                    print(datasets['Channels'][i])
                    self.createXSensorChannel(group, datasets['Channels'][i], {'SampleRate' : datasets['SampleRates'][i]})

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

        except:
            # Accessing group in file
            group = self.hdf5File[groupName]
            # Adding dataset to group
            maxDataSize = (None,)

            # Creating Temp Channel Name
            tempChanName = f"{channelName}_{self.extra}"
            group.create_dataset(tempChanName, shape = (0,), maxshape = maxDataSize)

            # Incrementing Extra Index
            self.extra += 1

            # Adding metadata if available
            if metaData is not None:
                # Adding metadata
                for key, value in metaData.items():
                    group[channelName].attrs[key] = value

            # Adding to channel number
            self.numChannels += 1

    """
    Creating XSensor Channel
    """
    def createXSensorChannel(self, groupName: str, channelName: str, metaData: dict = None) -> None:
        # Locating Group in file
        try:
            # Accessing group in file
            group = self.hdf5File[groupName]
            # Adding dataset to group
            maxDataSize = (None, 341)

            group.create_dataset(channelName, shape = (0, 341), maxshape = maxDataSize)

            # Adding metadata if available
            if metaData is not None:
                # Adding metadata
                for key, value in metaData.items():
                    group[channelName].attrs[key] = value

            # Adding to channel number
            self.numChannels += 1

        except Exception as e:
            print(e)
            print("Unable to format XSensor Channel")

    def openFile(self, fileName):
        # Opens file if not already open
        print("Opening hdf5 file.")
        if self.hdf5File == None:
            self.createFile(fileName)

    def addStartTime(self, startTime):
        # Adding start time as an attribute
        self.hdf5File.attrs['startTime'] = startTime

    def addStopTime(self, stopTime):
        # Adding stop time as an attribute
        self.hdf5File.attrs['stopTime'] = stopTime

    def addTransitionTime(self, terrain, transitionTime):
        # Adding Transition Time to List in h5pyFile
        if 'terrainTransition' in self.hdf5File.attrs.keys():
            # Loading Current List
            currentTerrainList = self.hdf5File.attrs['terrainTransition']
            currentTransitionList = self.hdf5File.attrs['terrainTransitionTime']

            # Appending Transition to List
            currentTerrainList = np.append(currentTerrainList, terrain)
            currentTransitionList = np.append(currentTransitionList, transitionTime)

            # Saving Attribute
            self.hdf5File.attrs['terrainTransition'] = currentTerrainList
            self.hdf5File.attrs['terrainTransitionTime'] = currentTransitionList

        else:
            # Creating Attribute
            self.hdf5File.attrs['terrainTransition'] = [terrain]
            self.hdf5File.attrs['terrainTransitionTime'] = [transitionTime]

    def closeFile(self):
        # Checking to see if file exists
        print("Closing hdf5 file.")
        if self.hdf5File is not None:
            # Closing file
            self.hdf5File.close()
            self.hdf5File = None

    def saveDelsysData(self, data):
        # Checking data length
        if (len(data) != 0):
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
                            currentLength = dataset.shape[0]
                            dataset.resize(currentLength + len(data[0][index]), axis = 0)
                            #dataset.resize(currentLength + len(data[index]), axis = 0)
                            
                            # Setting new data
                            dataset[currentLength:currentLength + len(data[0][index])] = list(data[0][index])
                            #dataset[currentLength:currentLength + len(data[index])] = list(data[index])

                        except Exception as e:
                            print(e)
                            print(f"Unable to add data to {sensor} : {channel}")
                    
                        # Incrementing index
                        index += 1

    def saveXSensorData(self, data):
        # Saving XSensor Data, since data structure is similar, but different
        # Checking data length
        if len(data) == 0:
            pass
        else:
            # Looping through sensors
            for sensorIndex, sensor in enumerate(list(self.XSensorFileStructure.keys())):
                # Looping through Sensor Channels
                for channel in self.XSensorFileStructure[sensor]['Channels']:
                    try:
                        dataset = self.hdf5File[f'{sensor}/{channel}']
                        # Getting current data from xsensor, saving full array for now
                        currentLength = dataset.shape[0]
                        dataset.resize(currentLength + len(data[sensorIndex]), axis = 0)

                        # Setting new data
                        dataset[currentLength:currentLength + len(data[sensorIndex])] = data[sensorIndex]

                    except Exception as e:
                        print(e)
                        print(f"Unable to add data to {sensor} : {channel}")

    def update(self, delsysData = None, XSensorData = None):
        # Updating information in file
        if delsysData:
            self.saveDelsysData(delsysData)
        if XSensorData:
            self.saveXSensorData(XSensorData)

    def plotTrialDataThread(self):
        plotThread = threading.Thread(target = self.plotTrialData)
        plotThread.start()

        self.plotTrialData()

    def plotDelsysTrialData(self):
        # Visualization for Trial Data
        # Looping Through Delsys Sensors
        for sensor in list(self.DelsysFileStructure.keys()):
            # Checking if Sensor in Name
            if ("Sensor" in sensor):
                # Creating Subplot for Data
                channelLength = len(self.DelsysFileStructure[sensor]['Channels'])
                fig, ax = plt.subplots(channelLength, figsize=(channelLength * 2.5, 10))

                # Iterating Through All Channels
                for index, channel in enumerate(self.DelsysFileStructure[sensor]['Channels']):
                    try:                  
                        # Getting Data From Sensor/Channel
                        dataset = self.hdf5File[f'{sensor}/{channel}'][()]

                        # Plotting on Axes With Appropriate Labelings
                        ax[index].plot(dataset, label = channel)
                        ax[index].legend(loc = 'upper right')
                        plt.suptitle(f"{sensor} - {self.trialName}")
                        plt.show(block = False)
                    except:
                        pass

    def plotXSensorTrialData(self):
        # Dynamically Creating Subplots for XSensor Data
        fig, ax = plt.subplots(1, len(self.XSensorFileStructure.keys()), figsize = (4 * len(self.XSensorFileStructure.keys()), 7))

        # Iterating Through Sensors
        for foot in list(self.XSensorFileStructure.keys()):
            # Creating List to Hold Samples
            datasetList = []

            # Iterating Through Channels
            for index, channel in enumerate(self.XSensorFileStructure[foot]['Channels']):
                try:
                    # Getting Data From Sensor/Channel
                    dataset = self.hdf5File[f'{foot}/{channel}'][()]

                    # Appending to Dataset List
                    datasetList.append(dataset)

                    # Adding Title to Subplot
                    ax[index].title.set_text(f"{self.hdf5File[f'{foot}/Foot']}")

                except:
                    pass

        # Iterating Through Data
        for sampleIndex in enumerate(datasetList[0]):
            # Iterating Through Axes
            for index, ax in enumerate(ax):
                # Reshapping Data
                reshapedData = datasetList[index][sampleIndex].reshape(31, 11)
            
                # Updating Plot
                ax.clear()
                ax.imshow(reshapedData, cmap = 'hot', interpolation = 'nearest')
            
            # Displaying Figure
            display(fig)
            clear_output(wait = True)
            plt.pause(0.001)

        # Showing Plot
        plt.show()

    def saveDelsysMVC(self, MVCData):
        # Saving Data As NP File
        if not os.path.exists(f"{self.filePath}/MVC.npy"):
            np.save(f"{self.filePath}/MVC.npy", MVCData, allow_pickle = True)

    def saveParticipantWeight(self, participantWeight):
        # Saving Into File
        self.hdf5File.attrs['participantWeight'] = participantWeight

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

'''
#-----------------------------------------------------------------------------------
# ---- Queue Class

def clearQueue(queue):
        """
        Clears all items from the queue.
        """
        while not queue.empty():
            try:
                queue.get()
            except queue.Empty:
                break

#-----------------------------------------------------------------------------------
# ---- Threading Module For Commands and Saving

# Setting Up DataFileHandler
dataHandler = DataFileHandler()

# Setting up Command Queue
commandQueue = queue.Queue()

# Stopping Event
stopEvent = threading.Event()
 
# Command Mapp
commandMap = {
    'setFilePath' : dataHandler.setFilePath,
    'createFile' : dataHandler.createFile,
    'formatFile' : dataHandler.formatFile,
    'addStartTime' : dataHandler.addStartTime,
    'addStopTime' : dataHandler.addStopTime,
    'saveDelsysData' : dataHandler.saveDelsysData,
    'saveXSensorData' : dataHandler.saveXSensorData,
    'saveDelsysMVC' : dataHandler.saveDelsysMVC,
    'addTransitionTime' : dataHandler.addTransitionTime,
    'plotTrialData' : dataHandler.plotTrialDataThread,
    'closeFile' : dataHandler.closeFile,
    'cleanUp' : dataHandler.closeFile,
    #'stop' : stopEvent.set
}

# Resolving Command Stream
print("Looking for RLCommandStream...")

try:
    # Creating a New Inlet to Read from the Stream
    streams = resolve_stream('type', 'command')

    # If No Stream
    if len(streams) == 0:
        print("Stream not found")

    # If Stream Found
    else:
        # Creating Inlet
        inlet = StreamInlet(streams[0])

except Exception as e:
    print(f"Error resolving command stream: {e}")

# Listener Function for Commands
def listener():
    # Infinite Loop for Listening
    while True:
        try:
            # Getting New Command From Command Stream
            command, timestamps = inlet.pull_sample()

            # If Command is Available
            if command:
                # Adding Command to Queue
                print(json.loads(command[0]))
                print("\n")
                commandQueue.put(json.loads(command[0]))

        # Decoding Error
        except json.JSONDecodeError as e:
            print(f"Error decoding sample: {e}")

# Queue Processor Function
def processQueue():
    # Infinite Loop for Processing
    while True:
        # Getting Command from Command Queue
        command = commandQueue.get()

        # Setting Default Function Name
        functionName = 'Start Command Processing'

        # If There Are Commands in Queue
        if command is not None:
            try:
                # Getting Command, Params
                functionName = command['function']
                params = command.get('params', {})

                if functionName == 'stop':
                    stopEvent.set()
                    inlet.close_stream()

                # Executing Commands
                commandMap[functionName](**params)

                # Clearing Queue If Command is Close File
                if functionName == 'closeFile':
                    clearQueue(commandQueue)

            except:
                print(f"Error executing command: {functionName}")         

#----------- Main Function --------------------------

if __name__ == '__main__':
    pass
    # Creating and Running Listener Thread
    listenerThread = threading.Thread(target = listener, daemon = True)
    listenerThread.start()

    # Creating and Running Processor Thread
    processerThread = threading.Thread(target = processQueue, daemon = True)
    processerThread.start()

    # Keeping Main Thread Alive
    while True:
        try:
            pass

        except LostError:
            # Closing Inlet
            inlet.close_stream()

            # Joining Listener Threads
            listenerThread.join()
            processerThread.join()

            break

        except KeyboardInterrupt:
            # Closing Inlet
            inlet.close_stream()

            # Joining Listener Threads
            listenerThread.join()
            processerThread.join()

            break

    print("Exiting DataFileHandler...")
'''