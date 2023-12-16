import sys
import platform
import numpy as np
import clr
import tkinter as tk
import threading


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
# from RLDependencies.DelsysLSLSender import *
# from RLDependencies.DelsysLSLReceiver import *

class DelsysEMG:
    """
    This is a wrapper class for the Delsys EMG System. This is inteneded to work with
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
    Version: 2023.11.10

    Usage:

        DelsysEMG = DelsysEMG()

    """
    def __init__(self):
        # Key and License are obtained from Delsys. You may want to reach out to them for 
        # a new key and license if the following no longer work. 
        self.key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABCs6LASqvLpxqpvzLA8QbLmUDDDlOqD54JhLUEadv+oAgG8JVVDtI0qMO2V2PQiXoKsY33+ea/Jtp12wDA3847g="
        self.license = "<License>  <Id>756caf49-ab7f-407f-970e-89f5933fa494</Id>  <Type>Standard</Type>  <Quantity>10</Quantity>  <LicenseAttributes>    <Attribute name='Software'></Attribute>  </LicenseAttributes>  <ProductFeatures>    <Feature name='Sales'>True</Feature>    <Feature name='Billing'>False</Feature>  </ProductFeatures>  <Customer>    <Name>Sonny Jones</Name>    <Email>sonny.jones@utah.edu</Email>  </Customer>  <Expiration>Fri, 05 Sep 2031 04:00:00 GMT</Expiration>  <Signature>MEUCIDx5YfJ4042zldgXWz+IJi//Z+ZQQ0b0LZoYIjcRm3BvAiEAjXJD2kb1fLqcFLD7/fAOoWOjRHANREyQwjDpDlaLYOg=</Signature></License>"
        self.data = []
        # sensorNames = [Trigno Avanti: 1 - 12, Trigno EKG: 13, Trigno Avanti Goniometer: 14 - end]
        self.sensorNames = [75503, 75548, 75596, 75587, 75467, 75672, 75641, 75461, 75148, 75268, 75247, 75406, 69065, 69657, 69699]
        self.sensorDict = {}
        self.numSensors = 16
        self.numSensorsConnected = 0
        self.status = "Off"

        # Text Input Box
        self.ROOT = tk.Tk()
        self.ROOT.withdraw()

        # LSL objects to be filled in when configure is pressed.
        self.LSLSender = 0
        self.LSLReceiver = 0

        # Sample Mode List
        self.sampleModeList = ['EMG plus gyro (+/- 2000 dps), +/-5.5mV, 20-450Hz', 
                               'EKG raw (2148 Hz), skin check (74 Hz), +/-5.5mV, 2-30Hz',
                               'EKG raw (2148 Hz), skin check (74 Hz), +/-11mv, 2-30Hz',
                               'SIG raw x4 (519Hz) (x1813)']

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
    
    def connectSensors(self, numSensors):
        """
        Connects sensors to the Delsys EMG system.

        To connect the sensors, the function runs through the TrigBase.PairSensor()
        command. This will put the system in pairing mode and will continue running
        until a sensor is paired. We can continue to pair additional sensors after.
        Sensors will quickly flash green when pairing is successful. Alternating 
        green and yellow flashing indicates waiting status.
        """
    
        print("Starting Sensor Pairing...")
        print("Awaiting Sensor Pair Request...")

        # Looping through num of sensors
        for num in range(int(numSensors)):
            # Calling Pairing Function
            self.TrigBase.PairSensor()
            # CheckPairStatus will be false when sensor is paired
            while self.TrigBase.CheckPairStatus():
                continue
            
