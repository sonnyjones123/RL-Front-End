"""Example program to demonstrate how to read a multi-channel time-series
from LSL in a chunk-by-chunk manner (which is more efficient)."""

from pylsl import StreamInlet, resolve_stream


def main():
    # first resolve an EEG stream on the lab network
    print("looking for an Delsys stream...")
    streams = resolve_stream('type', 'EEG')

    # create a new inlet to read from the stream
    if len(streams) == 0:
        print("Stream not found")
    else:
        inlet = StreamInlet(streams[0])

        while True:
            # get a new sample (you can also omit the timestamp part if you're not
            # interested in it)
            chunk, timestamps = inlet.pull_chunk()
            if timestamps:
                print(timestamps, chunk)


if __name__ == '__main__':
    main()