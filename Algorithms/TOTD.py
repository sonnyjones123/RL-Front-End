import numpy as np
from SelectiveKanervaCoding import *

class TOTD():
    def __init__(self, studyID = None, numInputs = 3, alpha = 0.001, gammas = [0.9, 0.71, 0.75], lambda_ = 0.9):
        """
        This is the Reinforcement Learning algorithm True Online Temporal Different Learning (Lambda) implemented
        with Selective Kanerva Coding used to create state representations of sensor signals.

        Written by Sonny Jones
        Version: 2024.05.19

        Parameters:
        - studyID: The study ID that will pull from SKC prototypes. Default: None.
        - numInputs: The number of inputs that are accepted by TOTD: Default: 3.
        - alpha: The learning rate for TOTD. Default: 0.001.
        - gammas: The discount factor. Default: [0.9, 0.71, 0.75].
        - lambd: Default: 0.9.
        """
        # SelectiveKanervaCoding
        self.SKC = SelectiveKanervaCoding(studyID = studyID, numInputs = numInputs)

        # Getting Feature Length From SKC
        self.featureLength = self.SKC.K * len(self.SKC.c)

        # Initializing Learning Params
        self.alpha = alpha
        self.gammas = np.array([gammas])
        self.lambda_ = lambda_

        # Loop Count
        self.loopCount = 0

        # Loading Previous Variables
        self.loadOld = False

    #-----------------------------------------------------------------------------------
    # ---- TOTD Update Algorithm

    # Variable Reset Function
    def reset(self):
        """
        Resets variables for new learning trial.
        """
        try:
            # Resetting Variables After Learning Completion
            self.featureVector = np.array(np.zeros(self.featureLength))
            self.weights = np.array(np.zeros(self.featureLength))
            self.VOld = np.array(np.zeros(self.featureLength))
            self.eTrace = np.array(np.zeros(self.eTrace.shape))
            self.loopCount = 0

        except:
            print("Variables Haven't Been Initiated Yet. Learning is Fresh")

    # Changing Loading Variable Function
    def setLoadOld(self, attribute):
        """
        Setting the variable that controls loading of previous variables.
        """
        # Setting Loading Variable to Attribute
        self.loadOld = attribute

    # Setting Params
    def setParams(self, **kwargs):
        """
        Setting params for the base classifier.

        Parameters:
        - kwargs(dict): A dictionary of args to be set.
        """
        # Iterating Through Params
        for key, value in kwargs.items():
            # Setting Attribute
            setattr(self, key, value)

        # Making Sure Gamma Is A List
        if not isinstance(self.gammas, np.ndarray):
            self.gammas = np.array([self.gammas])

    # TOTD Update Function
    def update(self, newState, Znew):
        """
        Performing TOTD Update

        Parameters:
        - newStates: The next input state for the update.
        - ZNew: The cumulant signal for prediction.
        """
        # Computing Feature Vector from SKC
        newFeatureVector = self.SKC.computeSKC(newState)

        # If This is Initial Loop
        if self.loopCount == 0:
            # Loading In Old Learning Variables If Applicable
            if self.loadOld is True:
                self.featureVector = self.pastFeatureVector
                self.weights = self.pastWeights
                self.eTrace = self.pastETrace
                self.VOld = self.pastVOld
            
            else:
                # Initializing params
                self.featureVector = np.array(np.zeros(self.featureLength))
                try:
                    # If ZNew is A N-Dimension Vector
                    self.weights = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.eTrace = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.VOld = np.array(np.zeros(Znew.shape[0]))

                    # Setting Output to None
                    output = np.zeros(Znew.shape[0])

                except:
                    # If ZNew is A Scalar
                    self.weights = np.array(np.zeros(self.featureLength))
                    self.eTrace = np.array(np.zeros(self.featureLength))
                    self.VOld = np.array([0])

                    # Setting Output to None
                    output = [0]

        else:
            # Computing general value function
            V = np.dot(self.weights, self.featureVector.T)
            VNew = np.dot(self.weights, newFeatureVector.T)

            # Computing TD error
            tdError = self.Z + self.gammas * VNew - V

            # Computing eligibility trace
            self.eTrace = (self.lambda_ * self.gammas.T * self.eTrace) + self.featureVector - (self.alpha * self.lambda_ * self.gammas * np.dot(self.featureVector, self.eTrace.T)).T * self.featureVector

            # Updating weights
            self.weights = self.weights + (self.alpha * (tdError + V - self.VOld)).T * self.eTrace - (self.alpha * np.array([(V - self.VOld)])).T * self.featureVector

            # Resetting Old General Value Function Output
            self.VOld = VNew

            # Setting Output
            output = VNew

        # Setting Old Feature Vector and Cumulant
        self.featureVector = newFeatureVector
        self.Z = np.array([Znew])

        # Updating Loop Count
        self.loopCount += 1
        
        # Returning Output
        return output * (1 - self.gammas)

    # Saving Old Weights and Eligibility Trace
    def saveInfo(self):
        """
        This is a function designed to keep the old weights and eligibility trace in case learning
        needs to start from a set point and not from old.
        """
        self.pastFeatureVector = self.featureVector
        self.pastWeights = self.weights
        self.pastETrace = self.eTrace
        self.pastVOld = self.VOld

if __name__ == '__main__':
    pass