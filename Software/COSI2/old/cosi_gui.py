import sys
from socket import *
import time
import atexit
import serial
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

sock = socket(AF_UNIX, SOCK_STREAM)
packet_size = 30
serPort = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS
)


class Container(QtGui.QX11EmbedContainer):

    def __init__(self):
        QtGui.QX11EmbedContainer.__init__(self)

    def sizeHint(self):
        size = QtCore.QSize(400, 500)
        return size.expandedTo(QtGui.QApplication.globalStrut())
        
class ExeMeasureThread(QtCore.QThread):

    signalCom = QtCore.pyqtSignal(object)

    def __init__(self, filename):
        QtCore.QThread.__init__(self)
        self.filename = filename

    def run(self):
        num_lines = sum(1 for line in open(self.filename))
        fin_lines = 0.0
        with open(self.filename) as coordinates:
            for line in coordinates:
                self.move_to(line)
                self.wait_for_completion()
                value = self.read_gaussmeter()
                fin_lines += 1
                self.signalCom.emit(((fin_lines/num_lines)*100, value))
        
    def wait_for_completion(self):
	sock.send("check_status" + ("\0" * (packet_size-len("check_status"))))
	msg = sock.recv(50)
	#print msg
	while msg == "busy":
	    sock.send("check_status" + ("\0" * (packet_size-len("check_status"))))
	    msg = sock.recv(50)
	    #print msg
	    time.sleep(0.1)
	
    def move_to(self, coordinates):
        G_CMD = "G0" + coordinates + "\n"
        sock.send(G_CMD + ("\0" * (packet_size-len(G_CMD))))

    def read_gaussmeter(self):
        serPort.write("ALLF?")
        value = ''
        time.sleep(0.2)
        while serPort.inWaiting() > 0:
            value += serPort.read(1)
        if value != '':
            print ">>" + value
            return value
        
        
