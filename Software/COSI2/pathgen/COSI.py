from numpy import array, unique, where, argsort
from pathlib import Path
import matplotlib.pyplot as plt

def G0(x=None, y=None, z=None):
    """
    Returns the G0 string 
    for a given combination of x,y,z coordinates.
    The units are in mm.

    Example:
    G0(x=123, z=42.1)  ->  'x123 z42.1'
    """
    # if x == None:
        # if y == None:
            # return 'z{}\n'.format(z)
        # elif z == None:
            # return 'y{}\n'.format(y)
        # else:
            # return 'y{} z{}\n'.format(y,z)
    # elif y == None: # x != None
        # if z == None:
            # return 'x{}\n'.format(x)
        # else:
            # return 'x{} z{}\n'.format(x,z)
    # elif z == None: # x & y != None
        # return 'x{} y{}\n'.format(x,y)
    # else:
        # return 'x{} y{} z{}\n'.format(x,y,z)
    return 'x{} y{} z{}\n'.format(x,y,z)

def decodeG0(line):
    length = len(line.split(' '))
    if length == 3:
        a = array(line.strip('\n').replace('x', '').replace('y','').replace('z','').split(' '), dtype=float)
    return (a)

def importPath(fileID):
    arr = []
    with open(fileID, 'r') as f:
        data = f.readlines()
        for line in data:
            arr += [decodeG0(line)]
    return arr

def decodeLakeShore(line):
    """
    Decoding standard data from Lake Shore Model 460 Gaussmeter
    in standard settings.
    The encoding is without comments: Bx, By, Bz, Bnorm
    """
    return array(line.strip('\n').split(','), dtype=float)

def importLakeShore(fileID):
    arr = []
    with open(fileID, 'r') as f:
        data = f.readlines()
        for line in data:
            arr += [decodeLakeShore(line)]
    return arr

def displayPath(fileID):
    filename = Path(fileID).name
    with open(fileID, 'r') as f:
        data = f.readlines()
        xCoords = []
        yCoords = []
        zCoords = []

        for line in data:
            point = decodeG0(line)
            xCoords += [point[0]]
            yCoords += [point[1]]
            zCoords += [point[2]]

    def plot1Layer(xCoords, yCoords, zCoord):
        _, ax = plt.subplots()
        ax.plot(xCoords, yCoords, marker='.', label='path (n={})'.format(len(xCoords)), zorder=-1)
        ax.scatter(xCoords[0], yCoords[0], marker='x', color='green', label='begin')
        ax.scatter(xCoords[-1], yCoords[-1], marker='+', color='red', label='end')
        ax.set_xlabel('x-coordinate in mm')
        ax.set_ylabel('y-coordinate in mm')
        ax.set_title('{} @ z={}'.format(filename, zCoord))
        plt.legend()
        plt.grid()
        #plt.savefig('../data/figures/{}{}.png'.format(filename, zCoord))

    zCoordsUnique, zCoordsUniqueIndices = unique(zCoords, return_index=True)
    zCoordsUnique = zCoordsUnique[argsort(zCoordsUniqueIndices)] # sort by occurence
    xCoords, yCoords, zCoords = array(xCoords), array(yCoords), array(zCoords)

    for zCoord in zCoordsUnique:
        layer = where(zCoord == zCoords)
        plot1Layer(xCoords[layer], yCoords[layer], zCoord)


def check4duplicates(fileID):
    with open(fileID, 'r') as f:
        data = f.readlines()
        if len(data) != len(unique(data)):
            print("There are duplicates in the pathfile!")
            return True
        else:
            print("No duplicates.")
            return False


def check4bounds(fileID):
    with open(fileID, 'r') as f:
        data = f.readlines()
        for line in data:
            x,y,z = decodeG0(line)
            if (x < 0) and (x > 500):
                print("There are points outside of COSY Measure!")
                return True
            elif (y < 0) and (y > 500):
                print("There are points outside of COSY Measure!")
                return True
            elif (z < 0) and (z > 600):
                print("There are points outside of COSY Measure!")
                return True
            else:
                pass
    print("All points are inside the limits of COSY Measure.")
    return False


def runWatchdogs(fileID):
    if check4duplicates(fileID) or check4bounds(fileID):
        print('Wooof wooof!')
        return True
    else:
        return False
