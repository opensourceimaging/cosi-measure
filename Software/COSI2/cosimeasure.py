'''240405 rst PTB rst030@protonmail.com'''

from PyQt5 import QtWidgets
import numpy as np

import serial
import time
from datetime import datetime
import os

import pth # path object

# endpoints - adjust them
minx = 0
miny = 0
minz = 0

maxx = 487
maxy = 460
maxz = 300 

class cosimeasure(object):
    
    head_position = [0,0,0];
    path = [];
    pathfile = None
    magnetometer = None
    working_directory = r'./dummies/pathfiles/'

    def __init__(self,isfake:bool): # if isfake then dont do serial and sudo
        print('initiating an instance of the cosimeasure object')
        self.path = pth.pth(filename='') # default path = dummy path
        self.head_position = [0,0,0]
        self.isfake = isfake   
        self.ser = None # serial connection is a field of cosimeasure 
        
        print(self)
            
        if isfake:
            return
        
        os.system('sudo service klipper stop')

        time.sleep(2)

        os.system('sudo service klipper start')

        time.sleep(1)

        self.ser = serial.Serial('/tmp/printer', 250000)
        print('serial connection for cosimeasure opened')
        time.sleep(1)

    def command(self,command:str):
        #start_time = datetime.now()
        #global ser
        command = command + "\r\n"
        if self.isfake:
            print('no serial connection to cosi, writing %s',command)
            return
        print('sending ', command)
        self.ser.write(str.encode(command)) 

        while True:
            line = self.ser.readline()
            print(line)

            if line == b'ok\n':
                break

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
        self.head_position = [x,y,z]


    def get_current_position(self): # return position of the head
        self.command("M114")
        while True:
            line = self.ser.readline()
            print(line)
            if line == b'ok\n':
                break
        return line


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
        print('TEMP: Only following the path, no magnetometer!')
        self.run_path_no_measure()

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
        self.head_position = self.path.path[0]

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

                