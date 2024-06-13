# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import os
import sys
import time
import numpy as np
import pyaudio
import cv2
import wave

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
    Version: 2024.01.17

    Usage:

        app = QApplication(sys.argv)
        window = VideoWidget()
        window.show()
        sys.exit(app.exec())

    """
    def __init__(self, filePath = None, recordingRate = 30):
        super().__init__()

        self.videoPanel = self.openCVPanel()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.videoPanel)
        self.recording = False
        
        # Setting OpenCV Capture Parameters
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        # self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.frameRate = 1000 // recordingRate # // 2
        self.frameDelay = recordingRate # * 2
        self.videoWriter = None

        # 1080p resolution
        self.outputWidth = 1920
        self.outputHeight = 1080

        # Setting Audio Capture Settings
        self.format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.framesPerBuffer = 1323

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format = self.format, channels = self.channels, rate = self.rate, input = True, frames_per_buffer = self.framesPerBuffer)
        self.audioBuffer = []
        self.audioWriter = None
        
        # Saving Location
        self.filePath = filePath

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

    # Creating Outlet
    def createOutlet(self, fileName = None):
         # If video writer object is none
        if self.videoWriter is None:
            # If filePath is provided
            if fileName == None:
                # Default Name
                defaultName = 'OpenCVWidget.avi'

                # Creating Complete Path with Default Name
                completePath = os.path.join(self.filePath, defaultName)

                # Creating Outlet
                self.videoWriter = cv2.VideoWriter(completePath, cv2.VideoWriter_fourcc(*'XVID'), self.frameRate, (self.outputWidth, self.outputHeight))
            else:
                # Formatting Custom File Name
                customFileName = f"{fileName}.avi"

                # Creating Complete Path
                completePath = os.path.join(self.filePath, customFileName)

                # Creating Outlet
                self.videoWriter = cv2.VideoWriter(completePath, cv2.VideoWriter_fourcc(*'XVID'), self.frameRate, (self.outputWidth, self.outputHeight))
        else:
            print("Video Outlet Already Exists")

        # If audio writer object is none
        if self.audioWriter is None:
            # If filePath is provided
            if fileName == None:
                # Default name
                defaultName = 'OpenCVWidget.wav'

                # Creating Complete Path with Default Name
                completePath = os.path.join(self.filePath, defaultName)

                # Creating Outlet
                self.audioWriter = wave.open(completePath, 'wb')

            else:
                # Formatting Custom File Name
                customFileName = f"{fileName}.wav"

                # Creating Complete Path
                completePath = self.filePath + '/' + customFileName

                # Creating Outlet
                self.audioWriter = wave.open(completePath, 'wb')

            # Setting attributes
            self.audioWriter.setnchannels(self.channels)
            self.audioWriter.setsampwidth(self.audio.get_sample_size(self.format))
            self.audioWriter.setframerate(self.rate)

        else:
            print("Audio Outlet Already Exists")

    # Update Frame Function
    def updateFrame(self):
        # Reading Frame
        ret, self.frame = self.cap.read()
        if ret:
            # Resizing Frame
            displayFrame = cv2.resize(self.frame, (720, 480))
            # Updating Frame on successful read
            height, width, channel = displayFrame.shape
            bytesPerLine = 3 * width
            qImage = QImage(displayFrame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qImage)
            self.videoLabel.setPixmap(pixmap)

    # Frame Saving Function
    def saveFrame(self):
        if self.recording:
            self.videoWriter.write(self.frame)

    # Saving AUdio
    def saveAudio(self):
        if self.recording:
            audioData = self.stream.read(self.framesPerBuffer)
            self.audioWriter.writeframes(audioData)
            
    # Releasing Outlet
    def releaseOutlet(self):
        if self.videoWriter:
            self.videoWriter.release()
            self.videoWriter = None

        if self.audioWriter:
            self.audioWriter.close()
            self.audioWriter = None

    # Releasing Camera and Output Stream
    def releaseConfig(self):
        self.cap.release()
        self.releaseOutlet()
        self.stream.close()
        self.audio.terminate()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoWidget()
    window.recording = True
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle("OpenCV Video Stream with PySide6")
    window.show()
    sys.exit(app.exec())
