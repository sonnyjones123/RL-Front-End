"""
The purpose of this function is to act as a background process that checks the incoming UDP ports for information from LabView.
This function sets up the background task on its own thread so it doesn't bog down other processes. 
"""
import os
import queue
import threading
import socket
import time
import concurrent.futures
import platform
import sys
from datetime import date

# Adding directories
if (platform.node() == "Garangatan_Comp"):
    sys.path.insert(0, "C:/Users/grang/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/Delsys/Example-Applications-main/Python")
elif (platform.node() == "Sonny_ThinkPad"):
    sys.path.insert(0, "C:/Users/sonny/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/Delsys/Example-Applications-main/Python")
elif (platform.node() == 'Purkinje'):
    sys.path.insert(0, "C:/Users/Purkinje/Box/NeuroRoboticsLab/NERVES Lab/Equipment Manuals/Delsys/Example-Applications-main/Python")

# Importing Dependencies
from RLDependencies.DelsysEMG import *
from RLDependencies.CameraCapture import *
from System.Collections.Generic import *
import clr
clr.AddReference("System.Collections")    

# Changing working directory to the directory containing the script
scriptpath = os.path.dirname(__file__)
print(scriptpath)
os.chdir(scriptpath)

class DelsysUDPBackGround:
    """
    Read incoming data from a UDP connection with LabView
    """
    def __init__(self):
        self.UDP_IP = "127.0.0.1"
        self.UDP_RECEIVE_PORT = 5005
        self.UDP_SEND_PORT = 9005
        self.UDP_EMG_SEND_PORT = 10005
        self.commandQueue = queue.Queue()
        self.listenUDPStart = 0
        
    def readUDP(self, queue):
        while True:
            # Setting UDP IP and Port Addresses
            UDP_PORT = 5005

            # Initiating Socket
            sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
            sock.bind((self.UDP_IP, self.UDP_RECEIVE_PORT))

            # Receiving Data
            data, addr = sock.recvfrom(1024) # Buffer Size is 1024 Bytes
            queue.put(data)

    #def sendDelsysStatus(self, MESSAGE, UDP_PORT):
    def sendDelsysStatus(self, MESSAGE):
        MESSAGE = bytes(DelsysEMG.status, 'utf-8')

        sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
        sock.sendto(MESSAGE, (self.UDP_IP, self.UDP_SEND_PORT))

    def sendDelsysEMG(self, MESSAGE):
        MESSAGE = bytes(MESSAGE, 'utf-8')

        sock = socket.socket(socket.AF_INET, #Internet
                             socket.SOCK_DGRAM) # UDP
        
        sock.sendto(MESSAGE, (self.UDP_IP, self.UDP_EMG_SEND_PORT))
    
    def listenUDP(self):
        self.listenUDPStart = threading.Thread(target = self.readUDP, args = (self.commandQueue,))
        self.listenUDPStart.start()

    


if __name__ == "__main__":
    print("Initiating Delsys Class...")
    DelsysEMG = DelsysEMG()
    UDPBackground = DelsysUDPBackGround()
    # Set up UDP connection to LabView
    UDPBackground.listenUDP()

    # Default status
    DelsysStatus = "off"
    UDPBackground.sendDelsysStatus(DelsysStatus)
    
    # Finding File Save Location
    fileLoc = "" # Insert Folder for File Saving
    folderName = str(date.today())
    print(os.getcwd())
    filePath = os.path.join(fileLoc, folderName)
    print(filePath)
    try:
        os.mkdir("./"+filePath)
    except Exception as e:
        print(e)
        print("Directory already exists.")

    # Input file name to save to
    fileName = input("RESPONSE REQUESTED: Please indicate file name with no extension\n")
    fileName += ".npy"
    fileName = os.path.join(filePath, fileName)

    # Initiating Camera Capture
    #print("Initiating Camera Capture Class...")
    #print("This may take a miniute")
    #CameraCapture = CameraCapture()
    #CameraCapture.thread = threading.Thread(target = CameraCapture.initCamera)

    # Start thread pool up here
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

    # While port is alive
    while UDPBackground.listenUDPStart.is_alive():
        if not UDPBackground.commandQueue.empty():
            command = UDPBackground.commandQueue.get()
            command = command.decode('utf-8')

            if command == 'quit':
                UDPBackground.listenUDPStart.kill()
            else:
                command = "DelsysEMG." + command
                exec(command)
                UDPBackground.sendDelsysStatus(DelsysEMG.status)

        # Sending Delsys Status
        if not DelsysEMG.status == DelsysStatus:
            DelsysStatus = DelsysEMG.status
            UDPBackground.sendDelsysStatus(DelsysStatus)

        # Sending EMG Data
        if DelsysEMG.status == "Running":
            DelsysEMG.processData()
            #CameraCapture.recording = True
            # Set a thread to start running in here before buffer is reset in plotEMG
            # pool.submit(DelsysEMG.savingEMGData(fileName))
            sendEMG = DelsysEMG.plotEMG()
            UDPBackground.sendDelsysEMG(sendEMG)

        # Waiting Until Next Call
        time.sleep(0.033)

    # Offloading Classes
    #CameraCapture.killCamera()