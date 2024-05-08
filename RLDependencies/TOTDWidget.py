import sys
import platform
import ctypes

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

class TOTDWidget(QWidget):
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
    def __init__(self):
        super().__init__()
        self.TOTD = None
        self.predictionStatus = 'Disabled'
        self.predictTOTD = False
        self.TOTDControlPanel = self.TOTDPanel()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.TOTDControlPanel)
        
    #-----------------------------------------------------------------------------------
    # ---- TOTD Control and Display Widget

    def TOTDPanel(self):
        # Panel Layout
        TOTDPanel = QWidget()
        TOTDPanel.setFixedSize(230, 190)
        TOTDPanelLayout = QVBoxLayout()
        TOTDPanelLayout.setAlignment(Qt.AlignTop)

        # Panel Label
        self.TOTDPanelLabel = QLabel("<b>ML Control Panel</b>", alignment = Qt.AlignCenter)
        self.TOTDPanelLabel.setStyleSheet('QLabel {color: black; font-size: 24px}')
        TOTDPanelLayout.addWidget(self.TOTDPanelLabel)

        # Prediciton Status
        self.TOTDStatusLabel = QLabel("<b>Status: </b>" + self.predictionStatus, alignment = Qt.AlignCenter)
        self.TOTDStatusLabel.setStyleSheet('QLabel {color: black;}')
        TOTDPanelLayout.addWidget(self.TOTDStatusLabel)

        # Predicting Checkmark
        self.predictionCheckmark = QCheckBox("Predictions", self)
        self.predictionCheckmark.objectName = 'Prediction Checkmark'
        self.predictionCheckmark.clicked.connect(self.predCheckCallback)
        self.predictionCheckmark.setEnabled(True)
        TOTDPanelLayout.addWidget(self.predictionCheckmark)

        # Study ID Label
        self.studyIDLabel = QLabel("<b>Enter Study ID:</b>")
        self.studyIDLabel.setStyleSheet('QLabel {color: black;}')
        TOTDPanelLayout.addWidget(self.studyIDLabel)

        # Study ID TextBox
        self.studyIDTextbox = QLineEdit(self)
        self.studyIDTextbox.setAlignment(Qt.AlignCenter)
        self.studyIDTextbox.setText("Default Study ID")
        self.studyIDTextbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.studyIDTextbox.objectName = 'Study ID'
        self.studyIDTextbox.setStyleSheet('QLineEdit {color: grey;}')
        self.studyIDTextbox.setEnabled(False)
        TOTDPanelLayout.addWidget(self.studyIDTextbox)

        # Configure TOTD
        self.configureTOTD = QPushButton("Configure")
        self.configureTOTD.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.configureTOTD.objectName = 'Study ID'
        self.configureTOTD.setStyleSheet('QPushButton {color: grey;}')
        self.configureTOTD.clicked.connect(self.configureTOTDCallback)
        self.configureTOTD.setEnabled(False)
        TOTDPanelLayout.addWidget(self.configureTOTD)

        # Setting Panel Layout
        TOTDPanel.setLayout(TOTDPanelLayout)

        return TOTDPanel
    
    #-----------------------------------------------------------------------------------
    # ---- TOTD Control Callbacks

    def predCheckCallback(self):
        # If CheckBox Moves to Checked State
        if self.predictionCheckmark.isChecked():
            # Moving Status to Enabled
            self.predictionStatus = 'Enabled'

            # Checking GUI Enabled
            self.studyIDTextbox.setEnabled(True)
            self.studyIDTextbox.setStyleSheet('QLineEdit {color: black;}')
            self.configureTOTD.setEnabled(True)
            self.configureTOTD.setStyleSheet('QPushButton {color: black;}')
            self.TOTDStatusLabel.setText("<b>Status: </b>" + self.predictionStatus)

        # If CheckBox Moves to Unchecked State
        else:
            # Moving Status to Disabled
            self.predictionStatus = 'Disabled'

            # Checking GUI Enabled
            self.studyIDTextbox.setEnabled(False)
            self.studyIDTextbox.setStyleSheet('QLineEdit {color: grey;}')
            self.configureTOTD.setEnabled(False)
            self.configureTOTD.setStyleSheet('QPushButton {color: grey;}')
            self.TOTDStatusLabel.setText("<b>Status: </b>" + self.predictionStatus)

    def configureTOTDCallback(self):
        # Running TOTD Setup
        pass
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TOTDWidget()
    window.show()
    sys.exit(app.exec())