# Importing Modules
import os
from moviepy.editor import AudioFileClip, VideoFileClip

# Combining Audio and Video Files with the Same Name
def combineAudioVideo(dirPath):
    # Setting FilePath
    dirPath = dirPath

    # Iterating Through Directory
    for path in os.listdir(dirPath):
        # Check if Path is .avi File
        fileName, fileExtension = os.path.splitext(path)
        
        # If File is .avi
        if fileExtension == '.avi':
            try:
                # Try Loading .avi and .wav file
                fileLocation = os.path.join(dirPath, fileName)
                videoClip = VideoFileClip(f"{fileLocation}.avi")
                audioClip = AudioFileClip(f"{fileLocation}.wav")

                # Setting Video Audio
                videoClip = videoClip.set_audio(audioClip)

                # Setting Output Name
                outputFile = f"{fileLocation}.mp4"

                # Writting to Output File
                videoClip.write_videofile(outputFile, codec='libx264', audio_codec='aac')

                # Closing Video and Audio File
                videoClip.close()
                audioClip.close()

            except Exception as e:
                print(e)

            # Deleting Previous Audio and Video File
            try:
                # Attempt to Delete FIle
                os.remove(f"{fileLocation}.avi")
                os.remove(f"{fileLocation}.wav")

            except Exception as e:
                print(e)
