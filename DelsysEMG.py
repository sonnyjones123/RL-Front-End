import sys
import platform
import numpy as np

import clr
clr.AddReference("System.Collections")

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

class DelsysEMG:
    """
    This is a wrapper class for the Delsys EMG System. This is inteneded to work with
    the Delsys TrignoBase EMG system and API. You will need to install all the dependencies
    and Delsys API software from their Github. The link to the Delsys Github Repository is
    below. 

    https://github.com/delsys-inc/Example-Applications/tree/main

    This class will interface with their API and will collect and store information obtained
    from the base. This class can also be used to conenct sensors, start and stop data collection,
    etc.  

    Author: Sonny Jones & Grange Simpson

    Usage:

    1. Create an instance of this class.
        DelsysEMG = DelsysEMG()
    """
    def __init__(self):
        # Key and License are obtained from Delsys. You may want to reach out to them for 
        # a new key and license if the following no longer work. 
        self.key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABCs6LASqvLpxqpvzLA8QbLmUDDDlOqD54JhLUEadv+oAgG8JVVDtI0qMO2V2PQiXoKsY33+ea/Jtp12wDA3847g="
        self.license = "<License>  <Id>756caf49-ab7f-407f-970e-89f5933fa494</Id>  <Type>Standard</Type>  <Quantity>10</Quantity>  <LicenseAttributes>    <Attribute name='Software'></Attribute>  </LicenseAttributes>  <ProductFeatures>    <Feature name='Sales'>True</Feature>    <Feature name='Billing'>False</Feature>  </ProductFeatures>  <Customer>    <Name>Sonny Jones</Name>    <Email>sonny.jones@utah.edu</Email>  </Customer>  <Expiration>Fri, 05 Sep 2031 04:00:00 GMT</Expiration>  <Signature>MEUCIDx5YfJ4042zldgXWz+IJi//Z+ZQQ0b0LZoYIjcRm3BvAiEAjXJD2kb1fLqcFLD7/fAOoWOjRHANREyQwjDpDlaLYOg=</Signature></License>"
        self.data = []
        self.sensorNames = [75503, 75548, 75596, 75587, 75467, 75672, 75641, 75461, 75148, 75268, 75247, 75406]
        self.sensorDict = {}
        self.numSensors = 16
        self.status = "Off"

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

        # Printing Current Status
        print(f"Current Status: {self.status}")

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
            
            # Adding sensorNames and sensorNum to dict
            for sensorName in self.TrigBase.GetSensorNames():
                if sensorName in self.sensorDict.keys():
                    pass
                else:
                    tempSensorName = sensorName.split(" ")[0]
                    self.sensorDict[int(tempSensorName)] = [num]

                    # Asking user for input
                    sensorMuscle = input("RESPONSE REQUESTED: Please indicate which muscle this sensor is on.\n")
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
        [print(sensor) for sensor in self.sensorDict.keys()]

    def selectAllSensors(self):
        """
        Selects all sensors conencted to the Delsys EMG System for streaming.
        """
        # Selecting all sensors.
        self.TrigBase.SelectAllSensors()

    def selectSensor(self, sensorNum):
        """
        Selects individual sensor at specifided sensor number for streaming.
        NOTE: when refering to sensors, the sensors start at 0.
        """
        # Selecting individual sensor at index sensor_num.
        self.TrigBase.SelectSensor(sensorNum)

    def availableSensorModes(self, sensorNum):
        """
        Outputs a string of the current sensor modes available for sensor.
        """
        # Getting sensor modes.
        self.modeList = self.TrigBase.AvailibleSensorModes(sensorNum)
        # Printing sensor mode list.

        for i, mode in enumerate(self.modeList):
            print(f"Mode {i} : {mode}")

    def getCurrentSensorMode(self, sensorNum):
        """
        Will get current sensor mode from sensor sensorNum.
        """
        # Getting current sensor mode.
        print(self.TrigBase.GetCurrentSensorMode(sensorNum))

    def setSampleMode(self, sensorList, sampleMode):
        """
        Setting sensor sensorNum to sampleMode.
        
        Inputs:
            sensorNum (int): The list of numbers for the sensors.
            sampleMode (str): The sample mode to be set.

        Sample Mode List can be found in the Delsys Manual folder under
        Delsys Sample Modes.
        """
        # Setting sensor sensorNum to sampleMode. This works for lists.
        for sensorNum in range(len(sensorList)):
            if sensorList[sensorNum] == 1:
                try:
                    sensorId = self.sensorNames[sensorNum]
                    sensorPairOrder = self.sensorDict[sensorId][0] 
                    self.TrigBase.SetSampleMode(sensorPairOrder, sampleMode)
                except:
                    print("Sensor Mode couldn't be set. SensorNum might be out of bounds of available sensors.")

    def setAllSampleModes(self, sampleMode):
        """
        This function will set all sensors to the same sample mode.
        
        Inputs:
            sampleMode (str): The sample mode to be set.
        """
        # Setting all sensors to sampleMode
        for sensorNum in range(self.sensorsFound):
            self.TrigBase.SetSampleMode(sensorNum, sampleMode)

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
            self.samplesPerFrame = [[] for i in range(self.sensorsFound)]

            # Looping through sensor list
            for sensorNum in range(self.sensorsFound):
                # Selecting sensor object
                selectedSensor = self.TrigBase.GetSensorObject(sensorNum)
                # Checking to see if sensor channels are greated than 0.
                if len(selectedSensor.TrignoChannels) > 0:
                    # Looping through num of channels in sensor sensorNum.
                    for channel in range(len(selectedSensor.TrignoChannels)):
                        self.channelCount += 1
                        self.DataHandler.allcollectiondata.append([])
                        self.channelNames.append(selectedSensor.TrignoChannels[channel].Name)
                        self.sampleRates.append(selectedSensor.TrignoChannels[channel].SampleRate)
                        self.samplesPerFrame.append(selectedSensor.TrignoChannels[channel].SamplesPerFrame)

    def startDataCollection(self):
        # Starting Data Collection
        if self.TrigBase.GetPipelineState() == "Armed":
            try:
                self.TrigBase.Start()
                print('Data Collection Started')
            except:
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
            except IndexError:
                pass

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
            print(e)
            averageEMG.append(np.zeros(self.sensorsFound))

        # Resetting Buffer
        self.data = []

        # Returning string formatted EMG data
        return ','.join(map(str, averageEMG))