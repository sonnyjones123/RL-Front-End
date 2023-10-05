import socket

UDP_IP = "10.16.83.28"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # Buffer Size is 1024 Bytes
    print("received messages: %s" % data)