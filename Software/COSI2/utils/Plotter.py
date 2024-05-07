'''
    Ilia Kulikov
    16 June 2022
    ilia.kulikov@fu-berlin.de
plotter.
matplotlib based.
mpl window is imbedded into the parent that has to be passed to the constructor.
    '''

import matplotlib
import numpy as np

import chg
import cv
import tp
import pth
import b0

import cosimeasure # for plotting path irl
import osi2magnet


matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSizePolicy, QVBoxLayout
from PyQt5.QtWidgets import QWidget


class PlotterCanvas(FigureCanvas):
    '''Plotter based on FigureCanvasQTAgg'''
    xlabel = 'pirates'
    ylabel = 'crocodiles'
    title = 'ultimate grapfh'
    parent = None # parent widget, [have to] pass it on construction for live updates
    plotType = 'GEN' # available: 'GEN,CV,CHG,EPR,TP'
    fig = Figure

    def __init__(self, plotType:str):
        self.plotType = plotType # assign and dont worry anymore!
        self.fig = Figure(figsize=(16, 16), dpi=100)
        fig = self.fig

        if plotType == 'PTH' or plotType == 'B0M':
            self.axes = fig.add_subplot(111,projection='3d')
            self.axes.set_aspect("equal")
            self.axes.set_proj_type('persp', focal_length=0.42)  # FOV = 157.4 deg
            self.axes.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.axes.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            self.axes.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

            fig.subplots_adjust(left=0.1,right=0.9,
                            bottom=0.1,top=0.9,
                            hspace=0.2,wspace=0.2)
        else:
            self.axes = fig.add_subplot(111)
