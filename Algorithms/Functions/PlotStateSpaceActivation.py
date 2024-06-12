# Importing Packages
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize

def plotStateSpaceActivation(SKC, data):
    """
    Plotting the state space activation for Selective Kanerva Coding. Used to visualize which prototpyes are being activated in the state space.

    Written by Sonny Jones
    Version: 2024.05.31

    Parameters:
    - SKC: SKC class initialized with prototypes, inputs, prototype lists, and studyID.
    - inputData: The data to be inputted to SKC.
    """
    # Checking Data Data Type
    if not type(data).__module__ == np.__name__:
        data = np.array([data])

    # Creating List to Hold Activations
    activationList = np.zeros(SKC.K)

    # Iterating Through Data
    for index in range(data.shape[1]):
        # Updating for Different Data Lenths and Types
        try:
            Z = data[:,index]
        except:
            Z = data[index]

        # Getting Prototypes
        activatedPrototypes = SKC.computeSKC(Z)

        # Interating Through List of Prototype Activations
        for cNum, C in enumerate(SKC.c):
            # Grabbing Acitvations Based on Prototypes
            selectedPrototypes = activatedPrototypes[cNum*SKC.K: (cNum + 1)*SKC.K]

            # Adding to ActivationList
            activationList += selectedPrototypes

    # Normalizing ActivationList
    activationList = activationList/max(activationList)

    # Creating Subplots
    fig, axes = plt.subplots(SKC.n, SKC.n, figsize = (20, 20), sharex = 'col', sharey = 'row', constrained_layout = True)

    # Creating Color Map for Plotting
    cmap = LinearSegmentedColormap.from_list('blue_white', ['lightgrey', 'darkblue'])

    # Creating X Labels and Y Labels
    labels = [f"P{i + 1}" for i in range(SKC.n)]

    # Iterating Through Columns
    for x, row in enumerate(axes):
        # Iterating Through Rows
        for y, cell in enumerate(row):

            # Iterating Through Prototype
            for index, prototype in enumerate(SKC.P):
                # Plotting Prototype
                cell.plot(prototype[y], prototype[x], marker = 'o', c = cmap(activationList[index]), markersize = 1)

            # Setting X and Y Label
            if x == len(axes) - 1:
                cell.set_xlabel(labels[y], fontsize = 25)
            if y == 0:
                cell.set_ylabel(labels[x], fontsize = 25)

    # Adding Color Bar
    cbar = fig.colorbar(
        plt.cm.ScalarMappable(norm = Normalize(vmin = 0, vmax = 1), cmap = cmap),
        ax = axes,
        orientation = 'vertical',
        fraction = 0.02,
        pad = 0.04
    )

    # Showing Plot
    plt.show()