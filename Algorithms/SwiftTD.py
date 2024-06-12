import numpy as np
import platform
import pandas as pd
from SelectiveKanervaCoding import *

class SwiftTD():
    def __init__(self, studyID = None, numInputs = 3, initAlpha = 1, gammas = [0.9, 0.71, 0.75], lambda_ = 0.9, epsilon = 1, maxStepSize = 0.501, stepSizeDecay = 0.9, metaStepSize = -2):
        """
        This is the Reinforcement Learning algorithm Swift Temporal Difference Learning (SwiftTD) implemented
        with Selective Kanerva Coding used to create state representations of sensor signals.

        Written by Sonny Jones
        Version: 2024.05.19

        Parameters:
        - studyID: The study ID that will pull from SKC prototypes. Default: None.
        - numInputs: The number of inputs that are accepted by SwiftTD: Default: 3.
        - alpha: The learning rate for SwiftTD. Default: 1.
        - gammas: The discount factor. Default: [0.9, 0.71, 0.75].
        - lambda_: Default: 0.9.
        - epsilon: Stability constant in learning rate update: Default 1. 
        - maxStepSize: The maximum step size the weights can be adjusted by. Default: 0.501
        - stepSizeDecay: Decay factor for step size. Default: 0.9
        - metaStepSize: Default: 
        """
        # SelectiveKanervaCoding
        self.SKC = SelectiveKanervaCoding(studyID = studyID, numInputs = numInputs)

        # Getting Feature Length From SKC
        self.featureLength = self.SKC.K * len(self.SKC.c)

        # Initializing Learning Params
        self.initAlpha = initAlpha
        self.gammas = np.array([gammas])
        self.lambda_ = lambda_
        self.epsilon = epsilon # Stability constant used during momentum calcualtion
        self.maxStepSize = maxStepSize
        self.stepSizeDecay = stepSizeDecay
        self.metaStepSize = metaStepSize

        # Loop Count
        self.loopCount = 0

        # Loading Previous Variables
        self.loadOld = False

    #-----------------------------------------------------------------------------------
    # ---- SwiftTD Update Algorithm

    # Variable Reset Function
    def reset(self):
        """
        Resets variables for new learning trial.
        """
        # Resetting Variables After Learning Completion
        try:
            self.featureVector = np.array(np.zeros(self.featureLength))
            self.weights = np.array(np.zeros(self.featureLength))
            self.VOld = np.array(np.zeros(self.featureLength))
            self.eTrace = np.array(np.zeros(self.eTrace.shape))
            self.betas = np.array(np.zeros(self.betas.shape))
            self.h = np.array(np.zeros(self.h.shape))
            self.hOld = np.array(np.zeros(self.hOld.shape))
            self.be = np.array(np.zeros(self.be.shape))
            self.idbdTrace = np.array(np.zeros(self.idbdTrace.shape))
            self.gradientNorm = np.array(np.zeros(self.gradientNorm.shape))
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

    # SwiftTD Update Function
    def update(self, newState, Znew):
        """
        Performing SwiftTD Update

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
                self.betas = self.pastBetas
                self.h = self.pastH
                self.hOld = self.pastHOld
                self.be = self.oldBE
                self.idbdTrace = self.oldIDBDTrace
                self.gradientNorm = self.oldGradientNorm
                    
            else:
                # Initializing params
                self.featureVector = np.array(np.zeros(self.featureLength))
                try:
                    # If ZNew is A N-Dimension Vector
                    self.weights = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.betas = np.array(np.full((Znew.shape[0], self.featureLength), np.log(self.initAlpha)))
                    self.h = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.hOld = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.be = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.idbdTrace = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.eTrace = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.gradientNorm = np.array(np.zeros((Znew.shape[0], self.featureLength)))
                    self.VOld = np.array(np.zeros(Znew.shape[0]))
                    self.featureCounter = np.array(np.zeros((Znew.shape[0], self.featureLength)))

                    # Setting Output to None
                    output = np.zeros(Znew.shape[0])

                except:
                    # If ZNew is A Scalar
                    self.weights = np.array(np.zeros((1, self.featureLength)))
                    self.betas = np.array(np.full((1, self.featureLength), np.log(self.initAlpha)))
                    self.h = np.array(np.zeros((1, self.featureLength)))
                    self.hOld = np.array(np.zeros((1, self.featureLength)))
                    self.be = np.array(np.zeros((1, self.featureLength)))
                    self.idbdTrace = np.array(np.zeros((1, self.featureLength)))
                    self.eTrace = np.array(np.zeros((1, self.featureLength)))
                    self.gradientNorm = np.array(np.zeros((1, self.featureLength)))
                    self.VOld = np.array([0])
                    self.featureCounter = np.array(np.zeros((1, self.featureLength)))

                    # Setting Output to None
                    output = [0]

        else:
            # Computing general value function
            V = np.dot(self.weights, self.featureVector.T) # Previous State Value
            VNew = np.dot(self.weights, newFeatureVector.T) # Current State Value

            # Computing TD error
            tdError = self.Z + self.gammas * VNew - V # Error from current reward, current and previous state

            # Computing Eligibility
            dotProductEligibility = np.array([np.dot(self.featureVector, self.eTrace.T)])

            # Sum of Step Sizes and Scaling Factor
            try:
                scaleFactor = np.array(np.ones(Znew.shape[0]))
                sumStepSize = np.array(np.zeros(Znew.shape[0]))
            except:
                scaleFactor = np.array([1])
                sumStepSize = np.array([0])

            #---------------------------------------
            # Scaling Factor Updating
            #---------------------------------------
            # Calculating and Updating Scaling Factor
            temp = np.exp(self.betas) * self.featureVector * self.featureVector # Dependent on which features are present, x(t)^2
            self.featureCounter += temp

            try:
                sumStepSize = np.sum(temp, axis = 1)
            except:
                sumStepSize = np.sum(temp)

            # Recaling if Sum of Step Size Exceeds Maximum Step Size
            scaleFactor = np.array([np.where(sumStepSize > self.maxStepSize, self.maxStepSize / sumStepSize, scaleFactor)])

            #---------------------------------------
            # Updating Weights with Adaptive Step-Size
            #---------------------------------------
            # Calculating IBDB Trace
            self.idbdTrace = (self.gammas.T * self.lambda_ * self.idbdTrace) + (self.h * self.featureVector) # Incremental Delta-Bar-Delta Trace. 

            # Scaling Step Size
            stepSize = np.array(np.exp(self.betas)) * scaleFactor.T

            # Updating be
            self.be = self.lambda_ * self.gammas.T * self.be + \
                    (stepSize * self.featureVector) - \
                    (stepSize * self.gammas.T * self.lambda_ * dotProductEligibility.T * self.featureVector) - \
                    (stepSize * self.gammas.T * self.lambda_ * (self.featureVector * self.featureVector) * self.be)

            # Updating Eligibility Trace
            self.eTrace = self.lambda_ * self.gammas.T * self.eTrace
            self.eTrace = self.eTrace + (stepSize * self.featureVector) - \
                    (stepSize * self.lambda_ * self.gammas.T * dotProductEligibility.T * self.featureVector) # Decaying trace of features that most impacted weight vector changes.

            # Updating weights
            self.weights = self.weights + (tdError.T * self.eTrace) - (stepSize * np.array([V - self.VOld]).T) * self.featureVector # Weight Update

            # Updating Temp
            temp = self.h
            
            # Updating h
            self.h = self.h + (tdError.T * self.be) + (self.eTrace * (-1 * self.hOld * self.featureVector)) - \
                    (self.featureVector * (stepSize * np.array([V - self.VOld]).T) + (stepSize * self.featureVector * (self.h - self.hOld))) # Decaying trace of cumulative sum of recent weight changes

            # Updating hOld
            self.hOld = temp

            # Updating Betas If Scaling Factor Is 1
            factorUpdate = np.array(np.where(scaleFactor == 1, 1, 0))
            self.betas += (self.metaStepSize / (np.exp(self.betas) + self.epsilon) * tdError.T * self.idbdTrace) * factorUpdate.T

            # If Betas Is Greater Than 0, Make 0
            self.betas = np.where(self.betas > 0, 0, self.betas)

            # Updating If Scaling Factor is Less than 1 and the feature is active
            factorUpdate = np.where(scaleFactor < 1, 1, 0)
            updateIndex = np.outer(factorUpdate, self.featureVector)
            self.betas += updateIndex * np.log(self.stepSizeDecay)
            booleanIndex = updateIndex.astype(bool)
            self.idbdTrace[booleanIndex] = 0
            self.h[booleanIndex] = 0
            self.hOld[booleanIndex] = 0
            self.be[booleanIndex] = 0

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
        self.pastBetas = self.betas
        self.pastH = self.h
        self.pastHOld = self.hOld
        self.oldBE = self.be
        self.oldIDBDTrace = self.idbdTrace
        self.oldGradientNorm = self.gradientNorm

if __name__ == '__main__':
    pass