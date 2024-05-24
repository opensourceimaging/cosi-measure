""" 2024 rst PTB rst030@protonmail.com"""


'''
### 3. Going into Bootloader Mode

1. Power On
2. Press and hold "boot"
3. Press "reset"
4. release "boot"

### 4. Searching Device ID:

     lsusb

Will show up something like

     Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
     Bus 001 Device 031: ID 0483:df11 STMicroelectronics STM Device in DFU Mode
     Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub


### 5. Compiling and Downloading to MCU test

Replace 0483:df11 with your hardware's ID from step 4 And execute the following command:

     cd klipper
     make flash FLASH_DEVICE=0483:df11
     
'''
#TODO: make csv import/export the standard procedure.
#TODO fix flipping coordinates in 2d slice plotter at imshow/contourf. deal with np.transpose on meshgrid.

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import * # needed for multithreading

import sys # for finding the script path and importing scripts
#import communication

import os
#import importlib.util

#Queues for 'fast' devices
from multiprocessing import Process, Queue
from time import sleep

import cosimeasure # the beast
import gaussmeter # the accesoir
import osi2magnet # the patient

from utils import Plotter  # an EMRE module for plotting
from pathgen import ball_path, sphere_path

# utility windows:
#import deviceManagerUtility
from utils import field_viewer
import b0


# logging for debug info and cmdline arg parsing
import logging
import argparse

# parse the log level
parser = argparse.ArgumentParser(description='This is the COSI2 control environment')
parser.add_argument('-d','--debug', dest='debug',help='switch to debug mode')
parser.add_argument('-q','--quiet', dest='quiet',help='run without gui')

my_args = parser.parse_args()
DEBUG=my_args.debug
QUIET=my_args.quiet # todo suppress gui and messages when called with -q


# multithreading - doing it like in EMRE
# one process measures, other process plots

# these two processes are required for multithreading


class data_generating_thread(QThread): # oт это у нас кусрэд, но наш, русскaй, родной, ТТТ.
    def __init__(self, _cosimeasure:cosimeasure.cosimeasure):  # and here is its constructor
        super(data_generating_thread, self).__init__() # from a parent to be born
        self.quit_flag = False # and no flag was given to ever quit anything
        self.cosimeasure = _cosimeasure
        
    def run(self): # it waits, like a cat in a bush, when you call it. Run! - you shout.

        print('cosimeasure''s data generating QThread running')

        self.cosimeasure.run_measurement()

        self.quit()
        #self.wait()
        
        
class data_visualisation_thread(QThread): # this is the data vis thread. Reads data from q and plots to Plotter
    def __init__(self,_plotter:Plotter.PlotterCanvas, _cosimeasure:cosimeasure.cosimeasure):
        super(data_visualisation_thread, self).__init__()
        self.cosimeasure = _cosimeasure
        self.plotter = _plotter
    def run(self):
        self.q = self.cosimeasure.q
        slp = float(0.5*self.cosimeasure.measurement_time_delay) # sleep between points how long, in seconds
        sleep(2*slp)
        
        while 1:
            empty = self.q.empty()
            print('vis thread waiting for data. queue empty? ', empty)
            if not empty:
                break
        
        while True:
            if not self.q.empty():
                while not self.q.empty():
                    self.cosimeasure.b0 = self.q.get()
                self.plotter.plot_head_on_path(cosimeasure=self.cosimeasure,magnet=self.cosimeasure.magnet)
                print('vis thread sleeping for %.2f s'%slp)
                sleep(slp)
            else: # if no data in queue, wait longer
                sleep(2*slp)
                if self.q.empty():
                    break
        self.quit()
        #self.wait()



















