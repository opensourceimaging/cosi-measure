"""
This script creates a snail like path file for COSI Measure  
     _   _   _
    | | | | | |              
    | | | | | |          
    | | | | | |      
    | | | | | |         
    | |_| |_| |        
      
A png of the created path is saved in a folder "figures" within the same directory
"""
from pathlib import Path
from numpy import arange, copy
from COSI import G0, displayPath, runWatchdogs# check4duplicates

##############################################################################
###################### set parameters for the path here ######################
##############################################################################

# Please enter the filename for the pathfile to be generated here
filename = '2021-10-14_PathfileTest_Snail'

# Set the min and max dimensions along x-y-z coordinates and step size
xMin       = 380 - 24 + 2.08 # [mm] minimum of x coordinate
xMax       = 380 + 24 + 2.08 # [mm] maximum of x coordinate

yMin       = 286 - 24 # [mm] minimum of y coordinate
yMax       = 286 + 24 # [mm] maximum of y coordinate

zMin       = 538.8 - 4 # [mm] minimum of z coordinate
zMax       = 538.8 + 4 # [mm] maximum of z coordinate

stepSize   = 4   # [mm] spacing of sample points

# in case the save rountine omitts the first point set doExtraPoint to True
# and set firstPoint to a point where you would like to start the measurement
center = (xMin+(xMax-xMin)/2, yMin+(yMax-yMin)/2, zMin+(zMax-zMin)/2)
firstPoint = (xMin, yMin, zMin-1)
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

xySteps = len(xSteps) + len(ySteps)

x0 = center[0]
y0 = center[1]
z0 = center[2]

with open(fileID, 'w+') as f:

    if doExtraPoint:
        f.write( G0(*firstPoint) )

    xIsReversed = False
    yIsReversed = False
    for z in zSteps:
        if yIsReversed:
            yIsReversed = False
            for y in reversed(ySteps):
                if xIsReversed:
                    xIsReversed = False
                    for x in reversed(xSteps):
                        f.write( G0(x=x, y=y, z=z) )
                else:
                    xIsReversed = True
                    for x in xSteps:
                        f.write( G0(x=x, y=y, z=z) )
        else:
            yIsReversed = True
            for y in ySteps:
                if xIsReversed:
                    xIsReversed = False
                    for x in reversed(xSteps):
                        f.write( G0(x=x, y=y, z=z) )
                else:
                    xIsReversed = True
                    for x in xSteps:
                        f.write( G0(x=x, y=y, z=z) )


if runWatchdogs(fileID) == False:
    displayPath(fileID)
