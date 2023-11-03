import cv2
import socket
import threading
import queue

cap = cv2.VideoCapture(0)

# Define the codec and create a VideoWriter object
video = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'XVID'), 30.0, (640, 480))

class DelsysUDPBackGround:
    """
    Read incoming data from a UDP connection with LabView
    """
    def __init__(self):
        self.UDP_IP = "127.0.0.1"
        self.UDP_RECEIVE_PORT = 10005
        self.UDP_SEND_PORT = 9005
        self.UDP_EMG_SEND_PORT = 10005
        self.commandQueue = queue.Queue()
        self.listenUDPStart = 0
        
    def readUDP(self, queue):
        while True:
            # Initiating Socket
            sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
            sock.bind((self.UDP_IP, self.UDP_RECEIVE_PORT))

            # Receiving Data
            data, addr = sock.recvfrom(1024) # Buffer Size is 1024 Bytes
            queue.put(data)

    def listenUDP(self):
        self.listenUDPStart = threading.Thread(target = self.readUDP, args = (self.commandQueue,))
        self.listenUDPStart.start()

recording = False

UDPBackground = DelsysUDPBackGround()
# Set up UDP connection to LabView
UDPBackground.listenUDP()

while UDPBackground.listenUDPStart.is_alive:
    if not UDPBackground.commandQueue.empty():
        command = UDPBackground.commandQueue.get()
        command = command.decode('utf-8')
    else:
        command = None
    
    ret, frame = cap.read()

    if ret:
        cv2.imshow('Webcam', frame)

    if recording:
        video.write(frame)

    key = cv2.waitKey(1) & 0xFF

    if command == 'record':
        recording = True

    if command == 'quit':
        break
        
UDPBackground.listenUDPStart.kill()
cap.release()
video.release()
cv2.destroyAllWindows()
