import sys
import platform
import ctypes
import pyqtgraph as pg
import numpy as np

from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

# Adding path for current computer
# Please add your computer name and path to the Python API folder for delsys.
if (platform.node() == "Garangatan_Comp"):
    sys.path.insert(0, "C:/Users/grang/Box/NeuroRoboticsLab/NERVES Lab/Project Groups/ML Gait/Software/Algorithms")
elif (platform.node() == "Sonny_ThinkPad"):
    sys.path.insert(0, "C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Project Groups/ML Gait/Software/Algorithms")
elif (platform.node() == 'Purkinje'):
    sys.path.insert(0, "C:/Users/Purkinje/Box/NeuroRoboticsLab/NERVES Lab/Project Groups/ML Gait/Software/Algorithms")

from TOTD import TOTD
from SwiftTD import SwiftTD

class RLWidget(QWidget):
    """
    This is the GUI controller for the TOTD Class. The TOTD class contains the implementation of True Online Temporal
    Difference Learning (TOTD) with Selective Kanerva Coding for feature representation. 

    Author: Sonny Jones & Grange Simpson
    Version: 2024.04.13

    Usage:
        app = QApplication(sys.argv)
        window = TOTDWidget()
        window.show()
        sys.exit(app.exec())

    """
    def __init__(self, recordingRate):
        super().__init__()

        # RL Algorithm Tracker
        self.algorithms = {}
        self.predictionStatus = 'Disabled'
        self.predict = False
        self.currentTerrain = None

        # Tracking for Transition Saving
        self.terrainList = ['Even Ground', 'Uneven Ground', 'UpStairs', 'DownStairs', 'UpRamp', 'DownRamp', 'Turn']
        self.currentTerrainList = np.zeros(len(self.terrainList))

        # Plotting
        self.numberOfTerrains = 7
        self.bufferSize = 100
        self.predPlottingBuffer = np.zeros((self.numberOfTerrains, self.bufferSize))
        self.terrainPlottingBuffer = np.zeros((self.numberOfTerrains, self.bufferSize))
        self.samples = np.arange(-(self.bufferSize - 1), 1)
        self.sampleCount = 0

        # Updating Timer for Plotting
        self.updateTimer = 50
        self.recordingRate = recordingRate

        # Widget Components
        self.RLControlPanel = self.RLPanel()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.RLControlPanel)
        
    #-----------------------------------------------------------------------------------
    # ---- TOTD Control and Display Widget

    def RLPanel(self):
        # Panel Layout
        RLPanel = QWidget()
        RLPanel.setFixedSize(300, 530)
        RLPanelLayout = QVBoxLayout()
        RLPanelLayout.setAlignment(Qt.AlignTop)

        # Panel Label
        self.TOTDPanelLabel = QLabel("<b>RL Control Panel</b>", alignment = Qt.AlignCenter)
        self.TOTDPanelLabel.setStyleSheet('QLabel {color: black; font-size: 24px}')
        RLPanelLayout.addWidget(self.TOTDPanelLabel)

        # Prediciton Status
        self.RLStatusLabel = QLabel("<b>Status: </b>" + self.predictionStatus, alignment = Qt.AlignCenter)
        self.RLStatusLabel.setStyleSheet('QLabel {color: black;}')
        RLPanelLayout.addWidget(self.RLStatusLabel)

        # Predicting Checkmark
        # self.predictionCheckmark = QCheckBox("Predictions", self)
        # self.predictionCheckmark.objectName = 'Prediction Checkmark'
        # self.predictionCheckmark.clicked.connect(self.predCheckCallback)
        # self.predictionCheckmark.setEnabled(True)
        # RLPanelLayout.addWidget(self.predictionCheckmark)

        # Study ID Label
        self.studyIDLabel = QLabel("<b>Enter Study ID:</b>")
        self.studyIDLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.studyIDLabel.setStyleSheet('QLabel {color: black;}')
        RLPanelLayout.addWidget(self.studyIDLabel)

        # Study ID TextBox
        self.studyIDTextbox = QLineEdit(self)
        self.studyIDTextbox.setAlignment(Qt.AlignCenter)
        self.studyIDTextbox.setText("Default Study ID")
        self.studyIDTextbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.studyIDTextbox.objectName = 'Study ID'
        self.studyIDTextbox.setStyleSheet('QLineEdit {color: grey;}')
        self.studyIDTextbox.setEnabled(False)
        RLPanelLayout.addWidget(self.studyIDTextbox)

        # Algorithm Heading
        self.algorithmsLabel = QLabel("<b>Algorithms:</b>", alignment = Qt.AlignCenter)
        self.algorithmsLabel.setStyleSheet('QLabel {color: black;}')
        RLPanelLayout.addWidget(self.algorithmsLabel)

        # TOTD CheckBox
        self.TOTDCheckBox = QCheckBox("TOTD", self)
        self.TOTDCheckBox.objectName = 'TOTD Checkbox'
        self.TOTDCheckBox.clicked.connect(self.TOTDCheckBoxCallback)
        self.TOTDCheckBox.setEnabled(False)
        RLPanelLayout.addWidget(self.TOTDCheckBox)

        # TOTD CheckBox
        self.SwiftTDCheckBox = QCheckBox("SwiftTD", self)
        self.SwiftTDCheckBox.objectName = 'SwitftTD Checkbox'
        self.SwiftTDCheckBox.clicked.connect(self.SwiftTDCheckBoxCallback)
        self.SwiftTDCheckBox.setEnabled(False)
        RLPanelLayout.addWidget(self.SwiftTDCheckBox)

        # Configure Button
        self.configureRL = QPushButton("Configure")
        self.configureRL.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.configureRL.objectName = 'Study ID'
        self.configureRL.setStyleSheet('QPushButton {color: grey;}')
        self.configureRL.clicked.connect(self.configureLearningCallback)
        self.configureRL.setEnabled(False)
        RLPanelLayout.addWidget(self.configureRL)

        # Terrain Transitions
        self.terrainTransitions = QLabel("<b>Terrain Transitions</b>", alignment = Qt.AlignCenter)
        self.terrainTransitions.setStyleSheet('QLabel {color: black; font-size: 20px}')
        RLPanelLayout.addWidget(self.terrainTransitions)

        # Current Terrain Label
        self.terrainLabel = QLabel(f"<b>Current Terrain: </b>{self.currentTerrain}", alignment = Qt.AlignCenter)
        self.terrainLabel.setStyleSheet('QLabel {color: black;}')
        RLPanelLayout.addWidget(self.terrainLabel)

        # Terrain Indication Buttons
        # Flat Even Ground Button
        self.evenGroundButton = QPushButton("Even Ground", self)
        self.evenGroundButton.objectName = 'Even Ground Button'
        self.evenGroundButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.evenGroundButton.clicked.connect(self.evenGroundButtonCallback)
        self.evenGroundButton.setEnabled(False)
        RLPanelLayout.addWidget(self.evenGroundButton)

        # Uneven Ground Button
        self.unevenGroundbutton = QPushButton("Uneven Ground", self)
        self.unevenGroundbutton.objectName = 'Uneven Ground Button'
        self.unevenGroundbutton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.unevenGroundbutton.clicked.connect(self.unevenGroundButtonCallback)
        self.unevenGroundbutton.setEnabled(False)
        RLPanelLayout.addWidget(self.unevenGroundbutton)

        # Up Stair Button
        self.upStairButton = QPushButton("Up Stairs", self)
        self.upStairButton.objectName = 'Up Stair Button'
        self.upStairButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.upStairButton.clicked.connect(self.upStairButtonCallback)
        self.upStairButton.setEnabled(False)
        RLPanelLayout.addWidget(self.upStairButton)

        # Down Stair Button
        self.downStairButton = QPushButton("Down Stairs", self)
        self.downStairButton.objectName = 'Down Stair Button'
        self.downStairButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.downStairButton.clicked.connect(self.downStairButtonCallback)
        self.downStairButton.setEnabled(False)
        RLPanelLayout.addWidget(self.downStairButton)

        # Up Ramp Buton
        self.upRampButton = QPushButton("Up Ramp", self)
        self.upRampButton.objectName = 'Up Ramp Button'
        self.upRampButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.upRampButton.clicked.connect(self.upRampButtonCallback)
        self.upRampButton.setEnabled(False)
        RLPanelLayout.addWidget(self.upRampButton)

        # Down Ramp Buton
        self.downRampButton = QPushButton("Down Ramp", self)
        self.downRampButton.objectName = 'Down Ramp Button'
        self.downRampButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.downRampButton.clicked.connect(self.downRampButtonCallback)
        self.downRampButton.setEnabled(False)
        RLPanelLayout.addWidget(self.downRampButton)

        # Turn Button
        self.turnButton = QPushButton("Turn", self)
        self.turnButton.objectName = 'Turn Button'
        self.turnButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.turnButton.clicked.connect(self.turnButtonCallback)
        self.turnButton.setEnabled(False)
        RLPanelLayout.addWidget(self.turnButton)


        # Setting Panel Layout
        RLPanel.setLayout(RLPanelLayout)

        return RLPanel
    
    #-----------------------------------------------------------------------------------
    # ---- TOTD Control Callbacks

    def predCheckCallback(self, value):
        # If CheckBox Moves to Checked State
        if value == True:
            # Moving Status to Enabled
            self.predictionStatus = 'Enabled'

            # Checking GUI Enabled
            self.studyIDTextbox.setEnabled(True)
            self.studyIDTextbox.setStyleSheet('QLineEdit {color: black;}')
            self.TOTDCheckBox.setEnabled(True)
            self.SwiftTDCheckBox.setEnabled(True)
            self.configureRL.setEnabled(True)
            self.configureRL.setStyleSheet('QPushButton {color: black;}')
            self.RLStatusLabel.setText("<b>Status: </b>" + self.predictionStatus)

        # If CheckBox Moves to Unchecked State
        else:
            # Moving Status to Disabled
            self.predictionStatus = 'Disabled'

            # Checking GUI Enabled
            self.studyIDTextbox.setEnabled(False)
            self.studyIDTextbox.setStyleSheet('QLineEdit {color: grey;}')
            self.TOTDCheckBox.setEnabled(False)
            self.SwiftTDCheckBox.setEnabled(False)
            self.configureRL.setEnabled(False)
            self.configureRL.setStyleSheet('QPushButton {color: grey;}')
            self.RLStatusLabel.setText("<b>Status: </b>" + self.predictionStatus)

    def TOTDCheckBoxCallback(self):
        # If Checkbox Moves to Checked State
        if self.TOTDCheckBox.isChecked():
            self.algorithms['TOTD'] = 1

        # If Checkbox Moves to Unchecked State
        else:
            self.algorithms.pop('TOTD')

    def SwiftTDCheckBoxCallback(self):
        # If Checkbox Moves to Checked State
        if self.SwiftTDCheckBox.isChecked():
            self.algorithms['SwiftTD'] = 1

        # If Checkbox Moves to Unchecked State
        else:
            self.algorithms.pop('SwiftTD')

    def configureLearningCallback(self, numInputs):
        # Running RL Setup
        # for algorithm in self.algorithms.keys():
            # Enabling Classes
            # self.algorithms[algorithm] = algorithm(studyID = self.studyIDTextbox.currentText(), numInputs = numInputs)

        # Updating GUI
        self.evenGroundButton.setEnabled(True)
        self.unevenGroundbutton.setEnabled(True)
        self.upStairButton.setEnabled(True)
        self.downStairButton.setEnabled(True)
        self.upRampButton.setEnabled(True)
        self.downRampButton.setEnabled(True)
        self.turnButton.setEnabled(True)

        # Terrain Transitions
        self.evenGround = 0
        self.unevenGround = 0
        self.upStairs = 0
        self.downStairs = 0
        self.upRamp = 0
        self.downRamp = 0
        self.turn = 0

        # Updating Prediction Setting
        self.predict = True

        # Creating Plots
        self.terrainPlots = self.terrainPlottingPanel()
        self.layout.addWidget(self.terrainPlots)

    def evenGroundButtonCallback(self):
        # Setting Current Terrain
        self.evenGround = 1

        # Resetting ALl Other Terrains
        self.unevenGround = 0
        self.upStairs = 0
        self.downStairs = 0
        self.upRamp = 0
        self.downRamp = 0
        self.turn = 0

        # Resetting Current Terrain Label
        self.currentTerrain = "Even Ground"
        self.terrainLabel.setText(f"<b>Current Terrain: </b>{self.currentTerrain}")

        # Updating Button Colors
        self.evenGroundButton.setStyleSheet("background-color: green")
        self.unevenGroundbutton.setStyleSheet("background-color: red")
        self.upStairButton.setStyleSheet("background-color: red")
        self.downStairButton.setStyleSheet("background-color: red")
        self.upRampButton.setStyleSheet("background-color: red")
        self.downRampButton.setStyleSheet("background-color: red")
        self.turnButton.setStyleSheet("background-color: red")

    def unevenGroundButtonCallback(self):
        # Setting Current Terrain
        self.unevenGround = 1

        # Resetting ALl Other Terrains
        self.evenGround = 0
        self.upStairs = 0
        self.downStairs = 0
        self.upRamp = 0
        self.downRamp = 0
        self.turn = 0

        # Resetting Current Terrain Label
        self.currentTerrain = "Uneven Ground"
        self.terrainLabel.setText(f"<b>Current Terrain: </b>{self.currentTerrain}")

        # Updating Button Colors
        self.evenGroundButton.setStyleSheet("background-color: red")
        self.unevenGroundbutton.setStyleSheet("background-color: green")
        self.upStairButton.setStyleSheet("background-color: red")
        self.downStairButton.setStyleSheet("background-color: red")
        self.upRampButton.setStyleSheet("background-color: red")
        self.downRampButton.setStyleSheet("background-color: red")
        self.turnButton.setStyleSheet("background-color: red")

    def turnButtonCallback(self):
        # Setting Current Terrain
        self.turn = 1

        # Resetting ALl Other Terrains
        self.evenGround = 0
        self.unevenGround = 0
        self.upStairs = 0
        self.downStairs = 0
        self.upRamp = 0
        self.downRamp = 0

        # Resetting Current Terrain Label
        self.currentTerrain = "Turn"
        self.terrainLabel.setText(f"<b>Current Terrain: </b>{self.currentTerrain}")

        # Updating Button Colors
        self.evenGroundButton.setStyleSheet("background-color: red")
        self.unevenGroundbutton.setStyleSheet("background-color: red")
        self.upStairButton.setStyleSheet("background-color: red")
        self.downStairButton.setStyleSheet("background-color: red")
        self.upRampButton.setStyleSheet("background-color: red")
        self.downRampButton.setStyleSheet("background-color: red")
        self.turnButton.setStyleSheet("background-color: green")

    def upStairButtonCallback(self):
        # Setting Current Terrain
        self.upStairs = 1

        # Resetting ALl Other Terrains
        self.evenGround = 0
        self.unevenGround = 0
        self.downStairs = 0
        self.upRamp = 0
        self.downRamp = 0
        self.turn = 0

        # Resetting Current Terrain Label
        self.currentTerrain = "Up Stairs"
        self.terrainLabel.setText(f"<b>Current Terrain: </b>{self.currentTerrain}")

        # Updating Button Colors
        self.evenGroundButton.setStyleSheet("background-color: red")
        self.unevenGroundbutton.setStyleSheet("background-color: red")
        self.upStairButton.setStyleSheet("background-color: green")
        self.downStairButton.setStyleSheet("background-color: red")
        self.upRampButton.setStyleSheet("background-color: red")
        self.downRampButton.setStyleSheet("background-color: red")
        self.turnButton.setStyleSheet("background-color: red")

    def downStairButtonCallback(self):
        # Setting Current Terrain
        self.downStairs = 1

        # Resetting ALl Other Terrains
        self.evenGround = 0
        self.unevenGround = 0
        self.upStairs = 0
        self.upRamp = 0
        self.downRamp = 0
        self.turn = 0

        # Resetting Current Terrain Label
        self.currentTerrain = "Down Stairs"
        self.terrainLabel.setText(f"<b>Current Terrain: </b>{self.currentTerrain}")

        # Updating Button Colors
        self.evenGroundButton.setStyleSheet("background-color: red")
        self.unevenGroundbutton.setStyleSheet("background-color: red")
        self.upStairButton.setStyleSheet("background-color: red")
        self.downStairButton.setStyleSheet("background-color: green")
        self.upRampButton.setStyleSheet("background-color: red")
        self.downRampButton.setStyleSheet("background-color: red")
        self.turnButton.setStyleSheet("background-color: red")

    def upRampButtonCallback(self):
        # Setting Current Terrain
        self.upRamp = 1

        # Resetting ALl Other Terrains
        self.evenGround = 0
        self.unevenGround = 0
        self.upStairs = 0
        self.downStairs = 0
        self.downRamp = 0
        self.turn = 0

        # Resetting Current Terrain Label
        self.currentTerrain = "Up Ramp"
        self.terrainLabel.setText(f"<b>Current Terrain: </b>{self.currentTerrain}")

        # Updating Button Colors
        self.evenGroundButton.setStyleSheet("background-color: red")
        self.unevenGroundbutton.setStyleSheet("background-color: red")
        self.upStairButton.setStyleSheet("background-color: red")
        self.downStairButton.setStyleSheet("background-color: red")
        self.upRampButton.setStyleSheet("background-color: green")
        self.downRampButton.setStyleSheet("background-color: red")
        self.turnButton.setStyleSheet("background-color: red")

    def downRampButtonCallback(self):
        # Setting Current Terrain
        self.downRamp = 1

        # Resetting ALl Other Terrains
        self.evenGround = 0
        self.unevenGround = 0
        self.upStairs = 0
        self.downStairs = 0
        self.upRamp = 0
        self.turn = 0

        # Resetting Current Terrain Label
        self.currentTerrain = "Down Ramp"
        self.terrainLabel.setText(f"<b>Current Terrain: </b>{self.currentTerrain}")

        # Updating Button Colors
        self.evenGroundButton.setStyleSheet("background-color: red")
        self.unevenGroundbutton.setStyleSheet("background-color: red")
        self.upStairButton.setStyleSheet("background-color: red")
        self.downStairButton.setStyleSheet("background-color: red")
        self.upRampButton.setStyleSheet("background-color: red")
        self.downRampButton.setStyleSheet("background-color: green")
        self.turnButton.setStyleSheet("background-color: red")

    def resetTerrainButtons(self):
        # Resetting Background Color of Buttons
        self.evenGroundButton.setStyleSheet("background-color: white")
        self.unevenGroundbutton.setStyleSheet("background-color: white")
        self.upStairButton.setStyleSheet("background-color: white")
        self.downStairButton.setStyleSheet("background-color: white")
        self.upRampButton.setStyleSheet("background-color: white")
        self.downRampButton.setStyleSheet("background-color: white")
        self.turnButton.setStyleSheet("background-color: white")

        # Resetting Terrain Labelings
        self.downRamp = 0
        self.evenGround = 0
        self.unevenGround = 0
        self.upStairs = 0
        self.downStairs = 0
        self.upRamp = 0
        self.turn = 0

        # Resetting Current Terrain
        self.currentTerrain = None
        self.terrainLabel.setText(f"<b>Current Terrain: </b>{self.currentTerrain}")
        self.currentTerrainList = np.zeros(len(self.terrainList))

        # Resetting Plots
        self.resetPlot()

    def getCurrentTerrain(self):
        # Returning Current Terrain
        return self.terrainList, [self.evenGround, self.unevenGround, self.upStairs, self.downStairs, self.upRamp, self.downRamp, self.turn]

    #-----------------------------------------------------------------------------------
    # ---- Plotting Callbacks

    def terrainPlottingPanel(self):
        # Creating Plotting Widgets
        terrainPlottingPanel = QWidget()
        terrainPlottingPanel.setFixedSize(300, 600)
        terrainPlottingLayout = QVBoxLayout()
        terrainPlottingPanel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        terrainPlottingPanel.setLayout(terrainPlottingLayout)

        # Creating Plotting Widget
        self.terrainPlot = pg.GraphicsLayoutWidget()

        # Styling for Title
        titleStyle = {'size': '8pt'}

        # Iterating Through Number of Terrains
        for i in range(self.numberOfTerrains):
            # Creating Plotting Panels
            exec(f"self.terrainPlot{i} = self.terrainPlot.addPlot(row = {i}, col = 0)")
            exec(f"self.terrainPlot{i}.setYRange(0, 1, padding = 0.05)")
            exec(f"self.terrainPlot{i}.setTitle(self.terrainList[{i}], **titleStyle)")
            exec(f"self.terrainPlotItem{i} = self.terrainPlot{i}.plot(self.samples, self.predPlottingBuffer[{i}])")
            exec(f"self.terrainPlotItem{i}.getViewBox().setContentsMargins(0, 0, 0, 0)")

        # Adding to Layout
        terrainPlottingLayout.addWidget(self.terrainPlot)

        # Setting Layout
        terrainPlottingPanel.setLayout(terrainPlottingLayout)

        return terrainPlottingPanel

    def updateTerrainPlot(self, data):
        # Updating Data Buffers
        self.predPlottingBuffer[:, -1] = data
        self.terrainPlottingBuffer[:, -1] = self.getCurrentTerrain[1]

        # Updating Sample Count
        self.sampleCount += 1
        self.samples = np.roll(self.samples, -1)
        self.samples[-1] = self.sampleCount

        # Performing Plot Update Based on Timer Setting
        if self.updateTimer == 50:
            # Iterating Through PLots
            for i in range(self.numberOfTerrains):
                # Setting New Data
                exec(f"self.terrainPlotItem{i}.setData(self.samples, self.predPlottingBuffer[i])")

        else:
            # Incrementing Timer
            self.updateTimer += self.recordingRate

        # Updating Buffers
        self.predPlottingBuffer = np.roll(self.predPlottingBuffer, -1)
        self.terrainPlottingBuffer = np.roll(self.terrainPlottingBuffer, -1)

    def resetPlot(self):
        # Resetting Variables
        self.predPlottingBuffer = np.zeros((self.numberOfTerrains, self.bufferSize))
        self.terrainPlottingBuffer = np.zeros((self.numberOfTerrains, self.bufferSize))
        self.samples = np.arange(-(self.bufferSize - 1), 1)
        self.sampleCount = 0

        # Clearing Plots Iteratively
        # Iterating Through Number of Terrains
        for i in range(self.numberOfTerrains):
            exec(f"self.terrainPlotItem{i}.clear()")

    #-----------------------------------------------------------------------------------
    # ---- Adaptive Switching Callbacks
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RLWidget(recordingRate = 10)
    window.predCheckCallback(True)
    window.show()
    sys.exit(app.exec())