#        fig.subplots_adjust(left = 0.18, right=0.99, top=0.94, bottom=0.1)

        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        if plotType == 'TP': # if a tunepicture plotter:
            tightrect = (0.01,0.06,0.99,1)
            self.axes.set_yticks([])
        else:
            tightrect = (0.16, 0.1, 0.99, 0.9)

        fig.tight_layout(rect = tightrect)
        self.compute_initial_figure()

    def parent(self):
        return QWidget()

    def clear(self):
        self.axes.cla()

    def set_title(self,title:str):
        self.title = title
        self.axes.set_title(title)
        self.update_plotter()

    def compute_initial_figure(self):
        self.clear()
        if self.plotType == 'GEN':
            pass
        if self.plotType == 'CV':
            self.preset_CV()
        if self.plotType == 'CHG':
            self.preset_CHG()
        if self.plotType == 'EPR':
            self.preset_EPR()
        if self.plotType == 'TP':
            self.preset_TP()
        if self.plotType == 'PTH':
            self.preset_PTH()
        if self.plotType == 'B0M':
            self.preset_B0M()
        

        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(self.title)


    def preset_CV(self):
        self.clear()
        self.xlabel = 'Volttage [V]'
        self.ylabel = 'Current [A]'
        self.title = 'CV'
        self.axes.grid()

        # plot sample cv
        cvDummy = cv.cv('./dummies/DEPOSITION_DEMO.csv')
        self.plotCv(cvDummy)


    def preset_CHG(self):
        self.clear()
        self.xlabel = 'Time [s]'
        self.ylabel = 'Voltage [V]'
        self.title = 'CHG'
        self.axes.grid()
        chgDummy = chg.chg('./dummies/lipton_4_CHG_DCG.csv')
        self.plotChg(chgDummy)

    def preset_TP(self):
        self.clear()
        self.xlabel = '$\Delta$ f [MHz]'
        self.ylabel = ''
        self.title = ''
        self.axes.set_yticks([])
        tpDummy = tp.tp('./dummies/TP.csv') #TP!
        self.plotTpData(tpDummy)


    def preset_PTH(self):
        self.clear()
        self.xlabel = 'X COSI'
        self.ylabel = 'Y COSI'
        self.zlabel = 'Z COSI'
        self.title = 'dummy path'
        pthDummy = pth.pth('./dummies/pathfiles/2021-10-14_PathfileTest_Spherical.path')
        self.plotPth(pthDummy)
        
        
    def preset_B0M(self):
        self.clear()
        self.xlabel = 'X MAGNET'
        self.ylabel = 'Y MAGNET'
        self.zlabel = 'Z MAGNET'
        self.title = 'dummy B0 map'
        b0Dummy = b0.b0(b0_filename='./dummies/b0_maps/a00_ball_R80mm_bvalues_coarse_5s_FAST.txt',path_filename='./dummies/pathfiles/2021-10-14_PathfileTest_Spherical.path')
        b0Dummy.magnet.set_origin(0,0,0)
        b0Dummy.path.center(origin=b0Dummy.magnet.origin)
        self.plotPathWithMagnet(b0map_object=b0Dummy)
        
        
    def plot_magnet(self,magnet:osi2magnet):
        print('plotting a magnet with radius ',magnet.bore_radius,' at',magnet.origin)

        magnet_origin  = magnet.origin
        xvec = magnet.xvector
        yvec = magnet.yvector
        zvec = magnet.zvector
        

        self.axes.quiver(magnet_origin[0],magnet_origin[1],magnet_origin[2], xvec[0]-magnet_origin[0], xvec[1]-magnet_origin[1], xvec[2]-magnet_origin[2], color='r')
        self.axes.quiver(magnet_origin[0],magnet_origin[1],magnet_origin[2], yvec[0]-magnet_origin[0], yvec[1]-magnet_origin[1], yvec[2]-magnet_origin[2], color='g')
        self.axes.quiver(magnet_origin[0],magnet_origin[1],magnet_origin[2], zvec[0]-magnet_origin[0], zvec[1]-magnet_origin[1], zvec[2]-magnet_origin[2], color='b')
        
        #self.axes.plot(magnet.bore_front_X,magnet.bore_front_Y,magnet.bore_front_Z,zdir='z',label='magnet front')
        #self.axes.plot(magnet.bore_back_X,magnet.bore_back_Y,magnet.bore_back_Z,zdir='z',label='magnet back')
        

        #todo: make osi2magnet class and plot here the damn cylinder. with the axes!

    def plot_head_on_path(self,cosimeasure: cosimeasure.cosimeasure,magnet:osi2magnet.osi2magnet):
        xheadpos = cosimeasure.head_position[0]
        yheadpos = cosimeasure.head_position[1]
        zheadpos = cosimeasure.head_position[2]

        
        pathInput = cosimeasure.path
        r = pathInput.r
        self.title = 'head at [%.2f %.2f %.2f] '%(xheadpos,yheadpos,zheadpos)

        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_zlabel(self.zlabel)        
        self.axes.set_title(self.title)
        self.plot_magnet(magnet)
        self.axes.plot(r[:,0],r[:,1],r[:,2],'ko--')
        self.axes.plot(xheadpos,yheadpos,zheadpos,'gx',linewidth=5)
        self.axes.autoscale(True)
        self.update_plotter()




    def plotPathWithMagnet(self,b0map_object:b0.b0,coordinate_system=None):
        self.axes.cla()
        self.xlabel = 'X COSI /tmp'
        self.ylabel = 'Y COSI /tmp'
        self.zlabel = 'Z COSI /tmp'
        if coordinate_system == 'magnet':
            self.xlabel = 'X magnet'
            self.ylabel = 'Y magnet'
            self.zlabel = 'Z magnet'

        self.axes.set_title(str(b0map_object.datetime))
        pth = b0map_object.path
        self.plotPth(pathInput=pth)
        self.plot_magnet(b0map_object.magnet)
        self.update_plotter()
        
    
    def plotB0Map(self,b0map_object:b0.b0,slice_number_xy=-1,slice_number_zx=-1,slice_number_yz=-1, show_sphere_radius = None, coordinate_system=None):
        # plot only one slice of data. Slice at the middle of the scan
        self.axes.cla()
        
        self.xlabel = 'X COSI /tmp'
        self.ylabel = 'Y COSI /tmp'
        self.zlabel = 'Z COSI /tmp'
        if coordinate_system == 'magnet':
            self.xlabel = 'X magnet'
            self.ylabel = 'Y magnet'
            self.zlabel = 'Z magnet'
        
        if show_sphere_radius is not None:
            u = np.linspace(0, 2 * np.pi, 100)
            v = np.linspace(0, np.pi, 100)
            x = show_sphere_radius * np.outer(np.cos(u), np.sin(v))
            y = show_sphere_radius * np.outer(np.sin(u), np.sin(v))
            z = show_sphere_radius * np.outer(np.ones(np.size(u)), np.cos(v))
            self.axes.plot_wireframe(x, y, z,alpha=0.1)

        
        # plot the coordinate mesh for beginning
        
        minval_of_b0 = np.nanmin(b0map_object.b0Data[:,:,:,1])
        maxval_of_b0 = np.nanmax(b0map_object.b0Data[:,:,:,1])
        
        print(minval_of_b0,maxval_of_b0,' = minvals')
        nlevels = 128

        if slice_number_xy >= 0:
            # if slice number xy given, plot Z slice

            x, y = np.meshgrid(b0map_object.xPts, b0map_object.yPts)
            z = b0map_object.zPts[slice_number_xy]#np.transpose(np.ones((len(b0map_object.xPts), len(b0map_object.yPts)))*b0map_object.zPts[slice_number_xy])
        
            vals = np.transpose(b0map_object.b0Data[:,:,slice_number_xy,1])
        
            
            self.axes.contourf(x,y,vals, offset = z, zdir = 'z', alpha=0.5,cmap='coolwarm',edgecolor='black',vmin = minval_of_b0, vmax = maxval_of_b0,levels=nlevels)
 
            #self.axes.set_zlim(min(b0map_object.zPts), max(b0map_object.zPts))


        if slice_number_zx >= 0:
            # if slice number zx given, plot Y slice

            z,x = np.meshgrid(b0map_object.xPts, b0map_object.zPts)      
            y = b0map_object.yPts[slice_number_zx]#np.transpose(np.ones((len(b0map_object.xPts), len(b0map_object.zPts)))*b0map_object.yPts[slice_number_zx])
        
            vals = b0map_object.b0Data[:,slice_number_zx,:,1]
            
        
            
            self.axes.contourf(x,vals,z,zdir = 'y', offset = y, alpha=0.5,cmap='coolwarm',edgecolor='black',vmin = minval_of_b0, vmax = maxval_of_b0,levels=nlevels)
            #self.axes.set_ylim(min(b0map_object.yPts), max(b0map_object.yPts))
            
        
        if slice_number_yz >= 0:
            # if slice number yz given, plot X slice
            
            y,z = np.meshgrid(b0map_object.yPts, b0map_object.zPts)
        
            x = b0map_object.xPts[slice_number_yz]#np.transpose(np.ones((len(b0map_object.yPts), len(b0map_object.zPts)))*b0map_object.xPts[slice_number_yz])
        
            vals = np.transpose(b0map_object.b0Data[slice_number_yz,:,:,1])
        
            #self.axes.plot_surface(x+vals,y,z,alpha=0.5,cmap='viridis',edgecolor='black',vmin = minval_of_b0+x, vmax = maxval_of_b0+x)
            self.axes.contourf(vals,y,z,zdir = 'x', offset = x, alpha=0.5,cmap='coolwarm',edgecolor='black',vmin = minval_of_b0, vmax = maxval_of_b0,levels=nlevels)
            
        #self.figure.show()
        #self.figure.canvas.draw()
        
        
        self.axes.set_xlim(min(b0map_object.xPts), max(b0map_object.xPts))
        self.axes.set_ylim(min(b0map_object.yPts), max(b0map_object.yPts))
        self.axes.set_zlim(min(b0map_object.zPts), max(b0map_object.zPts))
        
        # todo scale colormaps to one value
        
        
        # if len(self.axes) > 1:
        #     cax = self.axes[-1]    
        #  # remove the previous colorbar, if present
        # if cax is not None:
        #     cax.clear()

        #     norm = Normalize(vmin = minval_of_b0, vmax = maxval_of_b0)
        
        #     mappable = ScalarMappable(cmap='viridis', norm=norm)
        #     self.fig.colorbar(mappable, orientation="vertical", label="B0 [mT]", cax=cax)
                
        self.update_plotter()
        
        

    def plotPth(self,pathInput: pth.pth):
        r = pathInput.r
        
        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_zlabel(self.zlabel)        
        self.axes.set_title(self.title)
        self.axes.plot(r[:,0],r[:,1],r[:,2],'k+:')
        self.axes.autoscale(True)
        self.update_plotter()



    # EMRE electrochemistry
    def plotCvData(self, voltages, currents):
        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(self.title)
        self.axes.plot(voltages, currents, 'm+:', linewidth=1)
        self.axes.plot(voltages[-1], currents[-1], 'kx:', linewidth=5)
        self.axes.autoscale(True)
        self.update_plotter()

    def plotChg(self, chgInput: chg.chg):
        xValues = chgInput.time
        yValues = chgInput.voltage
        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(chgInput.filename)
        self.axes.plot(xValues, yValues,'o:')
        self.axes.plot(xValues[-1], yValues[-1], 'kx:', linewidth=5)
        self.axes.autoscale(True)
        self.axes.grid()
        self.update_plotter()
        
    def plotCv(self,cvToPlot:cv):
        voltages = cvToPlot.voltage
        currents = cvToPlot.current
        self.title = cvToPlot.filename

        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(self.title)
        self.axes.plot(voltages, currents, 'k-', linewidth=1)
        self.axes.autoscale(True)
        self.update_plotter()

    # EMRE Microwave
    def plotTpData(self,tpToPlot:tp):
        times = tpToPlot.time
        frequencies = tpToPlot.frequency
        tunepic = tpToPlot.tunepicture
        self.title = ''
        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(self.title)
        self.axes.plot(frequencies, tunepic, 'k-', linewidth=1)
        self.axes.autoscale(True)
        self.update_plotter()

    def plotTpFitData(self,tpToPlot:tp):
        frequencies = tpToPlot.frequencyFit
        tunepicFit = tpToPlot.tunepicFit
        
        self.title = ''
        #self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_title(self.title)
        # self.axes.plot(dipFreqtpToPlot.dipFreq, tpToPlot.dip, 'r-', linewidth=2) # dip without bg
        self.axes.plot(frequencies, tunepicFit, 'g--', linewidth=2)  # fit

        self.axes.autoscale(True)
        self.update_plotter()



    def update_plotter(self): # very useful and important method for live plotting.
        if self.plotType == 'PTH' or self.plotType == 'B0M' :
            self.fig.subplots_adjust(left=0.0,right=1.0,
                            bottom=0.0,top=1.0,
                            hspace=0.0,wspace=0.0)
            
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_zlabel(self.zlabel) 
        self.axes.set_title(self.title)
        self.figure.canvas.draw()
        #self.figure.canvas.flush_events()



    # a widget class to implement the toolbar
