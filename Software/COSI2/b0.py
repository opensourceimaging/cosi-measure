'''rst@PTB 240429 rst030@protonmail.com'''

import numpy as np
import os
import pth
import osi2magnet

class b0():
    '''b0 object. created for cosi data. contains path.'''

    path=None
    b0File = 0 # a file where b0 data is stored
    magnet = None
    datetime = 'timeless'

    def __init__(self,path_filename='', b0_filename='', magnet_object = ''):
        
        if path_filename!='':
            self.path = pth.pth(filename=path_filename)
            print('b0 object created on path %s'%self.path.filename)
            
        if b0_filename != '':
            self.filename = b0_filename
   
        if magnet_object!='':
            self.magnet = magnet_object

        with open(b0_filename) as file:
            raw_B0_data = file.readlines()     
            
        header_lines = raw_B0_data[0:5]    
        self.parse_header(header_lines)           
        
        # self.transfer_coordinates_of_the_path_from_cosi_to_magnet()  is called by btn on gui 



        print('read b0 data')
        print(header_lines)
        
        
        
    def transfer_coordinates_of_the_path_from_cosi_to_magnet(self):
        

        print('ROTATING THE PATH [not] NOW!')
        # center the path to the origin, as the origin of the path is the origin of the magnet
        print(self.magnet.origin)
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        #self.path.center(origin=self.magnet.origin)
        # rotate path according to the euler angles of the magnet, but backwards
        self.path.rotate_euler_backwards(gamma=self.magnet.gamma,beta=self.magnet.beta,alpha=self.magnet.alpha) 
        self.path.center(origin=self.magnet.origin)
        print('ROTATING THE MAGNET NOW!')
        # rotate the magnet
        self.magnet.rotate_euler_backwards(gamma=self.magnet.gamma,beta=self.magnet.beta,alpha=self.magnet.alpha) # for the backwards euler rotation rotate by negative values in the reversed order: was zyx, now xyz
        self.magnet.set_origin(0,0,0)        
        
        

    def parse_header(self,header_lines):
        self.datetime = header_lines[1]
        # ['COSI2 B0 scan\n', 
        # '2024-04-19 10:25:38.383373\n', 
        # 'MAGNET CENTER IN LAB: x 265.287 mm, y 166.332 mm, z 163.238 mm\n', 
        # 'MAGNET AXES WRT LAB: alpha -90.00 deg, beta -90.00 deg, gamma 0.00 deg\n',
        # 'path: ./data/240418/a00_ball_path_80mm_coarse_5s_FAST.path\n']
        
        mg_cor_str = header_lines[2].split(':')[1]
        mag_center_x = float(mg_cor_str.split(',')[0].split(' ')[2])
        mag_center_y = float(mg_cor_str.split(',')[1].split(' ')[2])
        mag_center_z= float(mg_cor_str.split(',')[2].split(' ')[2])

        mg_euler_str = header_lines[3].split(':')[1]
        mag_alpha = float(mg_euler_str.split(',')[0].split(' ')[2])
        mag_beta = float(mg_euler_str.split(',')[1].split(' ')[2])
        mag_gamma= float(mg_euler_str.split(',')[2].split(' ')[2])

        

        self.magnet = osi2magnet.osi2magnet(origin=[mag_center_x,mag_center_y,mag_center_z],euler_angles_zyx=[mag_alpha,mag_beta,mag_gamma])

            
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









    '''rudimentary'''
    # def loadPath(self, pathFileName: str):
    #     self.pathFile = pathFileName
    #     with open(pathFileName) as file:
    #         rawPathData = file.readlines()
    #         self.path = np.zeros((len(rawPathData),3))
            
    #         for idx, point in enumerate(rawPathData):
    #             splitPoint = point.rstrip("\n\r").split('Z')
    #             z = splitPoint[1]
    #             self.path[idx, 2] = z

    #             splitPoint = splitPoint[0].split('Y')
    #             y=splitPoint[1]
    #             self.path[idx, 1] = y

    #             splitPoint = splitPoint[0].split('X')
    #             x = splitPoint[1]
    #             self.path[idx, 0] = x

    #             self.headPosition = np.array([x,y,z])

    #             #print(self.headPosition)


    #         self.calculatePathCenter()


    # def calculatePathCenter(self):
    #     x_c = np.nanmean(self.path[:,0])
    #     y_c = np.nanmean(self.path[:,1])
    #     z_c = np.nanmean(self.path[:,2])
    #     self.pathCenter = np.array([x_c,y_c,z_c])
    #     print('path center: ',self.pathCenter)


    # def centerPath(self):
    #     self.calculatePathCenter()
    #    # shifts the path to 0,0,0, point by point  
             
    #     newPath = np.zeros((np.shape(self.path)))

    #     for idx in range(len(self.path)):
    #         newPath[idx,:] = self.path[idx,:] - self.pathCenter

    #         #print(self.path[idx,:],' -> ',newPath[idx,:])
        
    #     self.path = newPath
    #     print('path centered')
    #     self.calculatePathCenter()


    # def rotatePoint_zyx(self, point:np.array, origin:np.array, alpha, beta, gamma):
    #     # all rotations are extrinsic rotations in the laboratory frame of reference      
    #     # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_euler.html

    #     init_point = np.array([point[0], point[1], point[2]])
    #     origin_point = np.array([origin[0], origin[1], origin[2]])
        
    #     r = R.from_euler('zyx', [alpha, beta, gamma], degrees=True)
        
    #     rotation_matrix = r.as_matrix()
    #     #print(rotation_matrix)

    #     turned_point = np.add(rotation_matrix@np.add(init_point,-origin_point),origin_point) 

    #     return turned_point


    # def rotatePath_zyx(self, origin:np.array, alpha, beta, gamma):
    #     # rotates the path by euler angles around zyx at the origin, extrinsically, point by point        
    #     newPath = np.zeros((len(self.path),3))

    #     for idx in range(len(self.path)):
    #         tmp_point = np.array([self.path[idx,0], self.path[idx,1], self.path[idx,2]])
    #         turnedPoint = self.rotatePoint_zyx(point=tmp_point,origin=origin,alpha=alpha,beta=beta,gamma=gamma)
    #         newPath[idx,:] = turnedPoint 

    #         #print(self.path[idx,:],' -> ',newPath[idx,:])
        
    #     self.path = newPath
    #     self.calculatePathCenter()


    # def savePathInFile(self,filename: str):
    #     with open(filename,'w') as file:
    #         for point in self.path:
    #             file.write('X%dY%dZ%d\n'%(int(point[0]),int(point[1]),int(point[2])))
    #         print('rotated coords written to %s'%filename)



