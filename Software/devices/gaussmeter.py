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

    - set_filter_on()

    - set_filter_points()

    - set_filter_window()

    - read()

    # Internal Methods

    - parseB0()

    - readout_ser_buffer()
    '''
    def __init__(self,serial_port='/dev/ttyUSB0'):
        '''
        initializes the serial communication to the lakeshore gaussmeter.

        # Args

        serial_port: string. system dependend device name of serial port. Default: '/dev/ttyUSB0'
        
        '''
        self.t_measure = 0.6 # waiting time for filling the lakeshore filter with values

        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return
        
        self.ser = serial.Serial(
        port=serial_port,
        baudrate=9600,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.SEVENBITS,
        timeout=0.3 # in seconds
        )
        
        print('serial connection for gaussmeter opened')


    def readout_ser_buffer(self):
        '''
        reads the serial buffer

        returns a string of whatever was in the buffer.
        '''
        sleep(0.15)
        value=''
        #print(self.ser.out_waiting)
        while True:
            prey = self.ser.read()
            if not prey:
                break
            value += prey.decode()
        return value.removesuffix('\r\n')


    def set_mode(self, mode:str='fast'):
        '''
        sets the mode to either 'fast' or 'normal'

        # Args

        - mode: string. 'fast' or 'normal'

        # Returns 

        - current mode from lakeshore
        
        '''
        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return

        if mode=='fast':
            pass
        elif mode=='normal':
            pass
        else:
            raise ValueError('mode can either be \'fast\' or \'normal\', but \'' + str(mode) + '\' was given')
        
        # needed to ask 2 times because of async receive
        self.ser.write('FAST?'.encode())
        self.ser.write('FAST?'.encode())
        value = self.readout_ser_buffer()

        if int(value) == 1:
            read_mode = 'fast'
            print('Set gaussmeter into fast mode. Display off, temperatur compensation off.')
        if int(value) == 0:
            read_mode = 'normal'
            print('Setting gaussmeter into normal mode. Display on, temperatur compensation on')

        return read_mode
    

    def set_filter_on(self, on:bool=True):
        '''
        
        '''
        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return
        
        self.ser.write(('FILT ' + str(int(on))).encode())
        
        sleep(0.5)
        self.ser.write('FILT?'.encode())
        self.ser.write('FILT?'.encode())
        is_on = bool(self.readout_ser_buffer())

        if is_on:
            print('Set Filter On')
        if not is_on:
            print('Set Filter Off')

        return is_on  
    

    def set_filter_window(self, filter_window:int):
        '''
        sets the filter window. See Paragraph 3.6 of Lakeshore Manual 

        # Args

        - filter_window:int. Can be 1 to 10. in Percent.

        # Returns

        - None
        
        '''
        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return    
        
        self.ser.write(('FWIN ' + str(filter_window)).encode())
        self.ser.write('FWIN?'.encode())
        self.ser.write('FWIN?'.encode())
        value = int(self.readout_ser_buffer())

        print('Set Filter Window: FWIN = ' + str(value) + '%')

        return value


    def set_filter_points(self, f_num:int):
        '''
        sets the length of the filter buffer. Refer to 'FNUM' in Lakeshore datasheet. 

        # Args

        - f_num: int.

        # Returns

        - None
        
        '''
        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return
        
        self.ser.write(('FNUM ' + str(f_num)).encode())

        self.ser.write('FNUM?'.encode())
        self.ser.write('FNUM?'.encode())
        num_filter_points = int(self.readout_ser_buffer())

        print('Set Number of Filterpoints FNUM = ' + str(num_filter_points))

        return num_filter_points


    def read(self, t_measure:float=None):
        '''
        Reads the value of the gaussmeter.

        The gaussmeter will return the value which is in the buffer before it is requested.
        So this function waits for calling ALLF? until the measurement time t_meausure is over.
        The actual measurement time depends on a lot of values, refer to the datasheet from lakeshore.

        # Args

        - t_measure:float, optioal. measuring time in s. default: self.t_measure

        # Returns

        - b0x,b0y,b0z,b0abs. tuple of float. Values in [mT]

        '''
        if not has_serial:
            print('no serial on system. No connection to gaussmeter possible')
            return 0,0,0,0
        
        if t_measure==None:
            t_measure = self.t_measure
        
        sleep(t_measure)
        self.ser.write('ALLF?'.encode()) # returns the last ?command.
        value = ''
        sleep(0.1)
        value = self.readout_ser_buffer()
        b0x,b0y,b0z,b0abs = self.parse_B0(value)
        return b0x,b0y,b0z,b0abs


    def parse_B0(self,raw_reading):
        if raw_reading =='':
            raise ValueError('Can not parse an empty string as a B0 reading.')
        
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
    
