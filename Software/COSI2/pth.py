'''rst@PTB 240408 rst030@protonmail.com'''

import numpy as np
import os

class pth():
    '''path object. created for cosi.'''

    path=[]

    x = [0,1,2]
    y = [0,1,2] 
    z = [0,1,2]

    pathFile = 0 # a file where cv is stored

    def __init__(self,filename=''):
        self.filename = 'dummy'
        if filename != '':
            self.path = []
            self.x = []
            self.y = []
            self.z = []

            with open(filename) as file:
                rawPathData = file.readlines()
                self.path = np.zeros((len(rawPathData),3))
                for idx, point in enumerate(rawPathData):
                    splitPoint = point.rstrip("\n\r").split('z')
                    z = float(splitPoint[1])
                    self.path[idx, 2] = z

                    splitPoint = splitPoint[0].split('y')
                    y = float(splitPoint[1])
                    self.path[idx, 1] = y

                    splitPoint = splitPoint[0].split('x')
                    x = float(splitPoint[1])
                    self.path[idx, 0] = x

                    headPosition = np.array([x,y,z])

                    self.x.append(x)
                    self.y.append(y)
                    self.z.append(z)
                                       
                    #print('imported pth pt:',headPosition)

            
    def saveAs(self,filename: str):
        # open file filename and write comma separated values in it
        # experiment parameters
        # data
        with open(filename, 'w') as file:
            file.write('COSI pathfile generator output.')
            file.write('Date/Time,%s\n\n\n'%self.datetime)
            for pathpt in self.path:
                file.write('x%.2f,y%.2f,z%.2f\n'%(pathpt[0],pathpt[1],pathpt[2]))
        file.close()


def generate_spherical_path():
    empty_pth =  pth()
    pth.x = []
    pth.y = []
    pth.z = []
























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



