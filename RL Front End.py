"""
This is the main Reinforcement Learning GUI that incorperates the DelsyEMG control class, EMGPlot class, 
and XSensor Control Class. This GUI is used to control each data acqusition device and create a pipeline for saving data in real time.

Written by Sonny Jones & Grange Simpson
Version: 2024.07.17

Usage: Run the file.

"""

import os
import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6 import QtTest
from functools import partial
from datetime import date
import numpy as np
import queue

from RLDependencies.EMGPlot import *
from RLDependencies.DelsysEMG import *
from RLDependencies.OpenCVWidget import *
from RLDependencies.XSensorWidget import *
from RLDependencies.DataFileHandler import *
from RLDependencies.DataCommandSender import *
from RLDependencies.NoteTakingWidget import *
from RLDependencies.RLWidget import *
import threading

class FileSaverWorker(threading.Thread):
    def __init__(self, queue, handler):
        super().__init__()
        self.queue = queue
        self.running = True
        self.dataHandler = handler

    def run(self):
        # Loop for Running
        while self.running:
            try:
                # Getting Task
                task = self.queue.get()

                # Stop Statement
                if task is None:
                    break

                try:
                    # Getting Function Name and Params
                    function = task['function']
                    params = task.get('params', {})

                    # Calling Function from DataFileHandler
                    func = getattr(self.dataHandler, function)
                    func(**params)

                finally:
                    # Task Done Signal
                    self.queue.task_done()
            
            except queue.Empty:
                pass

            except Exception as e:
                print(f"Error processing : {function, params}")

    def stop(self):
        # Adding Stop To Queue
        self.running = False
        self.queue.put(None)

