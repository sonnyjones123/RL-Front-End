"""
This is the main Reinforcement Learning GUI that incorperates the DelsyEMG control class, EMGPlot class, Computer Vision class, 
and XSensor Control Class. This GUI is used to control each data acqusition device and create a pipeline for saving data in real time.

Written by Sonny Jones & Grange Simpson
Version: 2023.11.10

Usage: Run the file.

"""

import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from functools import partial
import threading
import csv
from datetime import date

from RLDependencies.EMGPlot import *
from RLDependencies.DelsysEMG import *
from RLDependencies.OpenCVWidget import *
from RLDependencies.XSensorWidget import *

class DataCollector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.data = []
        self.running = True

    def stop(self):
        self.running = False

    def save_to_csv(self, data, filename):
        with open(filename, 'a', newline='\n') as csvfile:
            writer = csv.writer(csvfile)
            #writer.writerow(['Collected Data'])
            for value in data:
                writer.writerow([value])

class MyWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Recording Params
        self.recording = False

        # Creating Widgets from Subclasses
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.DataControlPanel = self.dataControlPanel()
        layout = QHBoxLayout()
        collectionLayout = QVBoxLayout()
        layout.addWidget(self.DataControlPanel)
        self.DelsysEMG = DelsysEMG() 
        self.DelsysButtonPanel = self.delsysButtonPanel()
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.DelsysButtonPanel)
        self.EMGPlot = None
        self.videoCapture = VideoWidget()
        self.splitter.addWidget(self.videoCapture)
        self.setStyleSheet("background-color:#f5e1fd;")
        collectionLayout.addWidget(self.splitter)
        self.xSensorWidget = XSensorWidget()
        collectionLayout.addWidget(self.xSensorWidget)
        collectionWidget = QWidget()
        collectionWidget.setLayout(collectionLayout)
        layout.addWidget(collectionWidget)
        self.setWindowTitle("Data Collection GUI")
        self.centralWidget.setLayout(layout)

        # QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.dataProcessing)
        self.timer.start(1)
        self.videoTimer = self.videoCapture.frameDelay
        self.xSensorTimer = self.xSensorWidget.frameDelay

        # QElapsedTimer
        self.dataCollectionTimer = QElapsedTimer()

    
    #-----------------------------------------------------------------------------------
    # ---- Data Saving Panel
    def dataControlPanel(self):
        dataControlPanel = QWidget()
        dataControlLayout = QVBoxLayout()
        dataControlPanel.setFixedSize(400, 150)

        # Data Collection Label
        self.dataCollectionLabel = QLabel("<b>Data Collection</b>", alignment = Qt.AlignCenter)
        self.dataCollectionLabel.setStyleSheet('QLabel {color: black; font-size: 24px;}')
        dataControlLayout.addWidget(self.dataCollectionLabel)

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

        # Save Collected Data Button
        self.saveCollectedDataButton = QPushButton("Save Trial Data", self)
        self.saveCollectedDataButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.saveCollectedDataButton.objectName = 'Save Collection'
        self.saveCollectedDataButton.clicked.connect(self.saveDataCollectionCallback)
        self.saveCollectedDataButton.setStyleSheet('color: grey;')
        self.saveCollectedDataButton.setEnabled(False)
        dataCollectionButtonLayout.addWidget(self.saveCollectedDataButton)

        # Adding Collection Panel to Main
        dataControlLayout.addLayout(dataCollectionButtonLayout)

        # Setting Layout
        dataControlPanel.setLayout(dataControlLayout)

        return dataControlPanel

    #-----------------------------------------------------------------------------------
    # ---- Delsys Control Widget

    def delsysButtonPanel(self):
        delsysButtonPanel = QWidget()
        delsysButtonLayout = QVBoxLayout()
        delsysButtonPanel.setFixedSize(400, 500)
        
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
        self.connectButton.setStyleSheet('QPushButton {color: black;}')
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
        self.sensorSelectedDisplay = QLabel("Sensors Selected: " + str(self.sensorsSelected))
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
                self.DelsysEMG.processData()
                averageEMG = self.DelsysEMG.plotEMGGUI()
                self.EMGPlot.plotEMG(averageEMG)

                if self.xSensorTimer >= self.xSensorWidget.frameDelay:
                    self.xSensorWidget.processDataCallback()
                    self.xSensorTimer = 0
                else:
                    self.xSensorTimer += 1
            except Exception as e:
                print(e)
        
        # Video Processing
        if self.videoTimer >= self.videoCapture.frameDelay:
            self.videoCapture.dataProcessing()
            self.videoTimer = 0
        else:
            self.videoTimer += 1
    
    # Function to add and remove sensors from the sensor list on button press
    def button_grid_press(self, value):
        try:
            if (self.sensorsSelected.count(int(value)) > 0):
                valInd = self.sensorsSelected.index(int(value))
                self.sensorsSelected.pop(valInd)
            else:
                valInd = self.sensorsSelected.index(int(value))

        except:
            self.sensorsSelected.append(int(value))

        # Updating Sensor List
        self.sensorSelectedDisplay.setText("Sensors Selected: " + str(self.sensorsSelected))

    #-----------------------------------------------------------------------------------
    # ---- Callback Functions

    # Delsys Connection Callback
    def connectCallback(self):
        self.connectButton.setEnabled(False)
        self.connectButton.setStyleSheet("color: grey")
        self.DelsysEMG.connect()

        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.pairSensorButton.setEnabled(True)
        self.pairSensorButton.setStyleSheet('QPushButton {color: black;}')
        self.scanSensorButton.setEnabled(True)
        self.scanSensorButton.setStyleSheet('QPushButton {color: black;}')
    
    # Delsys Pair Sensor Callback
    def pairSensorCallback(self):
        self.DelsysEMG.connectSensors(self.sensorNumber.text())

        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.selectSensorButton.setEnabled(True)
        self.selectSensorButton.setStyleSheet('QPushButton {color: black;}')
        self.selectAllSensorButton.setEnabled(True)
        self.selectAllSensorButton.setStyleSheet('QPushButton {color: black;}')
        self.resetSensorSelection.setEnabled(True)
        self.resetSensorSelection.setStyleSheet('QPushButton {color: black;}')

    # Delsys Scan Sensor Callback
    def scanSensorCallback(self):
        self.DelsysEMG.connectSensors(0)

        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.selectSensorButton.setEnabled(True)
        self.selectSensorButton.setStyleSheet('QPushButton {color: black;}')
        self.selectAllSensorButton.setEnabled(True)
        self.selectAllSensorButton.setStyleSheet('QPushButton {color: black;}')
        self.resetSensorSelection.setEnabled(True)
        self.resetSensorSelection.setStyleSheet('QPushButton {color: black;}')

    # Delsys Select Sensor Callback
    def selectSensorCallback(self):
        for sensor in self.sensorsSelected:
            self.DelsysEMG.selectSensor(sensor)

        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.setSampleMode.setEnabled(True)
        self.setSampleMode.setStyleSheet('QPushButton {color: black;}')
        self.setAllSampleMode.setEnabled(True)
        self.setAllSampleMode.setStyleSheet('QPushButton {color: black;}')

    # Delsys Select All Sensor Callback
    def selectAllSensorCallback(self):
        self.DelsysEMG.selectAllSensors()

        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.setSampleMode.setEnabled(True)
        self.setSampleMode.setStyleSheet('QPushButton {color: black;}')
        self.setAllSampleMode.setEnabled(True)
        self.setAllSampleMode.setStyleSheet('QPushButton {color: black;}')

    # Reset Sensor Selection Callback
    def resetSensorSelectionCallback(self):
        self.sensorsSelected.clear()
        self.sensorSelectedDisplay.setText("Sensors Selected: " + str(self.sensorsSelected))

    # Set Sample Mode Callback
    def setSampleModeCallback(self):
        self.DelsysEMG.setSampleMode(self.sensorsSelected, self.sensorModeDropdown.currentText())

        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.configureButton.setEnabled(True)
        self.configureButton.setStyleSheet('QPushButton {color: black;}')

    # Set All Sample Mode Callback
    def setAllSampleModeCallback(self):
        self.DelsysEMG.setAllSampleModes(self.sensorModeDropdown.currentText())

        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.configureButton.setEnabled(True)
        self.configureButton.setStyleSheet('QPushButton {color: black;}')

    # Configure Callback
    def configureCallback(self):
        self.DelsysEMG.configure()

        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        self.startDataCollectionButton.setEnabled(True)
        self.startDataCollectionButton.setStyleSheet('QPushButton {color: black;}')

        # Adding Sensor Plots
        if self.EMGPlot is None:
            self.EMGPlot = EMGPlot(self.DelsysEMG.numEMGChannels, self.DelsysEMG.sensorDict, self.DelsysEMG.EMGSensors)
            self.splitter.insertWidget(1, self.EMGPlot.plotWidget)
            widget.resize(1700, 400)

    # Start Data Collection Callback
    def startDataCollectionCallback(self):
        self.DelsysEMG.startDataCollection()
        self.recording = True
        self.videoCapture.recording = True

        self.stopDataCollectionButton.setEnabled(True)
        self.stopDataCollectionButton.setStyleSheet("QPushButton {color: black;}")
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        
        self.saveCollectedDataButton.setEnabled(False)
        self.saveCollectedDataButton.setStyleSheet("QPushButton {color: grey;}")

        self.dataCollectionTimer.start()

    # Stop Data Collection Callback
    def stopDataCollectionCallback(self):
        self.DelsysEMG.stopDataCollection()
        self.videoCapture.recording = False
        self.recording = False
        self.xSensorWidget.stopDataCollection()
        self.delsysStatus.setText("<b>Delsys Status: </b>" + self.DelsysEMG.status)
        
        self.saveCollectedDataButton.setEnabled(True)
        self.saveCollectedDataButton.setStyleSheet("QPushButton {color: black;}")

        self.timeElapsed = self.dataCollectionTimer.elapsed()

    def saveDataCollectionCallback(self):
        print("called")
        fileName = simpledialog.askstring(title = 'Trial File Name Input',
                                                          prompt = 'Please provide a name for this trial (no file extension or date).')
        #fileName = self.openDialog('Trial File Name Input', 'Please provide a name for this trial (no file extension or date).')
        self.dataCollector = DataCollector()
        self.dataCollector.start()

        # Creating Timeseries
        self.timeSeriesGeneration()

        # Saving to a file
        if self.dataCollector:
            today = date.today()
            self.dataCollector.save_to_csv(self.DelsysEMG.returnAllData(), str(fileName) + '_' + str(today) +'.csv')

        if self.dataCollector is not None:
            self.dataCollector.stop()
            self.dataCollector.join()
            self.dataCollector = None

    def timeSeriesGeneration(self):
        """
        Generating Time Series For Export
        """
        # Creating array to track channel generation
        self.timeSeriesTracker = []

        # Looping through Channel Names
        for index, channel in enumerate(self.DelsysEMG.channelNames):
            chanName = str.split(channel, " ")[0]
            if chanName not in self.timeSeriesTracker:
                self.timeSeriesTracker.append(chanName)
                if chanName == "EMG":
                    self.EMGTimeSeries = np.arange(0, self.timeElapsed, len(self.DelsysEMG.DataHandler.allcollectiondata[index]))
                if chanName == "GYRO":
                    self.GYROTimeSeries = np.arange(0, self.timeElapsed, len(self.DelsysEMG.DataHandler.allcollectiondata[index]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.resize(400, 400)
    widget.show()
    sys.exit(app.exec())
