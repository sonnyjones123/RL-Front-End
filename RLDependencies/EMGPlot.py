import pyqtgraph as pg
import numpy as np
import sys
import time
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class EMGPlot(QWidget):
    def __init__(self, numGraphs=1):
        super().__init__()
        self.numGraphs = numGraphs
        self.bufferSize = 5000
        self.samples = np.arange(-(self.bufferSize - 1), 1)
        self.sampleCount = 0
        self.plottingBuffer = np.zeros((self.numGraphs, self.bufferSize))
        self.plottingPanel = self.PlottingPanel()
        
    def PlottingPanel(self):
        plottingPanel = QWidget()

        self.plotWidget = pg.GraphicsLayoutWidget()

        # Creating Plotting Panel with numGraphs
        for numGraph in range(self.numGraphs):
            exec(f"self.plot{numGraph} = self.plotWidget.addPlot(row = {numGraph}, col = 0)")
            exec(f"self.plotItem{numGraph} = self.plot{numGraph}.plot(self.samples, self.plottingBuffer[numGraph])")

        return plottingPanel
    
    #-----------------------------------------------------------------------------------
    # ---- Plotting Functions

    # Plot Updater
    def plotEMG(self, data):
        self.plottingBuffer[:, -1] = data
        self.sampleCount += 1
        self.samples = np.roll(self.samples, -1)
        self.samples[-1] = self.sampleCount
        for numGraph in range(self.numGraphs):
            exec(f"self.plotItem{numGraph}.setData(self.samples, self.plottingBuffer[numGraph])")

        self.plottingBuffer = np.roll(self.plottingBuffer, -1, axis = 1)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = EMGPlot()
    widget.show()
    sys.exit(app.exec())
