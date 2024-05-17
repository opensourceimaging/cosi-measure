"""
This script creates a spherical path file for COSI Measure
"""
from pathlib import Path
from numpy import arange, copy
import numpy as np
from COSI import G0, displayPath, runWatchdogs# check4duplicates

##############################################################################
###################### set parameters for the path here ######################
##############################################################################

# Please enter the filename for the pathfile to be generated here
filename = '2021-10-14_PathfileTest_Spherical'

# center of sphere
center = (380 + 2.08, 286, 538.8)

phiNumber = 10
thetaNumber = 10

radius = 20   # [mm] radius of sphere of FOV
maxRadius = 21 # [mm] maximal limit for a sphere around the center (watchdog)

# in case the save rountine omitts the first point set doExtraPoint to True
# and set firstPoint to a point where you would like to start the measurement
firstPoint = (center[0], center[1], center[2] + radius - 1)
doExtraPoint = True
##############################################################################
##############################################################################
##############################################################################

path2file = Path(__file__).resolve().parent
fileID = Path.joinpath(path2file, filename).with_suffix('.path')

def checkBounds(x,y,z,center,radius):
    """check if coordinates are in cylinder
    returns True if x,y,z are in cylinder with symmetry axis z
    
    * center - array of x,y(,z) coordinates of the center of the cylinder
    * radius - radius of the cylinder """
    r2 = (x-center[0])**2 + (y-center[1])**2 + (z-center[0])**2
    if r2 < radius**2:
        return True
    else:
        return False


def calcAngles(phiNumber, thetaNumber):
    """returns the angles of phi and theta for a given number of phi and theta angles
    the theta angles are set to be gauss legendre points and theta are equidistant"""
    samplePoints, weights = np.polynomial.legendre.leggauss(thetaNumber)
    samplePoints  = samplePoints[::-1]
    weights       = weights[::-1]
    
    thetaRad      = np.arccos(samplePoints) - np.pi/2
    
    phiMin        = 0    #[rad] Longitude limits
    phiMax        = 2*np.pi*(1-1/phiNumber)     
    phiRad        = np.linspace(phiMin,   phiMax,   phiNumber)

    return phiRad, thetaRad


def toCathesianCoords(r, phi, theta, center):
    x = r*np.sin(theta)*np.cos(phi) + center[0]
    y = r*np.sin(theta)*np.sin(phi) + center[1]
    z = r*np.cos(theta) + center[2]
    return x,y,z


phiRad, thetaRad = calcAngles(phiNumber, thetaNumber)
thetaRad += np.pi/2

print('Started to write pathfile.')

with open(fileID, 'w+') as f:
    g0 =  "X{:.2f}, Y{:.2f}, Z{:.2f}\n".format(*toCathesianCoords(radius-1, phiRad[0], thetaRad[0], center))
    # f.write( g0 ) 
    for theta in thetaRad:
        for phi in phiRad:
            g0 =  "x{:.2f} y{:.2f} z{:.2f}\n".format(*toCathesianCoords(radius, phi, theta, center))
            print(radius, phi, theta, 'gcode = ', g0)
            f.write( g0 ) 

print('Pathfile is written.')
print('Started to write angles.')

with open(filename+'.angles', 'w+') as f:
    for theta in thetaRad:
        for phi in phiRad:
            angl =  "{},{}\n".format(phi, theta)
            f.write( angl ) 

print('Angles are written.')
print('Running watchdogs.')

if runWatchdogs(fileID) == False:
    displayPath(fileID)