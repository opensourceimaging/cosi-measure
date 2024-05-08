'''rst@PTB 240429 rst030@protonmail.com'''

import numpy as np
import pth # path class to create a path object
import osi2magnet # osi2magnet class to create an osi2magnet object 

class b0():
    '''b0 object. created for cosi data. contains path.'''

    path=None
    b0File = 0 # a file where b0 data is stored
    magnet = None
    datetime = 'timeless'
    fieldDataAlongPath = None
    
    b0Data = None # tasty, berry, what we need. 3D array. ordered. sliceable. fittable. and so on. 
    

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
        self.parse_header_of_B0_file(header_lines)  
        field_lines = raw_B0_data[5:]
        self.parse_field_of_B0_file(field_lines)   
        
        
        # self.transfer_coordinates_of_the_path_from_cosi_to_magnet()  
        
        print('read b0 data')
        print(header_lines)
        
        
        
        
    ''' path transformation to the coordinate system of the magnet '''    
    def transfer_coordinates_of_the_path_from_cosi_to_magnet(self):
        # now does everything, like an entry point. separate.
        
        # is called by btn on gui     
        print('ROTATING THE PATH NOW!')
        # rotate path according to the euler angles of the magnet, but backwards
        self.path.rotate_euler_backwards(gamma=self.magnet.gamma,beta=self.magnet.beta,alpha=self.magnet.alpha) 
        # center the path to the origin, as the origin of the path is the origin of the magnet
        self.path.center(origin=self.magnet.origin)
        print('ROTATING THE MAGNET NOW!')
        # rotate the magnet
        self.magnet.rotate_euler_backwards(gamma=self.magnet.gamma,beta=self.magnet.beta,alpha=self.magnet.alpha) # for the backwards euler rotation rotate by negative values in the reversed order: was zyx, now xyz
        self.magnet.set_origin(0,0,0)    
        
         # now that we have the path and the b0 lets compare number of points in both.
        print('len(path.r)=',len(self.path.r))
        print('len(b0Data)=',len(self.fieldDataAlongPath))

        if len(self.path.r) == len(self.fieldDataAlongPath[:,0]):
            self.reorder_field_to_cubic_grid() # make a cubic grid with xPts, yPts, zPts and define B0 on that
    
        
        
            

        
    def reorder_field_to_cubic_grid(self):
        # what we want to do here is make the coordinate grid. A cube, essentially.
        # we know that the path has a fixed distance between the points. This is crucial.
        # but the path is a snake path! it is a 1d line. 
        # we want to parse it into a 3D grid. Would be nice to have this grid stored somewhere 
        # at the stage of path generation, like a tmp file or something.
        # but we did not generate it, although we could. hm.
        # so maybe just going back to the generating script and making the path with the same parameters would 
        # do the job for me and Id go write my batteries?
        # nay lets be fair and *measure* the points on the path.
        
        # limits of the path will give us the siye of the cube for that grid
        x_max = max(self.path.r[:,0])
        x_min = min(self.path.r[:,0])
        y_max = max(self.path.r[:,1])
        y_min = min(self.path.r[:,1])
        z_max = max(self.path.r[:,2])
        z_min = min(self.path.r[:,2])
        
        print(x_min,' < x < ',x_max)
        print(y_min,' < y < ',y_max)
        print(z_min,' < z < ',z_max)
        
        # now lets determine how many points we need per each axis
        # lets emasure the step on x
        step_size_x_list = []
        step_size_y_list = []
        step_size_z_list = []
        
        for idx in range(1,len(self.path.r)):
            step = self.path.r[idx,:] - self.path.r[idx-1,:]
            if step[0] > 1e-3:
                step_size_x_list.append(step[0])
            if step[1] > 1e-3:
                step_size_y_list.append(step[1])
            if step[2] > 1e-3:
                step_size_z_list.append(step[2])  
                  
        step_size_x = min(step_size_x_list)
        step_size_y = min(step_size_y_list)
        step_size_z = min(step_size_z_list)
        
        print('path step size: ',step_size_x,step_size_y,step_size_z)

        #num_steps_x = round((x_max-x_min)/step_size_x)+1
        #num_steps_y = round((x_max-x_min)/step_size_y)+1
        #num_steps_z = round((x_max-x_min)/step_size_z)+1

        # so there are unique_x x values between x_min and x_max
        # lets make a linspace
        self.xPts = np.arange(start=x_min,stop=x_max,step=step_size_x) #linspace(start=x_min,stop=x_max,num=num_steps_x)
        print("xPts: ", self.xPts)
        self.yPts = np.arange(start=y_min,stop=y_max,step=step_size_y) #linspace(start=y_min,stop=y_max,num=num_steps_y)
        print("yPts: ", self.yPts)
        self.zPts = np.arange(start=z_min,stop=z_max,step=step_size_z) #linspace(start=z_min,stop=z_max,num=num_steps_z)
        print("zPts: ", self.zPts)
        
                
        # now we do a trick
        # we will go through the snake. 
        # for each (3-valued) point see snake we take the its 0th value and scan xPts searching which is the closest.
        # that is, less than epsilon
        
        epsx = (self.xPts[1]-self.xPts[0])/3
        epsy = (self.yPts[1]-self.yPts[0])/3
        epsz = (self.zPts[1]-self.zPts[0])/3

        # then we get the index of xPts
        # and same for z and y
        # the b0Data will be a 3D array
        # indexing is the same for path and b0_values_1D
        
        b0Data = np.zeros((len(self.xPts),len(self.yPts),len(self.zPts),3))
        
        
        for idx in range(np.size(self.path.r,0)):
            x_value_along_path = self.path.r[idx,0]
            y_value_along_path = self.path.r[idx,1]
            z_value_along_path = self.path.r[idx,2]
            
            xArg = min(np.where(abs(self.xPts - x_value_along_path) < epsx))
            yArg = min(np.where(abs(self.yPts - y_value_along_path) < epsy))
            zArg = min(np.where(abs(self.zPts - z_value_along_path) < epsz))
        
            #print("pth r=[",self.path.r[idx,:],"] closest grid [",xPts[xArg],yPts[yArg],zPts[zArg],"]")
            b0Data[xArg,yArg,zArg,:] = abs(self.fieldDataAlongPath[idx,:])
            
        b0Data[b0Data==0]=np.NaN    
        # getting mean field
        meanField = np.nanmean(b0Data[:,:,:,1])
        print('Mean field <B0> = ',meanField, 'mT')
        # homogeniety
        maxField = np.nanmax(b0Data[:,:,:,1])
        minField = np.nanmin(b0Data[:,:,:,1])
        homogeneity = 1e6*(maxField-minField)/meanField
        print('homogeniety: %i ppm'%homogeneity)


        self.b0Data = b0Data

                
    def parse_field_of_B0_file(self,field_lines):
        #-2.842000 48.057000 -2.319000 48.197000
        self.fieldDataAlongPath = np.zeros((len(field_lines),3))
        for idx, line in enumerate(field_lines):
            self.fieldDataAlongPath[idx,:] = [float(line.split(' ')[0]),float(line.split(' ')[1]),float(line.split(' ')[2])]
        
        if self.fieldDataAlongPath[0,1] == 0:
            self.fieldDataAlongPath[0,0] = np.nanmean(self.fieldDataAlongPath[1:,0])
            self.fieldDataAlongPath[0,1] = np.nanmean(self.fieldDataAlongPath[1:,1])
            self.fieldDataAlongPath[0,2] = np.nanmean(self.fieldDataAlongPath[1:,2])
            
    def parse_header_of_B0_file(self,header_lines):
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


    

    def saveAsCsv_for_comsol(self, filename: str):
        # for comsol
        with open(filename, 'w') as file:
            file.write('X[m],Y[m],Z[m],Bx[T],By[T|,Bz[T]\n')
            for i in range(len(self.path.r[:,0])):
                ri = self.path.r[i,:]            
                # orthodox> file.write('%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n'%(ri[0]/1e3,ri[1]/1e3,ri[2]/1e3,self.fieldDataAlongPath[i,0]/1e3,self.fieldDataAlongPath[i,1]/1e3,self.fieldDataAlongPath[i,2]/1e3))
                file.write('%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n'%(ri[0]/1e3,ri[1]/1e3,ri[2]/1e3,0,0,max(abs(self.fieldDataAlongPath[i,0]/1e3),abs(self.fieldDataAlongPath[i,1]/1e3),abs(self.fieldDataAlongPath[i,2]/1e3))))
        



            
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



