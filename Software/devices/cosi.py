import time
from numpy import array, unique
import os
from utils.utils import run_bash_script, run_bash_command
try:
    import serial 
    has_serial = True
except: 
    print('no serial on system. Not connecting to machine')
    has_serial = False


class CosiMeasure():
    '''
    Class to control the main functionality of the 3-axis robot. 

    # Methods:

    - command()

    - home_x()

    - home_y()

    - home_z()

    - move_to()

    - measure_async_along_path()

    - enable_motors()

    - disable_motors()

    - query_endstops()

    - check4bounds()

    - check4duplicates()

    # Internal Methods

    - __init__()

    - decode_pathfile_line()

    - check_drive_state_enabled()

    
    '''
    # make sure that this class is a singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CosiMeasure, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    

    min_x = 0
    min_y = 0
    min_z = 0

    max_x = 497
    max_y = 460
    max_z = 610
    
    home_position_x = min_x
    home_position_y = max_y
    home_position_z = min_z

    #if has_serial:
    

    drives_disabled_by_hardware = False # see self.disable_motors()

    def __init__(self,):
        '''
        initialieses the robot:

        1. flashing MCU

        2. start klipper service

        '''
        if not has_serial:
            print('no serial thus no machine to init')
            return
        
        output = run_bash_script('flash-mcu.sh')
        time.sleep(1)

        output = run_bash_command('sudo service klipper stop')
        time.sleep(1)

        output = run_bash_command('sudo service klipper start')
        time.sleep(1)

        self.ser = serial.Serial('/tmp/printer', 250000)
        time.sleep(1)
        print('opened serial to klipper service')


    def command(self,command, verbose=False):
        '''
        Method to send a command directly to Klipper, the firmware of CosiMeasure. 
        Only use this if you know what you are doing. There are easy to use wrappers for standard stuff.

        # Args:

        - command: string, GCode etc. refer to https://www.klipper3d.org/G-Codes.html

        - verbose, optinal. default: False. If True, all answers from klipper will be printet to stdout

        # Return

        - klipper_output. List of strings.
        '''

        command = command + "\r\n"
        klipper_output = []

        if not has_serial:
            print('no serial. send: ' + command)
            return

        else:
            if verbose:
                print('send: '+ command)

        self.ser.write(str.encode(command)) 
        #time.sleep(1)

        while True:
            line = self.ser.readline()
            klipper_output.append(line)
            if verbose:
                print(line)

            if line == b'ok\n':
                break

        return klipper_output

    
    def home_x(self):
        '''
        homes x-axis as specified in printer.cfg
        '''
        state = self.check_drive_state_enabled()
        a = self.command('G28 X%.3f' % self.home_position_x)
        a = self.command('M400')                            # wait until Cosi has finished the previous command
        return self.get_last_requested_position()  # get last requested position


    def home_y(self):
        '''
        homes y-axis as specified in printer.cfg
        '''
        state = self.check_drive_state_enabled()
        a = self.command('G28 Y%.3f' % self.home_position_y)
        a = self.command('M400')                            # wait until Cosi has finished the previous command
        return self.get_last_requested_position()  # get last requested position


    def home_z(self):
        '''
        homes z-axis as specified in printer.cfg
        '''
        state = self.check_drive_state_enabled()
        a = self.command('G28 Z%.3f' % self.home_position_z)
        a = self.command('M400')                            # wait until Cosi has finished the previous command
        return self.get_last_requested_position()


    def move_to(self, x=None, y=None, z=None):
        '''
        moves to specified position in mm, after finsihed movement it returns the current position
        '''
        if x==None and y==None and z==None:
            raise ValueError('At least one position must be provided')
        
        self.check_drive_state_enabled()

        command = 'G0 '
        if x!=None:
            command += 'X%.3f ' %float(x)

        if y!=None:
            command += 'Y%.3f ' %float(y)

        if z!=None:
            command += 'Z%.3f ' %float(z)

        a = self.command(command, verbose=False)             # move to position
        a = self.command('M400')                            # wait until Cosi has finished the previous command
        return self.get_last_requested_position()

        


    def enable_motors(self):
        self.command("hard_enable_drives")
        time.sleep(0.3)
        self.drives_disabled_by_hardware = False


    def disable_motors(self):
        '''
        disables the drives by hardware.

        This is used for HF-measurements to avoid noise from the stepper motors.

        A movement (e.g. G0-commands) with disabled drives will lead to wrong tool_head_positions of Klipper. 
        Every method which causes a movement shall run `self.check_drive_state_enabled()` before.
        '''
        response = self.command('M400') # waits until all commands in the queue are executed
        response = self.command('M114')
        time.sleep(0.1)
        self.drives_disabled_by_hardware = True
        self.command("hard_disable_drives")
        time.sleep(0.1)


    def check_drive_state_enabled(self):
        '''raises an Exception if drives are disabled by hardware'''
        if self.drives_disabled_by_hardware==True:
            raise Exception('Drives are disabled by hardware. Use CosiMeasure.enable_motors() before executing a movement')


    def query_endstops(self):
        '''
        prints the state of all endstops
        '''
        print(self.command("QUERY_ENDSTOPS"))

    def get_last_requested_position(self):
        '''
        returns the result of M114 parsed into  3 floats x,y,z
        '''

        values = self.command("M114")[-2].decode().split(' ') # b'X:386.620 Y:286.000 Z:558.280 E:0.000\n'
        x = float(values[0].split(':')[1])
        y = float(values[1].split(':')[1])
        z = float(values[2].split(':')[1])

        return x, y, z

        


    def decode_pathfile_line(self, line):
        '''
        decodes a line of the path file

        returns numpy.array with x,y,z
        '''
        parts = line.strip().split(',')
        if len(parts) == 3:
            xyz = array([float(parts[0]), float(parts[1]), float(parts[2])], dtype=float)
        return xyz


    def check4bounds(self, filename):
        '''
        checks wheter there are poiints outside of CosiMeasure in a path file.

        Returns `False` if all points are inside the Cosi

        An exception is raised if a collision is detected, so that no script can continue to kamikaze
        '''
        is_colliding = None
        with open(filename, 'r') as f:
            data = f.readlines()
            for line in data:
                x,y,z = self.decode_pathfile_line(line)
                if (x < self.min_x) or (x > self.max_x):
                    print("There are points outside of COSY Measure!")
                    print(x)
                    is_colliding = True
                    break
                elif (y < self.min_y) or (y > self.max_y):
                    print("There are points outside of COSY Measure!")
                    print(y)
                    is_colliding = True
                    break
                elif (z < self.min_z) or (z > self.max_z):
                    print("There are points outside of COSY Measure!")
                    print(z)
                    is_colliding = True
                    break
                else:
                    pass

            if is_colliding:
                raise Exception('Abort. Please redefine the `path_file` without collisions')

        print("All points are inside the limits of COSI Measure.")
        return False
    

    def check4duplicates(self, fileID):
        with open(fileID, 'r') as f:
            data = f.readlines()
            if len(data) != len(unique(data)):
                print("There are duplicates in the pathfile!")
                return True
            else:
                print("No duplicates.")
                return False
            

    def measure_async_along_path(self, pathfile, rawdatfile, probe, header='X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]\n'):
        '''
        measrues along the points of a given pathfile and stores the data in a rawdatfile.

        The probe is expected to have an asynchronous read out. see gaussmeter.py for an example/ details.

        This method will write raw data, meaning there are no coordinate transformations etc. 
        It is recommended to do this in postprocessing only.

        # Args:

        - pathfile:str. path to file

        - rawdatfile:str. path to file

        - probe-object. It shall have a methode probe.read() which is expected to return an array-like object with (x,y,z,abs) values.

        - header:str. Optional. First line of rawdatfile. Default: 'X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]\\n'

        # Returns: 
        
        - None, but a rawdatfile will be on your file-system

        '''
        
        with open(pathfile, 'r') as _pathfile:
            path_data = _pathfile.readlines()
            coordinates = []
            for line in path_data:
                coordinates.append(self.decode_pathfile_line(line))

        with open(rawdatfile, 'w') as _rawdatfile:
            _rawdatfile.write(header)
            for i in range(len(coordinates)):

                self.move_to(x=coordinates[i][0], y=coordinates[i][1], z=coordinates[i][2])

                b0x,b0y,b0z,b0abs = probe.read()

                if not i==0:
                    line = '%.2f, %.2f, %.2f, %3f, %3f, %3f\n'%(coordinates[i-1][0],coordinates[i-1][1],coordinates[i-1][2], b0x,b0y,b0z)
                    print(line)
                    _rawdatfile.write(line)

            b0x,b0y,b0z,b0abs = probe.read()
            line = '%.2f, %.2f, %.2f, %3f, %3f, %3f\n'%(coordinates[len(coordinates)-1][0],coordinates[len(coordinates)-1][1],coordinates[len(coordinates)-1][2], b0x,b0y,b0z)
            _rawdatfile.write(line)

        print('finished measurement')