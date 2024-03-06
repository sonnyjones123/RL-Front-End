import sys
import cv2
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class VideoWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.videoLabel = QLabel(self)
        self.videoLabel.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.videoLabel)
        
        self.capture = cv2.VideoCapture(0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)

    def updateFrame(self):
        ret, frame = self.capture.read()
        if ret:
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImage = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

            pixmap = QPixmap.fromImage(qImage)
            self.videoLabel.setPixmap(pixmap)

    def closeEvent(self, event):
        self.capture.release()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = VideoWidget()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle("OpenCV Video Stream with PySide6")
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()