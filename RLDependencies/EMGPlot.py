import pyqtgraph as pg
import numpy as np
import sys
import time
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class EMGPlot(QWidget):
    """
    This is a live plot widget created to support the DelsysEMG class to visualize incoming EMG
    signals in real time. This class dynamically allocates plots based on the information from 
    DelsysEMG.configure(). 

    Author: Sonny Jones & Grange Simpson
    Version: 2023.11.10

    Usage: Check RL Front End, configureCallback Function

    """
    def __init__(self, numGraphs=1, sensorDict=None, sensorNames=None, EMGSensors=None, recordingRate=None):
        super().__init__()
        self.numGraphs = numGraphs
        self.sensorDict = sensorDict
        self.sensorNames = sensorNames
        self.EMGSensors = EMGSensors
        self.bufferSize = 600
        self.samples = np.arange(-(self.bufferSize - 1), 1)
        self.sampleCount = 0
        self.plottingBuffer = np.zeros((self.numGraphs, self.bufferSize))
        self.plottingPanel = self.PlottingPanel()
        self.updateTimer = recordingRate * 2
        self.frameDelay = recordingRate * 2
        self.recordingRate = recordingRate
        
    # Initializing Plotting Widget Panel
    def PlottingPanel(self):
        plottingPanel = QWidget()
        plottingLayout = QVBoxLayout()
        plottingPanel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Creating List of Items for Display
        self.sensorDisplayList = []

        # Iterative Through
        for i in range(self.numGraphs):
            # Grabbing Information from sensorDict
            sensorNumber = self.sensorNames.index(self.EMGSensors[i]) + 1
            sensorMuscle = self.sensorDict[self.EMGSensors[i]][1]

            self.sensorDisplayList.append(f"Sensor {sensorNumber} : {sensorMuscle}")

        # Sensor Selection
        self.sensorDisplaySelection = QComboBox(self)
        self.sensorDisplaySelection.addItems(self.sensorDisplayList)
        self.sensorDisplaySelection.currentIndexChanged.connect(self.updateEMGPlot)

        # Creating Plotting Widget
        self.plotWidget = pg.GraphicsLayoutWidget()
        self.plot = self.plotWidget.addPlot()
        # If only goniometers are being used
        if (len(self.sensorDisplayList) > 0):
            self.plot.setTitle(self.sensorDisplayList[0])
            self.plotItem = self.plot.plot(self.samples, self.plottingBuffer[0])

        # Current Plot
        self.currentPlot = 0

        # Setting Size Constraints
        self.plotWidget.setMaximumSize(800, 500)
        self.plotWidget.setMinimumSize(600, 500)
        plottingLayout.addWidget(self.plotWidget)
        plottingLayout.addWidget(self.sensorDisplaySelection)

        # Adding Layout
        plottingLayout.setContentsMargins(0, 0, 0, 0)
        plottingLayout.setSpacing(0)
        plottingPanel.setLayout(plottingLayout)

        return plottingPanel
    
    #-----------------------------------------------------------------------------------
    # ---- Plotting Functions

    # Plot Updater
    def plotEMG(self, data):
        """
        Updating graph widget window and data. Takea a new data data sample to the data buffer by circulating the buffer and adding the new
        data to the end of the buffer. Updates each plot with the new data.
        """

        self.plottingBuffer[:, -1] = data
        self.sampleCount += 1
        self.samples = np.roll(self.samples, -1)
        self.samples[-1] = self.sampleCount
        
        # Performing Graph Update on Timer Setting
        if self.updateTimer >= self.frameDelay:
            self.plotItem.setData(self.samples, self.plottingBuffer[self.currentPlot])
            self.updateTimer = 0
        
        # Upadting Plotting Timer
        self.updateTimer += self.recordingRate

        self.plottingBuffer = np.roll(self.plottingBuffer, -1, axis = 1)

    # Updating Current Plot
    def updateEMGPlot(self):
        # Updating Current Plot Index and Title
        self.currentPlot = self.sensorDisplayList.index(self.sensorDisplaySelection.currentText())
        self.plot.setTitle(self.sensorDisplaySelection.currentText())

    # Resetting Plot
    def resetPlot(self):
        # Resetting Tracking Variables
        self.samples = np.arange(-(self.bufferSize - 1), 1)
        self.sampleCount = 0
        self.plottingBuffer = np.zeros((self.numGraphs, self.bufferSize))

        # Clearing Plot
        self.plotItem.clear()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = EMGPlot()
    widget.show()
    sys.exit(app.exec())
