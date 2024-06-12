"""Example program to demonstrate how to read a multi-channel time-series
from LSL in a chunk-by-chunk manner (which is more efficient)."""

from pylsl import StreamInlet, resolve_stream
import json
import threading
import queue
import time

commandQueue = queue.Queue()

def main():
    # first resolve an EEG stream on the lab network
    print("looking for an Delsys stream...")
    try:
        streams = resolve_stream('type', 'command')

        # create a new inlet to read from the stream
        if len(streams) == 0:
            print("Stream not found")
        else:
            inlet = StreamInlet(streams[0])

            while True:
                try:
                    # get a new sample (you can also omit the timestamp part if you're not
                    # interested in it)
                    sample, timestamps = inlet.pull_sample()
                    if sample:
                        commandQueue.put(json.loads(sample[0]))
                except json.JSONDecodeError as e:
                    print(f"Error decoding sample: {e}")
                except Exception as e:
                    print(f"Error processing command: {e}")
    except Exception as e:
        print(f"Error setting up listener: {e}")

def processQueue():
    while True:
        command = commandQueue.get()
        if command is not None:
            functionName = command['command']
            params = command.get('params', {})

            print(f"Function Name: {functionName}")
            print(f"Params: {params}")

if __name__ == '__main__':
    listenerThread = threading.Thread(target = main, daemon = True)
    listenerThread.start()

    processerThread = threading.Thread(target = processQueue, daemon = True)
    processerThread.start()

    # Keep the main thread alive to allow the listener thread to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")