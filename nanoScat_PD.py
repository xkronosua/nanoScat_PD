from ET1255 import *
from smd004b import *
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Update a simple plot as rapidly as possible to measure speed.
"""

## Add path to library (just for examples; you do not need this)
#import initExample


from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
app = QtGui.QApplication([])

p = pg.plot()
p.setWindowTitle('pyqtgraph example: PlotSpeedTest')
p.setRange(QtCore.QRectF(0, -10, 5000, 20))
p.setLabel('bottom', 'Index', units='B')
curve = p.plot()

#curve.setFillBrush((0, 0, 100, 100))
#curve.setFillLevel(0)

#lr = pg.LinearRegionItem([100, 4900])
#p.addItem(lr)

data = np.array([[0, 0]])
ptr = 0
lastTime = time()
fps = None
def initET1255():
    ET_StartDrv()#p, p_l)
    print(get_last_error(), "<---")

    ET_SetADCChnl(c_int(1))
    print(get_last_error())

    ET_SetAmplif(c_int(4))
    ET_SetADCMode(c_int(1), c_int(1), c_int(1), c_int(0));

initET1255()

def initSMD():
    ATrtAddr = ctypes.c_int(255)
    ANumber = [ctypes.c_int(0), ctypes.c_int(1)]#[::-1]
    steps = 0
    COMPortNumber = None
    
    for i in range(7):
	    state = SMD_OpenComPort(ctypes.c_int32(i))
	    if state:
	    	print(state)
	    	COMPortNumber = i
	    	break


    print(SMD_GetPortNumber())
    print(SMD_SetPortNumber(ctypes.c_int(2)))


    print(SMD_GetAddr())
    print(str(SMD_ErrMsg()))
	#print(SMD_OnSHD(ATrtAddr, ANumber[0]))


    print(SMD_WriteTactFreq(ATrtAddr, ANumber[0], ctypes.c_int32(120)))
    print(SMD_WriteMarchIHoldICode(ATrtAddr, ANumber[0], ctypes.c_int(1), ctypes.c_int(0)))

initSMD()

def StepperMove(angle, Dir=1, calibr = 126.0):
    print(SMD_OnSHD(ATrtAddr, ANumber[0]))
    SMD_SetMoveParam(ATrtAddr, ANumber[0], ctypes.c_int(0), ctypes.c_bool(Dir), ctypes.c_int(int(calibr*angle)))
    SMD_ClearStep(ATrtAddr)



    
angle = 0
da = 0.05
dt = 1
timer = QtCore.QTimer()

def update():
    timer.stop()
    global curve, data, ptr, p, lastTime, fps, angle
    
    isMoving, *_ = getState()
    if not isMoving:
        i = 0
        s = []
        while i<10:
            ET_SetADCChnl(c_int(0))
            #data = np.vstack([data, np.array([ptr, angle, ET_ReadADC()pyqt +2.5])])
            s.append(ET_ReadADC() + 2.5)
            WaitADC(200)
            i += 1
        data = np.vstack([data, np.array([ angle, np.mean(s)]).T])
        curve.setData(x=data[:,0], y=data[:,1])
        angle += da
        StepperMove(da)
        timer.start(dt)
        app.processEvents()  ## force complete redraw for every plot
    else:
        timer.start()
    ptr += 1
    
    
    

timer.timeout.connect(update)
timer.start(dt)

'''
#ET_SetDeviceCount(c_int(1))
#print(get_last_error())
#ET_SetDeviceNumber(c_int(0))
print(get_last_error())

ET_StartDrv()#p, p_l)
print(get_last_error(), "<---")

ET_SetADCChnl(c_int(1))
print(get_last_error())

ET_SetAmplif(c_int(2))
ET_SetADCMode(c_int(3), c_int(1), c_int(1), c_int(0));

for i in range(2000000):
    #ET_SetStrob()
    s = []
    for j in range(0,4):
        ET_SetADCChnl(c_int(j))
        s.append(ET_ReadADC()+2.5)
    time.sleep(0.1)

    print(s,  i, get_last_error())
'''''

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()