# Need to check why adding 1 sensors on accident multiple times causes errors 

            # Adding sensorNames and sensorNum to dict
            for sensorName in self.TrigBase.GetSensorNames():
                tempSensorName = sensorName.split(" ")[0]
                if int(tempSensorName) in self.sensorDict.keys():
                    continue
                else:
                    self.sensorDict[int(tempSensorName)] = [num]

                    # Asking user for input
                    # sensorMuscle = input("RESPONSE REQUESTED: Please indicate which muscle this sensor is on.\n")
                    sensorMuscle = simpledialog.askstring(title = 'Sensor Muscle Input',
                                                          prompt = 'Please indicate where this sensor is on.', parent=self.ROOT)
                    self.sensorDict[int(tempSensorName)].append(sensorMuscle)

            tempSensorKey = list(self.sensorDict.keys())
            print(f"Sensor {self.sensorNames.index(tempSensorKey[num]) + 1} paired")

        # Scanning for Paired Sensors
        print("Scanning for paired sensors...")
        self.TrigBase.ScanSensors()

        # Getting Number of Sensors
        self.sensorsFound = len(self.sensorDict.keys())
        
        print("------Sensor List-----")
        # Printing Num of Sensors and Sensor List
        print(f"Sensors Found: {self.sensorsFound}")
        [print(str(sensor) + ': ' + self.sensorDict[sensor][1]) for sensor in self.sensorDict.keys()]

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

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
        # Selecting individual sensor at index sensor_num.
        self.TrigBase.SelectSensor(sensorNum)

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
            except:
                print("Sensor Mode couldn't be set. SensorNum might be out of bounds of available sensors.")

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
                    # Increase the number of sensors connected for LSL
                except:
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
            self.TrigBase.SetSampleMode(sensorNum, sampleMode)
            # Increase the number of sensors connected for LSL
            self.numSensorsConnected += 1

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
        self.DataHandler.allcollectiondata = [[]]

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
            self.DelsysLSLSensorDict = {}

            # Looping through sensor list
            for sensorNum in range(self.sensorsFound):
                # Sensor Index
                tempSensorName = f"Sensor: {sensorNum + 1}"
                # Selecting sensor object
                selectedSensor = self.TrigBase.GetSensorObject(sensorNum)
                # Checking to see if sensor channels are greated than 0.
                if len(selectedSensor.TrignoChannels) > 0:
                    # Temp Sensor Channel List
                    tempChannelList = []
                    # Looping through num of channels in sensor sensorNum.
                    for channel in range(len(selectedSensor.TrignoChannels)):
                        self.channelCount += 1
                        self.DataHandler.allcollectiondata.append([])
                        self.channelNames.append(selectedSensor.TrignoChannels[channel].Name)
                        tempChannelList.append(selectedSensor.TrignoChannels[channel].Name)
                        self.sampleRates.append(selectedSensor.TrignoChannels[channel].SampleRate)
                        self.samplesPerFrame.append(selectedSensor.TrignoChannels[channel].SamplesPerFrame)

                        # Updating numEMGChannels
                        if 'EMG' in selectedSensor.TrignoChannels[channel].Name:
                            self.numEMGChannels += 1    
                            self.EMGSensors.append(list(self.sensorDict.keys())[sensorNum])

                        # Adding Sensor and Channel List to Dict
                        self.DelsysLSLSensorDict[tempSensorName] = tempChannelList        

    def startDataCollection(self):
        # Starting Data Collection
        if self.TrigBase.GetPipelineState() == "Armed":
            try:
                self.TrigBase.Start()
                print('Data Collection Started')
            except Exception as e:
                print(342)
                print(e)
                pass
        else:
            print("Pipeline not in armed state.")

        # Updating Pipeline State
        self.status = self.TrigBase.GetPipelineState()

    def getData(self):
        """
        Checking data queue for incoming data packets. If there are data packets, will update 
        our current data buffer with the incoming data packets.
        """    
        # Checking Data Queue
        dataReady = self.TrigBase.CheckDataQueue()
        if dataReady:
            DataOut = self.TrigBase.PollData()
            outArr = [[] for i in range(len(DataOut.Keys))]
            keys = []
            for i in DataOut.Keys:
                keys.append(i)
            for j in range(len(DataOut.Keys)):
                outBuf = DataOut[keys[j]]
                outArr[j].append(np.asarray(outBuf, dtype='object'))
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
            for i in range(len(outArr)):
                self.DataHandler.allcollectiondata[i].extend(outArr[i][0].tolist())
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
                        
                # Send data off through LSL
                dataToSend = np.array([])
                dataColumnIterator = 0
                # Take self.data and save to a file
                if len(self.data) != 0:
                    for i in range(len(self.channelNames)):
                        if "EMG" in self.channelNames[i]:
                            if dataColumnIterator == 0:
                                dataToSend = self.data[0][i]
                            else:
                                dataToSend = np.dstack((dataToSend, self.data[0][i]))
                            dataColumnIterator += 1

                # Sending data over LSL
                # self.LSLSender.sendLSLData(dataToSend)
                
                # print(received_data)
                
            except IndexError as e:
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
                averageEMG.append(np.zeros(self.sensorsFound))

        except Exception as e:
            print(453)
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
                averageEMG = np.zeros(self.sensorsFound)
                pass

        except Exception as e:
            print(480)
            print(e)
            averageEMG = np.zeros(self.sensorsFound)
            pass

        # Resetting Buffer
        self.data = []

        # Returning string formatted EMG data
        return averageEMG
        #return emgData
    
    def returnAllData(self):
        return self.DataHandler.allcollectiondata