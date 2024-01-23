import platform
import sys

# Adding path for current computer
# Please add your computer name and path to the Python API folder for delsys.
if (platform.node() == "Garangatan_Comp"):
    sys.path.insert(0, "C:/Users/grang/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/XSENSOR/xscore-x4/wrappers/python")
elif (platform.node() == "Sonny_ThinkPad"):
    sys.path.insert(0, "C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/XSENSOR/xscore-x4/wrappers/python")
elif (platform.node() == 'Purkinje'):
    sys.path.insert(0, "C:/Users/Purkinje/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/XSENSOR/xscore-x4/wrappers/python")
elif (platform.node() == "Sonny-GamingPC"):
    sys.path.insert(0, "C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/XSENSOR/xscore-x4/wrappers/python")

import ctypes
import xscore
import time
import numpy as np

class XSensorForce:
    """
    This is a wrapper class for the XSensor Force Sensing Insoles X4. This is intended to work with the Force Insoles
    and their code. You will need to purchase a copy of their code to work with this class. This class is used to connect,
    communicate, and get data from XSensor Insoles.

    Author: Sonny Jones & Grange Simpson
    Version: 2023.11.17

    Usage:

        XSensorForce = XSensorForce()
    
    """
    def __init__(self, recordingRate = 10, enableIMU = False, allowX4 = True, wirelessX4 = True):
        """
        XSensors default to wireless communication.
        """
        # Initialize the DLL library
        self.xscore = xscore
        self.xscore.XS_InitLibrary()

        # Buffers
        self.dataBuffer = []
        self.allCollectionDataBuffer = []
        self.frameNumber = 0

        # pre-define some variables to hold data from the DLL.
        self.sensorPID = 0
        self.sensorIndex = 0
        self.senselRows = ctypes.c_ushort()
        self.senselColumns = ctypes.c_ushort()
        self.senselDimHeight = ctypes.c_float()
        self.senselDimWidth = ctypes.c_float()

        self.sampleYear = ctypes.c_ushort()
        self.sampleMonth = ctypes.c_ubyte()
        self.sampleDay = ctypes.c_ubyte()
        self.sampleHour = ctypes.c_ubyte()
        self.sampleMinute = ctypes.c_ubyte()
        self.sampleSecond = ctypes.c_ubyte()
        self.sampleMillisecond = ctypes.c_ushort()
        self.sampleMicrosecond = ctypes.c_ushort()
        self.localTime = False

        self.prevsampleMinute = ctypes.c_ubyte()
        self.prevsampleMinute.value = 0
        self.prevsampleSecond = ctypes.c_ubyte()
        self.prevsampleSecond.value = 0
        self.prevsampleMillisecond = ctypes.c_ushort()
        self.prevsampleMillisecond.value = 0

        self.pressureUnits = ctypes.c_ubyte()

        # IMU test
        self.qx = ctypes.c_float()
        self.qy = ctypes.c_float()
        self.qz = ctypes.c_float()
        self.qw = ctypes.c_float()
        self.ax = ctypes.c_float()
        self.ay = ctypes.c_float()
        self.az = ctypes.c_float()
        self.gx = ctypes.c_float()
        self.gy = ctypes.c_float()
        self.gz = ctypes.c_float()

        # hardware frame state
        self.hwSequence = ctypes.c_uint()
        self.hwTicks = ctypes.c_uint()

        self.pressure = ctypes.c_float() # pressure values only

        self.minPressureRange = ctypes.c_float()
        self.maxPressureRange = ctypes.c_float()

        self.wMajor = ctypes.c_ushort()
        self.wMinor = ctypes.c_ushort()
        self.wBuild = ctypes.c_ushort()
        self.wRevision = ctypes.c_ushort()

        self.nameBufferSize = ctypes.c_uint()

        # Configuration status
        self.connected = False

        # Data Saving File Structure
        self.dataSavingSensorDict = None
        self.tempChanList = ['Pressure']

        # query the DLL version (for XSENSOR support reference)
        self.xscore.XS_GetVersion(ctypes.byref(self.wMajor), ctypes.byref(self.wMinor), ctypes.byref(self.wRevision), ctypes.byref(self.wBuild))

        sVersion = 'DLL Version: ' + str(self.wMajor.value) + '.' + repr(self.wMinor.value) + '.' + repr(self.wRevision.value) + '.' + repr(self.wBuild.value) + '\n'
        print (sVersion)

        # Set a calibration cache folder. The DLL will download calibration files from the sensor and
        # place them in this folder. This will speed up enumeration on subsequent calls.
        # This call is optional, but recommended. You must also supply a valid path, or more specifically
        # a path with WRITE permissions.

        sCalCacheFolder = "C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/XSENSOR\Cache"
        self.xscore.XS_SetCalibrationFolderUTF8(sCalCacheFolder.encode('utf-8'))
        # xscore.XS_SetCalibrationFolder(sCalCacheFolder)

        self.targetRateHz = recordingRate # Hz

        self.enableIMU = enableIMU
        self.allowX4 = allowX4
        self.wirelessX4 = wirelessX4

        if self.allowX4:
            if self.wirelessX4:
                self.xscore.XS_SetAllowX4Wireless(True)

            # Use the following call with xTRUE if you are connecting to the sensors over USB wire
            if not self.wirelessX4:
                self.xscore.XS_SetAllowX4Wired(True)
            # If you use BOTH XS_SetAllowX4Wireless(xTRUE) and XS_SetAllowX4(xTRUE) at the same time, the DLL will favour USB wired over wireless.

            # Use 8 bit mode when transmitting over Bluetooth wireless to ensure higher framerates
            if self.wirelessX4:
                self.xscore.XS_SetX4Mode8Bit(True)

            self.xscore.XS_SetAcquisitionCycles(4) # 4 or 8 for X4 sensors. smaller number is faster, but with slightly worse signal-to-noise

            # if you're testing X4 insole sensor, you can use this
            if self.enableIMU:
                self.xscore.XS_SetEnableIMU(True) # if we want IMU data with each frame

        else:
            self.enableIMU = False # not supported by X3

            # 1, 2, 4, 8 for X3 sensors. smaller number is faster, but with slightly worse signal-to-noise
            self.xscore.XS_SetAcquisitionCycles(1)

    def configure(self):
        # Creating Saving Dictionary 
        self.dataSavingSensorDict = {}

        # Ask the DLL to scan the computer for attached sensors.
        self.xscore.XS_EnumSensors()
        self.numSensors = self.xscore.XS_EnumSensorCount()

        # Fetch last enum state. Examine this if no sensors are found. Look up EEnumerationError in xscore.py
        # The returned value might have a combination of the bits set from EEnumerationError.
        self.lastEnumState = self.xscore.XS_GetLastEnumState()

        sMesg = 'Found ' + str(self.numSensors) + ' sensors; ' + 'Last Enumeration State: ' + str(self.lastEnumState) + '\n'
        print (sMesg)

        # Build a sensor configuration. The DLL must be told which sensors to use.
        if self.numSensors > 0:
            sMesg = 'Building sensor configuration...'
            print (sMesg)
            self.sensorIndex = 0
            
            # This will automatically configure all sensors on the computer
            if self.xscore.XS_AutoConfig() == True:
            
                nbrSensors = self.xscore.XS_ConfigSensorCount()
                sMesg = 'Configured ' + str(nbrSensors) + ' sensors\n'
                print (sMesg)

                self.sPressureUnits = str(self.xscore.EPressureUnit.ePRESUNIT_PSI)
                self.pressureUnits = ctypes.c_ubyte(self.xscore.EPressureUnit.ePRESUNIT_PSI.value)
                self.xscore.XS_SetPressureUnit(ctypes.c_ubyte(self.xscore.EPressureUnit.ePRESUNIT_PSI.value))

        # Inspect the configured sensor(s) - this is for reference only
        while self.sensorIndex < self.numSensors:
            # fetch the sensors product ID - this is needed by some functions
            sensorPID = self.xscore.XS_ConfigSensorPID(self.sensorIndex)
            
            # fetch the sensor serial number. This is for reference only
            serialNbr = self.xscore.XS_SerialFromPID(sensorPID)

            # determine how many rows and columns this sensor has
            self.xscore.XS_SensorDimensions(sensorPID, ctypes.byref(self.senselRows), ctypes.byref(self.senselColumns))
            
            # determine the measurement dimensions of a single sensor cell (called a Sensel)
            self.xscore.XS_SenselDims(sensorPID, ctypes.byref(self.senselDimWidth), ctypes.byref(self.senselDimHeight))

            # fetch the buffer size for the sensor name buffer
            self.xscore.XS_SensorNameUTF8(sensorPID, ctypes.byref(self.nameBufferSize), None)
            
            # construct a buffer for the name
            nameBuff = (ctypes.c_char*(self.nameBufferSize.value))()

            # retrieve the name as a UTF8 string
            self.xscore.XS_SensorNameUTF8(sensorPID, ctypes.byref(self.nameBufferSize), ctypes.byref(nameBuff))
            sensorName = str(nameBuff.value.decode('utf-8'))

            # Setting up Data Saving Dictionary
            tempName = f'Foot {self.sensorIndex}'
            if sensorName.split('-')[2] == 'LF':
                tempSensorOrientation = 'Left'
            elif sensorName.split('-')[2] == 'RF':
                tempSensorOrientation = 'Right'

            self.dataSavingSensorDict[tempName] = {'Channels' : self.tempChanList,
                                                   'SampleRates' : [self.targetRateHz],
                                                   'Foot' : tempSensorOrientation}

            sMesg = '\tSensor Info PID ' + str(sensorPID) + '; Serial S' + str(serialNbr) + '; [' + sensorName + ']'
            print (sMesg)
            sMesg = '\tRows ' + str(self.senselRows.value) + '; Columns ' + str(self.senselColumns.value)
            print (sMesg)
            sMesg = '\tWidth(cm) {:0.3f}'.format(float(self.senselColumns.value) * self.senselDimWidth.value) + '; Height(cm) {:0.3f}'.format(float(self.senselRows.value) * self.senselDimHeight.value) + '\n'
            print (sMesg)

            # fetch the current calibration range of the sensor (calibrated min/max pressures)
            self.xscore.XS_GetConfigInfo(self.pressureUnits, ctypes.byref(self.minPressureRange), ctypes.byref(self.maxPressureRange))
            sMesg = '\tMin pressure {:0.4f} '.format(float(self.minPressureRange.value)) + self.sPressureUnits + ' Max pressure {:0.4f} '.format(float(self.maxPressureRange.value)) + self.sPressureUnits
            print (sMesg)

            exec(f"self.dataBuffer{self.sensorIndex} = []")

            # Creating dataBuffer object
            self.dataBuffer.append([np.zeros(self.senselRows.value * self.senselColumns.value)])
            
            self.sensorIndex = self.sensorIndex + 1
            
    def connect(self):
        # Initiating Connection
        if (self.xscore.XS_OpenConfig() == True) and (self.xscore.XS_StartRecord(self.targetRateHz) == True):
            self.connected = True
            print('XSensor Connection Established')

            # Printing sensorDict
            print(self.dataSavingSensorDict.keys())
            for key, value in self.dataSavingSensorDict.items():
                print(f"{key} : {value}")

            return True
        else:
            print("XSensor Connection Failed")
            return False

    def processData(self):
        """
        Data processing function for XSensor. Needs to be called from a loop, each call is one frame. 
        """
        # Checking connection
        if (self.connected == True):
            # Checking If Sample is Available
            if self.xscore.XS_Sample() == True:
                # Checking Timestamp of Last Sample
                try:
                    self.xscore.XS_GetSampleTimeUTC(ctypes.byref(self.sampleYear), ctypes.byref(self.sampleMonth), ctypes.byref(self.sampleDay), ctypes.byref(self.sampleHour), ctypes.byref(self.sampleMinute), ctypes.byref(self.sampleSecond), ctypes.byref(self.sampleMillisecond), ctypes.byref(self.sampleMicrosecond), self.localTime)
                except:
                    pass

                # Checking time sample against last time sample
                if ((self.sampleMinute.value == self.prevsampleMinute.value) and (self.sampleSecond.value == self.prevsampleSecond.value) and (self.sampleMillisecond.value == self.prevsampleMillisecond.value)):
                    return
                
                self.prevsampleMinute.value = self.sampleMinute.value
                self.prevsampleSecond.value = self.sampleSecond.value
                self.prevsampleMillisecond.value = self.sampleMillisecond.value
        
            # Going through Frames
            for sensor in range(self.numSensors):
                # Fetching Sensor ID
                sensorPID = self.xscore.XS_ConfigSensorPID(sensor)
                # need the sensor dimensions to pre-allocate some buffer space
                self.xscore.XS_SensorDimensions(sensorPID, ctypes.byref(self.senselRows), ctypes.byref(self.senselColumns))
                # Constructing Buffer
                frameBuffer = (ctypes.c_float*(self.senselRows.value*self.senselColumns.value))()

                # Retrieving Frame
                if self.xscore.XS_GetPressure(sensorPID, ctypes.byref(frameBuffer)) == 1:
                    # Dump Frame
                    self.dataBuffer[sensor] = frameBuffer

            # Appending Data to All Collection Data Buffer
            self.allCollectionDataBuffer.append(self.dataBuffer)        

    def stopDataCollection(self):
        """
        Stop data collection.
        """
        #self.connected = False

        # Resetting Buffer
        self.dataBuffer = []

    def releaseConfig(self):
        """
        Releasing XSensor Configuration
        """
        self.xscore.XS_StopRecord()
        self.xscore.XS_CloseConfig()
        self.xscore.XS_ReleaseConfig()

    def quit(self):
        """
        Exiting and releasing .dll
        """
        self.xscore.XS_ExitLibrary()
 