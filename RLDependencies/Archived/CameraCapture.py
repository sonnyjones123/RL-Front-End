import cv2
import pyaudio
import numpy as np
import threading
import os
import time

from DelsysLSLSender import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class CameraCapture:
    """
    This is the camerea capture capture class. This includes capturing video using OpenCV and capturing
    audio from PyAudio.
    """

    def __init__(self, fileLoc = None):
        if fileLoc is None:
            # Initiating Camera Capture Settings
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.frameRate = 30
            self.frameDelay = 1000 // self.frameRate
            self.videoWriter = cv2.VideoWriter('CameraCapture.avi', cv2.VideoWriter_fourcc(*'XVID'), 30.0, (1280, 720))

            # Initiating Audio Capture Settings
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, frames_per_buffer = 1024)
            self.audioBuffer = []
            self.initAudioOutlet(self)
            
            # Thread
            self.thread = None
            self.recording = False
        else:
            # Initiating Camera Capture Settings
            self.fileLoc = fileLoc
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.frameRate = 30
            self.frameDelay = 1000 // self.frameRate
            self.videoWriter = cv2.VideoWriter(self.fileLoc + '/CameraCapture.avi', cv2.VideoWriter_fourcc(*'XVID'), 30.0, (1280, 720))

            # Initiating Audio Capture Settings
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, frames_per_buffer = 1024)
            self.audioBuffer = None
            self.initAudioOutlet(self)
            
            # Thread
            self.thread = None
            self.recording = False
        
    def initAudioOutlet(self):
        """
        Initializing LSL Audio Outlet.
        """
        self.audioOutlet = DelsysLSLSender("Audio", "Audio", 1, 44100)
        self.audioOutlet.createOutlet()
    
    def initCamera(self):
        """
        Initializing camera capture. Showing video
        """
        while True:
            startTime = time.time()
            ret, frame = self.cap.read()

            if not ret:
                continue
            
            self.frame = frame
            cv2.imshow('Video', frame)

            if self.recording:
                self.videoWriter.write(frame)
                audioData = self.stream.read(1024)
                self.audioBuffer = np.frombuffer(audioData, dtype = np.int16)

                if self.audioBuffer is not None:
                    self.audioOutlet.sendLSLData(self.audioBuffer)

            # Timer for optimal FPS recording
            endTime = time.time()
            elapsedTime = endTime - startTime

            if elapsedTime < self.frameDelay / 1000:
                time.sleep((self.frameDelay / 1000) - elapsedTime)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def killCamera(self):
        """
        Releasing thread, camera, and audio.
        """
        self.cap.release()
        self.videoWriter.release()
        cv2.destroyAllWindows()
        self.thread.kill()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

def main():
    recording = CameraCapture("C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Project Groups/ML Gait/Software/Testing")
    recording.recording = True
    recording.thread = threading.Thread(target = recording.initCamera)
    recording.thread.start()


class Thread(QThread):
    updateFrame = Signal(QImage)

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.CameraCapture = CameraCapture()
        self.status = True

    def run(self):
        self.CameraCapture.initCamera()
        self.rgbFrame = cv2.cvtColor(self.CameraCapture.frame, cv2.COLOR_BGR2RGB)
        self.updateFrame.emit(self.rgbFrame)

if __name__ == '__main__':
    main()