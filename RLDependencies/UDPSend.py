import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 10005
MESSAGE = b'0.046894427478308534,0.11051005054341723,0.06613200852638242,0.059442356868074524'

# print("UDP target IP: %s" % UDP_IP)
# print("UDP target port: %s" % UDP_PORT)
# print("message: %s" % MESSAGE)
 
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))