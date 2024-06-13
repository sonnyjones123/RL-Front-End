import sys
import numpy as np

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from RLDependencies.XSensorForce import *

class XSensorWidget(QWidget):
    """
    This is a controller for the XSensorForce class to display the XSensor data on a PySide6 GUI.
    This is used to display the data using a grid intensity graph and control the XSensor configuration
    and data collection.

    Author: Sonny Jones & Grange Simpson
    Version: 2023.11.27

    Usage:

        app = QApplication(sys.argv)
        window = XSensorWidget()
        window.show()
        sys.exit(app.exec())

    """
    def __init__(self, recordingRate):
        super().__init__()
        self.XSensorStatus = "Idle"
        self.XSensorForce = XSensorForce(recordingRate = 1000//recordingRate)
        self.sensorsConnected = 0
        self.XSensorControlPanel = self.XSensorPanel()
        self.sensorDisplayTrack = {}
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.XSensorControlPanel)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.splitter)
        self.sensorData = []
        self.frameDelay = recordingRate * 2
        self.ready = False

    #-----------------------------------------------------------------------------------
    # ---- XSensor Control and Display Widget

    def XSensorPanel(self):
        # Panel Layout
        XSensorPanel = QWidget()
        XSensorPanelLayout = QVBoxLayout()
        XSensorPanel.setFixedSize(400, 170)

        # Panel Label
        self.XSensorPanelLabel = QLabel("<b>XSensor Force Insoles</b>", alignment = Qt.AlignCenter)
        self.XSensorPanelLabel.setStyleSheet('QLabel {color: black; font-size: 20px}')
        XSensorPanelLayout.addWidget(self.XSensorPanelLabel)

        # Status Panel
        self.XSensorStatusLabel = QLabel("<b>XSensor Status: " + self.XSensorStatus, alignment = Qt.AlignCenter)
        self.XSensorStatusLabel.setStyleSheet('QLabel {color: black;}')
        XSensorPanelLayout.addWidget(self.XSensorStatusLabel)
        
        # Sensors Connected
        self.sensorsConnected = QLabel("<b>Sensors Connected: " + str(self.sensorsConnected), alignment = Qt.AlignCenter)
        self.sensorsConnected.setStyleSheet('QLabel {color: black;}')
        XSensorPanelLayout.addWidget(self.sensorsConnected)

        # Configure Button
        self.configureButton = QPushButton("Configure", self)
        self.configureButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.configureButton.objectName = 'Configure Button'
        self.configureButton.clicked.connect(self.configureXSensorCallback)
        self.configureButton.setEnabled(False)
        XSensorPanelLayout.addWidget(self.configureButton)

        # Connect Button
        self.connectButton = QPushButton("Connect", self)
        self.connectButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.connectButton.objectName = 'Start Button'
        self.connectButton.clicked.connect(self.connectXSensorCallback)
        self.connectButton.setStyleSheet("color: grey")
        self.connectButton.setEnabled(False)
        XSensorPanelLayout.addWidget(self.connectButton)

        # Setting Panel Layout
        XSensorPanel.setLayout(XSensorPanelLayout)

        return XSensorPanel
    
    def XSensorDisplay(self, sensor):
        SensorDisplayPanel = QWidget()
        SensorDisplayLayout = QVBoxLayout()
        SensorDisplayLayout.setAlignment(Qt.AlignTop)
        SensorDisplayPanel.setFixedSize(220, 620)

        # Sensor Display Label
        self.sensorDisplayLabel = QLabel(f"<b>Insole {sensor + 1}</b>", alignment = Qt.AlignCenter)
        self.sensorDisplayLabel.setStyleSheet('QLabel {color: black;}')
        SensorDisplayLayout.addWidget(self.sensorDisplayLabel)

        # Creating QLabel array
        sensorLabel = QLabel()
        sensorLabel.setAlignment(Qt.AlignCenter)
        self.sensorDisplayTrack[sensor] = sensorLabel

        # Adding to Sensor Display Panel
        SensorDisplayLayout.addWidget(sensorLabel)

        # Setting Layout as Panel
        SensorDisplayPanel.setLayout(SensorDisplayLayout)

        return SensorDisplayPanel

    #-----------------------------------------------------------------------------------
    # ---- XSensor Control Callbacks

    # Configure Callback
    def configureXSensorCallback(self):
        try:
            self.XSensorForce.configure()
            self.XSensorStatus = "Configured"
            self.XSensorStatusLabel.setText("<b> XSensor Status: " + self.XSensorStatus)
            self.configureButton.setStyleSheet("color: black")

            # Setting Metadata for Insoles
            self.numRows = self.XSensorForce.senselRows.value
            self.numCols = self.XSensorForce.senselColumns.value
            self.minValue = self.XSensorForce.minPressureRange.value
            # self.maxValue = self.XSensorForce.maxPressureRange.value
            self.maxValue = 40

            # Adding Display
            for sensor in range(self.XSensorForce.numSensors):
                # Checking if Panel already exists
                sensorDisplay = self.XSensorDisplay(sensor)
                self.splitter.addWidget(sensorDisplay)

            # Adding Dummy Data
            self.updateDisplayInit()

        except Exception as e:
            print(e)
            self.XSensorStatus = "Configure Failed"
            self.XSensorStatusLabel.setText("<b> XSensor Status: " + self.XSensorStatus)

        # Updating Sensor Num
        self.numSensors = self.XSensorForce.numSensors
        self.sensorsConnected.setText("<b> Sensors Connected: " + str(self.numSensors))

        # Updating Connect Button
        self.connectButton.setEnabled(True)
        self.connectButton.setStyleSheet("color: black")

        """
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("color: black")

        self.quitButton.setEnabled(True)
        self.quitButton.setStyleSheet("color: black")
        """
        
    # Start Data Collection Callback
    def connectXSensorCallback(self):
        try:
            status = self.XSensorForce.connect()
            if status:
                """
                self.processDataButton.setEnabled(True)
                self.processDataButton.setStyleSheet("color: black")
                self.quitButton.setEnabled(True)
                self.quitButton.setStyleSheet("color: black")
                """
                
                self.XSensorStatus = "Connected"
                self.XSensorStatusLabel.setText("<b> XSensor Status: " + self.XSensorStatus)
                self.ready = True
        except:
            pass

    # Sensor Update Status
    def updateSensorStatus(self):
        self.XSensorStatus = "Running"
        self.XSensorStatusLabel.setText("<b> XSensor Status: " + self.XSensorStatus)

    # Data Processing Callback
    def processDataCallback(self):
        self.XSensorForce.processData()

    # Clearing Data Buffer
    def resetBuffer(self):
        self.XSensorForce.resetBuffer()

    # Stop Data Collection
    def stopDataCollection(self):
        self.XSensorForce.stopDataCollection()
        self.XSensorStatus = "Connected"
        self.XSensorStatusLabel.setText("<b> XSensor Status: " + self.XSensorStatus)

    # Releasing and Quitting Callback
    def releaseAndQuit(self):
        self.XSensorForce.releaseConfig()
        self.XSensorForce.quit()

    #-----------------------------------------------------------------------------------
    # ---- XSensor Display Callbacks

    # Getting color for display
    def getQImage(self, data):
        # Resetting Normalization
        self.maxValue = np.max(data) if np.max(data) > self.maxValue else self.maxValue
        mappedValue = abs((data - self.minValue) / (self.maxValue - self.minValue))
        
        # Creating Color Mapping (RGBA)
        colormap = np.zeros((data.shape[0], data.shape[1], 4), dtype = np.uint8)

        # Applying Mapping
        colormap[..., 0] = (255 * (1 - mappedValue)).astype(np.uint8)  # Red channel
        colormap[..., 1] = (255 * (1 - mappedValue)).astype(np.uint8)  # Green channel
        colormap[..., 2] = 255  # Blue channel (always 255 for blue)
        colormap[..., 3] = 255  # Alpha channel (fully opaque)

        # Converting to QImage
        height, width, channels = colormap.shape
        bytesPerLine = channels * width
        qImage = QImage(colormap.data, width, height, bytesPerLine, QImage.Format_RGBA8888)

        # Scaling Image
        return qImage.scaled(220, 620, Qt.KeepAspectRatio)
    
    # Updating Display for Example Sizes
    def updateDisplayInit(self):
        try:
            for sensorID, label in self.sensorDisplayTrack.items():
                # Getting Data From Sensor
                data = np.zeros((31, 11))

                # Creating Pixmap
                qImage = self.getQImage(data)
                pixmap = QPixmap.fromImage(qImage)

                # Setting Pixmap
                label.setPixmap(pixmap)

        except Exception as e:
            print(f"Error updating XSensor Display: {e}")

    # Display Update Function
    def updateDisplay(self):
        try:
            # Looping Through Each Sensor
            for sensorID, label in self.sensorDisplayTrack.items():
                # Getting Data From Sensor
                data = np.array(self.XSensorForce.data[sensorID])

                # Reshapping Data
                reshappedData = data.reshape(31,11)

                # Creating Pixmap
                qImage = self.getQImage(reshappedData)
                pixmap = QPixmap.fromImage(qImage)

                # Setting Pixmap
                label.setPixmap(pixmap)

        except Exception as e:
            print(f"Error updating XSensor Display: {e}")

    #-----------------------------------------------------------------------------------
    # ---- Archived

        """
        # Process Data Button
        self.processDataButton = QPushButton("Process Data", self)
        self.processDataButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.processDataButton.objectName = 'Process Data Button'
        self.processDataButton.clicked.connect(self.processDataCallback)
        self.processDataButton.setStyleSheet("color: grey")
        self.processDataButton.setEnabled(False)
        XSensorPanelLayout.addWidget(self.processDataButton)

        # Stop Button
        self.stopButton = QPushButton("Stop", self)
        self.stopButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stopButton.objectName = 'Stop Button'
        self.stopButton.clicked.connect(self.stopDataCollection)
        self.stopButton.setStyleSheet("color: grey")
        self.stopButton.setEnabled(False)
        XSensorPanelLayout.addWidget(self.stopButton)

        # Quit Button
        self.quitButton = QPushButton("Quit", self)
        self.quitButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.quitButton.objectName = 'Quit Button'
        self.quitButton.clicked.connect(self.XSensorForce.quit)
        self.quitButton.setStyleSheet("color: grey")
        self.quitButton.setEnabled(False)
        XSensorPanelLayout.addWidget(self.quitButton)
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XSensorWidget()
    window.show()
    sys.exit(app.exec())