from pylsl import StreamInfo, StreamOutlet, local_clock, IRREGULAR_RATE
import time

class DelsysLSLSender:

    def __init__(self, streamName, streamDataType, numChannels, uniqueID):
        # Initialize stream and start time
        self.info = StreamInfo(streamName, streamDataType, numChannels, IRREGULAR_RATE, 'float32', uniqueID)
        self.startTime = local_clock()
        self.sentSamples = 0

    def createOutlet(self, channelNames = None, sampleRates = None):
        """
        Addition of metadata for the stream.
        """

        # [TODO]:
        # Need to test new code here. Added functionality for metadata to be added. 

        # Adding metadata
        self.info.desc().append_child_value("NERVESLab", "ReinforcementLearningGUI")
        # Creating channel metadata if available
        if channelNames is not None:
            # Creating channelName metadata field
            chans = self.info.desc().append_child('channels')
            try:
                # Creating Index
                index = 0
                # Looping through channelNames
                for channelName in list(channelNames.keys()):
                    for channelType in channelNames[channelName]:
                            channelElem = chans.append_child("channel")
                            channelElem.append_child_value("label", channelName)
                            channelElem.append_child_value("type", channelType)
                            channelElem.append_child_value("samplingRate", sampleRates[index])
                            # channelElem.append_child_value("muscle", [insert muscle])

                            # Increasing Index
                            index += 1
            except Exception as e:
                print(e)

        self.outlet = StreamOutlet(self.info)

    def sendLSLData(self, data):
        elapsedTime = local_clock() - self.startTime
        # Send a chunk of data, will need to update time_stamp if we care
        try:
            self.outlet.push_chunk(data, elapsedTime)
            self.sentSamples += 1
        except Exception as e:
            print("DelsysLSLSender Issue")
            print(e)
            pass

def main():
    info = StreamInfo("Delsys", "EMG", 2, 100, 'float32')

    outlet = StreamOutlet(info)

    print("sending data")
    start_time = local_clock()
    sent_samples = 0
    while True:
        elapsed_time = local_clock() - start_time
        required_samples = int(100 * elapsed_time) - sent_samples
        mysample = [[42, 42], 
                    [42, 42]]
        outlet.push_sample([mysample])
        sent_samples += required_samples
        time.sleep(0.01)

if __name__ == '__main__':
    main()