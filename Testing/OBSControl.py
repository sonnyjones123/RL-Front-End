import obspython as obs
import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 10005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # Buffer Size is 1024 Bytes
    data = data.decode('utf-8')
    print(data)
    time.sleep(0.033)