import json
import pylsl

class DataCommandSender():
    """
    This is a Data Command Sender Class that is used to send data related commands to the Data File Handler
    over Lab Streaming Layer for threaded data file creation and live data saving.

    Author: Sonny Jones & Grange Simpson
    Version: 2024.06.10 
    """
    def __init__(self, name = 'RLCommandStream', type = 'command'):
        print("Initialize Data Command Sender")
        # Creating Data Command Outlet
        
        info = pylsl.StreamInfo(name = name, type = type, channel_count = 1, nominal_srate = 0, channel_format = "string", source_id = "nervesll120")
        self.outlet = pylsl.StreamOutlet(info)
        
    def sendCommand(self, command):
        # Sending Command
        print("Pushing Chunk")
        try:
            self.outlet.push_chunk([command])
            
        except:
            jsonCommand = json.dumps(command)
            self.outlet.push_chunk([jsonCommand])