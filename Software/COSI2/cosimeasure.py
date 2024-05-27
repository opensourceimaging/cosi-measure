'''240405 rst PTB rst030@protonmail.com'''

from PyQt5 import QtWidgets
import numpy as np

import serial
import time
from datetime import datetime
import os
import subprocess
from multiprocessing import Queue

import pth # path object

import gaussmeter # for mapping the field
import osi2magnet

import b0 # b0 object - here we write the path and the values along the path

# endpoints - adjust them
minx = 0
miny = 0
minz = 0

maxx = 487
maxy = 460
maxz = 300 

manstep = 5 # mm manual step

class cosimeasure(object):
    
    head_position = [0,0,0]
    path = []
    pathfile = None
    magnetometer = None
    working_directory = r'./dummies/pathfiles/'
    bvalues = [] # list of strings
    measurement_time_delay = 3 # s
    magnet = osi2magnet.osi2magnet


    def __init__(self,isfake:bool,gaussmeter:gaussmeter.gaussmeter,b0_filename=None,magnet=None,queue=None): # if isfake then dont do serial and sudo
        print('initiating an instance of the cosimeasure object')
        # multithreading things
        if queue is not None:
            self.q = queue
        # ---------------------
        self.path = pth.pth(filename='') # default path = dummy path
        self.b0 = b0.b0() # the empty b0 object - to be populated as the measurement is performed
        self.head_position = [0,0,0]
        self.isfake = isfake   
        self.ser = None # serial connection is a field of cosimeasure 

        self.gaussmeter=gaussmeter
        self.b0_filename = b0_filename
        print(b0_filename)

        print(self)
        print('COSI configured with a gaussmeter')       
        
        self.magnet = magnet

        self.measurement_time_delay = 3
        if isfake:
            self.measurement_time_delay = 0.25 # for quick testing
            return

        os.system('sudo service klipper stop')
        time.sleep(2)
        process = subprocess.Popen(['./backend/flash-mcu-start-klipper.sh'])
        process.wait()

        os.system('sudo service klipper start')
        time.sleep(2)


        self.ser = serial.Serial('/tmp/printer', 250000)
        print('serial connection for cosimeasure opened')
        time.sleep(1)

    def command(self,command:str):
        #start_time = datetime.now()
        #global ser
        command = command + "\r\n"
        if self.isfake:
            print('no serial connection to COSI, writing %s',command)
            return
        print('sending ', command)
        self.ser.write(str.encode(command)) 
        line = ''

        while True:
            lastline = line
            line = self.ser.readline()
            print(line)
            if line == b'ok\n':
                return lastline

    '''====== MOVING HEAD ======'''

    '''HOMING ROUTINES'''
    def home_x_plus(self):
        self.home_axis(axis='x',dir=1)
    def home_x_minus(self):
        self.home_axis(axis='x',dir=-1)
    def home_y_plus(self):
        self.home_axis(axis='y',dir=1)        
    def home_y_minus(self):
        self.home_axis(axis='y',dir=-1)        
    def home_z_plus(self):
        self.home_axis(axis='z',dir=1)        
    def home_z_minus(self):
        self.home_axis(axis='z',dir=-1)
    
    '''stepwise head movements'''
    def x_step_up(self):
        print('move x+ one /step/')
        x,y,z = self.get_current_position()
        x=x+manstep
        self.moveto(x,y,z)

    def x_step_down(self):
        print('move x- one /step/')
        x,y,z = self.get_current_position()
        x=x-manstep
        self.moveto(x,y,z)

    def y_step_up(self):
        print('move y+ one /step/')
        x,y,z = self.get_current_position()
        y=y+manstep
        self.moveto(x,y,z)

    def y_step_down(self):
        print('move y- one /step/')
        x,y,z = self.get_current_position()
        y=y-manstep
        self.moveto(x,y,z)

    def z_step_up(self):
        print('move z+ one /step/')
        x,y,z = self.get_current_position()
        z=z+manstep
        self.moveto(x,y,z)

    def z_step_down(self):
        print('move z- one /step/')
        x,y,z = self.get_current_position()
        z=z-manstep
        self.moveto(x,y,z)


    def quickhome_x(self):
        self.command("G0 X%.2f"%minx) # quick home x
    def quickhome_y(self):
        self.command("G0 Y%.2f"%miny) # quick home y
    def quickhome_z(self):
        self.command("G0 Z%.2f"%minz) # quick home z


    def home_axis(self,axis:str,dir:int):
        '''individually home axis in direction dir'''
        direction = '+' if dir > 0 else '-'
        if axis == 'x':
            print('homing X, direction:%s'%direction)
            if dir < 0:
                self.command("G28 X%.2f"%minx) # homing zero x

            else:
                self.command("G0 X%.2f"%maxx) # homing max x

        if axis == 'y':
            print('homing Y, direction:%s'%direction)
            if dir < 0:
                self.command("G28 Y%.2f"%miny) # homing zero y
            else:
                self.command("G0 Y%.2f"%maxy) # homing max y            

                
        if axis == 'z':
            print('homing Z, direction:%s'%direction)
            if dir < 0:
                self.command("G28 Z%.2f"%minz) # homing zero z
            else:
                self.command("G0 Z%.2f"%maxz) # homing max z               

    def moveto(self,x:float,y:float,z:float):
        print('moving head to %.2f, %.2f, %.2f'%(x,y,z))
        self.command("G0 X%.2f Y%.2f Z%.2f"%(x,y,z))
        self.head_position = self.get_current_position(fakePosition=[x,y,z])


    def get_current_position(self,fakePosition=None): # return position of the head
        if self.isfake:
            if fakePosition is not None:
                xpos = fakePosition[0]
                ypos = fakePosition[1]
                zpos = fakePosition[2]
                self.head_position=[xpos,ypos,zpos] # update the head_position field of the object every time head_position is queried
                print('fake COSI, returning fake head position')
                return xpos,ypos,zpos

            else:
                return 0,0,0
            
        vals = self.command("M114").decode().split(' ') # b'X:386.620 Y:286.000 Z:558.280 E:0.000\n'
        xpos = float(vals[0].split(':')[1])
        ypos = float(vals[1].split(':')[1])
        zpos = float(vals[2].split(':')[1])
        
        print('x: ',xpos, 'mm')
        print('y: ',ypos, 'mm')
        print('z: ',zpos, 'mm')

        self.head_position=[xpos,ypos,zpos]

        return xpos,ypos,zpos

    def enable_motors(self):
        self.command("hard_enable_drives")

    def disable_motors(self):
        self.command("hard_disable_drives")


    def init_path(self):
        if len(self.path.r):
            pathpt = self.path.r[0]
            print('moving head to %s'%str(pathpt))
            
            x = pathpt[0]
            y = pathpt[1]
            z = pathpt[2]
            self.moveto(x,y,z)
            self.get_current_position(fakePosition=self.path.r[0])
            
            # replot the head, always replot the head

        else:
            print('load path first!')

    def run_path_no_measure(self):
        print('running through pass witout measurement')
        if len(self.path.r):
            for pt in self.path.r:
                print(pt)
                self.moveto(pt[0],pt[1],pt[2])
                print('pt reached, magnetometer?')
        else:
            print('load path first!')

    ''' MEASUREMENTS '''

    def run_measurement(self):
        print('following the path, measuring the field.')
        #self.run_path_no_measure()
        self.run_path_measure_field(self.magnet)

    def measure_gradients(self,magnet:osi2magnet.osi2magnet):
        print('measuring b0 along x, center of bore')
        print('measuring b0 along y, center of bore')
        print('measuring b0 along z, center of bore')


    def run_path_measure_field(self,magnet:osi2magnet.osi2magnet):
        # todo: write to a b0 object, 
        # write both path points and b0 values along the path. 
        # after each point write the b0 object to self.q 
        # write simultaneously to file and to self.b0 - failsafe
        # todo: save in csv file
        self.path = self.b0.path
        
        print('cosimeasure uses path of the passed b0 object')
        self.gaussmeter.fast(state=True)
        print('running along path, no display on GM')
        if self.b0_filename: # if filename was given
            with open(self.b0_filename, 'w') as file: # open that file
                if len(self.path.r): # if path was given
                    file.write('# COSI2 B0 scan\n')                    
                    # Convert date and time to string
                    dateTimeStr = str(datetime.now())
                    file.write('# time '+dateTimeStr+'\n')
                    file.write('# MAGNET CENTER IN LAB: x %.3f mm, y %.3f mm, z %.3f mm\n'%(magnet.origin[0],magnet.origin[1],magnet.origin[2]))
                    file.write('# MAGNET AXES WRT LAB: alpha %.2f deg, beta %.2f deg, gamma %.2f deg\n'%(magnet.alpha,magnet.beta,magnet.gamma))   
                    file.write('# path: '+self.path.filename+'\n')
                    file.write('# X[mm],Y[mm],Z[mm],B0_x[mT],B0_y[mT],B0_z[mT],B0_abs[mT]\n')   
                    
                    self.b0.datetime = dateTimeStr
                    self.b0.magnet = magnet
                                     
                    self.command('G90') ### SEND G90 before any path movement to make sure we are in absolute mode
                    time.sleep(1)
                    self.moveto(self.path.r[0,0],self.path.r[0,1],self.path.r[0,2]) # move the head physically to the position
                    pt_prev = self.path.r[0]
                    dummy_data_likely_zero = self.gaussmeter.read_gaussmeter(fakeField=[0,100,0,0]) # after waiting get the averaged field vals
                    
                    time.sleep(5)
                    ptidx = 0 # index of the point along the path
                    for pt in self.path.r: # follow the path
                        
                        distance_to_prev_point = np.sqrt(np.dot(pt-pt_prev,pt-pt_prev))  
                                           
                        self.moveto(pt[0],pt[1],pt[2]) # move the head physically to the position
                        if distance_to_prev_point > 100: 
                            time.sleep(5)
                            
                        pos = self.get_current_position(fakePosition=pt) # update head position of the cosimeasure object, used for live plotting
                        print(pt) # if gui lags, the terminal still shows points
                        time.sleep(self.measurement_time_delay) # adjust according to the #averages of the gaussmeter
                        bx,by,bz,babs = self.gaussmeter.read_gaussmeter(fakeField=[0,100,0,0]) # after waiting get the averaged field vals
                        print('pt %d of %d'%(ptidx,len(self.path.r)),pos,'mm reached, B0=[%.1f,%.4f,%.1f] mT'%(bx,by,bz))
                        self.b0.path.current_index  = ptidx
                        
                        # first write to file: failsafe
                        bval_str = '%f %f %f %f\n'%(bx,by,bz,babs)
                        self.bvalues.append(bval_str) # save bvalues to ram
                        
                        file.write('%.3f,%.3f,%.3f,%.4f,%.4f,%.4f,%.4f\n'%(pt[0],pt[1],pt[2],bx,by,bz,babs))

                        
                        # then write to object
                        self.b0.fieldDataAlongPath[ptidx,:] = [bx,by,bz,babs] # populate the b0 values of the b0 object at current index 
                    
                        self.q.put(self.b0) # spit b0 object to the queue every time a new point is measured
                        
                        pt_prev = pt
                        ptidx +=1    
                        

                        
                        
                    print('path scanning done. saving file')
                    #write shim orientations to file

                else:
                    print('give path! No scan without path!')
        else:
            print('give B0 filename! No scan without filename!')
        self.gaussmeter.fast(state=False)


    def abort(self):
        print('STOP MOVING AND SWITCH MOTORS OFF!')

    '''PATH FILE LOADING'''
    def load_path(self,path_filename=None):
        print('cosi loads path from file.')
        if path_filename is None:
            print('no path file for cosimeasure given. using self.path_filename for import')
            path_filename = self.pathfile_path
            
        self.path = pth.pth(filename=path_filename)
        # assign the path to the b0 object
        self.b0.path =self.path
        self.pathfile_path = path_filename
        print('path successfully imported')
        self.head_position = self.get_current_position(fakePosition=self.path.r[0])

        self.calculatePathCenter()
        

    def calculatePathCenter(self):
        x_c = np.nanmean(self.path.r[:,0])
        y_c = np.nanmean(self.path.r[:,1])
        z_c = np.nanmean(self.path.r[:,2])
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

                