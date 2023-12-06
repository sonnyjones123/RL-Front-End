# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import os
import sys
import time
import numpy as np
import pyaudio
import cv2

# from DelsysLSLSender import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class VideoWidget(QWidget):
    """
    This is a controller for the VideoWidget operated through PySide6, OpenCV, and PyAudio.
    This is used to display video from whatever camera is currently plugged in (can be configured
    to use whichever camera if multiple devices are plugged in). The class will automatically save 
    video and audio files to a speficied location.

    Author: Sonny Jones & Grange Simpson
    Version: 2023.11.10

    Usage:

        app = QApplication(sys.argv)
        window = VideoWidget()
        window.show()
        sys.exit(app.exec())

    """
    def __init__(self):
        super().__init__()

        self.videoPanel = self.openCVPanel()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.videoPanel)
        self.recording = False
        
        # Setting OpenCV Capture Parameters
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.frameRate = 30
        self.frameDelay = 1000 // self.frameRate
        self.videoWriter = cv2.VideoWriter('OpenCVWidget.avi', cv2.VideoWriter_fourcc(*'XVID'), 30.0, (1280, 720))
        self.outputWidth = 1280
        self.outputHeight = 720

        # Setting Audio Capture Settings
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, frames_per_buffer = 1024)
        self.audioBuffer = []

    #-----------------------------------------------------------------------------------
    # ---- OpenCV Display Widget

    # Initalizing Camera Capture Display Window
    def openCVPanel(self):
        # Panel Layout
        openCVPanel = QWidget()
        openCVPanelLayout = QVBoxLayout()

        # Panel Label
        self.videoLabel = QLabel(self)
        self.videoLabel.setAlignment(Qt.AlignCenter)
        openCVPanelLayout.addWidget(self.videoLabel)

        # Adding Panel Label
        openCVPanel.setLayout(openCVPanelLayout)

        return openCVPanel

    # Updating Function
    def dataProcessing(self):
        self.updateFrame()
        self.saveFrame()
        self.saveAudio()

    #-----------------------------------------------------------------------------------
    # ---- Update and Exit Functions

    # Update Frame Function
    def updateFrame(self):
        # Reading Frame
        ret, self.frame = self.cap.read()
        if ret:
            # Updating Frame on successful read
            height, width, channel = self.frame.shape
            bytesPerLine = 3 * width
            qImage = QImage(self.frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qImage)
            self.videoLabel.setPixmap(pixmap)

    # Frame Saving Function
    def saveFrame(self):
        if self.recording:
            resizedFrame = cv2.resize(self.frame, (self.outputWidth, self.outputHeight))
            self.videoWriter.write(resizedFrame)

    # Saving AUdio
    def saveAudio(self):
        if self.recording:
            audioData = self.stream.read(1024)
            self.audioBuffer.append(audioData)

    # Releasing Camera and Output Stream
    def closeEvent(self, event):
        self.cap.release()
        self.videoWriter.release()
        self.stream.close()
        self.audio.terminate()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoWidget()
    window.recording = True
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle("OpenCV Video Stream with PySide6")
    window.show()
    sys.exit(app.exec())
