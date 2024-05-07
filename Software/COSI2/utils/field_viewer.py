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
        self.save_button.clicked.connect(self.save_rotated_path_in_a_csv_file)  # Remember to code the method in the class.
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
        self.XYcheckBox.stateChanged.connect(self.plot_B0M_slice)
        self.ZXcheckBox.stateChanged.connect(self.plot_B0M_slice)
        self.YZcheckBox.stateChanged.connect(self.plot_B0M_slice)
        self.ShowSphereCheckBox.stateChanged.connect(self.plot_B0M_slice)
        

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
        

    def plot_B0M_slice(self):
        # get the ticks
        plot_XY_sliceFlag = self.XYcheckBox.isChecked()
        plot_ZX_sliceFlag = self.ZXcheckBox.isChecked()
        plot_YZ_sliceFlag = self.YZcheckBox.isChecked()
        plot_sphere_flag = self.ShowSphereCheckBox.isChecked()
        
        XY_slice_number = int(self.XYspinBox.value()) if plot_XY_sliceFlag else -1
        ZX_slice_number = int(self.ZXspinBox.value()) if plot_ZX_sliceFlag else -1
        YZ_slice_number = int(self.YZspinBox.value()) if plot_YZ_sliceFlag else -1
        showSphRad = self.b0map.path.radius if plot_sphere_flag else None
        
        # plot the slices according to the checked boxes
        self.plotter.plotB0Map(b0map_object=self.b0map, 
                               slice_number_xy=XY_slice_number,slice_number_zx=ZX_slice_number,slice_number_yz=YZ_slice_number, 
                               show_sphere_radius=showSphRad, coordinate_system='magnet')
        



    def change_coords_to_magnet(self):
        self.b0map.transfer_coordinates_of_the_path_from_cosi_to_magnet()
        self.plotter.plotPathWithMagnet(self.b0map,coordinate_system='magnet')
        
        
        # foolproof checkboxes        
        print(len(self.b0map.zPts))
        
        self.XYspinBox.setMaximum(len(self.b0map.zPts)-1)     
        self.XYspinBox.setValue(round((len(self.b0map.zPts)-1)/2))        
        self.XYspinBox.valueChanged.connect(self.plot_B0M_slice)
        
        print(len(self.b0map.yPts))
        
        self.ZXspinBox.setMaximum(len(self.b0map.yPts)-1)     
        self.ZXspinBox.setValue(round((len(self.b0map.yPts)-1)/2))        
        self.ZXspinBox.valueChanged.connect(self.plot_B0M_slice)

        print(len(self.b0map.yPts))
        
        self.YZspinBox.setMaximum(len(self.b0map.xPts)-1)     
        self.YZspinBox.setValue(round((len(self.b0map.xPts)-1)/2))        
        self.YZspinBox.valueChanged.connect(self.plot_B0M_slice)

        
        
        #self.plotter.plotB0Map(self.b0map,slice_number=0,coordinate_system='magnet')
        


    def save_rotated_path_in_a_csv_file(self):
        print('save as file dialog etc, think of the format, Be compatible with the future imports')
        # open file dialog
        try:
            new_csv_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, caption="file name for csv export",
                                                                   directory=self.workingFolder,
                                                                   filter="comma separated Files (*.csv)")
            self.workingFolder = os.path.split(os.path.abspath(self.pathPath))[0]

        except:
            print('no filename given, do it again.')
            return 0
        
        self.b0map.saveAsCsv_for_comsol(new_csv_path)
        #self.b0map.path.saveAs(new_csv_path)
