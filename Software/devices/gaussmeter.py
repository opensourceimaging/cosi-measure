from time import sleep

try:
    import serial 
    has_serial = True
except: 
    print('no serial on system. Not connecting to machine')
    has_serial = False

class gaussmeter():
    '''
    class to control the Lakeshore Gaußmeter with 3-axis hallprobe via Serial over USB

    # Methods:

    - __init__()

    - set_mode()

    - read()

    # Internal Methods

    - parseB0()
    '''
    def __init__(self,serial_port='/dev/ttyUSB0'):
        '''
        initializes the serial communication to the lakeshore gaussmeter.

        # Args

        serial_port: string. system dependend device name of serial port. Default: '/dev/ttyUSB0'
        
        '''
        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return
        
        self.ser = serial.Serial(
        port=serial_port,
        baudrate=9600,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.SEVENBITS
        )

        self.has_read = False
        
        print('serial connection for gaussmeter opened')

        print('Try first measurement') # this is needed because self.read() will fail after a restart of the gaussmeter for the first time
        while not self.has_read:
            try:
                b_values = self.read()
                print(b_values)
                self.has_read = True
            except:
                sleep(0.6)
                pass


    def set_mode(self, mode:str='fast'):
        '''
        sets the mode to either 'fast' or 'normal'

        # Args

        mode: string. 'fast' or 'normal'

        returns a string from lakeshore
        
        '''
        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return
        
        self.has_read = False
        if mode=='fast':
            self.ser.write('FAST 1'.encode())
            print('Setting gaussmeter into fast mode. Display off, temperatur compensation off.')
        elif mode=='normal':
            self.ser.write('FAST 0'.encode())
            print('Setting gaussmeter into normal mode. Display on, temperatur compensation on')
        else:
            raise ValueError('mode can either be \'fast\' or \'normal\', but \'' + str(mode) + '\' was given')
        value = ''
        sleep(0.1)
        while self.ser.inWaiting() > 0:
            prey = self.ser.read(1)
            value += prey.decode()

        print('try first readout from gaussmeter after changing mode')
        while not self.has_read:
            try:
                b_values = self.read()
                print(b_values)
                self.has_read = True
            except:
                sleep(0.6)
                pass

        return value


    def read(self):
        '''
        reads asynchronous the value of the gaussmeter.

        at the time this method is called, a new readout of gaussmeter is initiated and the result of the last measurement is returned

        # Returns
        b0x,b0y,b0z,b0abs. float. Values in [mT]

        for now: 3 averages, 5% setting of window for MAF
        0.5 seconds per value
        '''
        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return 0,0,0,0
        
        self.ser.write('ALLF?'.encode())
        value = ''
        sleep(0.1)
        while self.ser.inWaiting() > 0:
            prey = self.ser.read(1)
            value += prey.decode()
        b0x,b0y,b0z,b0abs = self.parse_B0(value)
        sleep(0.55)
        return b0x,b0y,b0z,b0abs


    def parse_B0(self,raw_reading):
        if raw_reading !='':
            strvals=raw_reading.split(',')
            try:
                b0x = float(strvals[0])
                b0y = float(strvals[1])
                b0z = float(strvals[2])
                b0abs = float(strvals[3])
            except:
                print('failed to parse b-values from gaussmeter!')
                b0x = None
                b0y = None
                b0z = None
                b0abs = None
        return b0x,b0y,b0z,b0abs
    
