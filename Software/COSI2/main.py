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


### 5. Compiling and Downloading to MCU

Replace 0483:df11 with your hardware's ID from step 4 And execute the following command:

     cd klipper
     make flash FLASH_DEVICE=0483:df11
     
'''


from PyQt5 import QtWidgets, uic
import sys # for finding the script path and importing scripts
#import communication

import os
#import importlib.util

#Queues for 'fast' devices
from multiprocessing import Process, Queue
from time import sleep

import cosimeasure # the beast
import gaussmeter # the accesoir

import Plotter  # an EMRE module for plotting

# utility windows:
#import deviceManagerUtility


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

class Ui(QtWidgets.QMainWindow):
    """the main User Interface window."""
    def __init__(self):
        isfake = True # by default, the thing is fake as tested outside
        self.cosimeasure = cosimeasure.cosimeasure # just define type here
        self.gaussmeter = gaussmeter.gaussmeter
        #self.DevManGui = None # to be added later: device manager gui

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

        super(Ui, self).__init__() # Call the inherited classes __init__ method
        try:
            uic.loadUi('gui/COSIGUI.ui', self) # Load the .ui file
        except:
            print('loading UI failed, cd to script folder')
            exit()
        self.show() # Show the GUI


        # binding methods to buttons:
        self.connect_button.clicked.connect(self.connect_to_cosi)  # Remember to pass the definition/method, not the return value!
        self.devman_button.clicked.connect(self.open_dev_man)  # Remember to pass the definition/method, not the return value!
        self.load_path_file_btn.clicked.connect(self.load_path)
        self.run_btn.clicked.connect(self.run_experiment)
        self.abort_btn.clicked.connect(self.abort_experiment)

        '''plotter'''
        plotterWidgetFound = self.findChild(QtWidgets.QWidget, 'plotterWidget')
        self.pathPlotterWGT = Plotter.Plotter(parent=plotterWidgetFound, plotType='PTH')
        self.verticalLayout_plotter.addWidget(self.pathPlotterWGT)
        # self.verticalLayout_CV_plotter.addWidget(self.CHGplotter.toolbar)
        self.pathPlotter = self.pathPlotterWGT.PlotterCanvas
        self.pathPlotter.preset_PTH()  # just add some labels

        # todo: add head position


    def connect_to_cosi(self):
        '''connect to the robot. dont home, just connect, read acks'''
        self.isfake = False # todo: make a user friendly tick box
        print('connecting to COSI.')
        self.cosimeasure = cosimeasure.cosimeasure(isfake=self.isfake) # testing mode
        print('connecting to Gaussmeter.')
        self.gaussmeter= gaussmeter.gaussmeter(isfake=self.isfake)

        for i in range(10):
            sleep(0.5)
            print(self.gaussmeter.read_gaussmeter())

        self.init_btn.setEnabled(True)
        self.run_btn.setEnabled(True)
        self.abort_btn.setEnabled(True)
    

        self.home_x_plus_btn.clicked.connect(self.cosimeasure.home_x_plus)  # home X+
        self.home_x_minus_btn.clicked.connect(self.cosimeasure.home_x_minus)  # home X-

        self.home_y_plus_btn.clicked.connect(self.cosimeasure.home_y_plus)  # home Y+
        self.home_y_minus_btn.clicked.connect(self.cosimeasure.home_y_minus)  # home Y-
        self.home_z_plus_btn.clicked.connect(self.cosimeasure.home_z_plus)  # home Z+
        self.home_z_minus_btn.clicked.connect(self.cosimeasure.home_z_minus)  # home Z-

        self.init_btn.clicked.connect(self.cosimeasure.init_path)  
        self.run_btn.clicked.connect(self.cosimeasure.run_measurement)
        self.abort_btn.clicked.connect(self.cosimeasure.abort)
          
          
        

    def open_dev_man(self):
        '''open device manager window'''
        print('List known devices. See if connected.')

    def load_path(self):

        print('load the path file.')
        # open file dialog

        try:
            self.cosimeasure.pathfile_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="Select path data",
                                                                   directory=self.cosimeasure.working_directory,
                                                                   filter="path Files (*.path);;CSV Files (*.csv)")
            self.cosimeasure.working_directory = os.path.split(os.path.abspath(self.cosimeasure.pathfile_path))[0]

        except:
            print('no filename given, do it again.')
            return 0
        if self.cosimeasure.pathfile_path:
            print('loading path %s with cosimeasure.',self.cosimeasure.pathfile_path)
            self.cosimeasure.load_path()
            self.pathPlotter.plot_head_on_path(cosimeasure=self.cosimeasure)

    def run_experiment(self):
        print('all ready? run that scan')

    def abort_experiment(self):
        print('stop all! TEMP:')
        self.pathPlotter.plot_head_on_path(cosimeasure=self.cosimeasure)




if __name__ == "__main__":
    q = Queue()

    app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    window = Ui()  # Create an instance of our class
    app.exec_()  # Start the application

    # p_generator = Process(target=window.app.exec, args=(q,))
    # p_generator.start()
    #
    # p_generator.join()