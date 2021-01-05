import random as rand
import numpy as np

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