class RLFrontEnd(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        # Option for Threaded Data Saving
        self.DataFileHandler = DataFileHandler()
        self.threadedDataSaver = True

        # If Threaded Data Saver is Enabled
        if self.threadedDataSaver == True:
            # Creating Queue and Worker
            self.queue = queue.Queue()
            self.worker = FileSaverWorker(self.queue, self.DataFileHandler)
            self.worker.start()            
        
        # Recording Params
        self.recording = False
        self.filePlot = True
        self.recordingRate = 30 # Loop in ms, 10 ms = 100 Hz

        # Creating Central Widget
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("Data Collection GUI")
        self.setStyleSheet("background-color:#f5e1fd;")

        # Creating SubWidgets
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        collectionLayout = QVBoxLayout()

        # Component Control
        controlAndNotes = QVBoxLayout()
        controlAndNotes.setAlignment(Qt.AlignLeft)
        self.componentControl = self.componentController()
        controlAndNotes.addWidget(self.componentControl, alignment = Qt.AlignTop)

        # Note Taker
        self.saveLocation = "C:/Users/Purkinje/Box/NeuroRoboticsLab/NERVES Lab/Project Groups/ML Gait/Experimental Data/"

        self.noteTaker = NoteTakerWidget(self.saveLocation)
        controlAndNotes.addWidget(self.noteTaker)
        layout.addLayout(controlAndNotes)

        # ML Controller
        self.MLControl = RLWidget(self.recordingRate)
        layout.addWidget(self.MLControl, alignment = Qt.AlignTop)

        # Delsys EMG
        self.DelsysEMG = DelsysEMG() 
        self.DelsysButtonPanel = self.delsysButtonPanel()
        self.splitter.addWidget(self.DelsysButtonPanel)
        self.EMGPlot = None

        # Video Capture
        # self.videoCapture = VideoWidget(recordingRate = self.recordingRate)
        # self.splitter.addWidget(self.videoCapture)
        collectionLayout.addWidget(self.splitter)

        # XSensor
        self.xSensorWidget = XSensorWidget(recordingRate = self.recordingRate)
        collectionLayout.addWidget(self.xSensorWidget)

        # Adding to Main Widget
        collectionWidget = QWidget()
        collectionWidget.setLayout(collectionLayout)
        layout.addWidget(collectionWidget)
        self.centralWidget.setLayout(layout)

        # QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.dataProcessing)
        self.timer.start(self.recordingRate)

        # Creating Timer Delay for Video and XSensor
        # self.videoTimer = self.videoCapture.frameDelay
        self.xSensorTimer = self.xSensorWidget.frameDelay

        # QElapsedTimer
        self.dataCollectionTimer = QElapsedTimer()

        # Data Collection Ready
        self.ready = False

        # Default Delsys Sensor Configurations
        self.performMVC = False

        
        self.emgMode = 'EMG plus gyro (+/- 2000 dps), +/-5.5mV, 20-450Hz'
        self.goniometerMode = 'SIG raw x4 (519Hz) (x1813)'

        self.defaultDelsysAttachments = {'EMGSensors' : [0, 1, 2, 3, 4, 5, 6, 7], 
                                         'GonioSensors' : [14, 15],
                                         'Attachments' : ['TAL', 'TAR', 'LGL', 'LGR', 'VLL', 'VLR', 'BFL', 'BFR', 'None', 'None', 'None', 'None', 'None', 'LK', 'RK']}

        self.defaultDelsysAttachments2 = {'EMGSensors' : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 
                                         'GonioSensors' : [10, 11, 12, 13, 14, 15],
                                         'Attachments' : ['TAL', 'TAR', 'LGL', 'LGR', 'VLL', 'VLR', 'BFL', 'BFR', 'TFL', 'TFR', 'LK', 'RK', 'LH', 'RH', 'LA', 'RA']}

        # self.selectedEMGSensors = [0, 1, 2, 3, 4, 5, 6, 7]
        # self.selectedGoniometerSensors = [14, 15]
        # self.defaultDelsysAttachments = ['TAL', 'TAR', 'LGL', 'LGR', 'VLL', 'VLR', 'BFL', 'BFR', 'None', 'None', 'None', 'None', 'None', 'LK', 'RK']
        # self.defaultDelsysAttachments2 = ['TAL', 'TAR', 'LGL', 'LGR', 'VLL', 'VLR', 'BFL', 'BFR', 'TFL', 'TFR', 'LK', 'RK', 'LH', 'RH', 'LA', 'RA']

    #-----------------------------------------------------------------------------------
    # ---- Controller for Components
    def componentController(self):

        # Creating Dictionary for Tracking Connected Components
        self.componentTracker = {}

        # Creating Label for Components
        controllerPanel = QWidget()
        controllerPanel.setFixedSize(100, 240)
        
        controllerLayout = QVBoxLayout()
        controllerLayout.setAlignment(Qt.AlignTop)
        
        # Components Label
        self.componentsLabel = QLabel("<b>Components</b>")
        self.componentsLabel.setStyleSheet('QLabel {color: black; font-size: 24px;}')
        controllerLayout.addWidget(self.componentsLabel)

        # Delsys CheckBox
        self.delsysCheckBox = QCheckBox("Delsys (EMG, EKG)")
        self.delsysCheckBox.setStyleSheet('QCheckBox {color: black;}')
        self.delsysCheckBox.setChecked(False)
        self.delsysCheckBox.stateChanged.connect(self.delsysCheckedCallback)
        controllerLayout.addWidget(self.delsysCheckBox)
        
        # Delsys Default Sensors CheckBox
        self.DefaultDelsysSensorsCheckBox = QCheckBox("Default Delsys Sensors")
        self.DefaultDelsysSensorsCheckBox.setStyleSheet('QCheckBox {color: black; padding: 10px;}')
        self.DefaultDelsysSensorsCheckBox.setChecked(False)
        self.DefaultDelsysSensorsCheckBox.stateChanged.connect(self.DelsysDefaultSettingsCheckedCallback)
        controllerLayout.addWidget(self.DefaultDelsysSensorsCheckBox)

        # Delsys Default Sensors CheckBox
        self.DefaultDelsysSensors2CheckBox = QCheckBox("Default Delsys Sensors 2")
        self.DefaultDelsysSensors2CheckBox.setStyleSheet('QCheckBox {color: black; padding: 10px;}')
        self.DefaultDelsysSensors2CheckBox.setChecked(False)
        self.DefaultDelsysSensors2CheckBox.stateChanged.connect(self.DelsysDefault2SettingsCheckedCallback)
        controllerLayout.addWidget(self.DefaultDelsysSensors2CheckBox)

        # MVC CheckBox
        self.DelsysMVCCheckBox = QCheckBox("Delsys MVC")
        self.DelsysMVCCheckBox.setStyleSheet('QCheckBox {color: black; padding: 10px;}')
        self.DelsysMVCCheckBox.setChecked(False)
        self.DelsysMVCCheckBox.stateChanged.connect(self.DelsysMVCCheckBoxCallback)
        controllerLayout.addWidget(self.DelsysMVCCheckBox)

        # XSensor CheckBox
        self.XSensorCheckBox = QCheckBox("XSensor")
        self.XSensorCheckBox.setStyleSheet('QCheckBox {color: black;}')
        self.XSensorCheckBox.setChecked(False)
        self.XSensorCheckBox.stateChanged.connect(self.XSensorCheckedCallback)
        controllerLayout.addWidget(self.XSensorCheckBox)

        # RL Checkbox
        self.RLPredictionsCheckBox = QCheckBox("RL Predictions")
        self.RLPredictionsCheckBox.setStyleSheet('QCheckBox {color: black;}')
        self.RLPredictionsCheckBox.setChecked(False)
        self.RLPredictionsCheckBox.stateChanged.connect(self.RLPredictionsCheckBoxCallback)
        controllerLayout.addWidget(self.RLPredictionsCheckBox)

        # Adding to Panel
        controllerPanel.setLayout(controllerLayout)
        controllerPanel.setMaximumSize(400, 200)

        return controllerPanel

    #-----------------------------------------------------------------------------------
    # ---- Delsys Control Widget

    def delsysButtonPanel(self):

    #-----------------------------------------------------------------------------------
    # ---- Data Saving Panel

        # Creating Widget Params
        delsysButtonPanel = QWidget()
        delsysButtonLayout = QVBoxLayout()
        delsysButtonPanel.setFixedSize(400, 700)

        # Data Collection Label
        self.dataCollectionLabel = QLabel("<b>Data Collection</b>", alignment = Qt.AlignCenter)
        self.dataCollectionLabel.setStyleSheet('QLabel {color: black; font-size: 24px;}')
        delsysButtonLayout.addWidget(self.dataCollectionLabel)

        # File Configuration Section
        self.fileConfigSectionHead = QLabel("<b>File Configuration", alignment = Qt.AlignCenter)
        self.fileConfigSectionHead.setStyleSheet('QLabel {color: black;}')
        delsysButtonLayout.addWidget(self.fileConfigSectionHead)

        # Data File Creating Layout
        dataCreationLayout = QHBoxLayout()

        # Experiment Name Text Entry
        self.experimentNameEntry = QLineEdit(self)
        self.experimentNameEntry.setAlignment(Qt.AlignCenter)
        self.experimentNameEntry.setText("Enter Experiment Name")
        self.experimentNameEntry.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.experimentNameEntry.objectName = "Experiment Name"
        self.experimentNameEntry.setStyleSheet('QLineEdit {color: black;}')
        dataCreationLayout.addWidget(self.experimentNameEntry)

        # Trial Number Dropdown
        self.trialNames = ['Trial 1', 'Trial 2', 'Trial 3', 'Trial 4', 'Trial 5', 'Trial 6', 'Trial 7', 'Trial 8', 'Trial 9', 'Trial 10']
        self.trialEntry = QComboBox(self)
        self.trialEntry.addItems(self.trialNames)
        self.trialEntry.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.trialEntry.objectName = 'Trial Number Dropdown'
        self.trialEntry.setStyleSheet('QComboBox {color: black;}')
        dataCreationLayout.addWidget(self.trialEntry)

        # Adding to main layout
        delsysButtonLayout.addLayout(dataCreationLayout)

        # File Editing Panel
        fileEditingPanel = QHBoxLayout()

        # Configure Data File Button
        self.configureDataFileButton = QPushButton("Config File", self)
        self.configureDataFileButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.configureDataFileButton.objectName = 'Configure Data File'
        self.configureDataFileButton.clicked.connect(self.configureDataFileCallback)
        self.configureDataFileButton.setStyleSheet('color: black;')
        self.configureDataFileButton.setEnabled(True)
        fileEditingPanel.addWidget(self.configureDataFileButton)

        # Manual Closing File Option
        self.closeDataFileButton = QPushButton("Close File", self)
        self.closeDataFileButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.closeDataFileButton.objectName = "Close Data File"
        self.closeDataFileButton.clicked.connect(self.closeDataFileCallback)
        self.closeDataFileButton.setStyleSheet('color: grey;')
        self.closeDataFileButton.setEnabled(False)
        fileEditingPanel.addWidget(self.closeDataFileButton)

        # Adding to delsys Button Layout
        delsysButtonLayout.addLayout(fileEditingPanel)

        # Adding Checkbox
        filePlottingPanel = QHBoxLayout()

        # Blank Space
        self.blank = QLabel()
        filePlottingPanel.addWidget(self.blank)

        # Adding Checkbox
        self.filePlottingCheckBox = QCheckBox("Post-Trial Plot")
        self.filePlottingCheckBox.setStyleSheet('QCheckBox {color: black;}')
        self.filePlottingCheckBox.setChecked(True)
        self.filePlottingCheckBox.stateChanged.connect(self.filePlottingChecked)
        filePlottingPanel.addWidget(self.filePlottingCheckBox)

        # Adding to Layout
        delsysButtonLayout.addLayout(filePlottingPanel)

        # Data Collection Panel Label
        self.dataStartStopLabel = QLabel('<b>Start Stop Buttons</b>', alignment = Qt.AlignCenter)
        self.dataStartStopLabel.setStyleSheet('QLabel {color: black;}')
        delsysButtonLayout.addWidget(self.dataStartStopLabel)

        # Data Collection Layout
        dataCollectionButtonLayout = QHBoxLayout()

        # Data Collection Button
        self.startDataCollectionButton = QPushButton("Start", self)
        self.startDataCollectionButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.startDataCollectionButton.objectName = 'Start Collection'
        self.startDataCollectionButton.clicked.connect(self.startDataCollectionCallback)
        self.startDataCollectionButton.setStyleSheet('color: grey;')
        self.startDataCollectionButton.setEnabled(False)
        dataCollectionButtonLayout.addWidget(self.startDataCollectionButton)

        # Stop Data Collection Button
        self.stopDataCollectionButton = QPushButton("Stop", self)
        self.stopDataCollectionButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stopDataCollectionButton.objectName = 'Start Collection'
        self.stopDataCollectionButton.clicked.connect(self.stopDataCollectionCallback)
        self.stopDataCollectionButton.setStyleSheet('color: grey;')
        self.stopDataCollectionButton.setEnabled(False)
        dataCollectionButtonLayout.addWidget(self.stopDataCollectionButton)
        
        # Adding to Complete Layout
        delsysButtonLayout.addLayout(dataCollectionButtonLayout)
        
        # Title
        self.textDelsys = QLabel("<b>Delsy Trigno System</b>", alignment = Qt.AlignCenter)
        self.textDelsys.setStyleSheet('QLabel {color: black; font-size: 20px}')
        delsysButtonLayout.addWidget(self.textDelsys)

        # Delsys Status
        self.delsysStatus = QLabel("<b>Delsys Status: </b>" + self.DelsysEMG.status, alignment = Qt.AlignCenter)
        self.delsysStatus.setStyleSheet('QLabel {color: black;}')
        delsysButtonLayout.addWidget(self.delsysStatus)

        # Connect Button
        self.connectButton = QPushButton("Connect", self)
        self.connectButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.connectButton.objectName = 'Connect'
        self.connectButton.clicked.connect(self.connectCallback)
        self.connectButton.setEnabled(False)
        self.connectButton.setStyleSheet('QPushButton {color: grey;}')
        delsysButtonLayout.addWidget(self.connectButton)

        # Creating Next Layout
        findSensorLayout = QHBoxLayout()

        # Pair Sensor Button
        self.pairSensorButton = QPushButton("Pair Sensor", self)
        self.pairSensorButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.pairSensorButton.objectName = 'Pair Sensor'
        self.pairSensorButton.clicked.connect(self.pairSensorCallback)
        self.pairSensorButton.setStyleSheet('color: grey;')
        self.pairSensorButton.setEnabled(False)
        findSensorLayout.addWidget(self.pairSensorButton)

        # Scan Sensor Button
        self.scanSensorButton = QPushButton("Scan Sensor", self)
        self.scanSensorButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.scanSensorButton.objectName = 'Scan Sensor'
        self.scanSensorButton.clicked.connect(self.scanSensorCallback)
        self.scanSensorButton.setStyleSheet('color: grey;')
        self.scanSensorButton.setEnabled(False)
        findSensorLayout.addWidget(self.scanSensorButton)
        
        # Number of Sensors
        self.sensorNumber = QLineEdit(self)
        self.sensorNumber.setAlignment(Qt.AlignCenter)
        self.sensorNumber.setValidator(QIntValidator())
        self.sensorNumber.setText("Enter Num Sensors")
        self.sensorNumber.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.sensorNumber.objectName = 'Sensor Number Box'
        self.sensorNumber.setStyleSheet('QLineEdit {color: black;}')
        findSensorLayout.addWidget(self.sensorNumber)
        
        # Adding to main layout
        delsysButtonLayout.addLayout(findSensorLayout)

        # Adding label
        self.sensorGridLabel = QLabel("<b>Sensor Selection Grid</b>", self, alignment = Qt.AlignCenter)
        self.sensorGridLabel.setStyleSheet('QLabel {color: black; font-size: 16px}')
        delsysButtonLayout.addWidget(self.sensorGridLabel)

        # Grid Layout
        sensorGrid = QGridLayout()

        # Creating 16 Sensor Grides
        tempSensor = 1
        self.sensorsSelected = []

        for i in range(0,4):
            for j in range(0,4):
                btn = QPushButton(str(tempSensor))
                btn.setStyleSheet('QPushButton {color: black}')
                btn.pressed.connect(partial(self.button_grid_press, str(tempSensor - 1)))
                sensorGrid.addWidget(btn,i,j)
                tempSensor += 1

        # Adding to main layout
        delsysButtonLayout.addLayout(sensorGrid)

        # Displaying Selected Sensors
        self.sensorSelectedDisplay = QLabel("Sensors Selected: " + str([sensor + 1 for sensor in self.sensorsSelected]))
        self.sensorSelectedDisplay.setStyleSheet('QLabel {color: black;}')
        delsysButtonLayout.addWidget(self.sensorSelectedDisplay)

        # Creating next layout
        selectSensorLayout = QHBoxLayout()

        # Select Sensor Button
        self.selectSensorButton = QPushButton("Select Sensor(s)", self)
        self.selectSensorButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.selectSensorButton.objectName = 'Select Sensor'
        self.selectSensorButton.clicked.connect(self.selectSensorCallback)
        self.selectSensorButton.setStyleSheet("color: grey;")
        self.selectSensorButton.setEnabled(False)
        selectSensorLayout.addWidget(self.selectSensorButton)

        # Select All Sensor Button
        self.selectAllSensorButton = QPushButton("Select All Sensor", self)
        self.selectAllSensorButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.selectAllSensorButton.objectName = 'Select All Sensor'
        self.selectAllSensorButton.clicked.connect(self.selectAllSensorCallback)
        self.selectAllSensorButton.setStyleSheet('color: grey;')
        self.selectAllSensorButton.setEnabled(False)
        selectSensorLayout.addWidget(self.selectAllSensorButton)

        # Reset Sensor Selection Button
        self.resetSensorSelection = QPushButton("Reset Selection", self)
        self.resetSensorSelection.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.resetSensorSelection.objectName = 'Reset Selection'
        self.resetSensorSelection.clicked.connect(self.resetSensorSelectionCallback)
        self.resetSensorSelection.setStyleSheet('color: grey;')
        self.resetSensorSelection.setEnabled(False)
        selectSensorLayout.addWidget(self.resetSensorSelection)

        # Adding to main layout
        delsysButtonLayout.addLayout(selectSensorLayout)

        # Sensor Mode Title
        self.sensorModeTitle = QLabel("<b>Sensor Mode Dropdown</b>", alignment = Qt.AlignCenter)
        self.sensorModeTitle.setStyleSheet("QLabel {color: black; font-size: 16px}")
        delsysButtonLayout.addWidget(self.sensorModeTitle)

        # Sensor Mode Dropdown
        self.sensorModeDropdown = QComboBox(self)
        self.sensorModeDropdown.addItems(self.DelsysEMG.sampleModeList)
        self.sensorModeDropdown.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.sensorModeDropdown.objectName = 'Sensor Mode Dropdown'
        self.sensorModeDropdown.setStyleSheet('QComboBox {color: black;}')
        delsysButtonLayout.addWidget(self.sensorModeDropdown)

        # Adding next layout
        sampleModeLayout = QHBoxLayout()
        
        # Set Sample Mode Button
        self.setSampleMode = QPushButton("Set Sample Mode", self)
        self.setSampleMode.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setSampleMode.objectName = 'Set Sample Mode'
        self.setSampleMode.clicked.connect(self.setSampleModeCallback)
        self.setSampleMode.setStyleSheet('color: grey;')
        self.setSampleMode.setEnabled(False)
        sampleModeLayout.addWidget(self.setSampleMode)

        # Set All Sample Mode Button
        self.setAllSampleMode = QPushButton("Set All Sample Mode", self)
        self.setAllSampleMode.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.setAllSampleMode.objectName = 'Set Sample Mode'
        self.setAllSampleMode.clicked.connect(self.setAllSampleModeCallback)
        self.setAllSampleMode.setStyleSheet('color: grey;')
        self.setAllSampleMode.setEnabled(False)
        sampleModeLayout.addWidget(self.setAllSampleMode)

        # Adding to main layout
        delsysButtonLayout.addLayout(sampleModeLayout)

        # Creating configure button
        self.configureButton = QPushButton("Configure", self)
        self.configureButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.configureButton.objectName = 'Configure'
        self.configureButton.clicked.connect(self.configureCallback)
        self.configureButton.setStyleSheet('color: grey;')
        self.configureButton.setEnabled(False)
        delsysButtonLayout.addWidget(self.configureButton)

        # Setting Button Panel
        delsysButtonPanel.setLayout(delsysButtonLayout)

        return delsysButtonPanel
    
    # Data Processing Pipeline
    def dataProcessing(self):
        # Start Time
        startTime = time.perf_counter()

        # Data Processing Pipeline
        if self.recording:

            try:
                if 'Delsys' in self.componentTracker:
                    # Delsys Data Polling and Update
                    self.DelsysEMG.processData()

                    # Saving data to hdf5 file
                    if self.threadedDataSaver:
                        command = {
                            'function' : 'saveDelsysData',
                            'params' : {'data' : self.DelsysEMG.data}
                        }
                        self.queue.put(command)

                    else:
                        self.DataFileHandler.saveDelsysData(self.DelsysEMG.data)

                    # Buffer is cleared in plotEMGGUI
                    averageEMG = self.DelsysEMG.plotEMGGUI()

                    # Only plotting if EMG sensors have been added
                    self.EMGPlot.plotEMG(averageEMG)

            except Exception as e:
                print(f"\nIssue processing Delsys Data:\n{e}")

            try:
                if 'XSensor' in self.componentTracker:
                    # XSensor Polling and Update
                    self.xSensorWidget.processDataCallback()

                    # Saving data to hdf5 file
                    if self.threadedDataSaver:
                        command = {
                            'function' : 'saveXSensorData',
                            'params' : {'data' : self.xSensorWidget.XSensorForce.data}
                        }
                        self.queue.put(command)

                    else:
                         self.DataFileHandler.saveXSensorData(self.xSensorWidget.XSensorForce.data)
                   
                    if self.xSensorTimer >= self.xSensorWidget.frameDelay:
                        # Updating Display
                        self.xSensorWidget.updateDisplay()

                        # Resetting Timer    
                        self.xSensorTimer = 0

                    # Resetting Buffer
                    self.xSensorWidget.resetBuffer()

                    # Increasing Timer by Recording Rate
                    self.xSensorTimer += self.recordingRate
                    
            except Exception as e:
                print(f"Issue processing XSensor Data: {e}")

            try: 
                if 'RL' in self.componentTracker:
                    # Getting Current Transition Time
                    terrainList, currentTerrain = self.MLControl.getCurrentTerrain()

                    # Checking Against Current Data
                    if np.any(self.MLControl.currentTerrainList != currentTerrain):
                        # Getting Terrain
                        terrain = terrainList[currentTerrain.index(1)]

                        # Saving Transition Time
                        if self.threadedDataSaver:
                            command = {
                                    'function' : 'addTransitionTime',
                                    'params' : {
                                        'terrain' : terrain, 
                                        'transitionTime' : self.returnTime()
                                        }
                            }
                            self.queue.put(command)

                        else:
                            self.DataFileHandler.addTransitionTime(terrain, self.returnTime())

                        # Setting CurrentTerrainList
                        self.MLControl.currentTerrainList = currentTerrain
            
            except Exception as e:
                print(f"Issue Updating RL: {e}")

        #print(f"Loop Time: {(time.perf_counter() - startTime) * 1000} ms")
        
    # Function to add and remove sensors from the sensor list on button press
    def button_grid_press(self, value):
        try:
            # Button Panel Callback
            if (self.sensorsSelected.count(int(value)) > 0):
                valInd = self.sensorsSelected.index(int(value))
                self.sensorsSelected.pop(valInd)
            else:
                valInd = self.sensorsSelected.index(int(value))

        except:
            self.sensorsSelected.append(int(value))

        # Updating Sensor List
        self.sensorSelectedDisplay.setText("Sensors Selected: " + str([sensor + 1 for sensor in self.sensorsSelected]))

    # Exit function
    def closeEvent(self, event):
        # This function runs when the GUI Window is closed.
        # Cleanup when closing.

        print("Closing the application...")

        # Releasing XSensor
        try:
            self.xSensorWidget.releaseAndQuit()

        except:
            print("XSensors Not Connected")

        # Closing Data File
        try:
            if self.threadedDataSaver:
                command = {
                        'function' : 'closeFile',
                        'params' : {}
                }
                self.queue.put(command)

            else:
                self.DataFileHandler.closeFile()

        except Exception as e:
            print(f'Error Closing Data File : {e}')

        # Stopping Data Saving Threads
        try:
            if self.threadedDataSaver:
                # Stopping and Joining Worker Thread
                self.worker.stop()
                self.worker.join()

        except Exception as e:
            print(f"Error Stopping Data Saving Threads: {e}")

        # Closing Note Taking File
        try:
            if self.noteTaker.file is not None:
                # Save any notes taken in the notetaker that weren't added then close
                self.noteTaker.addNoteCallback()
                self.noteTaker.closeTextFile()

        except Exception as e:
            print(f'Error Closing Note Taker: {e}')

        print("Clean Up Successful")

        # Default closeEvent Action
        super().closeEvent(event)

    #-----------------------------------------------------------------------------------
    # ---- Callback Functions

    # Delsys Connection Callback
    def connectCallback(self):
        # Connecting to Delsys
        self.connectButton.setEnabled(False)
        self.connectButton.setStyleSheet("color: grey")
        self.DelsysEMG.connect()

        # Updating GUI
        # Delsys Status
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)

        # Pair Sensor Button
        self.pairSensorButton.setEnabled(True)
        self.pairSensorButton.setStyleSheet('QPushButton {color: black;}')

        # Scan Sensor Button
        self.scanSensorButton.setEnabled(True)
        self.scanSensorButton.setStyleSheet('QPushButton {color: black;}')
    
    # Delsys Pair Sensor Callback
    def pairSensorCallback(self):
        
        # Default settings for delsys sensors and attachments has been selected.
        if ("Default Delsys" in self.componentTracker):
            # Pairing Sensors
            # self.DelsysEMG.connectSensors(len(self.selectedEMGSensors) + len(self.selectedGoniometerSensors), self.defaultDelsysAttachments)
            self.DelsysEMG.connectSensors(len(self.defaultDelsysAttachments['EMGSensors']) + len(self.defaultDelsysAttachments['GonioSensors']), 
                                          self.defaultDelsysAttachments['Attachments'])

        elif ("Default Delsys 2" in self.componentTracker):
            # Pairing Sensors
            # self.DelsysEMG.connectSensors(len(self.selectedEMGSensors) + len(self.selectedGoniometerSensors), self.defaultDelsysAttachments2)
            self.DelsysEMG.connectSensors(len(self.defaultDelsysAttachments2['EMGSensors']) + len(self.defaultDelsysAttachments2['GonioSensors']), 
                                          self.defaultDelsysAttachments2['Attachments'])    

        else:
            # Pairing Sensors
            self.DelsysEMG.connectSensors(self.sensorNumber.text())

        # Updating GUI
        # Delsys Status
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)

        # Select Sensor Button
        self.selectSensorButton.setEnabled(True)
        self.selectSensorButton.setStyleSheet('QPushButton {color: black;}')

        # Select All Sensor Button
        self.selectAllSensorButton.setEnabled(True)
        self.selectAllSensorButton.setStyleSheet('QPushButton {color: black;}')

        # Reset Sensor Button
        self.resetSensorSelection.setEnabled(True)
        self.resetSensorSelection.setStyleSheet('QPushButton {color: black;}')

    # Delsys Scan Sensor Callback
    def scanSensorCallback(self):
        if ("Default Delsys" in self.componentTracker):
            # Scan for Connected Sensors
            self.DelsysEMG.scanForSensors(self.defaultDelsysAttachments['Attachments'])

        elif ("Default Delsys 2" in self.componentTracker):
            # Scan For Connected Sensors
            self.DelsysEMG.scanForSensors(self.defaultDelsysAttachments2['Attachments'])
        
        else:
            # Scan for Connected Sensors
            self.DelsysEMG.scanForSensors()

        # Updating GUI
        # Delsys Status
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)

        # Select Sensor Button
        self.selectSensorButton.setEnabled(True)
        self.selectSensorButton.setStyleSheet('QPushButton {color: black;}')

        # Select All Sensor Button
        self.selectAllSensorButton.setEnabled(True)
        self.selectAllSensorButton.setStyleSheet('QPushButton {color: black;}')

        # Reset Sensor Selection Button
        self.resetSensorSelection.setEnabled(True)
        self.resetSensorSelection.setStyleSheet('QPushButton {color: black;}')

    # Delsys Select Sensor Callback
    def selectSensorCallback(self):
        # Selecting Sensors in self.sensorsSelected
        for sensor in self.sensorsSelected:
            self.DelsysEMG.selectSensor(sensor)

        # Updating GUI
        # Delsys Status
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)

        # Set Sample Mode Button
        self.setSampleMode.setEnabled(True)
        self.setSampleMode.setStyleSheet('QPushButton {color: black;}')

        # Set All Sample Mode Button
        self.setAllSampleMode.setEnabled(True)
        self.setAllSampleMode.setStyleSheet('QPushButton {color: black;}')

    # Delsys Select All Sensor Callback
    def selectAllSensorCallback(self):
        # Select All Connected Sensors
        self.DelsysEMG.selectAllSensors()

        # Updating GUI
        # Delsys Status
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)

        # Set Sample Mode Button
        self.setSampleMode.setEnabled(True)
        self.setSampleMode.setStyleSheet('QPushButton {color: black;}')

        # Set All Sample Mode Button
        self.setAllSampleMode.setEnabled(True)
        self.setAllSampleMode.setStyleSheet('QPushButton {color: black;}')

    # Reset Sensor Selection Callback
    def resetSensorSelectionCallback(self):
        # Clearing self.sensorsSelected
        self.sensorsSelected.clear()
        self.sensorSelectedDisplay.setText("Sensors Selected: " + str(self.sensorsSelected))

    # Set Sample Mode Callback
    def setSampleModeCallback(self):
        # Setting Sample Mode of Sensors
        self.DelsysEMG.setSampleMode(self.sensorsSelected, self.sensorModeDropdown.currentText())

        # Updating GUI
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.configureButton.setEnabled(True)
        self.configureButton.setStyleSheet('QPushButton {color: black;}')

        # Clearing Sensor Selection 
        self.resetSensorSelectionCallback()

    # Set All Sample Mode Callback
    def setAllSampleModeCallback(self):
        # Setting Sample Mode of Sensors
        self.DelsysEMG.setAllSampleModes(self.sensorModeDropdown.currentText())

        # Updating GUI
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.configureButton.setEnabled(True)
        self.configureButton.setStyleSheet('QPushButton {color: black;}')

        # Clearing Sensor Selection 
        self.resetSensorSelectionCallback()

    # Configure Callback
    def configureCallback(self):
        # Configuring Delsys
        self.DelsysEMG.configure()

        # Updating GUI
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        
        # Updating ready status
        self.ready = True
        self.componentTracker['Delsys'] = True

        # Adding Sensor Plots
        if self.EMGPlot is None:
            self.EMGPlot = EMGPlot(self.DelsysEMG.numEMGChannels, self.DelsysEMG.sensorDict, self.DelsysEMG.sensorNames, self.DelsysEMG.EMGSensors, self.recordingRate)
            self.splitter.insertWidget(1, self.EMGPlot.plottingPanel)
            
            self.splitter.setStretchFactor(1, 3)
            self.splitter.update()

        # Doing MVC If Asked For
        if self.performMVC == True:
            self.DelsysEMG.createMVCNorm()

    # Configuring File for Data Saving
    def configureDataFileCallback(self):
        print("Configuring Save File...")

        # Checking XSensor Status
        if 'XSensor' in self.componentTracker.keys():
            if self.xSensorWidget.ready:
                self.componentTracker['XSensor'] = True

        # Checking RL Status
        if 'RL' in self.componentTracker.keys():
            if self.MLControl.predict:
                self.componentTracker["RL"] = True

        # Checking If All Components Are Ready
        if all(list(self.componentTracker.values())):
            try:
                # Creating file
                self.experimentName = self.experimentNameEntry.text()

                # Creating file save location path
                savePath = os.path.join(self.saveLocation, self.experimentName)

                # Creating object and initializing save location
                if self.threadedDataSaver:
                    command = {
                        'function' : 'setFilePath',
                        'params' : {'filePath' : savePath}
                    }
                    self.queue.put(command)

                else:
                    self.DataFileHandler.setFilePath(savePath)

                # Creating file object
                if self.threadedDataSaver:
                    command = {
                        'function' : 'createFile',
                        'params' : {'fileName' : self.trialEntry.currentText()}
                    }
                    self.queue.put(command)

                else:
                    self.DataFileHandler.createFile(self.trialEntry.currentText())

                # Formatting File
                if self.threadedDataSaver:
                    command = {
                        'function' : 'formatFile',
                        'params' : {
                            'sensorDictDelsys': self.DelsysEMG.dataSavingSensorDict,
                            'sensorDictXSensor': self.xSensorWidget.XSensorForce.dataSavingSensorDict
                        }
                    }
                    self.queue.put(command)

                else:
                    self.DataFileHandler.formatFile(self.DelsysEMG.dataSavingSensorDict, self.xSensorWidget.XSensorForce.dataSavingSensorDict)

                # Updating Close Data File Button
                self.closeDataFileButton.setEnabled(True)
                self.closeDataFileButton.setStyleSheet('QPushButton {color: black;}')

                # Updating Config File Button
                self.configureDataFileButton.setEnabled(False)
                self.configureDataFileButton.setStyleSheet('QPushButton {color: grey;}')

                # Updating Start Button
                self.startDataCollectionButton.setEnabled(True)
                self.startDataCollectionButton.setStyleSheet('QPushButton {color: black;}')

                print("Successfully Configured Data File")

            except Exception as e:
                print(f"\nUnable to Configure Data File:\n{e}")

            # Saving MVC Data If Available
            try:
                if self.performMVC == True:
                    if self.threadedDataSaver:
                        command = {
                                'function' : 'saveDelsysMVC',
                                'params' : {'MVCData' : self.DelsysEMG.normalizeDict}
                        }
                        self.queue.put(command)

                    else:
                        self.DataFileHandler.saveDelsysMVC(self.DelsysEMG.normalizeDict)

            except Exception as e:
                print(f'Error Saving MVC: {e}')

            try:
                # Saving Participant Weight Data
                if 'XSensor' in self.componentTracker.keys() and self.componentTracker['XSensor'] == True:
                    if self.threadedDataSaver:
                        command = {
                                'function' : 'saveParticipantWeight',
                                'params' : {'participantWeight' : self.xSensorWidget.weightEntryBox.text()}
                        }
                        self.queue.put(command)

                    else:
                        self.DataFileHandler.saveParticipantWeight(self.xSensorWidget.weightEntryBox.text())

            except Exception as e:
                print(f'Error Saving Participant Weight: {e}')

            # Waiting Before Continuing
            QtTest.QTest.qWait(5000)

            try:
                # Creating Note Taking File
                self.noteTaker.createTextFile(self.experimentName)
                self.noteTaker.addNoteButton.setEnabled(True)
                self.noteTaker.addNoteButton.setStyleSheet('QPushButton {color: black;}')
                
                # self.noteTaker.markTransitionButton.setEnabled(True)
                # self.noteTaker.markTransitionButton.setStyleSheet('QPushButton {color: black;}')
                
                # Adding Trial Name to Note Taker Widget
                self.noteTaker.addTrialName(self.trialEntry.currentText())

            except Exception as e:
                print(f"Couldn't Initialize Note Taking File: {e}")

        else:
            print(f'Check the Following Components : {[key for key, value in self.componentTracker.items() if value != True]}')

    # Manual Callback for Closing Data File
    def closeDataFileCallback(self):
        print("Closing Save File...")
        try:
            # Checking if Data File Handler Exists
            # if self.dataCommandSender:
            if self.DataFileHandler:
                print("Plotting Trial Data...")
                
                try:
                    # Plotting Trial Data for Delsys
                    if 'Delsys' in self.componentTracker and self.filePlot == True:
                        self.DataFileHandler.plotDelsysTrialData()

                except Exception as e:
                    print(f"Error Plotting Delsys Data : {e}")

                # Closing Data File

                if self.threadedDataSaver:
                    command = {
                        'function' : 'closeFile',
                        'params' : {}
                    }
                    self.queue.put(command)

                else:
                    self.DataFileHandler.closeFile()

            # Updating Close Data File Button
            self.closeDataFileButton.setEnabled(False)
            self.closeDataFileButton.setStyleSheet('QPushButton {color: grey;}')

            # Updating Config File Button
            self.configureDataFileButton.setEnabled(True)
            self.configureDataFileButton.setStyleSheet('QPushButton {color: black;}')

            # Updating Start Button
            self.startDataCollectionButton.setEnabled(False)
            self.startDataCollectionButton.setStyleSheet('QPushButton {color: grey;}')

            # Updating Stop Button
            self.stopDataCollectionButton.setEnabled(False)
            self.stopDataCollectionButton.setStyleSheet('QPushButton {color: grey;}')

            # Print Status
            print("Successfully Closed Save File")

        except Exception as e:
            print(e)
            print("Unable to Close File")

    # Start Data Collection Callback
    def startDataCollectionCallback(self):
        # Starting Data Collection
        try:
            if 'XSensor' in self.componentTracker:
                # Start Data Collection on Delsys
                self.xSensorWidget.XSensorForce.startDataCollection()

        except:
            print('Unable to Start XSensor Data Collection')

        try:
            if 'Delsys' in self.componentTracker:
                # Start Data Collection on Delsys
                self.DelsysEMG.startDataCollection()

                # Updating Delsys Status
                self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)

        except:
            print('Unable to Start Delsys Data Collection')
        
        # Start Data Collection on Other Platforms
        self.recording = True
        # self.videoCapture.recording = True

        # Adding start time to file
        self.startTime = datetime.now()

        if self.threadedDataSaver:
            command = {
                'function' : 'addStartTime',
                'params' : {'startTime' : self.returnTime()}
            }
            self.queue.put(command)

        else:
            self.DataFileHandler.addStartTime(self.returnTime())

        # Updating GUI
        # Start Data Collection Button
        self.startDataCollectionButton.setEnabled(False)
        self.startDataCollectionButton.setStyleSheet("QPushButton {color: grey;}")

        # Stop Data Collection Button
        self.stopDataCollectionButton.setEnabled(True)
        self.stopDataCollectionButton.setStyleSheet("QPushButton {color: black;}")

        # Close Data File Button
        self.closeDataFileButton.setEnabled(False)
        self.closeDataFileButton.setStyleSheet('QPushButton {color: grey;}')

        # Starting Timer
        self.dataCollectionTimer.start()

    # Stop Data Collection Callback
    def stopDataCollectionCallback(self):
        # Setting Recording To Stopped
        self.recording = False

        # Adding in Stop Time
        if self.threadedDataSaver:
            command = {
                'function' : 'addStopTime',
                'params' : {'stopTime' : self.returnTime()}
            }
            self.queue.put(command)

        else:
            self.DataFileHandler.addStopTime(self.returnTime())

        # Stopping Data Collection
        try:
            if 'Delsys' in self.componentTracker:
                # Stopping Delsys Data Collection
                self.DelsysEMG.stopDataCollection()

                # Clearing Delsys Buffers
                self.DelsysEMG.resetBuffer()

        except: 
            print("Can't Stop Delsys Data Collection")

        try:
            if 'XSensor' in self.componentTracker:
                # Start Data Collection on Delsys
                self.xSensorWidget.XSensorForce.stopDataCollection()
                 
                # Clearing XSensor Buffers
                self.xSensorWidget.XSensorForce.resetBuffer()

        except:
            print('Unable to Stop XSensor Data Collection')

         # Resetting RL Buttons
        try:
            if 'RL' in self.componentTracker:
                # Resetting RL Terrains
                self.MLControl.resetTerrainButtons()
                
        except:
            print("Can't Reset RL Terrain Indications")

        #self.xSensorWidget.stopDataCollection()
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        
        # Updating GUI
        # Start Data Collection Button
        self.startDataCollectionButton.setEnabled(True)
        self.startDataCollectionButton.setStyleSheet('QPushButton {color: black;}')

        # Stop Data Collection Button
        self.stopDataCollectionButton.setEnabled(False)
        self.stopDataCollectionButton.setStyleSheet('QPushButton {color: grey;}')

        # Close Data File Button
        self.closeDataFileButton.setEnabled(True)
        self.closeDataFileButton.setStyleSheet('QPushButton {color: black;}')

        # Saving Elapsed Time
        self.timeElapsed = self.dataCollectionTimer.elapsed()

    # Delsys Checked Callback
    def delsysCheckedCallback(self):
        # If CheckBox Moves to Checked State
        if self.delsysCheckBox.isChecked():
            self.componentTracker['Delsys'] = False

            # Updating GUI
            self.connectButton.setEnabled(True)
            self.connectButton.setStyleSheet('QPushButton {color: black;}')

        # If CheckBox Moves to Unchecked State
        else:
            # Deleting Key From Component Tracker Dictionary
            self.componentTracker.pop('Delsys')

            # Updating GUI
            self.connectButton.setEnabled(False)
            self.connectButton.setStyleSheet('QPushButton {color: grey;}')

    # XSensor Checked Callback
    def XSensorCheckedCallback(self):
        # If CheckBox Moves to Checked State
        if self.XSensorCheckBox.isChecked():
            self.componentTracker['XSensor'] = False

            # Updating GUI
            self.xSensorWidget.weightEntryBox.setDisabled(False)
            self.xSensorWidget.weightEntryBox.setStyleSheet('QLineEdit {color: black;}')
            self.xSensorWidget.configureButton.setEnabled(True)
            self.xSensorWidget.configureButton.setStyleSheet('QPushButton {color: black;}')

        # If CheckBox Moves to Unchecked State
        else:
            # Deleting Key From Component Tracker Dictionary
            self.componentTracker.pop('XSensor')

            # Updating GUI
            self.xSensorWidget.weightEntryBox.setDisabled(True)
            self.xSensorWidget.weightEntryBox.setStyleSheet('QLineEdit {color: grey;}')
            self.xSensorWidget.configureButton.setEnabled(False)
            self.xSensorWidget.configureButton.setStyleSheet('QPushButton {color: grey;}') 

    def DelsysDefaultSettingsCheckedCallback(self):
        # If CheckBox Moves to Checked State
        if self.DefaultDelsysSensorsCheckBox.isChecked():
            self.componentTracker['Default Delsys'] = True

         # If CheckBox Moves to Unchecked State
        else:
            self.componentTracker.pop('Default Delsys')

    def DelsysDefault2SettingsCheckedCallback(self):
        # If CheckBox Moves to Checked State
        if self.DefaultDelsysSensors2CheckBox.isChecked():
            self.componentTracker['Default Delsys 2'] = True

         # If CheckBox Moves to Unchecked State
        else:
            self.componentTracker.pop('Default Delsys 2')

    def DelsysMVCCheckBoxCallback(self):
        # If CheckBox Moves to Checked State
        if self.DelsysMVCCheckBox.isChecked():
            self.performMVC = True

        # If CheckBox Moves to Unchecked State
        else:
            self.performMVC = False

    def RLPredictionsCheckBoxCallback(self):
        # If CheckBox Moves to Checked State
        if self.RLPredictionsCheckBox.isChecked():
            self.componentTracker["RL"] = False
            self.MLControl.predCheckCallback(True)

        # If CheckBox Moves to Unchecked State
        else:
            self.componentTracker.pop("RL")
            self.MLControl.predCheckCallback(False)

    def filePlottingChecked(self):
        # If CheckBox Moves to Checked State
        if self.filePlottingCheckBox.isChecked():
            # Changing Post Trial Plotting To True
            self.filePlot = True

        # If CheckBox Moves to Unchecked State
        else:
            # Changing Post Trial Plotting To False
            self.filePlot = False

    def returnTime(self):
        # Returning Time Elapsed
        elapsed = datetime.now() - self.startTime

        return np.round(elapsed.total_seconds(), decimals = 3)    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = RLFrontEnd()
    widget.resize(400, 400)
    widget.show()
    sys.exit(app.exec())