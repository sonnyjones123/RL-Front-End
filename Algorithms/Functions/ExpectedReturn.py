import numpy as np

def expectedReturn(data, gamma, method = 'normal'):
    """
    This is a sanity check for the TOTD expected return value. This will take in an input signal
    and calculate the expected return with a timeStep of 5 * 1 / (1 - gamma).

    Args:
        data: Signal data.
        gamma: The gamma value/values to calculate for the expected return.
    Returns:
        np.array: Convoluted signal with expected return.
    """
    # Expected Return Via Convolution
    if method == 'conv':
        # Calulating WindowSize for Expected Return Over 5x Tau: where Tau = 1/ (1- gamma)
        timeStep = int(5 * 1 / (1 - gamma))

        # Creating Exponential Decay
        t = np.linspace(0, timeStep, timeStep)
        expDecay = gamma ** t

        # Returning Expected Cumulative Return
        return np.convolve(data, expDecay, mode = 'same') * (1 - gamma)

    # If Method Is Normal
    elif method == 'normal':
        # Calulating Expected Return Over 5x Tau: where Tau = 1/ (1- gamma)
        timeStep = int(5 * 1 / (1 - gamma))

        # Length of Data to be Processed
        try:
            lenData = int(len(data) - timeStep)
        except:
            lenData = int(data.shape[0] - timeStep)

        # Creating Array for Expected Return
        expectedReturn = np.zeros(lenData)

        # Iterating Over Timesteps
        for i in range(lenData):
            # Term to Hold Values
            term = np.zeros(timeStep)

            # Iterating Over Timestep
            for k in range(timeStep):
                # Getting Exponential Decay with Gamma
                term[k] = gamma ** (k) * data[i + k]

            # Saving Return
            expectedReturn[i] = np.sum(term)

        # Returning Array with Expected Returns
        return expectedReturn * (1 - gamma)
    
    # Else
    else:
        # Raising Error
        raise TypeError(f"No Method named {method}")