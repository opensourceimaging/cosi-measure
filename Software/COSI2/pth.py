'''rst@PTB 240408 rst030@protonmail.com'''
import numpy as np

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
                                       
                    print('imported pth pt:',headPosition)

            
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


