'''rst@PTB 240408 rst030@protonmail.com'''

import numpy as np
import os
import osi2magnet
from datetime import datetime

class pth():
    '''path object. created for cosi.'''
    r = np.zeros((10,3))
    
    
    datetime = ''
    pathCenter = None
    pathFile = 0 # a file where path data is stored
    radius = 0
    
    current_index = 0 # when scanned along path, its current index iterates. Used for live path plotting

    def __init__(self,filename='',csv_filename=None):
        
        self.filename = 'dummy'
        self.datetime = str(datetime.now())
        
        if csv_filename is not None:
            self.import_from_csv(csv_filename)
            self.get_path_center()
            self.get_path_radius()
        
        if filename != '':
            self.filename = filename
            self.r = []
              
            with open(filename) as file:
                rawPathData = file.readlines()
                self.r = np.zeros((len(rawPathData),3))
                for idx, point in enumerate(rawPathData):
                    splitPoint = point.rstrip("\n\r").split('z')
                    z = float(splitPoint[1])
                    self.r[idx, 2] = z

                    splitPoint = splitPoint[0].split('y')
                    y = float(splitPoint[1])
                    self.r[idx, 1] = y

                    splitPoint = splitPoint[0].split('x')
                    x = float(splitPoint[1])
                    self.r[idx, 0] = x

         
            self.get_path_center()
            self.get_path_radius()
                        
                        
    # ----- importer from csv -----
    # csv contains path data and b0 data. 
    # header lines start with #
    # read all lines first
    def import_from_csv(self,filename):
        print('importing path from a csv file')
        self.filename = filename
        
        with open(filename) as file:
            rawPathData = file.readlines()
            headerLength = 0
            for line in rawPathData:
                if line[0]=='#':
                    if 'time' in line:
                        self.datetime = line.split('time')[1]
                    headerLength += 1
                    
            PathDataNoHeader = rawPathData[headerLength:]
            
            self.r = np.zeros((len(PathDataNoHeader),3))
            
            for idx, txtPoint in enumerate(PathDataNoHeader):
                self.r[idx,0] = txtPoint.split(',')[0]
                self.r[idx,1] = txtPoint.split(',')[1]
                self.r[idx,2] = txtPoint.split(',')[2]

 
    def get_path_radius(self):
        self.radius = (np.nanmax(
            (abs(self.r[:,0]-self.pathCenter[0]))**2+
            (abs(self.r[:,1]-self.pathCenter[1]))**2+
            (abs(self.r[:,2]-self.pathCenter[2]))**2))**(1/2)
 
 
    def get_path_center(self):
        x_c = np.nanmean(self.r[:,0])
        y_c = np.nanmean(self.r[:,1])
        z_c = np.nanmean(self.r[:,2])
        self.pathCenter = np.array([x_c,y_c,z_c])
                    
                    
    def center(self,origin=None):
        # centering the path to the origin of the magnet if given, else center on the path center
        if origin is not None:
            x_c = origin[0]
            y_c = origin[1]
            z_c = origin[2]
        else:
            self.get_path_center()
            x_c = self.pathCenter[0]
            y_c = self.pathCenter[1]
            z_c = self.pathCenter[2]
            
        self.r[:,0] = self.r[:,0]-x_c
        self.r[:,1] = self.r[:,1]-y_c
        self.r[:,2] = self.r[:,2]-z_c
        self.get_path_center()
           
        print('path center set to: ',self.pathCenter)  


    def rotate_euler_backwards(self,alpha,beta,gamma):
        # uses the method defined in osi2magnet. todo: move to utils
        #orgn = [self.pathCenter[0],self.pathCenter[1],self.pathCenter[2]]
        
        for i in range(len(self.r[:,0])):
            self.r[i,:] = osi2magnet.rotatePoint_xyz(point = self.r[i,:],origin=self.pathCenter,gamma=-gamma,beta=-beta,alpha=-alpha)

    def saveAs(self,filename: str):
        # open file filename and write comma separated values in it
        # experiment parameters
        # data
        with open(filename, 'w') as file:
            #file.write('COSI pathfile generator output.')
            #file.write('Date/Time,%s\n\n\n'%self.datetime)
            for pathpt in self.r:
                file.write('x%.2f y%.2f z%.2f\n'%(pathpt[0],pathpt[1],pathpt[2]))
        file.close()


def generate_spherical_path():
    pass
    # todo: refer to utils or copy path gen methods here























    def loadPath(self, pathFileName: str):
        self.pathFile = pathFileName
        with open(pathFileName) as file:
            rawPathData = file.readlines()
            self.path = np.zeros((len(rawPathData),3))
            
            for idx, point in enumerate(rawPathData):
                splitPoint = point.rstrip("\n\r").split('Z')
                z = splitPoint[1]
                self.path[idx, 2] = z

                splitPoint = splitPoint[0].split('Y')
                y=splitPoint[1]
                self.path[idx, 1] = y

                splitPoint = splitPoint[0].split('X')
                x = splitPoint[1]
                self.path[idx, 0] = x

                self.headPosition = np.array([x,y,z])

                #print(self.headPosition)


            self.calculatePathCenter()


    def calculatePathCenter(self):
        x_c = np.nanmean(self.path[:,0])
        y_c = np.nanmean(self.path[:,1])
        z_c = np.nanmean(self.path[:,2])
        self.pathCenter = np.array([x_c,y_c,z_c])
        print('path center: ',self.pathCenter)


    def centerPath(self):
        self.calculatePathCenter()
       # shifts the path to 0,0,0, point by point        
        newPath = np.zeros((len(self.path),3))

        for idx in range(len(self.path)):
            tmp_point = np.array([self.path[idx,0], self.path[idx,1], self.path[idx,2]])
            shiftedPoint = np.add(tmp_point,-self.pathCenter)
            newPath[idx,:] = shiftedPoint 

            #print(self.path[idx,:],' -> ',newPath[idx,:])
        
        self.path = newPath
        print('path centered')
        self.calculatePathCenter()


    def rotatePoint_zyx(self, point:np.array, origin:np.array, alpha, beta, gamma):
        # all rotations are extrinsic rotations in the laboratory frame of reference      
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_euler.html

        init_point = np.array([point[0], point[1], point[2]])
        origin_point = np.array([origin[0], origin[1], origin[2]])
        
        r = R.from_euler('zyx', [alpha, beta, gamma], degrees=True)
        
        rotation_matrix = r.as_matrix()
        #print(rotation_matrix)

        turned_point = np.add(rotation_matrix@np.add(init_point,-origin_point),origin_point) 

        return turned_point


    def rotatePath_zyx(self, origin:np.array, alpha, beta, gamma):
        # rotates the path by euler angles around zyx at the origin, extrinsically, point by point        
        newPath = np.zeros((len(self.path),3))

        for idx in range(len(self.path)):
            tmp_point = np.array([self.path[idx,0], self.path[idx,1], self.path[idx,2]])
            turnedPoint = self.rotatePoint_zyx(point=tmp_point,origin=origin,alpha=alpha,beta=beta,gamma=gamma)
            newPath[idx,:] = turnedPoint 

            #print(self.path[idx,:],' -> ',newPath[idx,:])
        
        self.path = newPath
        self.calculatePathCenter()


    def savePathInFile(self,filename: str):
        with open(filename,'w') as file:
            for point in self.path:
                file.write('X%dY%dZ%d\n'%(int(point[0]),int(point[1]),int(point[2])))
            print('rotated coords written to %s'%filename)



