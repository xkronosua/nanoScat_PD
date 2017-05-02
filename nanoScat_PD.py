from ET1255 import *
#from smd004b import *
from SMD_test2 import *
import signal
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
from scipy.signal import medfilt
import pyqtgraph as pg
import signal
import re
from serial.tools import list_ports
import configparser
import threading
from multiprocessing import Process

import sys
from PyQt4 import uic
import time
from PyQt4.QtCore import QTimer, QThread, SIGNAL
from PyQt4.QtGui import QApplication, QMessageBox, QTableWidgetItem

import subprocess
import sys, os
import threading
import time
import signal
import struct





def sigint_handler(*args):
	"""Handler for the SIGINT signal."""
	sys.stderr.write('\r')
	QApplication.quit()


"""
import csv
with open('eggs.csv', 'w', newline='') as csvfile:
	spamwriter = csv.writer(csvfile, delimiter=' ',
							quotechar='|', quoting=csv.QUOTE_MINIMAL)
	spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
	spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])

"""

et = ET1255()
def initET1255():

	et.ET_StartDrv()#p, p_l)
	#print(get.ET_last_error(), "<---")

	et.ET_SetADCChnl(1)
	#print(get.ET_last_error())

	et.ET_SetAmplif(5)
	et.ET_SetADCMode(0, 1, 1, 0);

initET1255()

