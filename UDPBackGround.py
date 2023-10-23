"""
The purpose of this function is to act as a background process that checks the incoming UDP ports for information from LabView.
This function sets up the background task on its own thread so it doesn't bog down other processes. 
"""
import queue
import threading
import socket
import time

# Importing Dependencies
from DelsysEMG import *
from System.Collections.Generic import *
import clr
clr.AddReference("System.Collections")

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
    DelsysEMG = DelsysEMG()
    UDPBackground = DelsysUDPBackGround()
    # Set up UDP connection to LabView
    UDPBackground.listenUDP()

    # Default status
    DelsysStatus = "off"
    UDPBackground.sendDelsysStatus(DelsysStatus)
    
    # While port is alive
    while UDPBackground.listenUDPStart.is_alive():
        if not UDPBackground.commandQueue.empty():
            command = UDPBackground.commandQueue.get()
            command = command.decode('utf-8')

            if command == 'quit':
                break
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
            sendEMG = DelsysEMG.plotEMG()
            UDPBackground.sendDelsysEMG(sendEMG)

        # Waiting Until Next Call
        time.sleep(0.033)