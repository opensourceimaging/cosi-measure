'''rst@ptb 240429'''
'''field viewer class for visualizing B0 maps recorded with cosi measure'''

from PyQt5 import QtWidgets, uic
import os
from time import sleep # for dev only

from utils import Plotter  # an EMRE module for plotting
import b0  # class of b0, makes an object of a b0. Can import from file. Attributes: see shimming_david repo

from PyQt5 import QtWidgets
import numpy as np


class field_viewer_gui(QtWidgets.QMainWindow):
    '''the field viewer window.'''
    
    b0map = b0.b0  # instance of b0 scan, make an object.

    workingFolder = r"./dummies/b0_maps"  # where the openfiledialog opens

    def __init__(self):
        super(field_viewer_gui, self).__init__()  # Call the inherited classes __init__ method

        uic.loadUi('gui/field_viewer.ui', self)  # Load the .ui file
        self.show()  # Show the GUI

        # working folder
        self.b0Path = None

        # binding methods to buttons:
        self.save_button.clicked.connect(self.save_rotated_path)  # Remember to code the method in the class.
        self.load_button.clicked.connect(self.load_b0)  # Remember to code the method in the class.

        # --- adding the plotter: ---
        # CV plotter:
        plotterWidgetFound = self.findChild(QtWidgets.QWidget, 'plotter_widget')
        self.plotterWGT = Plotter.Plotter(parent=plotterWidgetFound, plotType = 'B0M')
        self.verticalLayout_CV_plotter.addWidget(self.plotterWGT)
        #self.verticalLayout_CV_plotter.addWidget(self.CVplotter.toolbar)
        self.plotter = self.plotterWGT.PlotterCanvas
        self.plotter.preset_B0M()  # just add some labels
        
        # connect tick box with plotter. on tick plot only one slice
        self.XYcheckBox.stateChanged.connect(self.plot_B0M_slice_Z)
        self.ZXcheckBox.stateChanged.connect(self.plot_B0M_slice_Y)
        self.YZcheckBox.stateChanged.connect(self.plot_B0M_slice_X)
        

        # todo code and import b0, see shimming script



    def load_b0(self):
        print('open a file dialog, get a b0 scan file name, slice by z, plot first scan')
        # open file dialog
        try:
            self.b0Path, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="Select B0 data",
                                                                   directory=self.workingFolder,
                                                                   filter="txt Files (*.txt)")
            self.workingFolder = os.path.split(os.path.abspath(self.b0Path))[0]

        except:
            print('no filename given, do it again.')
            return 0

        # open file dialog
        try:
            self.pathPath, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption="Select path data",
                                                                   directory=self.workingFolder,
                                                                   filter="path Files (*.path)")
            self.workingFolder = os.path.split(os.path.abspath(self.pathPath))[0]

        except:
            print('no filename given, do it again.')
            return 0

        # import the b0 as an object
        self.b0map = b0.b0(b0_filename = self.b0Path,path_filename=self.pathPath)
        self.coordinate_transform_btn.clicked.connect(self.change_coords_to_magnet)
        # and print it on the plotter.
        self.plotter.plotPathWithMagnet(self.b0map)
        


    def plot_B0M_slice_Z(self):
        # get states of Z slicing check boxes:
        if self.XYcheckBox.isChecked():
            XY_slice_number = int(self.XYspinBox.value())
            #print('slice the B0M data by XY plane, get slice number %d'%XY_slice_number)
            self.plotter.plotB0Map(b0map_object=self.b0map, slice_number=XY_slice_number, coordinate_system='magnet',slice_axis='Z')

    def plot_B0M_slice_Y(self):
        # get states of Z slicing check boxes:
        if self.ZXcheckBox.isChecked():
            ZX_slice_number = int(self.ZXspinBox.value())
            #print('slice the B0M data by XY plane, get slice number %d'%XY_slice_number)
            self.plotter.plotB0Map(b0map_object=self.b0map, slice_number=ZX_slice_number, coordinate_system='magnet',slice_axis='Y')

    def plot_B0M_slice_X(self):
        # get states of Z slicing check boxes:
        if self.YZcheckBox.isChecked():
            YZ_slice_number = int(self.YZspinBox.value())
            #print('slice the B0M data by XY plane, get slice number %d'%XY_slice_number)
            self.plotter.plotB0Map(b0map_object=self.b0map, slice_number=YZ_slice_number, coordinate_system='magnet',slice_axis='X')




    def change_coords_to_magnet(self):
        self.b0map.transfer_coordinates_of_the_path_from_cosi_to_magnet()
        self.plotter.plotPathWithMagnet(self.b0map,coordinate_system='magnet')
        
        
        # foolproof checkboxes        
        print(len(self.b0map.zPts))
        
        self.XYspinBox.setMaximum(len(self.b0map.zPts)-1)     
        self.XYspinBox.setValue(round((len(self.b0map.zPts)-1)/2))        
        self.XYspinBox.valueChanged.connect(self.plot_B0M_slice_Z)
        
        print(len(self.b0map.yPts))
        
        self.ZXspinBox.setMaximum(len(self.b0map.yPts)-1)     
        self.ZXspinBox.setValue(round((len(self.b0map.yPts)-1)/2))        
        self.ZXspinBox.valueChanged.connect(self.plot_B0M_slice_Y)

        print(len(self.b0map.yPts))
        
        self.YZspinBox.setMaximum(len(self.b0map.xPts)-1)     
        self.YZspinBox.setValue(round((len(self.b0map.xPts)-1)/2))        
        self.YZspinBox.valueChanged.connect(self.plot_B0M_slice_X)

        
        
        #self.plotter.plotB0Map(self.b0map,slice_number=0,coordinate_system='magnet')
        


    def save_rotated_path(self):
        print('save as file dialog etc, think of the format, Be compatible with the future imports')
        # open file dialog
        try:
            new_path_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="Select path data",
                                                                   directory=self.workingFolder,
                                                                   filter="path Files (*.path)")
            self.workingFolder = os.path.split(os.path.abspath(self.pathPath))[0]

        except:
            print('no filename given, do it again.')
            return 0
        self.b0map.path.saveAs(new_path_path)
