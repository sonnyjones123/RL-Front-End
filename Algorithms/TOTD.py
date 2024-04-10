import numpy as np
from SelectiveKanervaCoding import *

class TOTD():
    """
    This is the Reinforcement Learning algorithm True Online Temporal Different Learning (Lambda) implemented
    with Selective Kanerva Coding used to create state representations of sensor signals.

    Parameters:
    - studyID: The study ID that will pull from SKC prototypes. Default: None.
    - numStates: The number of inputs that are accepted by TOTD: Default: 0.
    - alpha: The learning rate for TOTD. Default: 0.001.
    - gamma: The discount factor. Default: 0.9.
    - lambd: Default: 0.5.
    """
    def __init__(self, studyID = None, numStates = 0, alpha = 0.001, gammas = [0.9, 0.71, 0.75], lambd = 0.9):
        # SelectiveKanervaCoding
        self.SKC = SelectiveKanervaCoding(studyID = studyID, numInputs = numStates)

        # [TODO: add initialization for S]
        # Initializing params
        self.alpha = alpha
        self.gammas = gammas
        self.lambd = lambd

        self.numStates = numStates
        self.weights = np.zeros(numStates)
        self.eligibility = np.zeros(numStates)
        self.VOld = np.zeros(numStates)
        self.x = np.zeros(numStates * self.SKC.K)

    #-----------------------------------------------------------------------------------
    # ---- TOTD Update Algorithm

    def setState(self, newState):
        """
        Setting new state for TOTD update.

        Parameters:
        - newState: List of information about the new state. Should have the same length as numInputs.
        """
        # Setting New Input State
        self.newState = newState

    def update(self, newState, reward):
        # Inputting new state
        self.newState = newState
        self.SKC.setState(newState)
        self.Z = reward

        # Computing Feature Vector from SKC
        self.xPrime = self.SKC.computeSKC(self.newState)

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