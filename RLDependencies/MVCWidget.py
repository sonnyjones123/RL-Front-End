from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import time
import sys

class MVC(QWidget):
    def mvcGUI(self, sensor, attachment):
        # Create the main application instance
        app = QApplication(sys.argv)

        # Create the main window
        window = QWidget()
        window.setWindowTitle("MVC DelsysEMG GUI")
        window.setFixedSize(350, 200)
        window.setStyleSheet("background-color:#f5e1fd;")

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        # Creating Beginning Label with Sensor And Attachment
        self.mvcLabel = QLabel(f"Ready for MVC of <b>{sensor} : {attachment}</b>?", alignment = Qt.AlignCenter)
        self.mvcLabel.setStyleSheet('QLabel {color: black; font-size: 18px; font-family: Arial;}')
        self.layout.addWidget(self.mvcLabel)

        # Creating Beginning Label with Sensor And Attachment
        self.trialCountLabel = QLabel(f"<b> Trials Left : <b>", alignment = Qt.AlignCenter)
        self.trialCountLabel.setStyleSheet('QLabel {color: black; font-size: 12px; font-family: Arial;}')
        self.layout.addWidget(self.trialCountLabel)

        # Blank
        self.blank = QLabel()
        self.layout.addWidget(self.blank)

        # Creating Push Button To Begin MVC
        self.beginMVC = QPushButton("Ready?")
        self.beginMVC.clicked.connect(self.startMVCSequence)
        self.beginMVC.setStyleSheet("QPushButton {color: black; font-size: 18px; font-family: Arial;}")
        self.layout.addWidget(self.beginMVC)

        # Adding Label
        self.mvcTimerLabel = QLabel(alignment = Qt.AlignCenter)
        self.mvcTimerLabel.setStyleSheet('QLabel {color: black; font-size: 18px; font-family: Arial;}')
        self.layout.addWidget(self.mvcTimerLabel)

        # Timer
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.mvcSequence)
        self.counter = None

        # Show Window
        window.show()

        # Running Event Loop
        sys.exit(app.exec())

    def startMVCSequence(self):
        """
        Starting Sequence for MVC Trial
        """
        # Removing Button
        self.beginMVC.hide()
        self.mvcTimerLabel.show()

        # Updating Label
        self.trialCountLabel.setText(f"<b>Trails Left: </b>{self.trialNumber}")

        # Starting Timer
        self.timer.start()

    def mvcSequence(self):
        # Count To Keep Track of Iterations
        if self.counter == None:
            self.counter = 0
        else:
            self.counter += 1

        # Updating Label
        if self.counter < 3:
            self.mvcTimerLabel.setText(f'Prepare to Flex in {3 - self.counter}...')
        else:
            self.startDataCollection()
            self.MVCRecording = True
            self.mvcTimerLabel.setText(f'FLEX FLEX FLEX : {13 - self.counter}...')

        # If Recording Is True
        if self.MVCRecording == True:
            self.processData()

        # Stopping Timer
        if self.counter >= 13:
            self.timer.stop()

            # Stopping Data Collection
            self.stopDataCollection()

            # Resetting Counter
            self.counter = None

            # Updating Trial Number
            self.trialNumber -= 1
            self.trialCountLabel.setText(f"<b>Trails Left: </b>{self.trialNumber}")
            self.mvcTimerLabel.setText("")

            # Resetting Data Buffer
            self.data = []

            # Checking Trial Number
            if self.trialNumber == 0:
                # Exiting GUI
                self.exitMVC()

                # Returning Tuple
                return (0, 1)

            # Hiding Label
            self.mvcTimerLabel.hide()

            # Showing Button
            self.beginMVC.show()

    def exitMVC(self):
        """
        Exiting MVC GUI
        """
        # Resetting Recording MVC Variable
        self.MVCRecording = False

        # Closing GUI
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MVC("dummy", "dummy", "dummy2")
    widget.show()
    sys.exit(app.exec())