'''240405 rst PTB rst030@protonmail.com'''

from PyQt5 import QtWidgets
import numpy as np

import serial
import time
from datetime import datetime
import os
import subprocess

import pth # path object

import gaussmeter # for mapping the field

# endpoints - adjust them
minx = 0
miny = 0
minz = 0

maxx = 487
maxy = 460
maxz = 300 

manstep = 5 # mm manual step

class cosimeasure(object):
    
    head_position = [0,0,0];
    path = [];
    pathfile = None
    magnetometer = None
    working_directory = r'./dummies/pathfiles/'
    bvalues = [] # list of strings


    def __init__(self,isfake:bool,gaussmeter:gaussmeter.gaussmeter,b0_filename=None): # if isfake then dont do serial and sudo
        print('initiating an instance of the cosimeasure object')
        self.path = pth.pth(filename='') # default path = dummy path
        self.head_position = [0,0,0]
        self.isfake = isfake   
        self.ser = None # serial connection is a field of cosimeasure 

        self.gaussmeter=gaussmeter
        self.b0_filename = b0_filename
        print(b0_filename)

        print(self)
        print('COSI configured with a gaussmeter')       
        
        if isfake:
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
        self.head_position = self.get_current_position()


    def get_current_position(self): # return position of the head
        if self.isfake:
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


    def init_path(self):
        if len(self.path.path):
            pathpt = self.path.path[0]
            print('moving head to %s'%str(pathpt))
            
            x = pathpt[0]
            y = pathpt[1]
            z = pathpt[2]
            self.moveto(x,y,z)

        else:
            print('load path first!')

    def run_path_no_measure(self):
        print('running through pass witout measurement')
        if len(self.path.path):
            for pt in self.path.path:
                print(pt)
                self.moveto(pt[0],pt[1],pt[2])
                print('pt reached, magnetometer?')
        else:
            print('load path first!')

    ''' MEASUREMENTS '''

    def run_measurement(self):
        print('following the path, measuring the field!')
        #self.run_path_no_measure()
        self.run_path_measure_field()

    def run_path_measure_field(self):
        print('running along pass')
        if len(self.path.path):
            for pt in self.path.path:
                print(pt)
                self.moveto(pt[0],pt[1],pt[2])
                pos = self.get_current_position()
                bx,by,bz,babs = self.gaussmeter.read_gaussmeter()
                print('pt',pos,'mm reached, B0=[%.1f,%.1f,%.1f] G'%(bx,by,bz))
                self.bvalues.append('%f %f %f %f\n'%(bx,by,bz,babs))
            print('path scanning done. saving file')
             #write shim orientations to file
        
            if self.b0_filename:
                with open(self.b0_filename, 'w') as file:
                    file.writelines(self.bvalues)

        else:
            print('load path first!')



    def abort(self):
        print('STOP MOVING AND SWITCH MOTORS OFF!')

    '''PATH FILE LOADING'''
    def load_path(self):
        print('cosi loads path from file.')
        if not self.pathfile_path:
            print('no path file for cosimeasure')
            return
        self.path = pth.pth(filename=self.pathfile_path)
        print('path successfully imported')
        self.head_position = self.get_current_position()

        self.calculatePathCenter()

    def calculatePathCenter(self):
        x_c = np.nanmean(self.path.path[:,0])
        y_c = np.nanmean(self.path.path[:,1])
        z_c = np.nanmean(self.path.path[:,2])
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

                