import numpy as np

class DataFileHandler():
    """
    This is a Data File Handler Class that is used to save data live to files during experiments. Utilizes
    numpy and .npy files to saving. 
    """

    #-----------------------------------------------------------------------------------
    # ---- File Handler

    def __init__(self):
        self.fileHandles = {}

    # Opening File Name and Appending to Dict
    def openFile(self, fileName):
        self.fileHandles[fileName] = open(fileName, 'ab')

    # Appending data to files
    def appendData(self, fileName, data):
        if fileName in self.fileHandles:
            self.fileHandles[fileName].seek(0, 2)
            np.save(self.fileHandles[fileName], data)
        else:
            raise ValueError(f"File '{fileName}' is not open. Call open_file('{fileName}') first.")
        
    # Closing File
    def closeFile(self, fileName):
        if fileName in self.fileHandles:
            self.fileHandles[fileName].close()
            del self.fileHandles[fileName]
        else:
            raise ValueError(f"File '{fileName}' is not open.")
        
    # Closing All Files
    def closeAllFiles(self):
        for fileHandle in self.fileHandles.values():
            fileHandle.close()
        self.fileHandles = {}