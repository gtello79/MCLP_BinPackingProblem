import matplotlib.pyplot as plt 
import random as rand

dimBox = dict()
vol = dict()
volBin = dict() #Volumen de cada bin

def popRandomBin(bins):
    rPos = int(rand.random()*len(bins))
    theBin = bins.pop(rPos)
    return theBin, bins

def calculateComplex(idBox, dim):
    x,y,z = dim
    expo = 1
    vol = x*y*z
    return ( ( (x/z)*(x/y)*(y/z) )**expo ) * vol

def vol(listBoxes, boxes):
    totalVol = 0
    for box in listBoxes:
        x,y,z = boxes[box]
        totalVol += x*y*z
    return totalVol


def getMostComplexBox(bin, boxes):
    idBox = []
    eval = 0
    
    for b in bin:
        boxShape = boxes[b] #Cargar instancia
        
        currentEval = calculateComplex(b,boxShape)    
        if (idBox is None):
            idBox = b
            eval = currentEval
        else:
            if(currentEval > eval):
                idBox = b
                eval = currentEval
    return idBox, eval

def createPlot(InitialVol, finalVol):
    id_bins_first = list( InitialVol.keys() )
    size_initial_bins = list( InitialVol.items() )

    id_bins_final = list( finalVol.keys() )
    size_final_bins = list( finalVol.items() )

    plt.plot(size_initial_bins, label = 'First Solution')
    plt.plot(size_final_bins, label = 'Final Solution')

    plt.title('Volumen asociado a cada bin')
    plt.legend()
    plt.show()
