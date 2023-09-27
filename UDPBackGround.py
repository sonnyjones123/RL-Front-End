"""
The purpose of this function is to act as a background process that checks the incoming UDP ports for information from LabView.
This function sets up the background task on its own thread so it doesn't bog down other processes. 
"""
import queue
import threading
import socket

def readUDP(queue):
    while True:
        # Setting UDP IP and Port Addresses
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005

        # Initiating Socket
        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))

        # Receiving Data
        data, addr = sock.recvfrom(1024) # Buffer Size is 1024 Bytes
        queue.put(data)

result_queue = queue.Queue()

listenUDP = threading.Thread(target = readUDP, args = (result_queue,))
listenUDP.start()

while listenUDP.is_alive():
    if not result_queue.empty():
        results = result_queue.get()
        print(f"Data: {results}")
