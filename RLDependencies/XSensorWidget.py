import sys
import ctypes

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
    def __init__(self):
        super().__init__()
        self.XSensorStatus = "Idle"
        self.XSensorForce = XSensorForce()
        self.sensorsConnected = 0
        self.XSensorControlPanel = self.XSensorPanel()
        self.sensorDisplayTrack = []
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.XSensorControlPanel)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.splitter)
        self.sensorData = []
        self.frameDelay = 1000/self.XSensorForce.targetRateHz
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
        SensorDisplayPanel.setFixedSize(220, 620)

        # Sensor Display Label
        self.sensorDisplayLabel = QLabel(f"<b>Insole {sensor + 1}</b>", alignment = Qt.AlignCenter)
        self.sensorDisplayLabel.setStyleSheet('QLabel {color: black;}')
        SensorDisplayLayout.addWidget(self.sensorDisplayLabel)
        
        # Creating Sensor Grid
        sensorGridLayout = QGridLayout()

        # Creating QLabel array
        exec(f"self.sensorLabel{sensor} = []")

        # Creating Sensor Display Grid
        for i in range(self.numRows):
            rowLabels = []
            for j in range(self.numCols):
                sensorWidget = QLabel()
                sensorWidget.setAutoFillBackground(True)
                sensorWidget.setStyleSheet("background-color: black;")
                sensorWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
                sensorWidget.setMaximumSize(20, 20)
                sensorWidget.setMinimumSize(20, 20)
                sensorGridLayout.addWidget(sensorWidget, i, j)
                rowLabels.append(sensorWidget)
            exec(f"self.sensorLabel{sensor}.append(rowLabels)")
        
        # Setting Size Constraints
        sensorGridLayout.setHorizontalSpacing(1)
        sensorGridLayout.setVerticalSpacing(1)

        # Adding Sensor Grid to Layout
        SensorDisplayLayout.addLayout(sensorGridLayout)

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
                if f"XSensorVisualPanel{sensor}" not in self.sensorDisplayTrack:
                    # Creating panel
                    exec(f"self.XSensorVisualPanel{sensor} = self.XSensorDisplay({sensor})")
                    exec(f"self.splitter.addWidget(self.XSensorVisualPanel{sensor})")
                    self.sensorDisplayTrack.append(f"XSensorVisualPanel{sensor}")

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
        self.updateDisplay()

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
    def getColor(self, value):
        if value > self.maxValue:
            self.maxValue = value
        mappedValue = abs((value - self.minValue) / (self.maxValue - self.minValue))
        return QColor(int(255 * mappedValue), int(255 * (1 - mappedValue)), 0)

    # Display Update Function
    def updateDisplay(self):
        try:
            for sensor in range(self.XSensorForce.numSensors):
                for row in range(self.numRows):
                    for col in range(self.numCols):
                        value = self.XSensorForce.dataBuffer[sensor][row * self.numCols + col]
                        color = self.getColor(value)
                        exec(f"self.sensorLabel{sensor}[row][col].setStyleSheet('background-color: {color.name()};')")
        except Exception as e:
            print(e)
            print("Could not update XSensor display")

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