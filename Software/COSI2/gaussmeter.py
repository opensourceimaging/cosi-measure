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


    def read_gaussmeter(self):
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
            b0x = float(strvals[0])
            #todo: b0y test with healthy sensor
            b0z = float(strvals[2])
            
        return b0x,b0y,b0z,b0abs
        

                