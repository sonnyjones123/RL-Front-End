"""Example program to demonstrate how to send a multi-channel time-series
with proper meta-data to LSL."""
import time
import json
from random import random as rand

import pylsl

def main():
    dataPacket = {
                'command': 'dataSaving',
                'params': {
                    'data' : 'Delsys Data',
                    'sampleData' : [[-0.0307, 0.0949, -0.0047], [0.0307, 0.0949, -0.0047]]
                }
    }

    info = pylsl.StreamInfo('RLCommandStream', 'command', 1, 0, 'string')
    outlet = pylsl.StreamOutlet(info)

    print("now sending data...")
    while True:
        jsonCommand = json.dumps(dataPacket)
        outlet.push_chunk([jsonCommand])
        time.sleep(2)

if __name__ == '__main__':
    main()