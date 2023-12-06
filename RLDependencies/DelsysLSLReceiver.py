"""Example program to demonstrate how to read a multi-channel time-series
from LSL in a chunk-by-chunk manner (which is more efficient)."""

from pylsl import StreamInlet, resolve_stream
import numpy as np
import threading

class DelsysLSLReceiver:
    def __init__(self, stream_data_type):
        self.streams = resolve_stream('type', stream_data_type)
        self.inlet = StreamInlet(self.streams[0])
        
    
    def receiveLSLData(self):
        chunk, time_stamps = self.inlet.pull_chunk()
        dataToSave = np.array([])
        #print(chunk, time_stamps)

        if time_stamps:
            #for ()
            return [chunk]
        else:
            return []

def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams = resolve_stream('type', 'Audio')

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    while True:
        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        chunk, timestamps = inlet.pull_chunk()
        if timestamps:
            print(timestamps, chunk)


if __name__ == '__main__':
    main()