class Ui(QtWidgets.QMainWindow):
    """the main User Interface window."""
    def __init__(self):
        self.cosimeasure = cosimeasure.cosimeasure # just define type here
        self.gaussmeter = gaussmeter.gaussmeter
        self.magnet = osi2magnet.osi2magnet()
        #self.DevManGui = None # to be added later: device manager gui

        #self.communicator = None # later: make a dev manager
        #self.communicator = None # later: make a dev manager

        self.qGlob = Queue(maxsize = 100000) # the global queue that is used to store the data before plotting

        self.log = logging.getLogger("COSI_logger")
        self.log.setLevel(logging.DEBUG if DEBUG == '1' else logging.INFO)
        logging.debug('Plain debug test') # for some reason necessary to initialise logging
        # get the script's directory
        # print('scripts working directory',os.path.dirname(sys.argv[0]))
        # os.chdir(os.path.dirname(sys.argv[0]))
        # get the root dir of the main exec script
        ROOT_PATH = os.path.dirname(sys.argv[0])
        if ROOT_PATH == '':
            # get current dir
            ROOT_PATH = os.getcwd()

        self.log.debug('Main working directory: %s'% ROOT_PATH)
        os.chdir(ROOT_PATH)
        print(os.getcwd())
        self.working_directory = ROOT_PATH 
        print('working directory: ',self.working_directory)

        super(Ui, self).__init__() # Call the inherited classes __init__ method
        try:
            uic.loadUi('gui/COSIGUI.ui', self) # Load the .ui file
        except:
            print('loading UI failed, cd to script folder')
            exit()
        self.show() # Show the GUI

        self.isfake = True  #True # by default, the thing is fake as tested outside

        # binding methods to buttons:
        self.connect_button.clicked.connect(self.connect_to_cosi)  # Remember to pass the definition/method, not the return value!
        self.devman_button.clicked.connect(self.open_dev_man)  # Remember to pass the definition/method, not the return value!
        self.abort_btn.clicked.connect(self.abort_experiment)

        self.cmd_send_cosi_btn.clicked.connect(self.send_cmd_to_cosi)
        
        '''utility buttons'''
        self.field_viewer_btn.clicked.connect(self.open_field_viewer)


        '''PATH plotter'''
        plotterWidgetFound = self.findChild(QtWidgets.QWidget, 'plotterWidget')
        self.pathPlotterWGT = Plotter.Plotter(parent=plotterWidgetFound, plotType='PTH')
        self.verticalLayout_plotter.addWidget(self.pathPlotterWGT)
        # self.verticalLayout_CV_plotter.addWidget(self.CHGplotter.toolbar)
        self.pathPlotter = self.pathPlotterWGT.PlotterCanvas
        self.pathPlotter.preset_PTH()  # just add some labels




        ''' PATH GENERATOR '''
        self.load_path_file_btn.clicked.connect(self.load_path)
        self.path_gen_btn.clicked.connect(self.gen_ball_path)
        self.grad_path_gen_btn.clicked.connect(self.gen_gradient_path)
        


    def send_cmd_to_cosi(self):
        cmd = self.cmd_to_cosi_edit.text()
        if cmd == '':
            return

        print(cmd, 'will be sent to cosi')
        response = self.cosimeasure.command(cmd)
        #self.cmd_to_cosi_edit.setText(str(response))
        return response


    def connect_to_cosi(self):
        '''connect to the robot. dont home, just connect, read acks'''
        self.isfake = self.fake_check_box.isChecked()  #True # by default, the thing is fake as tested outside


        print('connecting to Gaussmeter.')
        self.gaussmeter= gaussmeter.gaussmeter(isfake=self.isfake)

        print('connecting to COSI.')

        self.cosimeasure = cosimeasure.cosimeasure(isfake=self.isfake,gaussmeter=self.gaussmeter,magnet=self.magnet,queue=self.qGlob) 
        #isfake for testing mode, queue is where it puts the b0 object.

        self.init_btn.setEnabled(True)
        self.run_btn.setEnabled(True)
        self.abort_btn.setEnabled(True)

        self.mag_pos_btn.clicked.connect(self.recenter_magnet) # get xyz of the magnet center and plot it 

        self.home_x_plus_btn.clicked.connect(self.cosimeasure.home_x_plus)  # home X+
        self.home_x_minus_btn.clicked.connect(self.cosimeasure.home_x_minus)  # home X-
        self.x_quickhome_btn.clicked.connect(self.cosimeasure.quickhome_x)  # home X- quick

        self.home_y_plus_btn.clicked.connect(self.cosimeasure.home_y_plus)  # home Y+
        self.home_y_minus_btn.clicked.connect(self.cosimeasure.home_y_minus)  # home Y-
        self.y_quickhome_btn.clicked.connect(self.cosimeasure.quickhome_y)  # home Y- quick

        self.home_z_plus_btn.clicked.connect(self.cosimeasure.home_z_plus)  # home Z+
        self.home_z_minus_btn.clicked.connect(self.cosimeasure.home_z_minus)  # home Z-
        self.z_quickhome_btn.clicked.connect(self.cosimeasure.quickhome_z)  # home Z- quick

        self.x_right_btn.clicked.connect(self.cosimeasure.x_step_up)
        self.x_left_btn.clicked.connect(self.cosimeasure.x_step_down)
        self.y_right_btn.clicked.connect(self.cosimeasure.y_step_up)
        self.y_left_btn.clicked.connect(self.cosimeasure.y_step_down)
        self.z_right_btn.clicked.connect(self.cosimeasure.z_step_up)
        self.z_left_btn.clicked.connect(self.cosimeasure.z_step_down)
        
        self.init_btn.clicked.connect(self.init_path)  
        self.run_btn.clicked.connect(self.run_measurement)
        self.abort_btn.clicked.connect(self.cosimeasure.abort)
        
    def init_path(self):
        self.cosimeasure.init_path()
        self.pathPlotter.plot_head_on_path(cosimeasure=self.cosimeasure,magnet=self.magnet)
    
    def run_measurement(self):
        self.b0_scan_glob = b0.b0(path=self.cosimeasure.path) # an empty instance of the b0 object to be shared between the cosimeasure and the plotter
        self.cosimeasure.b0 = self.b0_scan_glob
        
        while not self.cosimeasure.q.empty():
            self.cosimeasure.q.get()

        self.gen_trd = data_generating_thread(_cosimeasure=self.cosimeasure)
        self.vis_trd = data_visualisation_thread(_plotter = self.pathPlotter,_cosimeasure=self.cosimeasure)

        self.vis_trd.start()
        print(' VIS thread started')
        self.gen_trd.start()
        print('GEN thread started')

        
        
            
    def recenter_magnet(self):
            magcoords = self.mag_pos_edit.text().split(',')
            x = float(magcoords[0])
            y = float(magcoords[1])
            z = float(magcoords[2])  
            mageulers = self.euler_edit.text().split(',')
            
            alpha = float(mageulers[0])
            beta = float(mageulers[1])
            gamma = float(mageulers[2])
            
            # plot initial magnet position in lab frame
            self.magnet.set_origin(x,y,z)
            self.magnet.rotate_euler(alpha=alpha,beta=beta,gamma=gamma)
        
            self.cosimeasure.head_position = [x,y,z]       
            self.pathPlotter.plot_head_on_path(cosimeasure=self.cosimeasure,magnet=self.magnet)
            
            
    def open_dev_man(self):
        '''open device manager window'''
        print('List known devices. See if connected.')


    def abort_experiment(self):
        print('stop all! TEMP:')
        self.pathPlotter.plot_head_on_path(cosimeasure=self.cosimeasure,magnet=self.magnet)



    ''' PATHS '''

    def gen_gradient_path(self):
        xc = float(self.path_dim_edit.text().split(",")[0])
        yc = float(self.path_dim_edit.text().split(",")[1])
        zc = float(self.path_dim_edit.text().split(",")[2])
        rad = float(self.path_dim_edit.text().split(",")[3]) # mm
        axis = str(self.path_dim_edit.text().split(",")[4]) # x,y or z

        radpts = int(self.path_res_edit.text())
        try:
            self.cosimeasure.pathfile_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="path filename",
                                                            directory=self.cosimeasure.working_directory,
                                                            filter="path Files (*.path);;CSV Files (*.csv)")
            self.cosimeasure.working_directory = os.path.split(os.path.abspath(self.cosimeasure.pathfile_path))[0]

        except:
            print('no filename given, do it again.')
            return 0
        
        base_filename = os.path.splitext(self.cosimeasure.pathfile_path)[0]
        
        self.cosimeasure.b0_filename=base_filename+'_bvals.csv'
        # todo: do the path generator inside the pth class
        #cross_path = ball_path.gradient_path(filename_input=self.cosimeasure.pathfile_path,center_point_input=(xc,yc,zc),radius_input=rad,radius_npoints_input=radpts)
        cross_path = ball_path.gradient_path(filename_input=self.cosimeasure.pathfile_path,center_point_input=(xc,yc,zc),radius_input=rad,radius_npoints_input=radpts,axis=axis) 
        
        self.cosimeasure.load_path() # change to automatic loading of path when the path filename is given
        self.pathPlotter.plot_head_on_path(cosimeasure=self.cosimeasure,magnet=self.magnet)


    def gen_ball_path(self):
        xc = float(self.path_dim_edit.text().split(",")[0])
        yc = float(self.path_dim_edit.text().split(",")[1])
        zc = float(self.path_dim_edit.text().split(",")[2])
        rad = float(self.path_dim_edit.text().split(",")[3]) # mm
        radpts = int(self.path_res_edit.text())
        
        try:
            self.cosimeasure.pathfile_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="path filename",
                                                            directory=self.cosimeasure.working_directory,
                                                            filter="path Files (*.path);;CSV Files (*.csv)")
            self.cosimeasure.working_directory = os.path.split(os.path.abspath(self.cosimeasure.pathfile_path))[0]

        except:
            print('no filename given, do it again.')
            return 0
        
        base_filename = os.path.splitext(self.cosimeasure.pathfile_path)[0]
        
        self.cosimeasure.b0_filename=base_filename+'_bvals.csv'
        # todo: do the path generator inside the pth class
        sphere_path = ball_path.ball_path(filename_input=self.cosimeasure.pathfile_path,center_point_input=(xc,yc,zc),radius_input=rad,radius_npoints_input=radpts)
        self.cosimeasure.load_path() # change to automatic loading of path when the path filename is given
        self.pathPlotter.plot_head_on_path(cosimeasure=self.cosimeasure,magnet=self.magnet)


    def load_path(self,pathfilename=None):
        print('load the path file.')
        
        if pathfilename is not None:
            print("given filename: ",pathfilename)
            self.cosimeasure.pathfile_path = pathfilename#+'.path'
        # if no filename given, open file dialog
        else:
            try:
                self.cosimeasure.pathfile_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="Select path data",
                                                                       directory=self.cosimeasure.working_directory,
                                                                       filter="path Files (*.path);;CSV Files (*.csv)")
                self.cosimeasure.working_directory = os.path.split(os.path.abspath(self.cosimeasure.pathfile_path))[0]

            except:
                print('no filename given, do it again.')
            return 
        
        if self.cosimeasure.pathfile_path:
            print('loading path %s with cosimeasure.'%self.cosimeasure.pathfile_path)
            self.cosimeasure.load_path(path_filename=self.cosimeasure.pathfile_path)
            self.pathPlotter.plot_head_on_path(cosimeasure=self.cosimeasure,magnet=self.magnet)



    '''utuilities'''
    def open_field_viewer(self):
        print('opening a window with a B0 field viewer')
        self.field_viewer_gui = field_viewer.field_viewer_gui()




if __name__ == "__main__":
    q = Queue()

    app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    window = Ui()  # Create an instance of our class
    app.exec_()  # Start the application

    # p_generator = Process(target=window.app.exec, args=(q,))
    # p_generator.start()
    #
    # p_generator.join()
    
    
    
    