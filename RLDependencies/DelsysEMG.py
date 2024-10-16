import sys
import platform
import numpy as np
import clr
import tkinter as tk
import matplotlib.pyplot as plt

clr.AddReference("System.Collections")

from tkinter import simpledialog
from System.Collections.Generic import *

# Adding path for current computer
# Please add your computer name and path to the Python API folder for delsys.
if (platform.node() == "Garangatan_Comp"):
    sys.path.insert(0, "C:/Users/grang/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/Delsys/Example-Applications-main/Python")
elif (platform.node() == "Sonny_ThinkPad"):
    sys.path.insert(0, "C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/Delsys/Example-Applications-main/Python")
elif (platform.node() == 'Purkinje'):
    sys.path.insert(0, "C:/Users/Purkinje/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/Delsys/Example-Applications-main/Python")

from AeroPy.TrignoBase import *
from AeroPy.DataManager import *

try:
    from RLDependencies.NERVESLabKeys import *
    from NERVESLabKeys import *
except:
    pass

class DelsysEMG:
    """
    This is a wrapper class for the Delsys EMG System. This is intended to work with
    the Delsys TrignoBase EMG system and API. You will need to install all the dependencies
    and Delsys API software from their Github. The link to the Delsys Github Repository is
    below. 

    Note: We have tested additional functionally with other Delsys products like the Goniometers and EKG with the EMG base and the API. 
    Everything seems to work as intended.

    https://github.com/delsys-inc/Example-Applications/tree/main

    This class will interface with their API and will collect and store information obtained
    from the base. This class can also be used to conenct sensors, start and stop data collection,
    etc.  

    Author: Sonny Jones & Grange Simpson
    Version: 2024.03.06

    Usage:

        DelsysEMG = DelsysEMG()

    """
    def __init__(self):
        # Key and License are obtained from Delsys. You may want to reach out to them for 
        # a new key and license if the following no longer work. 
        self.key = key
        self.license = license
        
        self.data = []
        # sensorNames = [Trigno Avanti: 1 - 12, Trigno EKG: 13, Trigno Avanti Goniometer: 14 - end]
        # self.sensorNames = [75503, 75548, 75596, 75587, 75467, 75672, 75641, 75461, 75148, 75268, 75247, 75406, 69065, 69657, 69699]
        # sensorNames = [Trigno Avanti: 1 - 8, Trigno Mini: 9 - 10, Trigno Avanti Goniometer: 11 - end]
        self.sensorNames = [75503, 75548, 75596, 75587, 75467, 75672, 75641, 75461, 75148, 75268, 69331, 69650, 69273, 69657, 69699, 69631]
        self.sensorDict = {}
        self.numSensors = 16
        self.numSensorsConnected = 0
        self.status = "Off"

        # Sensor Tracking
        self.sensorsScannedOrder = []
        self.sensorsScannedOrderCheck = []
        self.defaultConfiguration = 0

        # Normalization Information
        self.normalize = False
        self.normalizeDict = {}
        self.normalizeList = []
        self.trialNumber = 3
        self.MVCRecording = False

        # Text Input Box
        self.ROOT = tk.Tk()
        self.ROOT.withdraw()

        # Sample Mode List
        self.sampleModeList = ['EMG plus accelerometer (+/- 16g), +/-5.5mV, 20-450Hz',
                               'EMG plus gyro (+/- 2000 dps), +/-5.5mV, 20-450Hz',
                               'EKG raw (2148 Hz), skin check (74 Hz), +/-5.5mV, 2-30Hz',
                               'EKG raw (2148 Hz), skin check (74 Hz), +/-11mv, 2-30Hz', 
                               'SIG raw x4 (519Hz) (x1813)',
                               'SIG raw x4 (296Hz), ACC 16g (148Hz), GYRO 250dps (148Hz), Gain  x2221']
        
        # Data Saving File Structure
        self.dataSavingSensorDict = None

    def connect(self):
        """ 
        Initializes the connection to the Delsys EMG system.

        Usage:
            DelsysEMG.connect()
        """
        # Creating base class instance from Delsys API
        base = TrignoBase()
        self.TrigBase = base.BaseInstance

        # Validating connection to Delsys Base 
        print("Validating TrignoBase connection...")
        self.TrigBase.ValidateBase(self.key, self.license)

        try: 
            self.status = self.TrigBase.GetPipelineState()
            #self.status = "Active"
            print("TrignoBase Connection Valid")
        except:
            self.status = "Connection Refused"
            print("TrignoBase Not Connected")
        
    def checkStatus(self):
        """
        Checks the pipline status of the Delsys EMG system.
            
        Usage:
            DelsysEMG.checkStatus()
        """
        # Checking the status of the Delsys EMG system
        self.status = self.TrigBase.GetPipelineState()

    def currentStatus(self):
        """
        Checks current status of Delsys EMG system.
        """
        return self.status
    
    def connectSensors(self, numSensors, defaultAttachments = None):
        """
        Connects sensors to the Delsys EMG system.

        To connect the sensors, the function runs through the TrigBase.PairSensor()
        command. This will put the system in pairing mode and will continue running
        until a sensor is paired. We can continue to pair additional sensors after.
        Sensors will quickly flash green when pairing is successful. Alternating 
        green and yellow flashing indicates waiting status.
        """

        if (defaultAttachments is not None):
            print("Starting Sensor Pairing...")
            print("Awaiting Sensor Pair Request...")

            # TODO: TEST THIS AGAIN

            # Setting Variable for Default Sensor Configuration
            self.defaultConfiguration = 1

            # Looping through num of sensors
            for num in range(int(numSensors)):
                # Calling Pairing Function
                self.TrigBase.PairSensor()
                # CheckPairStatus will be false when sensor is paired
                while self.TrigBase.CheckPairStatus():
                    continue

                # Adding sensorNames and sensorNum to dict
                for index, sensorName in enumerate(self.TrigBase.GetSensorNames()):
                    tempSensorName = sensorName.split(" ")[0]
                    if int(tempSensorName) in self.sensorDict.keys():
                        # Updating Index
                        self.sensorDict[int(tempSensorName)][0] = index
                    else:
                        self.sensorDict[int(tempSensorName)] = [index]
                        sensorMuscle = defaultAttachments[self.sensorNames.index(int(tempSensorName))]
                        self.sensorDict[int(tempSensorName)].append(sensorMuscle)

                tempSensorKey = list(self.sensorDict.keys())

                print(f"Sensor {self.sensorNames.index(tempSensorKey[num]) + 1} paired")

            # Required otherwise pipeline state doesn't update
            self.TrigBase.ScanSensors()
            for index, sensorName in enumerate(self.TrigBase.GetSensorNames()):
                # Seeing what the actual order of adding sensors is
                self.sensorsScannedOrder.append(sensorName)
                sensorObject = self.TrigBase.GetSensorObject(index)
                self.sensorsScannedOrderCheck.append(sensorObject.Properties.get_Sid())

        else:
            print("Starting Sensor Pairing...")
            print("Awaiting Sensor Pair Request...")

            # Looping through num of sensors
            for num in range(int(numSensors)):
                # Calling Pairing Function
                self.TrigBase.PairSensor()
                # CheckPairStatus will be false when sensor is paired
                while self.TrigBase.CheckPairStatus():
                    continue

                # Adding sensorNames and sensorNum to dict
                for index, sensorName in enumerate(self.TrigBase.GetSensorNames()):
                    tempSensorName = sensorName.split(" ")[0]
                    if int(tempSensorName) in self.sensorDict.keys():
                        # Updating Index
                        self.sensorDict[int(tempSensorName)][0] = index
                    else:
                        self.sensorDict[int(tempSensorName)] = [index]

                        # Asking user for input
                        sensorMuscle = simpledialog.askstring(title = 'Sensor Muscle Input',
                                                            prompt = f'Please indicate what muscle sensor {self.sensorNames.index(int(tempSensorName)) + 1} will be on.', parent=self.ROOT)
                        #sensorMuscle = defaultAttachments[num]
                        self.sensorDict[int(tempSensorName)].append(sensorMuscle)

                tempSensorKey = list(self.sensorDict.keys())

                print(f"Sensor {self.sensorNames.index(tempSensorKey[num]) + 1} paired")

            # Required otherwise pipeline state doesn't update
            self.TrigBase.ScanSensors()
            for index, sensorName in enumerate(self.TrigBase.GetSensorNames()):
                # Seeing what the actual order of adding sensors is
                self.sensorsScannedOrder.append(sensorName)
                sensorObject = self.TrigBase.GetSensorObject(index)
                self.sensorsScannedOrderCheck.append(sensorObject.Properties.get_Sid())
        
        # Getting Number of Sensors
        self.sensorsFound = len(self.sensorDict.keys())
        
        print("------Sensor List-----")
        # Printing Num of Sensors and Sensor List
        print(f"Sensors Found: {self.sensorsFound}")
        [print(str(sensor) + ': ' + self.sensorDict[sensor][1]) for sensor in self.sensorDict.keys()]

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def scanForSensors(self, defaultAttachments = None):
        # Scanning for Paired Sensors with default settings
        if (defaultAttachments is not None):
            print("Scanning for paired sensors...")
            """Callback to tell the base to scan for any available sensors"""

            # TODO: TEST THIS AGAIN

            # Setting Variable for Default Sensor Configuration
            self.defaultConfiguration = 1

            try:
                f = self.TrigBase.ScanSensors().Result
            except Exception as e:
                print("Scan failed")
                #time.sleep(1)
                self.scanForSensors()

            # Iterating Along Current Sensor Names
            for index, sensorName in enumerate(self.TrigBase.GetSensorNames()):
                # Seeing what the actual order of adding sensors is
                self.sensorsScannedOrder.append(sensorName)

                tempSensorName = sensorName.split(" ")[0]
                if int(tempSensorName) in self.sensorDict.keys():
                    continue
                else:
                    self.sensorDict[int(tempSensorName)] = [index]
                    sensorNameIndex = self.sensorNames.index(int(tempSensorName))
                    sensorMuscle = defaultAttachments[sensorNameIndex]
                    self.sensorDict[int(tempSensorName)].append(sensorMuscle)     

        else:
            print("Scanning for paired sensors...")
            """Callback to tell the base to scan for any available sensors"""
            try:
                f = self.TrigBase.ScanSensors().Result
            except Exception as e:
                print("Scan failed")
                #time.sleep(1)
                self.scanForSensors()

            # Iterating Along Current Sensor Names
            for index, sensorName in enumerate(self.TrigBase.GetSensorNames()):
                # Seeing what the actual order of adding sensors is
                self.sensorsScannedOrder.append(sensorName)

                tempSensorName = sensorName.split(" ")[0]
                if int(tempSensorName) in self.sensorDict.keys():
                    continue
                else:
                    self.sensorDict[int(tempSensorName)] = [index]

                    # Asking user for input
                    sensorMuscle = simpledialog.askstring(title = 'Sensor Muscle Input',
                                                            prompt = 'Please indicate which muscle sensor ' + str(self.sensorNames.index(int(tempSensorName)) + 1) +' is on.', parent=self.ROOT)
                    self.sensorDict[int(tempSensorName)].append(sensorMuscle)

        print(self.sensorsScannedOrder)

        # Getting Number of Sensors
        self.sensorsFound = len(self.sensorDict.keys())
        
        print("------Sensor List-----")
        # Printing Num of Sensors and Sensor List
        print(f"Sensors Found: {self.sensorsFound}")
        [print(str(sensor) + ': ' + self.sensorDict[sensor][1]) for sensor in self.sensorDict.keys()]

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()      

    def pairSensors(self, numSensors):
        self.connectSensors(numSensors)

    def selectAllSensors(self):
        """
        Selects all sensors conencted to the Delsys EMG System for streaming.
        """
        # Selecting all sensors.
        self.TrigBase.SelectAllSensors()

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def selectSensor(self, sensorNum):
        """
        Selects individual sensor at specifided sensor number for streaming.
        NOTE: when refering to sensors, the sensors start at 0.
        """
        try:
            sensorID = self.sensorNames[sensorNum]
            sensorPairOrder = self.sensorDict[sensorID][0]
            self.TrigBase.SelectSensor(sensorPairOrder)

        except Exception as e:
            print(e)
            print(F"Unable to Select Sensor: {sensorNum}")

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def availableSensorModes(self, sensorNum):
        """
        Outputs a string of the current sensor modes available for sensor.
        """
        # Getting sensor modes.
        self.modeList = self.TrigBase.AvailibleSensorModes(sensorNum)
        # Printing sensor mode list.

        for i, mode in enumerate(self.modeList):
            print(f"Mode {i} : {mode}")

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def getCurrentSensorMode(self, sensorNum):
        """
        Will get current sensor mode from sensor sensorNum.
        """
        # Getting current sensor mode.
        print(self.TrigBase.GetCurrentSensorMode(sensorNum))

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def setSampleMode(self, sensorList, sampleMode):
        """
        Setting sensor sensorNum to sampleMode.
        
        Inputs:
            sensorList (int): The list of numbers for the sensors.
            sampleMode (str): The sample mode to be set.

        Sample Mode List can be found in the Delsys Manual folder under
        Delsys Sample Modes.
        """
        for sensorNum in sensorList:
            try:
                sensorID = self.sensorNames[sensorNum]
                sensorPairOrder = self.sensorDict[sensorID][0]
                self.TrigBase.SetSampleMode(sensorPairOrder, sampleMode)
            except Exception as e:
                print(e)
                print("Sensor Mode couldn't be set. SensorNum might be out of bounds of available sensors.")
                print("Additionally, you might be trying to set a sensor to a sample mode it doesn't have.")
                print(f"Sensor: {sensorNum + 1} SampleMode: {sampleMode}")

        print(f"Sample mode of {sensorList} set tp {sampleMode}" )

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def setSampleModeLabView(self, sensorList, sampleMode):
        """
        Setting sensor sensorNum to sampleMode.
        
        Inputs:
            sensorList (int): The list of numbers for the sensors.
            sampleMode (str): The sample mode to be set.

        Sample Mode List can be found in the Delsys Manual folder under
        Delsys Sample Modes.
        """
        # Setting sensor sensorNum to sampleMode. This works for lists.
        for sensorNum in range(len(sensorList)):
            if sensorList[sensorNum] == 1:
                try:
                    sensorID = self.sensorNames[sensorNum]
                    sensorPairOrder = self.sensorDict[sensorID][0] 
                    self.TrigBase.SetSampleMode(sensorPairOrder, sampleMode)
                except Exception as e:
                    print(e)
                    print("Sensor Mode couldn't be set. SensorNum might be out of bounds of available sensors.")

        print(f"Sample mode of {sensorList} set tp {sampleMode}" )

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def setAllSampleModes(self, sampleMode):
        """
        This function will set all sensors to the same sample mode.
        
        Inputs:
            sampleMode (str): The sample mode to be set.
        """
        # Setting all sensors to sampleMode
        for sensorNum in range(self.sensorsFound):
            try:
                self.TrigBase.SetSampleMode(sensorNum, sampleMode)
                # Increase the number of sensors connected for LSL
                self.numSensorsConnected += 1
            except Exception as e:
                print(e)
                print("Sensosr Mode couldn't be set. You may be trying to set a sample mode for a sensor without that sample mode.")
                print(f"Sensor: {sensorNum + 1} SmapleMode: {sampleMode}")

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def configure(self, startTrigger = False, stopTrigger = False):
        """
        Configures the Delsys EMG for streaming. Will set the current pipeline state to armed.
        To enable a start and stop trigger, set the startTrigger and stopTrigger parameters to True.
        Then you can use the IsWaitingForStartTrigger() and IsWaitingForStopTrigger() functions to
        enable and stop streaming.
        """
        # Creating data manager class
        self.DataHandler = DataKernel(self.TrigBase)
        self.DataHandler.packetCount = 0

        # Checking to see if Delsys EMG is in connected state.
        if self.TrigBase.GetPipelineState() == "Connected":
            # Configuring Delsys EMG for streaming.
            self.TrigBase.Configure(starttrigger = startTrigger, stoptrigger = stopTrigger)
            print("Pipeline Armed")
        
            # Updated Pipeline State
            self.status = self.TrigBase.GetPipelineState()
            print(self.status)

            # Creating variables
            self.channelCount = 0
            self.channelNames = []
            self.sampleRates = []
            self.EMGSensors = []
            self.numEMGChannels = 0
            self.samplesPerFrame = [[] for i in range(self.sensorsFound)]
            self.dataSavingSensorDict = {}
            self.collectionOutputOrder = []
            self.defaultMVCIndexer = {}

            # Looping through sensor list
            for sensorNum in range(self.sensorsFound):
                # Selecting sensor object
                selectedSensor = self.TrigBase.GetSensorObject(sensorNum)

                # Getting Sensor ID
                sensorID = selectedSensor.Properties.get_Sid()

                # Creating temp sensor name                
                tempSensorName = f"Sensor {self.sensorNames.index(sensorID) + 1}"
                
                # Checking to see if sensor channels are greated than 0.
                if len(selectedSensor.TrignoChannels) > 0:
                    # Creating temp chanName and sampleRate lists
                    tempChanNameList = []
                    tempSampRateList = []
                    channelSet = set()
                    extra = 1

                    # Looping through num of channels in sensor sensorNum.
                    for channel in range(len(selectedSensor.TrignoChannels)):
                        # Updating Channel Count
                        self.channelCount += 1

                        # Grabbing Sensor Object and Appending Relevant Information
                        channelObject = selectedSensor.TrignoChannels[channel]
                        channelName = channelObject.Name
                        self.channelNames.append(channelName)
                        self.sampleRates.append(channelObject.SampleRate)
                        self.samplesPerFrame.append(channelObject.SamplesPerFrame)

                        # Checking if Channel Already Exists for Saving Purposes
                        if channelName in channelSet:
                            # Creating New Channel Name and Appending to List
                            tempChannelName = f"{channelName}_{extra}"
                            tempChanNameList.append(tempChannelName)
                            extra += 1

                        else:
                            # Appending To Channel List
                            tempChanNameList.append(channelName)
                            channelSet.add(channelName)

                        # Appending Channel Sample Rate to List
                        tempSampRateList.append(channelObject.SampleRate)
                        
                        # Adding Channel ID
                        self.collectionOutputOrder.append(channelObject.Id)

                        # Updating numEMGChannels
                        if 'EMG' in selectedSensor.TrignoChannels[channel].Name:
                            self.numEMGChannels += 1    
                            self.EMGSensors.append(sensorID)
                            self.defaultMVCIndexer[tempSensorName] = self.channelCount - 1

                    # Adding to DataSavingSensorDict
                    self.dataSavingSensorDict[tempSensorName] = {'Channels': tempChanNameList,
                                                             'SampleRates' : tempSampRateList,
                                                             'Attachment' : self.sensorDict[sensorID][1]}

    def startDataCollection(self):
        """
        Starts data collection.
        """
        # Starting Data Collection
        if self.TrigBase.GetPipelineState() == "Armed":
            try:
                self.TrigBase.Start()
                print('Data Collection Started')
            except Exception as e:
                print(e)
                pass
        else:
            print("Pipeline not in armed state.")

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()            

    def getData(self):
        """ Check if data ready from DelsysAPI via Aero CheckDataQueue() - Return True if data is ready
            Get data (PollData)
            Organize output channels by their GUID keys

            Return array of all channel data
        """
        # If Data Is In Queue
        dataReady = self.TrigBase.CheckDataQueue()                      # Check if DelsysAPI real-time data queue is ready to retrieve
        if dataReady:
            # Grabbing Data from TrignoBase
            DataOut = self.TrigBase.PollData()                          # Dictionary<Guid, List<double>> (key = Guid (Unique channel ID), value = List(Y) (Y = sample value)
            outArr = [[] for i in range(len(DataOut.Keys))]
            
            # Iterating Through CollectionOutputOrder
            for j in range(len(self.collectionOutputOrder)):
                # Grabbing Data from Key and Appending to OurArr
                chan_data = DataOut[self.collectionOutputOrder[j]]
                outArr[j].append(list(np.asarray(chan_data, dtype = 'object')))

            return outArr
        else:
            return None

    def processData(self):
        """
        The checkData function outputs a System.Collections.Generic dictionary object. This function
        will clean up the data from the checkData function and output it into a Python dictionary.
        """
        outArr = self.getData()
        if outArr is not None:
            try:
                for i in range(len(outArr[0])):
                    if np.asarray(outArr[0]).ndim == 1:
                        self.data.append(list(np.asarray(outArr, dtype='object')[0]))
                    else:
                        self.data.append(list(np.asarray(outArr, dtype='object')[:, i]))
                try:
                    self.DataHandler.packetCount += len(outArr[0])
                    self.DataHandler.sampleCount += len(outArr[0][0])
                except:
                    pass
                
            except IndexError as e:
                print("Delsys EMG Process data function index error.")
                print(e)

    def stopDataCollection(self):
        """
        Stops data collection.
        """
        # Stopping data collection.
        self.TrigBase.Stop()
        print('Data Collection Complete')

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def resetPipeline(self):
        """
        Resets data pipeline to connected state. This is used when you want to update the current sensors
        paired with the Delsys System.
        """
        # Resetting Pipeline State
        self.TrigBase.ResetPipeline()
        print('Resetting Pipeline State')

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def plotEMG(self):
        """
        Plotting EMG data by taking the average value of data within self.data. Will reset the buffer after each iteration.
        """
        averageEMG = []

        # Looping through self.data
        try:
            if (len(self.data) != 0):
                for i in range(len(self.channelNames)):
                    if "EMG" in self.channelNames[i]:
                        avg_data = np.average(self.data[0][i])
                        averageEMG.append(avg_data)
            else:
                averageEMG.append(np.zeros(self.numEMGChannels))

        except Exception as e:
            print(e)
            averageEMG.append(np.zeros(self.sensorsFound))

        # Resetting Buffer
        self.data = []

        # Returning string formatted EMG data
        return ','.join(map(str, averageEMG))
    
    def plotEMGGUI(self):
        """
        Plotting EMG data by taking the average value of data within self.data. Will reset the buffer after each iteration.
        """
        averageEMG = []
        # emgData = []

        # Looping through self.data
        try:
            if (len(self.data) != 0):
                for i in range(len(self.channelNames)):
                    if "EMG" in self.channelNames[i]:
                        # emgData.append(self.data[0][i])
                        avg_data = np.average(self.data[0][i])
                        averageEMG.append(avg_data)
            else:
                averageEMG = np.zeros(self.numEMGChannels)

        except Exception as e:
            print(e)
            averageEMG = np.zeros(self.sensorsFound)
            pass

        # Resetting Buffer
        self.data = []

        # Returning string formatted EMG data
        return averageEMG
        #return emgData

    def resetBuffer(self):
        # Resetting Data Buffer
        self.data = []

    #-----------------------------------------------------------------------------------
    # ---- MVC Protocol

    def createMVCNorm(self):
        """
        Goes through EMG sensors and creates normalizations values for those sensors.
        """
        # MVC Recording
        self.MVCRecording = True

        # TODO: TEST THIS AGAIN

        # Checking to see if Delsys EMG is in armed state.
        if self.TrigBase.GetPipelineState() == "Armed":
            # Checking if Default Sensor Protocol is Enabled
            if self.defaultConfiguration:
                # Default Sensor Order
                emgSensorList = ['Sensor 8', 'Sensor 7', 'Sensor 6', 'Sensor 5', 'Sensor 4', 'Sensor 2', 'Sensor 3', 'Sensor 1']

            else:
                # Getting Sensors In Configuration That Have EMG Channels
                emgSensorList = self.defaultMVCIndexer.keys()

            # Iterating Through Sensors
            for sensor in emgSensorList:
                # Checking if Sensor in EMG Indexer
                if sensor in self.defaultMVCIndexer:
                    # Exiting Variable
                    self.trialExit = False

                    while self.trialExit == False:
                        # Variables to Hold Max Values
                        maxVoluntaryContraction = float("-inf")
                        MVCData = []

                        # Creating Figure
                        plt.figure()

                        # Creating Indexer To Help With Unsuccessful Trials
                        failedTrials = 0

                        # 3 Trials
                        for trial in range(3):
                            # Grabbing Information
                            attachment = self.dataSavingSensorDict[sensor]['Attachment']
                            self.mvcGUI(sensor, attachment, trial)

                            # Getting Relavent Data and Clearning Buffer
                            try:
                                MVCData.append(self.data[0][self.defaultMVCIndexer[sensor]])

                                # Rectifying and Sorting Acquired Data
                                sortedMVCList = np.sort(np.abs(MVCData[trial - failedTrials] - np.average(MVCData[trial - failedTrials])), kind = 'quicksort')

                                # Computing MVC
                                maxVoluntaryContraction = max(maxVoluntaryContraction, np.average(sortedMVCList[-106:-6]))

                                # Plotting and Asking for Input
                                plt.plot(MVCData[trial - failedTrials])

                            except Exception as e:
                                print(f"Couldnt Process Delsys Data for Trial {trial}: {e}")

                                # Incrementing Failed Trial List
                                failedTrials += 1

                            self.resetBuffer()    

                        # Showing Plot
                        plt.xlabel("Samples")
                        plt.ylabel("Amplitude (mv)")
                        plt.show()

                        # Closing GUI
                        self.exitTrialGUI()

                        # Closing Plot
                        plt.close()

                    # Adding to List and Dictionary
                    self.normalizeList.append(maxVoluntaryContraction)
                    self.normalizeDict[sensor] = maxVoluntaryContraction
                        
            # Setting Status of Normalization to True
            self.normalize = True

        else:
            print("System Not Armed")

    def mvcGUI(self, sensor, attachment, trial):
        """
        Tkinter GUI for MVC
        """
        # Trial Numer
        self.trialNumber = trial + 1
        self.trialCounter = 0

        # Loading Dialog Box With Instructions
        self.root = tk.Tk()
        self.root.title("MVC Calulcation")

        # Setting Dimensions and Color
        self.root.geometry("350x250")
        self.root.configure(bg = "#f5e1fd")
        self.root.eval('tk::PlaceWindow . center')

        # Trial Number Label
        self.trialLabel = tk.Label(self.root, text = f"Trial {self.trialNumber}", font = ("Arial", 20, "bold"))
        self.trialLabel.pack(side=tk.TOP, pady=(25,0))

        # Create a Label
        self.label = tk.Label(self.root, text = f"Ready for MVC of {sensor} : {attachment}?", font = ("Arial", 14))
        self.label.pack(side=tk.TOP, pady=(50, 0))

        # Creating Button
        self.button = tk.Button(self.root, text = "Ready!", command = self.startMVCSequence, font = ("Arial", 14))
        self.button.pack(side=tk.BOTTOM, pady=(0, 50))

        # Running Event
        # self.root.mainloop()
        self.root.wait_window(self.root)

    def startMVCSequence(self):
        """
        Starting Sequence for MVC Trial
        """
        # Removing Button
        self.button.pack_forget()

        # Adding Additional Label
        self.countLabel = tk.Label(self.root, text = "", font = ("Arial", 14))
        self.countLabel.pack(side=tk.BOTTOM, pady=(0, 50))

        # Data Loop
        self.MVCDataLoop()

    def MVCDataLoop(self):
        """
        Data processing loop for EMG MVC protocol.
        """
        # Preparation Time
        if self.trialCounter <= 3:
            if self.trialCounter == 2: 
                # Starting Data Collection
                self.startDataCollection()

            # Updating GUI Components
            self.countLabel.config(text = f"Prepare to Flex in {3 - self.trialCounter}...")

            # Updating Trial Counter
            self.trialCounter += 1

            # Proceeding in GUI
            self.root.after(1000, self.MVCDataLoop)

        # Flex Time
        elif self.trialCounter <= 8:
            # Updating GUI Components
            self.countLabel.config(text = f"FLEX FLEX FLEX for {8 - self.trialCounter}...")

            # Updating Trial Counter
            self.trialCounter += 1
            
            # Proceeding in GUI
            self.root.after(1000, self.MVCDataLoop)

        # Resting Time
        elif self.trialCounter <= 18:
            # Updating GUI Components
            self.countLabel.config(text = f"Rest for {18 - self.trialCounter}...")

            # Processing and Stop Command
            if self.trialCounter == 9:
                # Try Processing Data
                try:
                    self.processData()
                except Exception as e:
                    print(e)
                    print("Could not process flex MVC data.")

                # Stopping Data Collection
                self.stopDataCollection()

            # Updating Trial Counter
            self.trialCounter += 1

            # Proceeding in GUI
            self.root.after(1000, self.MVCDataLoop)

        # Quit Time
        else:
            # Updating GUI Components
            self.countLabel.config(text = f"Trial {self.trialNumber} Completed")

            # Closing GUI
            self.root.after(1000, self.root.destroy())

    def exitTrialGUI(self):
        """
        Tkinter Exit GUI
        """
        # Loading Dialog Box With Instructions
        self.root = tk.Tk()
        self.root.title("MVC Exit")

        # Setting Dimensions and Color
        self.root.geometry("350x250")
        self.root.configure(bg = "#f5e1fd")
        self.root.eval('tk::PlaceWindow . center')

        # Trial Number Label
        self.MVCQuestion = tk.Label(self.root, text = "Close or Redo MVC?", font = ("Arial", 20, "bold"))
        self.MVCQuestion.pack(side=tk.TOP, pady=(25,0))

        # Creating Button
        self.closeButton = tk.Button(self.root, text = "Close!", command = self.closeMVCSequence, font = ("Arial", 14))
        self.closeButton.pack(side=tk.LEFT, padx=(50, 50))

        # Creating Button
        self.redoButton = tk.Button(self.root, text = "Redo!", command = self.redoMVCSequence, font = ("Arial", 14))
        self.redoButton.pack(side=tk.RIGHT, padx=(50, 50))

        # Running Even
        self.root.wait_window(self.root)

    def closeMVCSequence(self):
        self.trialExit = True
        self.root.after(1000, self.root.destroy)

    def redoMVCSequence(self):
        self.root.after(1000, self.root.destroy)