class Main(QtGui.QMainWindow):

    def __init__(self):
        super(Main, self).__init__()
        self.initUI()

    def initUI(self):
        self.frameSysIni = QtGui.QFrame()
        self.frameSysIni.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameHoming = QtGui.QFrame()
        self.frameHoming.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameMoving = QtGui.QFrame()
        self.frameMoving.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameMeasure = QtGui.QFrame()
        self.frameMeasure.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameConsole = QtGui.QFrame()
        self.frameConsole.setFrameShape(QtGui.QFrame.StyledPanel)
        self.outputText = QtGui.QTextEdit()
        #self.frameOutput = QtGui.QFrame()
        #self.frameOutput.setFrameShape(QtGui.QFrame.StyledPanel)

        self.splitterVLeft = QtGui.QSplitter(Qt.Vertical)
        self.splitterVLeft.addWidget(self.frameSysIni)
        self.splitterVLeft.addWidget(self.frameHoming)
        self.splitterVLeft.addWidget(self.frameMoving)
        self.splitterVLeft.addWidget(self.frameMeasure)
        self.splitterVLeft.setSizes([200,150,150,300])
        self.splitterVRight = QtGui.QSplitter(Qt.Vertical)
        self.splitterVRight.addWidget(self.frameConsole)
        #self.splitterVRight.addWidget(self.frameOutput)
        self.splitterVRight.addWidget(self.outputText)
        self.splitterVRight.setSizes([400,400])
        self.splitterH = QtGui.QSplitter(Qt.Horizontal)
        self.splitterH.addWidget(self.splitterVLeft)
        self.splitterH.addWidget(self.splitterVRight)
        self.splitterH.setSizes([500,500])
        self.setCentralWidget(self.splitterH)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))

        font11 = QtGui.QFont()
        font11.setPointSize(11)
        font11.setBold(True)
        font11.setUnderline(True)
        font11.setWeight(75)
        font10 = QtGui.QFont()
        font10.setPointSize(10)

        self.lableIni = QtGui.QLabel('System Initialization')
        self.lableIni.setGeometry(QtCore.QRect(10, 10, 150, 20))
        self.lableIni.setFont(font11)
        self.lableStatusController = QtGui.QLabel('Movement controller')
        self.lableStatusController.setGeometry(QtCore.QRect(310, 50, 20, 20))
        self.lableStatusController.setFont(font10)
        self.lableStatusSerial = QtGui.QLabel('Serial port')
        self.lableStatusSerial.setGeometry(QtCore.QRect(30, 80, 100, 30))
        self.lableStatusSerial.setFont(font10)
        self.pushButtonIni = QtGui.QPushButton('Initialize')
        self.pushButtonIni.setGeometry(QtCore.QRect(30, 80, 100, 30))
        self.frameStatusController = QtGui.QFrame()
        self.frameStatusController.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameStatusController.setFrameShadow(QtGui.QFrame.Raised)
        self.frameStatusSerial = QtGui.QFrame()
        self.frameStatusSerial.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameStatusSerial.setFrameShadow(QtGui.QFrame.Raised)
        self.gridLayoutSysIni = QtGui.QGridLayout()
        self.gridLayoutSysIni.addWidget(self.lableIni, 0, 0, 1, 3)
        self.gridLayoutSysIni.addWidget(self.lableStatusController, 1, 3, 1, 1)
        self.gridLayoutSysIni.addWidget(self.lableStatusSerial, 3, 3, 1, 1)
        self.gridLayoutSysIni.addWidget(self.frameStatusSerial, 3, 5, 1, 1)
        self.gridLayoutSysIni.addWidget(self.frameStatusController, 1, 5, 1, 1)
        self.gridLayoutSysIni.addWidget(self.pushButtonIni, 2, 1, 1, 1)
        self.frameSysIni.setLayout(self.gridLayoutSysIni)

        self.pushButtonIni.clicked.connect(self.sys_ini)


        self.lableHoming = QtGui.QLabel('Homing')
        self.lableHoming.setFont(font11)
        self.lableHomingStatus = QtGui.QLabel('Homing status')
        self.lableHomingStatus.setFont(font10)
        self.pushButtonHoming = QtGui.QPushButton('Home')
        self.frameStatusHoming = QtGui.QFrame()
        self.frameStatusHoming.resize(20,20)
        self.frameStatusHoming.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameStatusHoming.setFrameShadow(QtGui.QFrame.Raised)
        self.spacerItem1 = QtGui.QSpacerItem(379, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.spacerItem2 = QtGui.QSpacerItem(20, 48, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayoutHoming = QtGui.QGridLayout()
        self.gridLayoutHoming.addWidget(self.lableHoming, 0, 0, 1, 1)
        self.gridLayoutHoming.addWidget(self.lableHomingStatus, 3, 2, 1, 1)
        self.gridLayoutHoming.addWidget(self.pushButtonHoming, 3, 0, 1, 1)
        self.gridLayoutHoming.addWidget(self.frameStatusHoming, 3, 3, 1, 1)
        self.gridLayoutHoming.addItem(self.spacerItem1, 1, 0, 2, 4)
        self.gridLayoutHoming.addItem(self.spacerItem2, 2, 1, 2, 1)
        self.frameHoming.setLayout(self.gridLayoutHoming)
        
        self.pushButtonHoming.clicked.connect(self.homing)


        self.lableMove = QtGui.QLabel('Move to a point and measure')
        self.lableMove.setFont(font11)
        self.lableMoveTo = QtGui.QLabel('Move to:')
        self.lableMoveTo.setFont(font10)
        self.lineEditCoordinates = QtGui.QLineEdit()
        self.pushButtonExeMove = QtGui.QPushButton('Execute')
        self.spacerItem3 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayoutMove = QtGui.QGridLayout()
        self.gridLayoutMove.addWidget(self.lableMove, 0, 0, 1, 2)
        self.gridLayoutMove.addWidget(self.lableMoveTo, 2, 0, 1, 1)
        self.gridLayoutMove.addWidget(self.lineEditCoordinates, 2, 1, 1, 1)
        self.gridLayoutMove.addWidget(self.pushButtonExeMove, 2, 3, 1, 1)
        self.gridLayoutMove.addItem(self.spacerItem3, 2, 2, 1, 1)
        self.gridLayoutMove.addItem(self.spacerItem4, 1, 0, 1, 1)
        self.frameMoving.setLayout(self.gridLayoutMove)
        
        self.pushButtonExeMove.clicked.connect(self.ExeMove)
        

        self.lableMeasure = QtGui.QLabel('Move along a path and measure')
        self.lableMeasure.setFont(font11)
        self.lableLoadFile = QtGui.QLabel('Load path file:')
        self.lableLoadFile.setFont(font10)
        self.lableSaveFile = QtGui.QLabel('Save data as:')
        self.lableSaveFile.setFont(font10)        
        self.lableFileName1 = QtGui.QLabel('')
        self.lableFileName1.setFont(font10)
        self.lableFileName2 = QtGui.QLabel('')
        self.lableFileName2.setFont(font10)
        iconOpenFile = QtGui.QIcon()
        iconOpenFile.addPixmap(QtGui.QPixmap('open.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonOpenFile = QtGui.QPushButton('')
        self.pushButtonOpenFile.setIcon(iconOpenFile)
        self.pushButtonSaveFile = QtGui.QPushButton('')
        self.pushButtonSaveFile.setIcon(iconOpenFile)        
        self.pushButtonExeMeasure = QtGui.QPushButton('Execute')
        self.pushButtonStopMeasure = QtGui.QPushButton('Stop')
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setProperty("value", 0)
        self.spacerItem5 = QtGui.QSpacerItem(127, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.spacerItem6 = QtGui.QSpacerItem(81, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.spacerItem7 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        self.spacerItem8 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self.spacerItem9 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.spacerItem10 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        #spacerItem11 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayoutMeasure = QtGui.QGridLayout()
        self.gridLayoutMeasure.addWidget(self.lableMeasure, 0, 0, 1, 2)
        self.gridLayoutMeasure.addItem(self.spacerItem8, 1, 0, 1, 1)        
        self.gridLayoutMeasure.addWidget(self.lableLoadFile, 2, 0, 1, 1)
        self.gridLayoutMeasure.addWidget(self.pushButtonOpenFile, 2, 1, 1, 1)        
        self.gridLayoutMeasure.addWidget(self.lableFileName1, 2, 2, 1, 1)
        self.gridLayoutMeasure.addWidget(self.lableSaveFile, 3, 0, 1, 1)
        self.gridLayoutMeasure.addWidget(self.pushButtonSaveFile, 3, 1, 1, 1)        
        self.gridLayoutMeasure.addWidget(self.lableFileName2, 3, 2, 1, 1)
        self.gridLayoutMeasure.addWidget(self.pushButtonExeMeasure, 4, 0, 1, 1)
        self.gridLayoutMeasure.addWidget(self.pushButtonStopMeasure, 4, 1, 1, 1)
        self.gridLayoutMeasure.addItem(self.spacerItem6, 4, 2, 1, 1)
        self.gridLayoutMeasure.addItem(self.spacerItem5, 4, 3, 1, 1)
        self.gridLayoutMeasure.addItem(self.spacerItem7, 5, 0, 1, 1)
        self.gridLayoutMeasure.addWidget(self.progressBar, 6, 0, 1, 4)
        self.gridLayoutMeasure.addItem(self.spacerItem9, 7, 0, 1, 1)
        #self.gridLayoutMeasure.addItem(self.spacerItem10, 3, 0, 1, 1)
        #gridLayoutMeasure.addItem(spacerItem11, 2, 3, 1, 2)
        self.frameMeasure.setLayout(self.gridLayoutMeasure)
        
        self.pushButtonOpenFile.clicked.connect(self.getOpenFileName)
        self.pushButtonSaveFile.clicked.connect(self.getSaveFileName)
        self.pushButtonExeMeasure.clicked.connect(self.ExeMeasure)
        self.pushButtonExeMeasure.clicked.connect(self.StopMeasure)
        
        self.console = Container()
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(self.console)
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addStretch(1)
        self.vbox.addLayout(self.hbox)
        self.frameConsole.setLayout(self.vbox)
        
        self.setGeometry(100,100,1000,800)
        self.setWindowTitle("COSI-Measure")
        self.show()
        
    def sys_ini(self):
        wid=QtCore.QString.number(self.console.winId())
        self.process = QtCore.QProcess(self)
        args = [
            "-into",
            wid,
            "-bc",
            "-e",
            "\"./mendel.elf\"",
        ]
        self.process.start("xterm", args)
        time.sleep(7)
        socketStatus = sock.connect_ex("/tmp/socket") 
        if socketStatus == 0:
            self.frameStatusController.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(0, 255, 0).name())
        else:
	    self.frameStatusController.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(255, 0, 0).name())

	if(serPort.isOpen() == False):
            self.frameStatusSerial.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(255, 0, 0).name())
        else:
	    self.frameStatusSerial.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(0, 255, 0).name())        

    def homing(self):
	sock.send("G161XYZ\n" + ("\0" * (packet_size-len("G161XYZ\n"))))
	sock.send("G161XYZ\n" + ("\0" * (packet_size-len("G161XYZ\n"))))
	sock.send("G162XYZ\n" + ("\0" * (packet_size-len("G162XYZ\n"))))
	sock.send("G162XYZ\n" + ("\0" * (packet_size-len("G162XYZ\n"))))
	self.wait_for_completion()
	self.frameStatusHoming.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(0, 255, 0).name())
	
    def wait_for_completion(self):
	sock.send("check_status" + ("\0" * (packet_size-len("check_status"))))
	msg = sock.recv(50)
	#print msg
	while msg == "busy":
	    sock.send("check_status" + ("\0" * (packet_size-len("check_status"))))
	    msg = sock.recv(50)
	    #print msg
	    time.sleep(1)
	    
    def ExeMove(self):
        coordinates = str(self.lineEditCoordinates.text())
        self.move_to(coordinates)
	self.wait_for_completion()
	value = self.read_gaussmeter()
	cursor = self.outputText.textCursor() 
	cursor.insertText(value)
	
    def move_to(self, coordinates):
        G_CMD = "G0" + coordinates + "\n"
        sock.send(G_CMD + ("\0" * (packet_size-len(G_CMD))))

    def read_gaussmeter(self):
        serPort.write("ALLF?")
        value = ''
        time.sleep(1)
        while serPort.inWaiting() > 0:
            value += serPort.read(1)
        if value != '':
            print ">>" + value
            return value
        
    def getOpenFileName(self):
        self.filenameOpen = QtGui.QFileDialog.getOpenFileName(self, 'Open File',".","(*.path)")
        self.lableFileName1.setText(self.filenameOpen)
        
    def getSaveFileName(self):
        self.filenameSave = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        self.lableFileName2.setText(self.filenameSave)
        
    def ExeMeasure(self):
        worker = ExeMeasureThread(self.filenameOpen)
        worker.signalCom.connect(self.onDataReady)
        self.threads = []
        self.threads.append(worker)
        worker.start()
        
        
    def onDataReady(self, value):
        cursor = self.outputText.textCursor() 
        cursor.insertText(value[1])
        with open(self.filenameSave,"a") as dataFile:
            dataFile.write(value[1])
        self.progressBar.setValue(value[0])
        
    def StopMeasure(self):
        pass
        
    def finish(self):
        sock.send("quit"+ ("\0" * (packet_size-len("quit"))))
        sock.close()
        print 'finished\n'
    
def main():
    app = QtGui.QApplication(sys.argv)
    main = Main()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()