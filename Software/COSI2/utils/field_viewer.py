'''rst@ptb 240429'''
'''field viewer class for visualizing B0 maps recorded with cosi measure'''

from PyQt5 import QtWidgets, uic
import os
from time import sleep # for dev only

from utils import Plotter  # an EMRE module for plotting
import b0  # class of b0, makes an object of a b0. Can import from file. Attributes: see shimming_david repo

from PyQt5 import QtWidgets


class field_viewer_gui(QtWidgets.QMainWindow):
    '''the field viewer window.'''
    
    b0map = None  # instance of b0 scan, make an object.

    workingFolder = r"./dummies/"  # where the openfiledialog opens

    def __init__(self):
        super(field_viewer_gui, self).__init__()  # Call the inherited classes __init__ method

        uic.loadUi('gui/field_viewer.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        # working folder
        self.b0Path = None

        # binding methods to buttons:
        self.save_button.clicked.connect(self.save_b0_slice)  # Remember to code the method in the class.
        self.load_button.clicked.connect(self.load_b0)  # Remember to code the method in the class.

        # --- adding the plotter: ---
        # CV plotter:
        plotterWidgetFound = self.findChild(QtWidgets.QWidget, 'plotter_widget')
        self.plotterWGT = Plotter.Plotter(parent=plotterWidgetFound, plotType = 'B0M')
        self.verticalLayout_CV_plotter.addWidget(self.plotterWGT)
        #self.verticalLayout_CV_plotter.addWidget(self.CVplotter.toolbar)
        self.plotter = self.plotterWGT.PlotterCanvas
        self.plotter.preset_B0M()  # just add some labels

        # todo code and import b0, see shimming script



    def load_b0(self):
        print('open a file dialog, get a b0 scan file name, slice by z, plot first scan')
        # open file dialog
        try:
            self.b0Path, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="Select B0 data",
                                                                   directory=self.workingFolder,
                                                                   filter="All Files (*);;txt Files (*.txt)")
            self.workingFolder = os.path.split(os.path.abspath(self.b0Path))[0]

        except:
            print('no filename given, do it again.')
            return 0

        # import the cv curve as an object
        self.b0map = b0.b0(b0_filename = self.b0Path)
        # and print it on the plotter.
        self.plotter.plotB0(self.b0map)



    def save_b0_slice(self):
        print('save as file dialog etc, think of the format, Be compatible with the future imports')