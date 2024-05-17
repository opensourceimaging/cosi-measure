"""
This script creates a spiral (inside out) like path file for COSI Measure
"""
from pathlib import Path
from numpy import arange, copy
from COSI import G0, displayPath, runWatchdogs# check4duplicates

##############################################################################
###################### set parameters for the path here ######################
##############################################################################
filename = '2021-10-14_Testpath_InsideOutCylinder'


xMin       = 342 # [mm] minimum of x coordinate
xMax       = 373 # [mm] maximum of x coordinate

yMin       = 263 # [mm] minimum of y coordinate
yMax       = 293 # [mm] maximum of y coordinate

zMin       = 126 # [mm] minimum of z coordinate
zMax       = 126 # [mm] maximum of z coordinate

stepSize   = 1   # [mm] spacing of sample points

maxRadius  = 16   # [mm] radius of cylinder / bore

# in case the save rountine omitts the first point set doExtraPoint to True
# and set firstPoint to a point where you would like to start the measurement
center = (xMin+(xMax-xMin)/2, yMin+(yMax-yMin)/2, zMin+(zMax-zMin)/2)
firstPoint = (center[0], center[1], zMax+1)
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
    r2 = (x-center[0])**2 + (y-center[1])**2# + (z-center[0])**2
    if r2 < radius**2:
        return True
    else:
        return False

xSteps = arange(xMin, xMax+stepSize, step=stepSize)
ySteps = arange(yMin, yMax+stepSize, step=stepSize)
zSteps = arange(zMin, zMax+stepSize, step=stepSize)

xySteps = len(xSteps)*len(ySteps)

x0 = center[0]
y0 = center[1]
z0 = center[2]



with open(fileID, 'w+') as f:

    if doExtraPoint:
        f.write( G0(*firstPoint) )

    xIsReversed = False
    yIsReversed = False
    # slice z in layers
    for z in zSteps:
        # in the x and y plane do corny circles
        f.write( G0(x0,y0,z))    # move to the center and z
        x = copy(x0)
        y = copy(y0)
        for i in range(xySteps):
            if  i % 2 == 0:
                for _ in range(i):
                    x = x+stepSize
                    if checkBounds(x,y,z,center,maxRadius):
                        f.write( G0(x=x, y=y, z=z) )
                for _ in range(i):
                    y = y+stepSize
                    if checkBounds(x,y,z,center,maxRadius):
                        f.write( G0(x=x, y=y, z=z) )
            if i % 2 == 1:
                for _ in range(i):
                    x = x-stepSize
                    if checkBounds(x,y,z,center,maxRadius):
                        f.write( G0(x=x, y=y, z=z) )
                for _ in range(i):
                    y = y-stepSize
                    if checkBounds(x,y,z,center,maxRadius):
                        f.write( G0(x=x, y=y, z=z) )

if runWatchdogs(fileID) == False:
    displayPath(fileID)