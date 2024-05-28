'''240409 rstPTB rst030@protonmail.com'''

import serial
from time import sleep

class gaussmeter(object):
    
    port = '/dev/ttyUSB0'
    working_directory = r'./dummies/scans/'

    def __init__(self,isfake:bool): # if isfake then dont do serial and sudo
        print('initiating an instance of the gaussmeter object')
        self.scan = None #todo: default scan = dummy scan
        self.isfake = isfake   
        self.ser = None # serial connection is a field of gaussmeter 
        
        print(self)
            
        if isfake:
            return

        self.ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=9600,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS
            )
        
        print('serial connection for gaussmeter opened')


    def fast(self,state):
        if self.isfake:
            return 'no gm'
        if state:
            self.ser.write('FAST 1'.encode())
        else:
            self.ser.write('FAST 0'.encode())
        value = ''
        sleep(0.1)
        while self.ser.inWaiting() > 0:
            prey = self.ser.read(1)
            value += prey.decode()
        return value


    def read_gaussmeter(self):
        if self.isfake:
            return 0,0,0,0
        self.ser.write('ALLF?'.encode())
        value = ''
        sleep(0.1)
        while self.ser.inWaiting() > 0:
            prey = self.ser.read(1)
            value += prey.decode()
        b0x,b0y,b0z,b0abs = self.parse_B0(value)
        return b0x,b0y,b0z,b0abs

    def parse_B0(self,raw_reading):
        b0x = 0
        b0y = 0
        b0z = 0
        b0abs = 0
        
        if raw_reading !='':
            strvals=raw_reading.split(',')
            try:
                b0x = float(strvals[0])
                b0y = float(strvals[1])
                b0z = float(strvals[2])
                b0abs = float(strvals[3])
            except:
                pass
        return b0x,b0y,b0z,b0abs
        

                