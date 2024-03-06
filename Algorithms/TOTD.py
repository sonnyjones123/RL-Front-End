import numpy as np
from SelectiveKanervaCoding import *

class TOTD(SelectiveKanervaCoding):
    """
    This is the Reinforcement Learning algorithm True Online Temporal Different Learning (Lambda) implemented
    with Selective Kanerva Coding used to create state representations of sensor signals.
    """
    def __init__(self, studyID = None, numStates = 0, alpha = 0.001, gamma = 0.9, lambd = 0.5):
        # SelectiveKanervaCoding
        self.SKC = SelectiveKanervaCoding(studyID = studyID, numInputs = numStates)

        # [TODO: add initialization for S]
        # Initializing params
        self.alpha = alpha
        self.gamma = gamma
        self.lambd = lambd

        self.numStates = numStates
        self.weights = np.zeros(numStates)
        self.eligibility = np.zeros(numStates)
        self.VOld = np.zeros(numStates)
        self.x = np.zeros(numStates * self.SKC.K)

    #-----------------------------------------------------------------------------------
    # ---- TOTD Update Algorithm

    def update(self, newState, reward):
        # Inputting new state
        self.newState = newState
        self.SKC.setState(newState)
        self.Z = reward

        # Computing Feature Vector from SKC
        self.xPrime = self.computeSKC(self.newState)

        # Computing general value function
        self.V = self.weights.T * self.x
        self.VPrime = self.weights.T * self.xPrime

        # Computing TD error
        self.tdError = self.Z + (self.gamma * self.VPrime) - self.V

        # Computing eligibility trace
        self.eligibility = (self.gamma * self.lambd * self.eligibility) + self.x - (self.alpha * self.gamma * self.lambd * (self.eligibility.T * self.x) * self.x)
        
        # Updating weights
        self.weights = self.weights + self.alpha * (self.tdError + self.V - self.VOld) * self.eligibility - self.alpha * (self.V - self.VOld) * self.x

        # Applying new variables
        self.VOld = self.VPrime
        self.x = self.xPrime

if __name__ == '__main__':
    pass