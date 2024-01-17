import numpy as np
import math
import os
import matplotlib.pyplot as plt

class SelectiveKanervaCoding():
    def __init__(self, numPrototypes = 5000, numInputs = 0, cList = [500, 125, 25], studyID = None):
        # Initializing Params
        self.K = numPrototypes
        self.n = numInputs
        self.c = cList
        
        # Creating Randomized Prototypes
        self.initPrototypes(studyID)

    #-----------------------------------------------------------------------------------
    # ---- Initialization 

    def initPrototypes(self, studyID):
        """
        This function initializes the prototypes the input number of parameters. This only needs to be done once
        and will automatically checked if a previous call has initiated a prototypes list. 
        """  
        try:
            # Looking for prototypes in path
            print("Loading prototypes if available...")
            w = os.listdir("../Algorithms/Prototypes")
            if f"Prototypes_{studyID}.npy" in w:
                self.P = np.load(f"../Algorithms/Prototypes/{studyID}_input{self.n}.npy", allow_pickle = False)
                print("Prototypes loaded successfully")
            else:
                print("No prototypes found")
                print(f"Creating prototypes for {studyID}...")
                # Creating prototypes and saving
                self.P = []

                # Looping through number of prototypes
                for i in range(self.K):
                    self.P.append(np.random.rand(self.n))

                # Saving initiaized prototypes list
                np.save(f"../Algorithms/Prototypes/{studyID}_input{self.n}.npy", self.P, allow_pickle = False)
        except Exception as e:
            print(e)
            print("Failed to load or create prototypes")

    #-----------------------------------------------------------------------------------
    # ---- SKC Update Algorithm

    def setState(self, newState):
        # Inputting new state
        self.newState = newState
        
    def computeSKC(self):
        # Resetting 
        D = np.zeros(self.K)
        # Looping Through Params
        for i in range(self.K):
            # Computing Euclidean Distance
            D[i] = math.dist(self.P[i], self.newState)
                
        # QuickSort
        sortedIndex = np.argsort(D, kind = 'quicksort')
        
        # Setting Feature Vector
        featureVector = []

        # Looping Through C List
        for m in self.c:
            # Creating temporary vector and setting feature binary vector
            tempVector = np.zeros(self.K)
            tempIndices = sortedIndex[0:m]
            tempVector[tempIndices] = 1

            # Appending to featureVector
            featureVector.append(tempVector)

        return featureVector

    #-----------------------------------------------------------------------------------
    # ---- Archived Functions

    def partition(self, array, left, right):
        """
        This implements the Hoare partition algorithm.
        Input:
            Array: List
            Left: First position of list
            Right: Last position of list
        """
        x = array[right]
        i = left
        
        # Looping through
        for j in range(left, right):
            if array[j] <= x:
                array[i], array[j] = array[j], array[i]
                i += 1
            print(array)    
                
        array[i], array[right] = array[right], array[i]
        print(array)
        print(i)
        return i
        
    def quickSelect(self, array, left, right, k = 1):
        """
        QuickSort algorithm.
        Input:
            Array: List
            Low: First position of list
            High: Last position of
            k: kth smallest element in array
        """
        # If k is smaller than elements in array
        if (k > left and k <= right - left + 1):
            
            # Partition the array around the last element
            # and get position of pivotIndex in sorted array
            pivotIndex = self.partition(array, left, right)

            # If positions is the same as k
            if (pivotIndex - left == k - 1):
                return array[pivotIndex]
                
            # If position is more, recursive for left subarray
            if (pivotIndex - left > k - 1):
                return self.quickSelect(array, left, pivotIndex - 1, k)
                
            # Else, position is less than k. Recursive for right subarray
            return self.quickSelect(array, pivotIndex + 1, right, k - pivotIndex + left - 1)
            
        print("Index out of bounds")

if __name__ == "__main__":
    SKC = SelectiveKanervaCoding(numInputs = 2, experiment = "Testing")
    SKC.setState([0.98, 0.14])
    featureVector = SKC.compute()
    print(np.sum(featureVector))