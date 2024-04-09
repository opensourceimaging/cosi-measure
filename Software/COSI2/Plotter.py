'''
    Ilia Kulikov
    16 June 2022
    ilia.kulikov@fu-berlin.de
plotter.
matplotlib based.
mpl window is imbedded into the parent that has to be passed to the constructor.
    '''

import matplotlib
import numpy

import chg
import cv
import tp
import pth

import cosimeasure # for plotting path irl
import osi2magnet


matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
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

    def __init__(self, plotType:str):
        self.plotType = plotType # assign and dont worry anymore!
        fig = Figure(figsize=(16, 16), dpi=100)
        if plotType == 'PTH':
            self.axes = fig.add_subplot(111,projection='3d')
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
        self.xlabel = 'X'
        self.ylabel = 'Y'
        self.zlabel = 'Z'
        self.title = 'dummy path'
        pthDummy = pth.pth('./dummies/pathfiles/2021-10-14_PathfileTest_Spherical.path')
        self.plotPth(pthDummy)
        
    def plot_magnet(self,magnet:osi2magnet):
        print('plotting a magnet with radius ',magnet.bore_radius,' at',magnet.origin)

        magnet_origin  = magnet.origin
        xvec = magnet.xvector
        yvec = magnet.yvector
        zvec = magnet.zvector
        


        self.axes.quiver(magnet_origin[0],magnet_origin[1],magnet_origin[2], xvec[0], xvec[1], xvec[2], color='r')
        self.axes.quiver(magnet_origin[0],magnet_origin[1],magnet_origin[2], yvec[0], yvec[1], yvec[2], color='g')
        self.axes.quiver(magnet_origin[0],magnet_origin[1],magnet_origin[2], zvec[0], zvec[1], zvec[2], color='b')
        
        self.axes.plot(magnet.bore_X,magnet.bore_Y,magnet.bore_Z,zdir='z',label='magnet front')

        #todo: make osi2magnet class and plot here the damn cylinder. with the axes!

    def plot_head_on_path(self,cosimeasure: cosimeasure.cosimeasure):
        xheadpos = cosimeasure.head_position[0]
        yheadpos = cosimeasure.head_position[1]
        zheadpos = cosimeasure.head_position[2]

        
        pathInput = cosimeasure.path
        xpathvalues = pathInput.x
        ypathvalues = pathInput.y
        zpathvalues = pathInput.z
        self.title = 'head at [%.2f %.2f %.2f] '%(xheadpos,yheadpos,zheadpos)

        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_zlabel(self.zlabel)        
        self.axes.set_title(self.title)
        dummy_magnet = osi2magnet.osi2magnet()
        self.plot_magnet(dummy_magnet)
        self.axes.plot(xpathvalues,ypathvalues,zpathvalues,'ko--')
        self.axes.plot(xheadpos,yheadpos,zheadpos,'gx',linewidth=5)
        self.axes.autoscale(True)
        self.update_plotter()


    def plotPth(self,pathInput: pth.pth):
        xvalues = pathInput.x
        yvalues = pathInput.y
        zvalues = pathInput.z

        self.axes.cla()
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)
        self.axes.set_zlabel(self.zlabel)        
        self.axes.set_title(self.title)
        self.axes.plot(xvalues,yvalues,zvalues,'k+:')
        self.axes.autoscale(True)
        self.update_plotter()


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



    def update_plotter(self): # very useful and important method for live plotting.
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