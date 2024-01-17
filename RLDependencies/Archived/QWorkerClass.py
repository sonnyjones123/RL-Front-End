import sys
import time
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class Worker(QObject):
    finished = Signal()

    def __init__(self,taskID):
        super().__init__()
        self.taskID = taskID