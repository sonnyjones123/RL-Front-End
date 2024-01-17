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
    def __init__(self, numGraphs=1, sensorDict=None, EMGSensors=None, recordingRate=None):
        super().__init__()
        self.numGraphs = numGraphs
        self.sensorDict = sensorDict
        self.EMGSensors = EMGSensors
        self.bufferSize = 600
        self.samples = np.arange(-(self.bufferSize - 1), 1)
        self.sampleCount = 0
        self.plottingBuffer = np.zeros((self.numGraphs, self.bufferSize))
        self.plottingPanel = self.PlottingPanel()
        self.updateTimer = 50
        self.recordingRate = recordingRate
        
    # Initializing Plotting Widget Panel
    def PlottingPanel(self):
        plottingPanel = QWidget()

        self.plotWidget = pg.GraphicsLayoutWidget()

        # Creating Plotting Panel with numGraphs
        for numGraph in range(self.numGraphs):
            sensorMuscle = self.sensorDict[self.EMGSensors[numGraph]][1]

            exec(f"self.plot{numGraph} = self.plotWidget.addPlot(title = sensorMuscle, row = {numGraph}, col = 0)")
            # exec(f"self.plot{numGraph} = self.plotWidget.addPlot(row = {numGraph}, col = 0)")
            exec(f"self.plot{numGraph}.setTitle(sensorMuscle)")
            exec(f"self.plotItem{numGraph} = self.plot{numGraph}.plot(self.samples, self.plottingBuffer[numGraph])")
            
        return plottingPanel
    
    #-----------------------------------------------------------------------------------
    # ---- Plotting Functions

    # Plot Updater
    def plotEMG(self, data):
        """
        Updating graph widget window and data. Takea a new data data sample to the data buffer by circulating the buffer and adding the new
        data to the end of the buffer. Updates each plot with the new data.
        """

        """
        # Creating Temporary Data Length Veriable
        # Checking Dimension of Data
        if len(np.array(data).shape) == 1:
            # If Dimension is 1
            lengthNewData = len(data)
        else:
            # If Dimension is 2+
            lengthNewData = len(data[0])

        # Rotating Buffers
        self.plottingBuffer[:, (-lengthNewData - 1):-1] = data
        self.prevSampleCount = self.sampleCount
        self.sampleCount+= lengthNewData
        self.samples = np.roll(self.samples, -lengthNewData)
        self.samples[(-lengthNewData - 1):-1] = np.arange(self.prevSampleCount, self.sampleCount)
        """

        self.plottingBuffer[:, -1] = data
        self.sampleCount += 1
        self.samples = np.roll(self.samples, -1)
        self.samples[-1] = self.sampleCount
        
        # Performing Graph Update on Timer Setting
        if self.updateTimer == 50:
             for numGraph in range(self.numGraphs):
                 exec(f"self.plotItem{numGraph}.setData(self.samples, self.plottingBuffer[numGraph])")
             self.updateTimer = 0
        else:
            self.updateTimer += self.recordingRate

        self.plottingBuffer = np.roll(self.plottingBuffer, -1, axis = 1)
        # self.plottingBuffer = np.roll(self.plottingBuffer, -lengthNewData, axis = 1)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = EMGPlot()
    widget.show()
    sys.exit(app.exec())
