"""
This is the main Reinforcement Learning GUI that incorperates the DelsyEMG control class, EMGPlot class, Computer Vision class, 
and XSensor Control Class. This GUI is used to control each data acqusition device and create a pipeline for saving data in real time.

Written by Sonny Jones & Grange Simpson
Version: 2024.05.08

Usage: Run the file.

"""

import os
import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from functools import partial
from datetime import date
import numpy as np
import time
import json

from RLDependencies.EMGPlot import *
from RLDependencies.DelsysEMG import *
from RLDependencies.OpenCVWidget import *
from RLDependencies.XSensorWidget import *
from RLDependencies.DataFileHandler import *
from RLDependencies.DataCommandSender import *
from RLDependencies.NoteTakingWidget import *
from RLDependencies.RLWidget import *
from RLDependencies.AudioVideoMuxing import combineAudioVideo

class MyWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Data Saving Location
        self.dataCommandSender = DataCommandSender()
        self.saveLocation = "C:/Users/Purkinje/Box/NeuroRoboticsLab/NERVES Lab/Project Groups/ML Gait/Experimental Data/"

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
        self.splitter = QSplitter(self)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        collectionLayout = QVBoxLayout()

        # Component Control
        controlAndNotes = QVBoxLayout()
        self.componentControl = self.componentController()
        controlAndNotes.addWidget(self.componentControl, alignment = Qt.AlignTop)

        # Note Taker
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
        self.videoCapture = VideoWidget(recordingRate = self.recordingRate)
        self.splitter.addWidget(self.videoCapture)
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
        self.videoTimer = self.videoCapture.frameDelay
        self.xSensorTimer = self.xSensorWidget.frameDelay

        # QElapsedTimer
        self.dataCollectionTimer = QElapsedTimer()

        # Data Collection Ready
        self.ready = False

        # Default Delsys Sensor Configurations, no ekg right now
        self.performMVC = False
        self.selectedEMGSensors = [0, 1, 2, 3, 4, 5, 6, 7]
        self.selectedGoniometerSensors = [14, 15]
        self.emgMode = 'EMG plus gyro (+/- 2000 dps), +/-5.5mV, 20-450Hz'
        self.goniometerMode = 'SIG raw x4 (519Hz) (x1813)'
        self.defaultDelsysAttachments = ['TAL', 'TAR', 'LGL', 'LGR', 'VLL', 'VLR', 'BFL', 'BFR','None', 'None', 'None', 'None', 'None', 'LK', 'RK']

    #-----------------------------------------------------------------------------------
    # ---- Controller for Components
    def componentController(self):

        # Creating Dictionary for Tracking Connected Components
        self.componentTracker = {}

        # Creating Label for Components
        controllerPanel = QWidget()
        controllerPanel.setFixedSize(80, 210)
        
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
        controllerPanel.setMaximumSize(300, 100)

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

        # Data Processing Pipeline
        if self.recording:

            try:
                if 'Delsys' in self.componentTracker:
                    tic = time.time()

                    # Delsys Data Polling and Update
                    self.DelsysEMG.processData()

                    # Saving data to hdf5 file
                    command = {
                        'function' : 'saveDelsysData',
                        'params' : {'data' : self.DelsysEMG.data[0]}
                    }
                    self.dataCommandSender.sendCommand(json.dumps(command))

                    # Buffer is cleared in plotEMGGUI
                    averageEMG = self.DelsysEMG.plotEMGGUI()

                    # Only plotting if EMG sensors have been added
                    self.EMGPlot.plotEMG(averageEMG)

                    print(f"Delsys Processing Completed in {time.time() - tic}")

            except Exception as e:
                print(f"\nIssue processing Delsys Data:\n{e}")

            try:
                if 'XSensor' in self.componentTracker:
                    tic = time.time()
                    # XSensor Polling and Update
                    self.xSensorWidget.processDataCallback()

                    # Saving data to hdf5 file
                    command = {
                        'function' : 'saveXSensorData',
                        'params' : {'data' : self.xSensorWidget.XSensorForce.data}
                    }
                    self.dataCommandSender.sendCommand(json.dumps(command))

                    print(f"XSensor Processing Completed in {time.time() - tic}")

                    tic = time.time()

                    if self.xSensorTimer >= self.xSensorWidget.frameDelay:
                        # Updating Display
                        self.xSensorWidget.updateDisplay()

                        # Resetting Timer    
                        self.xSensorTimer = 0

                    # Resetting Buffer
                    self.xSensorWidget.resetBuffer()

                    # Increasing Timer by Recording Rate
                    self.xSensorTimer += self.recordingRate

                    print(f"XSensor Display Update Completed in {time.time() - tic}")

                    
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
                        command = {
                            'function' : 'addTransitionTime',
                            'params' : {
                                'terrain' : terrain, 
                                'transitionTime' : self.returnTime()
                                }
                        }
                        self.dataCommandSender.sendCommand(json.dumps(command))

                        # Resetting CurrentTerrainList
                        self.MLControl.currentTerrainList = currentTerrain
            
            except Exception as e:
                print(f"Issue Updating RL: {e}")
        
        # Video Processing
        tic = time.time()
        if self.videoTimer >= self.videoCapture.frameDelay:
            self.videoCapture.dataProcessing()
            self.videoTimer = 0 
        
        # Updating VideoTimer 
        self.videoTimer += self.recordingRate

        print(f"Camera Capture Processing Completed in {time.time() - tic}")
    
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
        
        # Saving MVC Data If Available
        try:
            if self.performMVC == True:
                command = {
                    'function' : 'saveDelsysMVC',
                    'params' : {'MVCData' : self.DelsysEMG.normalizeDict}
                }
                self.dataCommandSender.sendCommand(json.dumps(command))

        except Exception as e:
            print(f'Error Saving MVC: {e}')

        # Closing Data File
        try:
            if self.dataCommandSender is not None:
                command = {
                        'function' : 'closeFile',
                        'params' : {}
                }
                self.dataCommandSender.sendCommand(json.dumps(command))

        except Exception as e:
            print(f'Error Closing Data File : {e}')

        # Stopping Data Saving Threads
        try:
            if self.dataCommandSender:
                command = {
                        'function' : 'stop',
                        'params' : {}
                }
                self.dataCommandSender.sendCommand(json.dumps(command))

        except Exception as e:
            print(f"Error Stopping Data Saving Threads: {e}")
        
        # Releasing Camera and Audio
        try:
            self.videoCapture.releaseConfig()

        except Exception as e:
            print(f'Error Releasing Camera and Audio: {e}')

        # Closing Note Taking File
        try:
            if self.noteTaker.file is not None:
                # Save any notes taken in the notetaker that weren't added then close
                self.noteTaker.addNoteCallback()
                self.noteTaker.closeTextFile()

        except Exception as e:
            print(f'Error Closing Note Taker: {e}')

        # Muxxing Files
        print("Muxing Audio and Video files...")
        try:
            combineAudioVideo(self.videoCapture.filePath, self.videoCapture.frameRate)
            print("Muxing Completed")

        except Exception as e:
            print(f'Error Muxing Audio and Video: {e}')

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
            self.DelsysEMG.connectSensors(len(self.selectedEMGSensors) + len(self.selectedGoniometerSensors), self.defaultDelsysAttachments)

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
            self.DelsysEMG.scanForSensors(self.defaultDelsysAttachments)

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
                command = {
                        'function' : 'setFilePath',
                        'params' : {'filePath' : savePath}
                }
                self.dataCommandSender.sendCommand(json.dumps(command))

                # Creating file object
                command = {
                    'function' : 'createFile',
                    'params' : {'fileName' : self.trialEntry.currentText()}
                }
                self.dataCommandSender.sendCommand(json.dumps(command))

                # Formatting File
                command = {
                    'function' : 'formatFile',
                    'params' : {
                        'sensorDictDelsys': self.DelsysEMG.dataSavingSensorDict,
                        'sensorDictXSensor': self.xSensorWidget.XSensorForce.dataSavingSensorDict
                        }
                }
                self.dataCommandSender.sendCommand(json.dumps(command))

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

            try:
                # If save path not in class
                if self.videoCapture.filePath is None:
                    # Getting Experiment Name
                    self.experimentName = self.experimentNameEntry.text()

                    # Creating file save location path
                    savePath = os.path.join(self.saveLocation, self.experimentName)

                    # Adding Path
                    self.videoCapture.filePath = savePath

                # Creating Video Outlet
                # TODO: Error creating the outlet, output file doesn't seem to be created
                self.videoCapture.createOutlet(self.trialEntry.currentText())

                print("Successfully Configured Video Outlet")

            except Exception as e:
                print(f"\nUnable to Configure Video Outlet:\n{e}")

        else:
            print('Delsys and XSensor Not Ready')

        try:
            # Creating Note Taking File
            self.noteTaker.createTextFile(self.experimentNameEntry.text())
            self.noteTaker.addNoteButton.setEnabled(True)
            self.noteTaker.addNoteButton.setStyleSheet('QPushButton {color: black;}')
            
            # self.noteTaker.markTransitionButton.setEnabled(True)
            # self.noteTaker.markTransitionButton.setStyleSheet('QPushButton {color: black;}')
            
            # Adding Trial Name to Note Taker Widget
            self.noteTaker.addTrialName(self.trialEntry.currentText())

        except Exception as e:
            print(f"Couldn't Initialize Note Taking File: {e}")

    # Manual Callback for Closing Data File
    def closeDataFileCallback(self):
        print("Closing Save File...")
        try:
            # Checking if Data File Handler Exists
            if self.dataCommandSender:
                print("Plotting Trial Data...")
                
                # Plotting Trial Data for Delsys
                if 'Delsys' in self.componentTracker and self.filePlot == True:
                    command = {
                        'function' : 'plotTrialData',
                        'params' : {}
                    }
                    self.dataCommandSender.sendCommand(json.dumps(command))

                # Closing Data File
                command = {
                    'function' : 'closeFile',
                    'params' : {}
                }
                self.dataCommandSender.sendCommand(json.dumps(command))

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

        try:
            # Closing Video Outlet
            self.videoCapture.releaseOutlet()

        except Exception as e:
            print(e)
            print("Unable to Close Video Outlet")

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
        self.videoCapture.recording = True

        # Adding start time to file
        self.startTime = datetime.now()
        command = {
            'function' : 'addStartTime',
            'params' : {'startTime' : self.returnTime()}
        }
        self.dataCommandSender.sendCommand(json.dumps(command))

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
        # Stopping Data Collection
        try:
            if 'Delsys' in self.componentTracker:
                # Stopping Delsys Data Collection
                self.DelsysEMG.stopDataCollection()

        except: 
            print("Can't Stop Delsys Data Collection")

        try:
            if 'XSensor' in self.componentTracker:
                # Start Data Collection on Delsys
                self.xSensorWidget.XSensorForce.stopDataCollection()

        except:
            print('Unable to Stop XSensor Data Collection')

         # Resetting RL Buttons
        try:
            if 'RL' in self.componentTracker:
                # Resetting RL Terrains
                self.MLControl.resetTerrainButtons()
                
        except:
            print("Can't Reset RL Terrain Indications")

        self.videoCapture.recording = False
        self.recording = False

        # Adding stop time to file
        command = {
            'function' : 'addStopTime',
            'params' : {'stopTime' : self.returnTime()}
        }
        self.dataCommandSender.sendCommand(json.dumps(command))
        
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
            self.xSensorWidget.configureButton.setEnabled(True)
            self.xSensorWidget.configureButton.setStyleSheet('QPushButton {color: black;}')

        # If CheckBox Moves to Unchecked State
        else:
            # Deleting Key From Component Tracker Dictionary
            self.componentTracker.pop('XSensor')

            # Updating GUI
            self.xSensorWidget.configureButton.setEnabled(False)
            self.xSensorWidget.configureButton.setStyleSheet('QPushButton {color: grey;}') 

    def DelsysDefaultSettingsCheckedCallback(self):
        # If CheckBox Moves to Checked State
        if self.DefaultDelsysSensorsCheckBox.isChecked():
            self.componentTracker['Default Delsys'] = True

         # If CheckBox Moves to Unchecked State
        else:
            self.componentTracker.pop('Default Delsys')

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
    widget = MyWidget()
    widget.resize(400, 400)
    widget.show()
    sys.exit(app.exec())