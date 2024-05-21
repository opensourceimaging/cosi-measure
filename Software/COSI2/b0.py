'''rst@PTB 240429 rst030@protonmail.com'''

from datetime import datetime
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
    filename = 'Dummy B0 map'
    
    b0Data = None # tasty, berry, what we need. 3D array. ordered. sliceable. fittable.
    

    def __init__(self,path_filename='', path:pth.pth = None, b0_filename='', magnet_object = ''):
        
        if path_filename!='':
            self.path = pth.pth(filename=path_filename)
            print('b0 object created with path %s'%self.path.filename)
            
        if path is not None:
            self.path = path
               
        if magnet_object!='':
            self.magnet = magnet_object

        # if filename was given on init, read the b0 from that file.
        if b0_filename != '':
            self.filename = b0_filename
            print("WARNING. do csv reading of path and b0 all together, instead of txt reading.")

            with open(b0_filename) as file:
                raw_B0_data = file.readlines()     
                
            header_lines = raw_B0_data[0:5]    
            self.parse_header_of_B0_file(header_lines)  
            field_lines = raw_B0_data[5:]
            self.parse_field_of_B0_file(field_lines)   
            # self.transfer_coordinates_of_the_path_from_cosi_to_magnet()  
            print('read b0 data')
            print(header_lines)
        
        else:
            # if no filename was given
            # create an instance of a b0 object, populate some fields. be ready to fill in b0 values
            if self.path is None:
                print('No path object given on construction of b0 object.\n b0 instance initialized without path.')
                return
            self.fieldDataAlongPath = np.zeros((len(self.path.r),4)) # bx,by,bz,babs
        
        
        
    ''' path transformation to the coordinate system of the magnet '''    
    def transfer_coordinates_of_the_path_from_cosi_to_magnet(self):
        # now does everything, like an entry point. separate.
        
        # is called by btn on gui     
        print('ROTATING THE PATH NOW!')
        # rotate path according to the euler angles of the magnet, but backwards
        self.path.rotate_euler_backwards(gamma=self.magnet.gamma,beta=self.magnet.beta,alpha=self.magnet.alpha) 
        # center the path to the origin, as the origin of the path is the origin of the magnet
        temp_origin_offset = [0,0,0]
        self.path.center(origin=self.magnet.origin+temp_origin_offset)
        print('ROTATING THE MAGNET NOW!')
        # rotate the magnet
        self.magnet.rotate_euler_backwards(gamma=self.magnet.gamma,beta=self.magnet.beta,alpha=self.magnet.alpha) # for the backwards euler rotation rotate by negative values in the reversed order: was zyx, now xyz
        self.magnet.set_origin(temp_origin_offset[0],temp_origin_offset[1],temp_origin_offset[2])    
        
         # now that we have the path and the b0 lets compare number of points in both.
        print('len(path.r)=',len(self.path.r))
        print('len(b0Data)=',len(self.fieldDataAlongPath))

        if len(self.path.r) == len(self.fieldDataAlongPath[:,0]):
            self.reorder_field_to_cubic_grid() # make a cubic grid with xPts, yPts, zPts and define B0 on that
    
        
    # ----------------- artificial data generation ----------------- 
    def make_artificial_field_along_path(self,coordinates_of_singularity,radius_of_singularity:float):
        path = self.path
        x0 = coordinates_of_singularity[0]
        y0 = coordinates_of_singularity[1]
        z0 = coordinates_of_singularity[2]
        
        self.fieldDataAlongPath = np.zeros((len(self.path.r),4)) # bx,by,bz,babs
        for idx in range(len(path.r)):
            self.fieldDataAlongPath[idx,:] = [0,1,0,0]
            if np.sqrt((path.r[idx,0]-x0)**2+(path.r[idx,1]-y0)**2+(path.r[idx,2]-z0)**2)<radius_of_singularity:
                self.fieldDataAlongPath[idx,:] = [414,414,414,414]
                
        self.reorder_field_to_cubic_grid()

        
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
        
        b0Data = np.zeros((len(self.xPts),len(self.yPts),len(self.zPts),4))
        
        
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
        try:
            homogeneity = float(1e6*(maxField-minField)/meanField)
        except:
            homogeneity = 0
        print('homogeniety: %.0f ppm'%homogeneity)


        self.b0Data = b0Data
        print('B0.B0DATA GENERATED ON A RECT GRID')

    # ------------------- data parsers -------------------
                
    def parse_field_of_B0_file(self,field_lines):
        #-2.842000 48.057000 -2.319000 48.197000
        self.fieldDataAlongPath = np.zeros((len(field_lines),4))
        for idx, line in enumerate(field_lines):
            b0x = float(line.split(' ')[0])
            b0y = float(line.split(' ')[1])
            b0z = float(line.split(' ')[2])
            b0abs = float(line.split(' ')[3])
            self.fieldDataAlongPath[idx,:] = [b0x,b0y,b0z,b0abs]
        
        if self.fieldDataAlongPath[0,1] == 0:
            self.fieldDataAlongPath[0,0] = np.nanmean(self.fieldDataAlongPath[1:,0])
            self.fieldDataAlongPath[0,1] = np.nanmean(self.fieldDataAlongPath[1:,1])
            self.fieldDataAlongPath[0,2] = np.nanmean(self.fieldDataAlongPath[1:,2])
            self.fieldDataAlongPath[0,3] = np.nanmean(self.fieldDataAlongPath[1:,3])
                        
    def parse_field_of_CSV_file(self,field_lines):
        # 315.17	152.35	113.75	0	100	0	0
        self.fieldDataAlongPath = np.zeros((len(field_lines),4))
        for idx, line in enumerate(field_lines):
            b0x = float(line.split(',')[3])
            b0y = float(line.split(',')[4])
            b0z = float(line.split(',')[5])
            b0abs = float(line.split(',')[6])
            
            self.fieldDataAlongPath[idx,:] = [b0x,b0y,b0z,b0abs]

            
    def parse_header_of_CSV_file(self,header_lines):
        # COSI2 B0 scan						
        # time 2024-05-17 13:21:45.456312						
        # MAGNET CENTER IN LAB: x 265.170 mm	 y 182.350 mm	 z 163.750 mm				
        # MAGNET AXES WRT LAB: alpha 0.00 deg	 beta 0.00 deg	 gamma 0.00 deg				
        # path: C:/cosi-measure/Software/COSI2/dummies/b0_maps/testcsv.path						
        # X[mm]	Y[mm]	Z[mm]	B0_x[mT]	B0_y[mT|	B0_z[mT]	B0_abs[mT]
        self.datetime = header_lines[1].split(' ')[2:3]
        mg_cor_str = header_lines[2].split(':')[1]
        mag_center_x = float(mg_cor_str.split(',')[0].split(' ')[2])
        mag_center_y = float(mg_cor_str.split(',')[1].split(' ')[2])
        mag_center_z= float(mg_cor_str.split(',')[2].split(' ')[2])
        
        mg_euler_str = header_lines[3].split(':')[1]
        mag_alpha = float(mg_euler_str.split(',')[0].split(' ')[2])
        mag_beta = float(mg_euler_str.split(',')[1].split(' ')[2])
        mag_gamma= float(mg_euler_str.split(',')[2].split(' ')[2])

        self.magnet = osi2magnet.osi2magnet(origin=[mag_center_x,mag_center_y,mag_center_z],euler_angles_zyx=[mag_alpha,mag_beta,mag_gamma])

        path_filename_str = str(header_lines[4].split('path:')[1])
        print('warning. path file %s not used. path data taken from csv!'%path_filename_str)
    
    
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
        magnet = self.magnet
        with open(filename, 'w') as file:
            
            file.write('# COSI2 B0 scan\n')                    
            # Convert date and time to string
            dateTimeStr = str(datetime.now())
            file.write('# time '+dateTimeStr+'\n')
            file.write('# MAGNET CENTER IN LAB: x %.3f mm, y %.3f mm, z %.3f mm\n'%(magnet.origin[0],magnet.origin[1],magnet.origin[2]))
            file.write('# MAGNET AXES WRT LAB: alpha %.2f deg, beta %.2f deg, gamma %.2f deg\n'%(magnet.alpha,magnet.beta,magnet.gamma))   
            file.write('# path: '+self.path.filename+'\n')
            file.write('# X[mm],Y[mm],Z[mm],B0_x[mT],B0_y[mT|,B0_z[mT],B0_abs[mT]\n')   

            for i in range(len(self.path.r[:,0])):
                ri = self.path.r[i,:]            
                bi = self.fieldDataAlongPath[i,:]
                file.write('%.3f,%.3f,%.3f,%.4f,%.4f,%.4f,%.4f\n'%(ri[0],ri[1],ri[2],bi[0],bi[1],bi[2],bi[3]))
        
    def import_from_csv(self,b0_filename: str):
        print('importing b0 object from csv file%s'%b0_filename)

        # make an empty instance of b0 and get the b0 values from the csv file.
        self.__init__()        
        with open(b0_filename) as file:
                raw_B0_data = file.readlines()     
                headerlength = 0
                for line in raw_B0_data:
                    if line[0] == '#':
                        headerlength += 1
                        
                header_lines = raw_B0_data[0:headerlength]    
                field_lines = raw_B0_data[headerlength:]
                self.parse_header_of_CSV_file(header_lines)
                self.parse_field_of_CSV_file(field_lines) 
         
        # import the path from the path file
        self.path = pth.pth(csv_filename = b0_filename)

                
        
            
    # def saveAs(self,filename: str):
    #     # open file filename and write comma separated values in it
    #     # experiment parameters
    #     # data
    #     with open(filename, 'w') as file:
    #         file.write('COSI pathfile generator output.')
    #         file.write('Date/Time,%s\n\n\n'%self.datetime)
    #         for pathpt in self.path:
    #             file.write('x%.2f,y%.2f,z%.2f\n'%(pathpt[0],pathpt[1],pathpt[2]))
    #     file.close()
