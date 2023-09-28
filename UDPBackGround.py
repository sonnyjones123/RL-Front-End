"""
The purpose of this function is to act as a background process that checks the incoming UDP ports for information from LabView.
This function sets up the background task on its own thread so it doesn't bog down other processes. 
"""
import queue
import threading
import socket
import time

def readUDP(queue):
    while True:
        # Setting UDP IP and Port Addresses
        UDP_IP = "10.16.83.28"
        UDP_PORT = 5005

        # Initiating Socket
        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))

        # Receiving Data
        data, addr = sock.recvfrom(1024) # Buffer Size is 1024 Bytes
        queue.put(data)

def sendDelsysStatus(MESSAGE, UDP_PORT):
    UDP_IP = "10.16.83.28"
    MESSAGE = bytes(DelsysStatus, 'utf-8')
 
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

commandQueue = queue.Queue()

listenUDP = threading.Thread(target = readUDP, args = (commandQueue,))
listenUDP.start()

# Importing Dependencies
from DelsysEMG import DelsysEMG
from System.Collections.Generic import *

import clr
clr.AddReference("System.Collections")

# Setting up DelsysEMG Class
DelsysEMG = DelsysEMG()
DelsysStatus = "Off"
sendDelsysStatus(DelsysStatus, 9005)

while listenUDP.is_alive():
    if not commandQueue.empty():
        command = commandQueue.get()
        command = command.decode('utf-8')
        
        command = "DelsysEMG." + command
        exec(command)

    if not DelsysEMG.status == DelsysStatus:
        DelsysStatus = DelsysEMG.status
        sendDelsysStatus(DelsysStatus, 9005)

    # Waiting Until Next Call
    time.sleep(0.033)