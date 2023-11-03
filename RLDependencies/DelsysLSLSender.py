from pylsl import StreamInfo, StreamOutlet, local_clock
import time

class DelsysLSLSender:

    def __init__(self, streamName, streamDataType, numChannels, sampRate):
        # Initialize stream and start time
        self.info = StreamInfo(streamName, streamDataType, numChannels, sampRate, 'float32')
        self.startTime = local_clock()
        self.sampRate = sampRate
        self.sentSamples = 0

    def createOutlet(self, channelNames = None, sampleRates = None):
        """
        Addition of metadata for the stream.
        """
        # Creating channel metadata if available
        if channelNames is not None:
            # Creating channelName metadata field
            self.info.desc().append_child('channels')
            # Looping through channelNames
            for index, channelName in enumerate(channelNames):
                try:
                    channelElem = self.info.desc().child("channel").append_child('channel')
                    channelElem.append_child_value("label", channelName)
                    channelElem.append_child_value("type", channelName)
                    channelElem.append_child_value("samplingRate", sampleRates[index])
                    # channelElem.append_child_value("muscle", [insert muscle])
                except:
                    pass

        self.outlet = StreamOutlet(self.info)

    def sendLSLData(self, data):
        elapsedTime = local_clock() - self.startTime
        requiredSamples = int(self.sampRate * elapsedTime) - self.sentSamples
        # Send a chunk of data, will need to update time_stamp if we care
        self.outlet.push_chunk(data, elapsedTime)
        # self.outlet.push_chunk(data)
        self.sentSamples += requiredSamples
        #time.sleep(0.01)


"""
def main():
    info = StreamInfo("Delsys", "EMG", 2, 100, 'float32')

    outlet = StreamOutlet(info)

    print("sending data")
    start_time = local_clock()
    sent_samples = 0
    while True:
        elapsed_time = local_clock() - start_time
        required_samples = int(100 * elapsed_time) - sent_samples
        mysample = 42
        outlet.push_sample([mysample])
        sent_samples += required_samples
        time.sleep(0.01)

if __name__ == '__main__':
    main()
"""