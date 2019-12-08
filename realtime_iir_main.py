################################################################################
# Main running code for the 3rd Assignment of Digital Signal Processing Course #
# Part of "X-Wing-IIR-Filtering"                                               #
# University of Glasgow                                                        #
# Authors: Alexandros Charitonidis                                             #
#          Alessandro Tadema                                                   #
#                                                                              #
# For more information please read README.md from GitHub Repo                  #
# Github link: https://github.com/Alexandros-Charitonidis/X-Wing-IIR-Filltering#                                                         
################################################################################

import AmazingUI
import IIRFilters
import scipy.signal as sig
import math
import sys
import pyqtgraph
import numpy as np
from pyfirmata2 import Arduino
from PyQt5 import QtGui,QtCore



class AcceleroApp(QtGui.QMainWindow, AmazingUI.Ui_MainWindow):
    def __init__(self,parent=None):
        super(AcceleroApp, self).__init__(parent) # Create inheritence for __init__
        pyqtgraph.setConfigOption('background', 'w') # Set the background of pyqtgraphs white
        self.setupUi(self) # Initialize the UI
        self.PitchGraph.plotItem.showGrid(True, True, 0.7) # Show Grids on pitch plots
        self.RollGraph.plotItem.showGrid(True, True, 0.7) # Show Grids on roll plots
        self.pen=pyqtgraph.mkPen(color='r') # First pen| Coloring for the plots
        self.pen2=pyqtgraph.mkPen(color='b') # Second pen| Coloring for the plots
        
        self.unfilx=[] # Unfiltered x axes list creation
        self.unfily=[] # Unfiltered y axes list creation
        self.filx=[] # Filtered x axes list creation
        self.fily=[] # Filtered y axes list creation
        self.xx = 0 # X Axes
        self.yy = 0 # Y Axes
        self.zz = 0 # Z Axes
        self.angle_x = 0 # Variable for calculating Pitch
        self.angle_y = 0 # Variable for calculating Roll
        self.filterx = 0 # Variable for filtered Pitch
        self.filtery = 0 # Variable for filtered Roll
        # TODO: Check offsets for more accuracy
        
        self.xoffset = 2.4956 #TODO Offset of sensor
        self.yoffset = 2.4779 #TODO Offset of sensor
        
        self.timer = QtCore.QTimer() # Timer setup
        self.timer.timeout.connect(self.update) # Connect the timer end to update funciton
        self.timer.start(100) # Start the timer
        
        
    def update(self): # Called continuously to update the graphics
        self.unfilx = self.unfilx[-500:] # Take the last 500 samples
        self.unfily = self.unfily[-500:] # Take the last 500 samples
        self.filx = self.filx[-500:] # Take the last 500 samples
        self.fily = self.fily[-500:] # Take the last 500 samples
        
        self.PitchGraph.plot(self.filx,clear=True,pen=self.pen) # Graph in the left plot the filtered Pitch
        self.RollGraph.plot(self.fily,clear=True,pen=self.pen2) # Graph in the rifht plot the filtered Roll

        if self.ShowFiltered.isChecked(): # Checkbox check
            self.PitchGraph.plot(self.unfilx,pen=self.pen2) # Graph in the left plot also the unfiltered Pitch
            self.RollGraph.plot(self.unfily,pen=self.pen) # Graph in the right plot also the unfiltered Roll
       

        if self.filx[-1] > 0 and self.filx[-1] <= 10: # Statement to check changes in angle to visualize PAPI
            self.label_2.setPixmap(QtGui.QPixmap(":/images/noredpng.png")) # Very low approach 
        elif self.filx[-1] > 10 and self.filx[-1] <= 20:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/1redpng.png")) # Low approach
        elif self.filx[-1] > 30 and self.filx[-1] <= 40:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/2redpng.png")) # You're OK
        elif self.filx[-1] > 40 and self.filx[-1] <= 50:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/3redpng.png")) # High approach
        else:
            self.label_2.setPixmap(QtGui.QPixmap(":/images/4redpng.png")) # You're gonna fly all night
            

        self.PitchBar.setValue(self.filx[-1]) # Set value on the progress bar for Pitch
        self.RollBar.setValue(self.fily[-1]) # Set value on the progress bar for Roll
        
        self.RollLcd.display(self.filx[-1]) # Set LCD value for Pitch
        self.PitchLcd.display(self.fily[-1]) # Set LCD value for Roll
        self.UnfilteredLcd.display(self.unfilx[-1]*1) # Set LCD value for Unfiltered Pitch

    def addandfilter(self,x,y,z):
        self.xx = ((x  * 5) - self.yoffset)/0.3 # Calculations to find the gravitanional force on each axes
        self.yy = ((y  * 5) - self.yoffset)/0.3 # Calculations to find the gravitanional force on each axes
        self.zz = ((z  * 5) - self.yoffset)/0.3 # Calculations to find the gravitanional force on each axes
        
        self.angle_x = (math.atan2(-self.yy,-self.zz)*57.2957795)+180 # Calculate pitch by arctan of the two axes
        self.angle_y = (math.atan2(-self.xx,-self.zz)*57.2957795)+180 # Calculate roll by arctan of the two axes

        self.unfilx.append(self.angle_x) # Fill the list with unfiltered Pitch
        self.unfily.append(self.angle_y) # Fill the list with unfiltered Roll

        
        if self.dial.value() == 0.0: # Check the cut-off frequency the user has chosen default 0.0 --> 0.5 Hz
            self.filterx = iir.filter(self.angle_x) # Default is 0.5 so iir is called |.filter to commence filtering| Pitch
            self.filtery = iir2.filter(self.angle_y) # Default is 0.5 so iir2 is called |.filter to commence filtering| Roll
        else: # If position is 1.0 the cut-off frequency is 1.0 hz then 
            self.filterx = iir3.filter(self.angle_x) # 1.0 is chosen so iir3 is called |.filter to commence filtering| Pitch
            self.filtery = iir4.filter(self.angle_y) # 1.0 is chosen so iir3 is called |.filter to commence filtering| Roll
            
        self.filx.append(self.filterx) # Fill the list with filtered Pitch
        self.fily.append(self.filtery) # Fill the list with filtered Roll


    def Portshow(self, port): # Here just to print the port the Arduino is connected
        self.label_9.setText(port) # Set the labels' text
        
