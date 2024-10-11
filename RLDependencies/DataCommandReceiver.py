import json
from pylsl import StreamInlet, resolve_stream

class DataCommandReceiver():
    """
    This is a Data Command Receiver Class that is used to receive data related commands to the Data File Handler
    over Lab Streaming Layer for threaded data file creation and live data saving.

    Author: Sonny Jones & Grange Simpson
    Version: 2024.06.18 
    """
    def __init__(self):
        # Creating a New Inlet to Read from the Stream
        streams = resolve_stream('type', 'command')

        # If No Stream
        if len(streams) == 0:
            print("Stream not found")

        # If Stream Found
        else:
            # Creating Inlet
            inlet = StreamInlet(streams[0])