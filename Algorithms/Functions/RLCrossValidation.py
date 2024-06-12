# Importing Packages
import pandas as pd
import numpy as np
from itertools import product, tee
from tqdm import tqdm
import scipy
import matplotlib.pyplot as plt

try:
    from ExpectedReturn import expectedReturn
except:
    from Functions.ExpectedReturn import expectedReturn

# Cross Validation Function
def CrossValidation(agent, data, Z, parameters, plot = False, xLimit = None):
    """
    Cross Validation function for TOTD. Will run through all combinations of parameters inputted 
    and evaluate the predictions on its cross correlation with the action return. Make sure arrays
    are correctly formatted in row orientation.

    Accuracy validation scores the model on the percentage of correct predictions. 
    F1 scores the model on the percentage on a ratio of precision and recall.

    Parameters:
    - data: The raw/processed signals that will be input for our feature space.
    - Z: The target label for training.
    - parameters: A dictionary {'param name' : list[parameter values]}.
    """
    # Checking Parameters Data Type
    if isinstance(parameters, dict):
        pass
    else:
        raise TypeError("Parameters not in dictionary format. Please reformat to {'parameter': list(params)}")
    
    # Checking Data Data Type
    if not type(data).__module__ == np.__name__:
        data = np.array([data])
    
    # Checking Data Data Type
    if not type(Z).__module__ == np.__name__:
        Z = np.array([Z])
    
    # Storing Best Params, Values, and Model
    bestParams = None
    bestLag = float('-inf')
    lagList = []

    # Loading in TOTD
    learningAgent = agent(studyID = 'CrossVal', numInputs = data.shape[0])
    iterations = data.shape[1]

    # Printing Message
    print(f"Performing Cross Validation on {list(parameters.keys())}")

    # Creating Combinations of Hyperparameters
    lengthIterable, hyperParameterCombinations = tee(product(*parameters.values()))

    # Looking at Length of Hyperparameter Combinations
    lengthCombinations = sum(1 for _ in lengthIterable)

    # Iterating through self.parameters
    for hyperParameters in tqdm(hyperParameterCombinations, desc = 'Running Cross Validation', unit = 'iteration', total = lengthCombinations):
        # Setting New Parameters for Model
        learningAgent.setParams(**dict(zip(parameters.keys(), hyperParameters)))

        # Resetting Model Weights for New HyperParameters
        try:
            learningAgent.reset()
        except:
            pass

        # Iterating Through Data and Predicting with TOTD
        predicted = []

        # Iterating Through Data
        for index in range(iterations):
            # Updating for Different Data Lenths and Types
            try:
                ZIndexed = Z[:,index]
            except:
                ZIndexed = Z[index]

            # Predicting
            predictions = learningAgent.update(data[:,index], ZIndexed)

            # Appending Predictions to List
            predicted.append(predictions)

        # Turning Predictions into Array
        predicted = np.concatenate(predicted).T
        
        # Calculating Actual Return
        actualReturn = expectedReturn(Z, learningAgent.gammas, method = 'conv')

        # Calculating Lag Between Prediction and Actual Return
        crossCor = scipy.signal.correlate(actualReturn, predicted)
        lags = scipy.signal.correlation_lags(len(actualReturn), len(predicted))
        lag = lags[np.argmax(crossCor)]

        # Plotting
        if plot == True:
            # Creating Tickmarks
            samples = np.linspace(0, iterations, iterations)
            
            # Plotting
            plt.figure(figsize=(20,10))
            plt.plot(samples, Z, color = 'm', alpha = 0.2)
            plt.plot(samples, predicted, color = 'c')
            plt.plot(samples, actualReturn, 'b', alpha = 0.5)
            plt.title(f"Predicted vs Actual Return (Gamma: {learningAgent.gammas}))")
            plt.xlabel('Samples')
            plt.legend(['Raw Signal', 'Predicted Return', 'Actual Return'])

            # Setting xLim
            try:
                plt.xlim(xmin = xLimit[0], xmax = xLimit[1])
            except:
                pass

            plt.show()
        
        # Appending to List
        lagList.append(lag)

        # Printing Average Score
        print("")
        print(f"Params: {dict(zip(parameters.keys(), hyperParameters))}")
        print(f"Lag: {lag}")
        print("")

        # If Accuracy is Better
        if lag > bestLag:
            # Update Best Score and Best Params
            bestLag = lag
            bestParams = dict(zip(parameters.keys(), hyperParameters))

    print("")
    print(f"Best Lag: {bestLag}")
    print(f"Best Params: {bestParams}")

    # Returning Best Score and Best Params
    return bestLag, bestParams, lagList