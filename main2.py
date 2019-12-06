###############################################################################
# Main running code for the 3rd Assignment of Digital Signal Processing Course#
# Part of "...."                                                              #
# University of Glasgow                                                       #
# Authors: Alexandros Charitonidis                                            #
#          Alessandro Tadema                                                  #
#                                                                             #
# For more information please read README.md from GitHub Repo                 #
# insert GIthub link                                                          #
###############################################################################

import VOltcurrent2
import IIRFilters
import scipy.signal as sig
import math
import sys
import pyqtgraph
import numpy as np
from pyfirmata2 import Arduino
from PyQt5 import QtGui,QtCore



class OpenApp(QtGui.QMainWindow, VOltcurrent2.Ui_MainWindow):
    def __init__(self,parent=None):
        pyqtgraph.setConfigOption('background', 'w') #before loading widget
        super(OpenApp, self).__init__(parent)
        self.setupUi(self)
        self.PitchGraph.plotItem.showGrid(True, True, 0.7)
        self.RollGraph.plotItem.showGrid(True, True, 0.7)
        self.pen=pyqtgraph.mkPen(color='r')
        self.pen2=pyqtgraph.mkPen(color='b')
        
        #self.PitchGraph.setXRange(0,500)
        self.unfilx=[]
        self.unfily=[]
        self.filx=[]
        self.fily=[]
        self.xx = 0
        self.yy = 0
        self.zz = 0
        self.angle_x = 0
        self.angle_y = 0
        self.filterx = 0
        self.filtery = 0
        # TODO: Check offsets for more accuracy

        
        self.xoffset = 2.4956 #TODO
        self.yoffset = 2.4779 #TODO
        
        self.UnfilteredLcd.setProperty("value",2000.215)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        
        
    def update(self):
        self.unfilx = self.unfilx[-500:]
        self.unfily = self.unfily[-500:]
        self.filx = self.filx[-500:]
        self.fily = self.fily[-500:]
        
        self.PitchGraph.plot(self.filx,clear=True,pen=self.pen)
        self.RollGraph.plot(self.fily,clear=True,pen=self.pen2)

        if self.ShowFiltered.isChecked():
            self.PitchGraph.plot(self.unfilx,pen=self.pen2)
            self.RollGraph.plot(self.unfily,pen=self.pen)
       

        if self.filx[-1] > 0 and self.filx[-1] <= 20:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/noredpng.png"))
        elif self.filx[-1] > 20 and self.filx[-1] <= 40:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/1redpng.png"))
        elif self.filx[-1] > 40 and self.filx[-1] <= 60:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/2redpng.png"))
        elif self.filx[-1] > 60 and self.filx[-1] <= 80:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/3redpng.png"))
        else:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/4redpng.png"))
            

        self.PitchBar.setValue(self.filx[-1])
        self.RollBar.setValue(self.fily[-1])
        
        self.RollLcd.display(self.filx[-1])
        self.PitchLcd.display(self.fily[-1])
        self.UnfilteredLcd.display(self.unfilx[-1]*1)

    def addandfilter(self,x,y,z):
        self.xx = ((x  * 5) - self.yoffset)/0.3 # 0.3 sensitivity dont forget the offset
        self.yy = ((y  * 5) - self.yoffset)/0.3
        self.zz = ((z  * 5) - self.yoffset)/0.3
        
        #pitch
        self.angle_x = (math.atan2(-self.yy,-self.zz)*57.2957795)+180
        self.angle_y = (math.atan2(-self.xx,-self.zz)*57.2957795)+180
        #roll
        #filter
        self.unfilx.append(self.angle_x)
        self.unfily.append(self.angle_y)

        
        if self.dial.value() ==0.0:
            self.filterx = iir.filter(self.angle_x)
            self.filtery = iir2.filter(self.angle_y)
        else:
            self.filterx = iir3.filter(self.angle_x)
            self.filtery = iir4.filter(self.angle_y)
            
        self.filx.append(self.filterx)
        self.fily.append(self.filtery)

        #like x=iirfilter
        #y = iirfilter
        #append them
        
    def Portshow(self, port):
        self.label_9.setText(port)
        
if __name__=="__main__":

    samplingRate = 100
    app = QtGui.QApplication(sys.argv)
    form = OpenApp()
    form.show()
    
    PORT = Arduino.AUTODETECT
    running = True
    
    def callBack(data):
        ch1 = board.analog[1].read()
        ch2 = board.analog[2].read()
        #form.addData(data)
        #print(data)
        if ch1:
            form.addandfilter(data,ch1,ch2)
            #print(data)


    #bandstop = sig.butter(N = 8, Wn = [15/50, 49.9/50], btype = 'bandstop', output = 'sos')
    lowpass = sig.butter(N = 2, Wn = 0.5/50, btype = 'lowpass', output = 'sos')
    lowpass1 = sig.butter(N = 2, Wn = 1/50, btype = 'lowpass', output = 'sos')

    print(lowpass)
    #sos = np.append(bandstop, highpass)
    #sos = sos.reshape(int(len(sos)/6), 6)
    iir = IIRFilters.IIRFilter(lowpass)
    iir2 = IIRFilters.IIRFilter(lowpass)
    iir3 = IIRFilters.IIRFilter(lowpass1)
    iir4 = IIRFilters.IIRFilter(lowpass1)
        
    board = Arduino(PORT)    
    board.samplingOn(1000/samplingRate)
    board.analog[0].register_callback(callBack)
    board.analog[0].enable_reporting()
    board.analog[1].enable_reporting()
    board.analog[2].enable_reporting()
    form.Portshow(str(board))
    print(str(board))


    app.exec_()
    board.exit()
    print("DONE")

 