class nanoScat_PD(QtGui.QMainWindow):
	ui = None
	stepperCOMPort = None
	ATrtAddr = 255
	currentAngle = 0
	prevMove = ([0, 0], [0, 0])
	line0, line1, line2, line3, line4, line5, line6, line7 = None, None, None, None, None, None, None, None
	lines = [line0, line1, line2, line3, line4, line5, line6, line7]
	steppingTimer = None
	calibrTimer = None
	measTimer = None
	stepperStateTimer = None
	FWCalibrationCounter = 0
	FWCalibrationCounterList = []

	angleSensorSerial = None
	angleUpdateTimer = None
	angleUpdateThread = None
	lastDirection = 1
	tmpData = None
	num = 10
	calibrData=np.array([])
	measData=np.array([])
	intStepCounter = 0
	moveFlag = 0
	extLaserStrob = None
	extDataBuffer = None
	#et = ET1255()
	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.ui = uic.loadUi("mainwindow.ui")
		self.ui.closeEvent = self.closeEvent
		self.steppingTimer = QtCore.QTimer()
		self.calibrTimer = QtCore.QTimer()
		self.calibrHomeTimer = QtCore.QTimer()
		self.calibrFWTimer = QtCore.QTimer()
		self.measTimer = QtCore.QTimer()
		self.angleUpdateTimer = QtCore.QTimer()

		self.stepperStateTimer = QtCore.QTimer()


		self.config = configparser.ConfigParser()
		self.config.read('settings.ini')
		print(sys.argv[0],self.config.sections())
		self.globalSettingsDict = self.config['STEPPER1']#.read('globalSettings.ini')
		self.updateSettingsTable()
		
		self.uiConnect()
		self.initUi()
		
		self.initET1255()
		self.tmpData = []#[[0,0,0]]
		self.calibrData = np.array([])#[0,0,0])
		self.SMD = SMD004()
		#self.extLaserStrob = laserStrob(0.1)
	
		
		#self.startLaserStrob(0.02)
	def updateSettingsTable(self):
		
		for n, key in enumerate(sorted(self.globalSettingsDict.keys())):
			newitem = QTableWidgetItem(key)
			self.ui.globalSettings.setItem(n,0,newitem)
			newitem = QTableWidgetItem(self.globalSettingsDict[key])
			self.ui.globalSettings.setItem(n,1,newitem)



	def initStepper(self):
		self.config.read('settings.ini')
		#self.config.read('test.ini')
		print("StepperInit:",self.config.sections())
		sm1Config = self.config['STEPPER1']
		sm2Config = self.config['STEPPER2']
		try:
			print("\tfMode:\t\t", self.SMD.eSetPhaseMode(1, int(sm1Config['PhaseMode'])))
			print("\tfrec:\t\t",  self.SMD.eSetTactFreq( 1, int(sm1Config['TactFreq'])))
			print("\tfMult:\t\t", self.SMD.eSetMulty(1, int(sm1Config['Multy'])))
			print("\tI:\t\t", self.SMD.eWriteMarchIHoldICode(1, int(sm1Config['MarchI']), int(sm1Config['HoldI'])))
			#print("\tStep:\t\t", SMD_SetMoveParam(self.ATrtAddr, 0, False, False, 0))
			
			print("\tfMode:\t\t", self.SMD.eSetPhaseMode(2, int(sm2Config['PhaseMode'])))
			print("\tfrec:\t\t",  self.SMD.eSetTactFreq( 2, int(sm2Config['TactFreq'])))
			print("\tfMult:\t\t", self.SMD.eSetMulty(2, int(sm2Config['Multy'])))
			print("\tI:\t\t", self.SMD.eWriteMarchIHoldICode(2, int(sm2Config['MarchI']), int(sm2Config['HoldI'])))
			self.SMD.eClearStep()
			#self.intStepCounter = ord(self.SMD.eGetState()[5:6])#int(getState(self.ATrtAddr, 0)[4])
			#self.getIntPositionCorrection()
			
		except:
			traceback.print_exc()
			print('StepperInitErr')

	def initET1255(self):
		#et.ET_SetDeviceCount(c_int(1))
		#et.ET_SetDeviceNumber(c_int(0))
		et.ET_StartDrv()#" "*255,255)#p, p_l)
		#print(get.last_error(), "<---")

		et.ET_SetAmplif(5)
		et.ET_SetScanMode(0, False);
		et.ET_SetADCMode(0, 1, 1, 0);
		#threading.Timer(1,self.laserStrob).start()
		#self.laserStrobTimer.start(20)


	
	"""
	def dataBuffering(self):
		et.ET_SetAmplif(3)
		print(et.ET_MeasEnd())
		et.ET_SetADCChnl(0)
		s1 = []
		for i in range(2):
			if et.ET_MeasEnd():
				et.ET_SetStrob()
			v = et.ET_ReadADC()+2.5
			s1.append(v)
		self.num += 1
		self.tmpData.append([self.num,0,np.mean(s1)])
		threading.Timer(0.01,self.dataBuffering).start()
	""" 

	def initUi(self):
		self.pw = pg.PlotWidget(name='Plot1')  ## giving the plots names allows us to link their axes together
		self.ui.l.addWidget(self.pw)
		self.pw2 = pg.PlotWidget(name='Plot2')
		self.ui.l.addWidget(self.pw2)

		self.ui.show()


		## Create an empty plot curve to be filled later, set its pen
		colors = ['red', "green", 'blue', 'cyan', 'magenta', 'yellow', 'purple', 'olive']
		#for i in range(0,self.ui.channelsSettings.rowCount()):
		#	self.lines[i] = self.pw.plot()
		#	self.lines[i].setPen(QtGui.QColor(colors[i]))
		self.line0 = self.pw2.plot()
		print(self.line0)
		self.line0.setPen(QtGui.QColor('red'))
		self.line1 = self.pw.plot()
		self.line1.setPen(QtGui.QColor("green"))
		self.line2 = self.pw.plot()
		self.line2.setPen(QtGui.QColor("blue"))
		self.line3 = self.pw.plot()
		self.line3.setPen(QtGui.QColor("cyan"))

		self.pw.setLabel('left', 'Signal', units='arb. un.')
		self.pw.setLabel('bottom', 'Angle', units='deg.')
		self.pw.setXRange(0, 360)
		self.pw.setYRange(0, 1e10)
		self.pw2.setMaximumHeight(300)

		'''
		for i in range(self.ui.channelsSettings.rowCount()):
			checkbox = QtGui.QCheckBox()
			checkbox.setObjectName("Channel"+str(i)+"State")
			self.ui.channelsSettings.setCellWidget(i, 0, checkbox)

			item = QtGui.QTableWidgetItem("Chnl_" + str(i))
			self.ui.channelsSettings.setItem(i, 1, item)

			color = QtGui.QTableWidgetItem()
			color.setBackgroundColor(QtGui.QColor(colors[i]))
			self.ui.channelsSettings.setItem(i, 2, color)

			amplif = QtGui.QTableWidgetItem("3")
			self.ui.channelsSettings.setItem(i, 3, amplif)



		self.ui.channelsSettings.setColumnWidth(0,20)
		self.ui.channelsSettings.setColumnWidth(1,100)
		self.ui.channelsSettings.setColumnWidth(2,20)
		self.ui.channelsSettings.setColumnWidth(3,40)
		'''
	def isStepperConnected(self):
		'''
		if self.stepperCOMPort == -1:
			return -1
		val = SMD_GetPortNumber()
		print(">"*10,val)
		if val == self.stepperCOMPort:
			return 1
		else:
			self.ui.openCOMPort_btn.setText("Open")
			self.ui.openCOMPort_btn.setStyleSheet('background-color: green; color: black;')
			return 0
		'''
		return self.SMD.isConnected()
	'''
	def getStepperState(self):
		motorState = [i.value for i in getState(self.ATrtAddr, 1)]
		if sum(motorState) == 0:
			motorState = -1
			step_time = self.ui.step_time.value()
	'''
	def Open_CloseStepperCOMPort(self, state):
		print(state)
		portNumber = self.ui.stepperPortNumber.value()
		
		dev = serial.tools.list_ports.comports()
		dev_list = []
		for d in dev:
			dev_list.append(d)
			try:
				com, info = dev_list[-1][0], dev_list[-1][2]

				m = re.search('VID_(\d+)\+PID_(\d+)',info)
				if m.group(0) == 'VID_0403+PID_6001':
					portNumber = int(com[3:])
					self.ui.stepperPortNumber.setValue(portNumber)
			except: pass
		
		if state:
			print("PortNumber:", portNumber, portNumber==0)
			res = 0
			'''
			if portNumber == 0:
				print("AutoPort")
				for i in range(1,10):
					print(self.SMD.eOpenCOMPort(i))
					t = self.SMD.isConnected()#SMD_OpenComPort(i)
					if t:
						portNumber = i
						self.ui.stepperPortNumber.setValue(i)
						print("PortNumber:", portNumber)
						break
			'''
			res = self.SMD.eOpenCOMPort(portNumber)
			print("res:", res)
			if res:
				self.stepperCOMPort = portNumber
				self.ui.openCOMPort_btn.setText('Close')
				self.ui.openCOMPort_btn.setStyleSheet('background-color: red; color: black;')
				self.initStepper()
				self.stepperStateTimer.start(100)

		else:
			self.SMD.ser.close()#SMD_CloseComPort()
			print("PortClosed")
			self.ui.openCOMPort_btn.setText('Open')
			self.ui.openCOMPort_btn.setStyleSheet('background-color: green; color: black;')
			self.ui.openCOMPort_btn.setChecked(False)
			self.stepperStateTimer.stop()

	def setStepperParam(self):
		pass
		#motor = self.ui.ANumber.currentIndex()
		#frec = self.ui.Frec.value()
		#fMult = self.ui.fMult.value()
		#AMarchI = self.ui.AMarchI.currentIndex()
		#AHoldI = self.ui.AHoldI.currentIndex()
		#fInd = [0, 1, 10]
		#fMode = fInd[self.ui.fMode.currentIndex()]
		#if self.isStepperConnected():
		#	print("\tfMode:\t\t", SMD_WritePhaseMode(self.ATrtAddr, motor, fMode))
		#	print("\tfrec:\t\t", SMD_WriteTactFreq(self.ATrtAddr, motor, frec))
		#	print("\tfMult:\t\t", SMD_WriteMulty(self.ATrtAddr, motor, fMult))
		#	print("\tI:\t\t", SMD_WriteMarchIHoldICode(self.ATrtAddr, motor, AMarchI, AHoldI))
		#	print("\tStep:\t\t", SMD_SetMoveParam(self.ATrtAddr, motor, False, False, 0))
		#SMD_OnSHD(self.ATrtAddr, motor)
	def getCorrectedAngle(self):
		angle = self.ui.steppingAngle.value()
		calibr = float(self.config['STEPPER1']['calibrationCoefficient']) #self.ui.steppingCalibr.value()
		tmp_angle = int(angle*calibr)/calibr
		self.ui.steppingAngle.setValue(tmp_angle)
		return int(tmp_angle*calibr), tmp_angle
		#return tmp_angle*calibr, tmp_angle

	def steps2angle(self, steps, motor=1):
		calibr = float(self.config['STEPPER'+str(motor)]['calibrationCoefficient']) #self.ui.steppingCalibr.value()
		return steps/calibr

	def prepInternCounter(self, direction):
		if direction != self.lastDirection:
			self.SMD.eClearSteps()#SMD_ClearStep(self.ATrtAddr)
			self.lastDirection = direction

	def CCWSingleMove(self):
		steps, angle = self.getCorrectedAngle()
		direction = 1
		motor = 1#self.ui.ANumber.currentIndex()
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected() and  not motorState[0]:
			self.SMD.makeStepCCW(motor,steps,True)
			self.moveFlag = 1
			self.updateAngle( angle * direction )



	def CWSingleMove(self):
		steps, angle = self.getCorrectedAngle()
		direction = -1
		motor = 1#self.ui.ANumber.currentIndex()
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected() and  not motorState[0]:
			self.SMD.makeStepCW(motor,steps,True)
			self.moveFlag = 1
			self.updateAngle( angle * direction )
	
	def CCWMoveToStop(self):
		steps, angle = self.getCorrectedAngle()
		direction = 1
		motor = 1#self.ui.ANumber.currentIndex()
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected() and  not motorState[0]:
			self.SMD.moveCCW(1)
			self.updateAngle( angle * direction )

	def CWMoveToStop(self):
		steps, angle = self.getCorrectedAngle()
		direction = -1
		motor = 1#self.ui.ANumber.currentIndex()
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected() and  not motorState[0]:
			self.SMD.moveCW(1)
			self.updateAngle( angle * direction )
	
	def CCWHome(self):
		steps, angle = self.getCorrectedAngle()
		direction = 1
		motor = 1#self.ui.ANumber.currentIndex()
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected() and  not motorState[0]:
			self.SMD.moveCCW(1)
			self.updateAngle( angle * direction )
			self.calibrHomeTimer.start(200)


	def CWHome(self):
		steps, angle = self.getCorrectedAngle()
		direction = -1
		motor = 1#self.ui.ANumber.currentIndex()
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected() and  not motorState[0]:
			self.SMD.moveCW(1)
			self.updateAngle( angle * direction )
			self.calibrHomeTimer.start(200)

	def onCalibrHomeTimer(self):
		info = self.getNanoScatInfo(['zero','angle'])
		if info['zero'] == 1:
			print("Zero at:", info['angle'])
			self.stepperStop()
			self.updateAngle(0)
			self.setNanoScatState(angle=0)
			self.currentAngle = 0
			self.calibrHomeTimer.stop()
		else:
			print("angle:", info['angle'])
		

	def getCurrentFilter(self):
		row = self.ui.filtersTab.currentRow()
		try:
			name = self.ui.filtersTab.item(row,0).text()
		except:
			name = 'none'
		try:
			val = self.ui.filtersTab.item(row,1).text()
		except:
			val = 'none'
		#	return (None, None)
		return name, val



	def prevFilter(self):
		calibr = float(self.config['STEPPER2']['calibrationCoefficient'])
		direction = 1
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected():
			#print("StepParam:", SMD_SetMoveParam(self.ATrtAddr, 1,  False, direction>0, c_ulong(int(calibr))))
			self.SMD.makeStepCW(2,steps=int(calibr))
			#print("On", SMD_OnSHD(self.ATrtAddr, 1))
			row = self.ui.filtersTab.currentRow()
			row -= 1
			if row<0:
				row = 5
			self.ui.filtersTab.setCurrentCell(row,0)
			print(row)
			name, val = self.getCurrentFilter()
			print(name, val)

	def nextFilter(self):
		calibr = float(self.config['STEPPER2']['calibrationCoefficient'])
		direction = -1
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected():
			#print("StepParam:", SMD_SetMoveParam(self.ATrtAddr, 1,  False, direction>0, c_ulong(int(calibr))))
			#print("On", SMD_OnSHD(self.ATrtAddr, 1))
			self.SMD.makeStepCCW(2,steps=int(calibr))
			row = self.ui.filtersTab.currentRow()
			row += 1
			if row>=6:
				row = 0
			self.ui.filtersTab.setCurrentCell(row,0)
			print(row)
			name, val = self.getCurrentFilter()
			print(name, val)

	def calibrFW(self):
		#steps, angle = self.getCorrectedAngle()
		#direction = -1
		#motor = 1#self.ui.ANumber.currentIndex()
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected() and  not motorState[0]:
			self.SMD.moveCW(2)
			#self.updateAngle( angle * direction )
			self.calibrFWTimer.start(50)

	def onCalibrFWTimer(self):
		info = self.getNanoScatInfo(['FW'])
		print(info)
		if info['FW'] == 1:
			self.calibrFWTimer.stop()
			self.stepperStop()
			self.ui.filtersTab.setCurrentCell(0,0)
			#self.FWCalibrationCounter+=1
			#print(self.FWCalibrationCounter)

		else:
			'''
			mp = 0
			if self.FWCalibrationCounter != 0:
				self.FWCalibrationCounterList.append(self.FWCalibrationCounter)
				print(self.FWCalibrationCounterList)
				if len(self.FWCalibrationCounterList)>=6:
					self.stepperStop()
					self.calibrFWTimer.stop()
					self.FWCalibrationCounterList = 0
					m = max(self.FWCalibrationCounterList)
					mp = 0
					for i,j in enumerate(self.FWCalibrationCounterList):
						if m<j:
							m=j
							mp = i
			print(mp)
			self.FWCalibrationCounter=0
			'''
			#self.stepperStop()
			#self.updateAngle(0)
			#self.setNanoScatState(angle=0)
			#self.currentAngle = 0
			#self.calibrFWTimer.stop()
		

	def stepperStop(self):
		#motor = self.ui.ANumber.currentIndex()
		#SMD_OffSHD(self.ATrtAddr, 0)
		#SMD_OffSHD(self.ATrtAddr, 1)
		self.SMD.eStop()
		self.calibrHomeTimer.stop()
		self.calibrFWTimer.stop()
		#intStepDiff = self.getIntPositionCorrection()
		#print('diff:',intStepDiff, self.steps2angle(intStepDiff))

	def getIntPositionCorrection(self, direction=1):
		#motorState = getState(self.ATrtAddr, 0)
		#print("Motor1 ", motorState)
		intStepDiff = None# motorState[4].value - self.intStepCounter
		#self.intStepCounter = motorState[4].value
		#if intStepDiff<0 and direction==1:
		#	intStepDiff += 2**16 
		#	intStepDiff *= -1
		return intStepDiff
	





	def updateAngle(self, new_angle=0, mode='None'):
		if self.sender().objectName() == "resetAngle": mode = "reset"
		if mode == "reset":
			self.currentAngle = 0
		elif mode == "set":
			self.currentAngle = new_angle
		else:
			self.currentAngle += new_angle
		self.ui.currentAngle.display(self.currentAngle)
		return self.currentAngle

	def setCustomAngle(self):
		dlg =  QtGui.QInputDialog(self)
		dlg.setInputMode( QtGui.QInputDialog.DoubleInput)
		dlg.setLabelText("Angle:")
		dlg.setDoubleDecimals(6)
		dlg.setDoubleRange(-999999,999999)
		ok = dlg.exec_()
		angle = dlg.doubleValue()

		if ok:
			self.updateAngle(angle, mode='set')

	def startMeasurement(self, state):
		if state:
			if self.isStepperConnected():
				self.steppingTimer.start()
				self.ui.startMeasurement.setText("Stop")
				self.getCurrentFilter(self)

			else:
				self.ui.startMeasurement.setChecked(False)
				self.ui.startMeasurement.setText("Start")
		else:
			self.steppingTimer.stop()
			self.ui.startMeasurement.setText("Start")
			self.num = 0
			self.calibrData = []

	def pauseMeasurements(self, state):
		if not state:
			self.angleUpdateTimer.stop()
			#et.openSerialPort('COM'+str(self.ui.angleSensorPort.value()))
			f = lambda : et.ET_FStrobDataRead('COM'+str(self.ui.angleSensorPort.value()), self.ui.saveToPath.text(),self.ui.dataFreq.value())
			t = threading.Thread(name='child procs', target=f)
			with open(self.ui.saveToPath.text(), 'a') as f:
				f.write("\n#Filter:"+self.getCurrentFilter()[0]+"\n")
			
			filterName,fVal = self.getCurrentFilter()
			t.deamon = True
			t.start()

			self.measTimer.start(self.ui.plotPeriod.value())
			
			direction = 1 if self.ui.measurementDirCW.isEnabled() else -1
			if direction == 1:
				self.SMD.moveCW(1)
			else:
				self.SMD.moveCCW(1)
			
		else:
			with open(self.ui.saveToPath.text(), 'a') as f:
				f.write("\n#Filter:"+self.getCurrentFilter()[0]+"\n")
			et.ET_stopStrobData()
			self.SMD.eStop()
			self.measTimer.stop()
			self.angleUpdateTimer.start()
			self.calibrData=np.array([])
			#data = np.loadtxt(self.ui.saveToPath.text(),comments='#')
			#self.line2.setData(x=data[:,4], y=data[:,1])
			#self.line3.setData(x=data[:,4], y=data[:,2])

	def stepperOn(self):

		steps, angle = self.getCorrectedAngle()
		direction = 1 if self.ui.measurementDirCW.isEnabled() else -1
		motor = 0#self.ui.ANumber.currentIndex()
		motorState = getState(self.ATrtAddr, 0)
		if self.isStepperConnected() and  not motorState[0]:
			if self.prevMove[motor][0] != steps.value or self.prevMove[motor][1] != int(direction):
				self.prevMove[motor][0] = steps.value
				self.prevMove[motor][1] = direction
				
				print("StepParam:", SMD_SetMoveParam(self.ATrtAddr, motor,  False, direction>0, steps))
				#self.prepInternCounter(direction)
			print("On", SMD_OnSHD(self.ATrtAddr, motor))
			#self.updateAngle( angle * direction )

	def getStepperState(self):
		state = [ i.value for i in getState(self.ATrtAddr, 1)]
		#if sum(state) == 0:
		#	state [0] = 1
		return state

	

	def startCalibr(self, state):
		if state:

			self.angleUpdateTimer.stop()
			self.openAngleSensorPort(False)
			#et.openSerialPort('COM'+str(self.ui.angleSensorPort.value()))
			f = lambda : et.ET_FStrobDataRead('COM'+str(self.ui.angleSensorPort.value()), "calibr.txt",self.ui.dataFreq.value())
			t = threading.Thread(name='child procs', target=f)
			t.deamon = True
			t.start()
			self.calibrTimer.start(self.ui.plotPeriod.value())
			
			direction = 1 if self.ui.measurementDirCW.isEnabled() else -1
			self.line0.setData(x=[],y=[])
			self.line1.setData(x=[],y=[])
			self.line2.setData(x=[],y=[])
			self.line3.setData(x=[],y=[])
			#if direction == 1:
			#	self.SMD.moveCW(1)
			#else:
			#	self.SMD.moveCCW(1)
			
		else:

			et.ET_stopStrobData()
			self.calibrTimer.stop()
			self.openAngleSensorPort(True)
			self.angleUpdateTimer.start()
			self.calibrData=np.array([])
			#data = np.loadtxt(self.ui.saveToPath.text(),comments='#')
			#self.line2.setData(x=data[:,4], y=data[:,1])
			#self.line3.setData(x=data[:,4], y=data[:,2])
			self.SMD.eStop()
			
	def onCalibrTimer(self):
		r = et.getData()
		if len(self.calibrData)>0:
			
			self.calibrData = np.vstack((self.calibrData,r))
		else:
			self.calibrData = np.array(r)
		data = self.calibrData
		#print(r)
		data = data[data[:,2]<5]
		data = data[data[:,3]<5]
		self.line0.setData(x=data[:,0], y=data[:,2])
		self.line1.setData(x=data[:,0], y=data[:,3])
		self.updateAngle(data[-1,-1])
		app.processEvents()  

	def startContMeas(self, state):
		if state:
			self.angleUpdateTimer.stop()
			self.openAngleSensorPort(False)
			#et.openSerialPort('COM'+str(self.ui.angleSensorPort.value()))
			f = lambda : et.ET_FStrobDataRead('COM'+str(self.ui.angleSensorPort.value()), self.ui.saveToPath.text(),self.ui.dataFreq.value())
			t = threading.Thread(name='child procs', target=f)
			with open(self.ui.saveToPath.text(), 'a') as f:
				f.write("\n#Filter:"+self.getCurrentFilter()[0]+"\n")
			
			filterName,fVal = self.getCurrentFilter()
			t.deamon = True
			t.start()

			self.measTimer.start(self.ui.plotPeriod.value())
			
			direction = 1 if self.ui.measurementDirCW.isEnabled() else -1
			if direction == 1:
				self.SMD.moveCW(1)
			else:
				self.SMD.moveCCW(1)
			
		else:

			et.ET_stopStrobData()
			try:
			
				self.SMD.eStop()
			except:
				print('Err')
			self.measTimer.stop()
			self.openAngleSensorPort(True)
			self.angleUpdateTimer.start()
			self.calibrData=np.array([])
			#data = np.loadtxt(self.ui.saveToPath.text(),comments='#')
			#self.line2.setData(x=data[:,4], y=data[:,1])
			#self.line3.setData(x=data[:,-1], y=data[:,2])
			
			
	def onContMeasTimer(self):
		r = et.getData()
		if len(self.measData)>0:
			
			self.measData = np.vstack((self.measData,r))
		else:
			self.measData = np.array(r)
		data = self.measData
		#print(r)
		data = data[data[:,2]<5]
		data = data[data[:,3]<5]
		self.line0.setData(x=data[:,-1], y=data[:,2])
		self.line1.setData(x=data[:,-1], y=data[:,3])
		self.updateAngle(data[-1,-1])
		app.processEvents()  ## force complete redraw for every plot
		
	def openAngleSensorPort(self,state):
		if state:
			portNumber = self.ui.angleSensorPort.value()
			dev = serial.tools.list_ports.comports()
			print(dev)
			dev_list = []
			for d in dev:
				dev_list.append(d)
				
				try:
					com, info = dev_list[-1][0], dev_list[-1][2]
					m = re.search('1A86:7523',info)
					print(m,info)
					if m.group(0) == '1A86:7523':
						print(info,com)
						portNumber = int(com[3:])
						self.ui.angleSensorPort.setValue(portNumber)
				except: pass
			
			
			print("open")
			#et.openSerialPort('COM'+str(self.ui.angleSensorPort.value()))
			#self.angleSensorSerial = serial.Serial('COM'+str(self.ui.angleSensorPort.value()), baudrate=19200, dsrdtr=False)
			self.angleSensorSerial = serial.Serial()
			self.angleSensorSerial.port = 'COM'+str(self.ui.angleSensorPort.value())
			self.angleSensorSerial.baudrate = 19200
			self.angleSensorSerial.timeout = 1
			self.angleSensorSerial.setDTR(False)
			self.angleSensorSerial.open()
			self.angleSensorSerial.flush()
			self.angleSensorSerial.flushInput()
			self.angleSensorSerial.flushOutput()
			self.angleSensorSerial.write(b'1')
			self.setNanoScatState(frecMode=[20,20])
			self.setNanoScatState(angleCalibrCoef=0.49)
			self.angleUpdateTimer.start(1000)
			#self.angleSensorSerial.write(b'2')
			

		else:
			self.angleUpdateTimer.stop()
			self.angleSensorSerial.write(b'RM')
			self.angleSensorSerial.close()
	def getAngle_(self):
		self.angleSensorSerial.write(b'3')
		a = self.angleSensorSerial.read(4)
		s = self.angleSensorSerial.read(1)
		sa = sum(a)
		if sa >255: sa -= 255
		if sa == ord(s):
			return struct.unpack('f', a )[0]
		else:
			return None
	def getAngle_ordinaryMode(self):
		if not self.angleSensorSerial.isOpen():
			self.openAngleSensorPort(True)
			return None
		else: 
			a = self.angleSensorSerial.readline().decode("utf-8")
			#print(a)
			self.angleSensorSerial.flush()
			self.angleSensorSerial.flushInput()
			self.angleSensorSerial.flushOutput()
			angle = float(a.split('a:')[-1].split('\t')[0])
			return angle
	
	def getNanoScatInfo(self,keys=['angle']):
		if not self.angleSensorSerial.isOpen():
			self.openAngleSensorPort(True)
			return None
		else:
			outDict = {}
			self.angleSensorSerial.flush()
			self.angleSensorSerial.flushInput()
			self.angleSensorSerial.flushOutput()
			line = self.angleSensorSerial.readline().decode("utf-8")

			if 'angle' in keys:
				try:
					outDict['angle'] = float(line.split('\tA:')[-1].split('\t')[0])
				except ValueError:
					outDict['angle'] = None
			if 'zero' in keys:
				try:
					outDict['zero'] = int(line.split('\tZ:')[-1].split('\t')[0])
				except ValueError:
					outDict['zero'] = None
			if 'FW' in keys:
				try:
					outDict['FW'] = int(line.split('\tFW:')[-1].split('\t')[0])
				except ValueError:
					outDict['FW'] = None

			if 'freqMode' in keys:
				try:
					outDict['freqMode'] = [float(i) for i in (line.split('\tFM:')[-1].split('\t')[0]).split('x')]
				except ValueError:
					outDict['freqMode'] = [None, None]
			return outDict

	def setNanoScatState(self,angle=None, frecMode=[None, None], angleCalibrCoef=None):
		if not self.angleSensorSerial.isOpen():
			self.openAngleSensorPort(True)
			return None
		else:
			res = None
			if not angle is None:
				res = self.angleSensorSerial.write(b'A'+str(angle).encode())
			if not angleCalibrCoef is None:
				res = self.angleSensorSerial.write(b'CC'+str(angleCalibrCoef).encode())

			if sum([i is None for i in frecMode]) != 2:
				res = self.angleSensorSerial.write(b'FM'+str(frecMode[0]).encode()+b'x'+str(frecMode[1]).encode())
			print(res)
			return 1

		

	def onAngleUpdateTimer(self):
		
		angle = self.getNanoScatInfo(['angle'])['angle']
		try:
			self.currentAngle = angle#et.getAngle()
		except:
			pass
		print("angle", angle)
		self.ui.currentAngle.display(self.currentAngle)

	def checkStepperState(self):
		state = self.getStepperState()
		self.stepperStateTimer.stop()
		if self.moveFlag:
			self.moveFlag = 0
			def fu():
				SMD_OnSHD(ATrtAddr, 0)
			threading.Thread(target=fu).start()
		self.stepperStateTimer.start(100)

	def setADCAmplif(self, value):
		et.ET_SetAmplif(value)

	def cleanPlot(self):
		self.calibrData=np.array([])
		self.measData=np.array([])
		self.line0.setData(x=[], y=[])
		self.line1.setData(x=[], y=[])

	def setStrobMode(self, mode):
		m = et.setStrobMode(mode)
		print('strobMode:%d'%(m))

	def setLaserFreq(self, value):
		print('SetLaserFreq:')
		#if not self.angleSensorSerial.inWaiting():
		
		#	self.angleSensorSerial = serial.Serial()
		#	self.angleSensorSerial.port = 'COM'+str(self.ui.angleSensorPort.value())
		#	self.angleSensorSerial.baudrate = 19200
		#	self.angleSensorSerial.timeout = 1
		#	self.angleSensorSerial.setDTR(False)
		#	self.angleSensorSerial.open()
		self.angleSensorSerial.write(b'f'+str(value).encode('ascii')+b'\n')

	def closeEvent(self, event):
		print("event")
		reply = QtGui.QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			self.angleSensorSerial.close()
			event.accept()
			#self.stopLaserStrob()
			#self.stopDataBuffering()
		else:
			event.ignore()

	def uiConnect(self):
		#self.ui.btnExit.clicked.connect(self.closeAll)
		#self.ui.actionExit.triggered.connect(self.closeAll)
		self.ui.measurementDirCW.clicked.connect(lambda state: (self.ui.measurementDirCCW.setChecked(False), self.ui.measurementDirCW.setEnabled(False),self.ui.measurementDirCCW.setEnabled(True)))
		self.ui.measurementDirCCW.clicked.connect(lambda state: (self.ui.measurementDirCW.setChecked(False), self.ui.measurementDirCCW.setEnabled(False),self.ui.measurementDirCW.setEnabled(True)))

		self.ui.startCalibr.toggled[bool].connect(self.startCalibr)
		self.ui.startMeasurement.toggled[bool].connect(self.startContMeas)
		self.ui.ADCAmplif.valueChanged[int].connect(self.setADCAmplif)
		#self.ui.laserFreq.valueChanged[int].connect(self.setLaserFreq)
		
		self.ui.pauseMeasurements.toggled[bool].connect(self.pauseMeasurements)
		self.ui.openCOMPort_btn.toggled[bool].connect(self.Open_CloseStepperCOMPort)
		self.ui.openAngleSensorPort.toggled[bool].connect(self.openAngleSensorPort)
		self.ui.editStepperSettings.clicked.connect(self.setStepperParam)
		self.ui.CCWSingleMove.clicked.connect(self.CCWSingleMove)
		self.ui.CWSingleMove.clicked.connect(self.CWSingleMove)
		self.ui.strobMode.toggled[bool].connect(self.setStrobMode)
		self.ui.cleanPlot.clicked.connect(self.cleanPlot)

		self.ui.CCWMoveToStop.clicked.connect(self.CCWMoveToStop)
		self.ui.CWMoveToStop.clicked.connect(self.CWMoveToStop)
		self.ui.CCWHome.clicked.connect(self.CCWHome)
		self.ui.CWHome.clicked.connect(self.CWHome)
		#self.ui.CCWMoveToStop.clicked.connect(self.CCWMoveToStop)
		#self.ui.CWMoveToStop.clicked.connect(self.CWMoveToStop)

		self.ui.nextFilter.clicked.connect(self.nextFilter)
		self.ui.prevFilter.clicked.connect(self.prevFilter)

		self.ui.stepperStop.clicked.connect(self.stepperStop)
		self.ui.resetAngle.clicked.connect(self.updateAngle)
		self.ui.setCustomAngle.toggled[bool].connect(self.setCustomAngle)
		self.ui.calibrFW.clicked.connect(self.calibrFW)

		#self.ui.startMeasurement.clicked.connect(self.startMeasurement)

		#self.steppingTimer.timeout.connect(self.stepMeasurement)
		self.calibrTimer.timeout.connect(self.onCalibrTimer)
		self.measTimer.timeout.connect(self.onContMeasTimer)
		self.angleUpdateTimer.timeout.connect(self.onAngleUpdateTimer)
		self.calibrHomeTimer.timeout.connect(self.onCalibrHomeTimer)
		self.calibrFWTimer.timeout.connect(self.onCalibrFWTimer)
		#self.stepperStateTimer.timeout.connect(self.checkStepperState)
		#self.laserStrobTimer.timeout.connect(self.laserStrob)

		self.ui.actionClose.triggered.connect(self.close)
		#self.ui.actionExit.triggered.connect(self.close)



if __name__ == "__main__":
	signal.signal(signal.SIGINT, sigint_handler)
	app = QtGui.QApplication(sys.argv)
	myWindow = nanoScat_PD(None)
	app.exec_()
	SMD_CloseComPort()
	print(":)")
	sys.exit(1)