if __name__=="__main__":

    samplingRate = 100 # Set sampling rate here is max for the arduino
    app = QtGui.QApplication(sys.argv) # Create the application using sys
    form = AcceleroApp() # Just notation
    form.show() # Show the App
    
    PORT = Arduino.AUTODETECT # The port is set using the autodetect function since port will not be known
    running = True # All threads running
    
    def callBack(data): # CallBack function to get all the data from the arduino
        ch1 = board.analog[1].read() # Read analog port 1
        ch2 = board.analog[2].read() # Read analog port 2
        if ch1: # If the secind sample has come then send the data up to the functions
            form.addandfilter(data,ch1,ch2) # Call the addandfilter function to commence the filtering
            

    lowpass = sig.butter(N = 2, Wn = 0.5/50, btype = 'lowpass', output = 'sos') # Butterworth filter to create a lowpass with 0.5 Hz cutoff
    lowpass1 = sig.butter(N = 2, Wn = 1/50, btype = 'lowpass', output = 'sos') # Butterworth filter to create a lowpass with 1 Hz cutoff

    iir = IIRFilters.IIRFilter(lowpass) # Send the sos coefficients to the filter
    iir2 = IIRFilters.IIRFilter(lowpass) # Send the sos coefficients to the filter
    iir3 = IIRFilters.IIRFilter(lowpass1) # Send the sos coefficients to the filter
    iir4 = IIRFilters.IIRFilter(lowpass1) # Send the sos coefficients to the filter
        
    board = Arduino(PORT) # Initialize board to look up for pins
    board.samplingOn(1000/samplingRate) # Set the sampling rate for the board
    board.analog[0].register_callback(callBack) # Register the callBack to a Port
    board.analog[0].enable_reporting() # Enable port reporting for pin 0
    board.analog[1].enable_reporting() # Enable port reporting for pin 1
    board.analog[2].enable_reporting() # Enable port reporting for pin 2
    form.Portshow(str(board)) # Call the function to show the Port 
    app.exec_() # Execute our application
    board.exit() # Close the board
    print("DONE")

 