class Plotter(QWidget):
    plotType = 'general' # can be EPR, TP, CV and CHG plotType
    def __init__(self, parent, plotType, *args, **kwargs): # you have to pass the main window here, else crashes on click save
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.PlotterCanvas = PlotterCanvas(plotType = plotType) # Plotter is a class defined above. plotType defines which plotter to be created ('CV,CHG,EPR,TP')

        # navigation toolbar
        self.toolbar = NavigationToolbar(self.PlotterCanvas, parent = self)

        '''custom buttons on navigation toolbar'''
        # self.toolbar.clear()
        #
        # a = self.toolbar.addAction(self.toolbar._icon("home.png"), "Home", self.toolbar.home)
        # # a.setToolTip('returns axes to original position')
        # a = self.toolbar.addAction(self.toolbar._icon("move.png"), "Pan", self.toolbar.pan)
        # a.setToolTip("Pan axes with left mouse, zoom with right")
        # a = self.toolbar.addAction(self.toolbar._icon("zoom_to_rect.png"), "Zoom", self.toolbar.zoom)
        # a.setToolTip("Zoom to Rectangle")
        # a = self.toolbar.addAction(self.toolbar._icon("filesave.png"), "Save", self.toolbar.save_figure)
        # a.setToolTip("Save the figure")

        def save_figure():
            print('SAVE THE DATA! - write that method in your free time')

        a = self.toolbar.addAction(self.toolbar._icon("filesave.png"), "Save data", save_figure)
        a.setToolTip("Save data in file")


        'insert plotter'
        self.layout().addWidget(self.PlotterCanvas)
        'insert toolbar'
        self.layout().addWidget(self.toolbar)