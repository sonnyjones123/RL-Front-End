import json
import pylsl

class DataCommandSender():
    """
    This is a Data Command Sender Class that is used to send data related commans to the Data File Handler
    over Lab Streaming Layer for threaded data file creation and live data saving.

    Author: Sonny Jones & Grange Simpson
    Version: 2024.06.10 
    """
    def __init__(self):
        # Creating Data Command Outlet
        
        info = pylsl.StreamInfo(name = "RLCommandStream", type = "command", channel_count = 1, nominal_srate = 0, channel_format = "string", source_id = "nervesll120")
        self.outlet = pylsl.StreamOutlet(info)
        
    def sendCommand(self, command):
        # Sending Command
        try:
            self.outlet.push_chunk([command])
            
        except Exception as e:
            print(e)
            # TODO: Issue here with json.dumps(command)
            # 1. length of the sample (178) must correspond to the stream's channel count (1).
            jsonCommand = json.dumps(command)
            self.outlet.push_chunk([jsonCommand])