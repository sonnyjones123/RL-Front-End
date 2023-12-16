import numpy as np
import math

class SelectiveKanervaCoding():
    def __init__(self, numPrototypes = 0, numSensors = 0, cList = 0):
        # Initializing Params
        self.K = numPrototypes
        self.n = numSensors
        self.c = cList
        
        # Creating Randomized P
        self.P = np.random.rand(self.K, self.n)
        # [TODO]
        # Ask how to properly set up prototypes
        
    #-----------------------------------------------------------------------------------
    # ---- SKC Update Algorithm
        
    def newState(self, nextState):
        self.nextState = nextState
        
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
        return i
        
    def QuickSelect(self, array, left, right, k):
        """
        QuickSelect algorithm
        Input:
            Array: List
            Left: First index in array
            Right: Last index in array
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
                return self.QuickSelect(array, left, pivotIndex - 1, k)
                
            # Else, position is less than k. Recursive for right subarray
            return self.QuickSelect(array, pivotIndex + 1, right, k - pivotIndex + left - 1)
            
        print("Index out of bounds")
        
    def SKC(self):
        # Resetting 
        self.D = np.zeros(self.K, 1)
        # Looping Through Params
        for i in range(self.K):
            for j in range(self.n):
                # Computing Euclidean Distance
                self.D[i] = math.dist(self.P[i][j], self.nextState[j])
                
        # QuickSelect
        
        # Looping Through C
        for m in range(len(self.c)):
            pass

if __name__ == "__main__":
    SKC = SelectiveKanervaCoding()
    arr = [10, 4, 5, 8, 6, 11, 26]
    n = len(arr)
    k = 1
    print(SKC.QuickSelect(arr, 0, n - 1, k))
