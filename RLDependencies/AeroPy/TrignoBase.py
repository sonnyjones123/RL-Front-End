"""
This class creates an instance of the Trigno base. Put your key and license here.
"""
import clr
clr.AddReference("/resources/DelsysAPI")
clr.AddReference("System.Collections")

from Aero import AeroPy
from NERVESLabKeys import *

key = key
license = license

class TrignoBase():
    def __init__(self):
        self.BaseInstance = AeroPy()