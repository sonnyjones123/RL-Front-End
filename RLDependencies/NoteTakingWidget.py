import numpy as np
import os
import sys
from datetime import datetime

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class NoteTakerWidget(QWidget):
    """
    This is a Note Taking Widget Class that is used to save notes taken during experiment time.
    Author: Sonny Jones & Grange Simpson
    Version: 2024.01.23 
    """

    def __init__(self, filePath = None):
        super().__init__()

        # Layout
        self.layout = QVBoxLayout(self)
        self.noteTaker = self.noteTaker()
        self.layout.addWidget(self.noteTaker)

        # File Path
        self.filePath = filePath

        # File
        self.file = None

    #-----------------------------------------------------------------------------------
    # ---- Widget for Taking Notes
    def noteTaker(self):
        
        # Creating Label for Note taking Components
        noteTakerPanel = QWidget()
        noteTakerPanel.setFixedSize(300, 700)
        noteTakerLayout = QVBoxLayout()
        noteTakerLayout.setAlignment(Qt.AlignTop)
        
        # Note taking label
        self.noteTakingLabel = QLabel("<b>Note Taking</b>", alignment = Qt.AlignLeft)
        self.noteTakingLabel.setStyleSheet('QLabel {color: black; font-size: 24px;}')
        noteTakerLayout.addWidget(self.noteTakingLabel)

        # Note taking screen
        self.text_edit = QTextEdit(self)
        # self.text_edit.setMaximumSize(200, 500)
        # self.text_edit.setMinimumSize(180, 100)
        self.text_edit.setStyleSheet("background-color:#ffefff;")
        noteTakerLayout.addWidget(self.text_edit)

        # Add Note Button
        self.addNoteButton = QPushButton("Add Note", self)
        self.addNoteButton.objectName = "Add Note Button"
        self.addNoteButton.clicked.connect(self.addNoteCallback)
        self.addNoteButton.setStyleSheet("QPushButton {color: grey;}")
        self.addNoteButton.setEnabled(False)
        noteTakerLayout.addWidget(self.addNoteButton)

        """
        # Mark Transition Timepoint Button
        self.markTransitionButton = QPushButton("Mark Transition Time")
        self.markTransitionButton.objectName = "Mark Transition Time Button"
        self.markTransitionButton.clicked.connect(self.markTransitionCallback)
        self.markTransitionButton.setStyleSheet("QPushButton {color: grey;}")
        self.markTransitionButton.setEnabled(False)
        noteTakerLayout.addWidget(self.markTransitionButton)
        """
        
        # Add in saving button
        noteTakerPanel.setLayout(noteTakerLayout)
        noteTakerPanel.setMaximumSize(300, 700)

        return noteTakerPanel
    
    #-----------------------------------------------------------------------------------
    # ---- Callback Functions
    def addNoteCallback(self):
        # Formatting Message
        message = f"{self.trialName}({datetime.now().strftime('%H:%M:%S')}): {self.text_edit.toPlainText()} \n"
        self.file.write(message)

        # Clearing Note From QTextEdit
        self.text_edit.clear()

    def markTransitionCallback(self):
        # Mark transition timepoint with a timestamp
        message = f"{self.trialName}({datetime.now().timestamp()}): Terrain Transition \n" 
        self.file.write(message)

    # Create Text File Button
    def createTextFile(self, experimentName):
        if self.file is None:
            # Checking filePath
            fileName = "notes.txt"

            # Creating File Path
            completePath = self.filePath + experimentName + "/" + fileName

            # Creating Complete File Path
            # completePath = os.path.join(self.filePath, experimentName, fileName)

            # Creating File
            self.file = open(completePath, 'a')

    # Closing File
    def closeTextFile(self):
        # Closing Text File
        self.file.close()

    # Adding Trial Name
    def addTrialName(self, trialName):
        # Adding filename to class variable
        self.trialName = trialName
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = NoteTakerWidget()
    widget.show()
    sys.exit(app.exec())