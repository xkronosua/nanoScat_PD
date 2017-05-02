__author__ = 'Admin'
from ctypes import *
import time

#lib = WinDLL('C:\\WINDOWS\\ET1255.dll', use_last_error=True)
#lib1 = WinDLL('C:\\WINDOWS\\Project2.dll', use_last_error=True)
# lib = ctypes.WinDLL('full/path/to/mylibrary.dll')

'''
ET_SetADCChnl = lib['ET_SetADCChnl']
ET_SetADCChnl.restype = c_
ET_StartDrv = lib1['test1']
#ET_StartDrv.argtypes = []#c_wchar_p, c_]  # lib['ET_StartDrv']#my func is double myFunc(double);
#ET_StartDrv.restype = c_long
ET_ReadADC = lib['ET_ReadADC']
ET_ReadADC.restype = c_float
# opt_flag = ctypes.c_char_p.in_dll(lib, "ET1255_DLL_Name")
ET_SetDeviceCount = lib['ET_SetDeviceCount']
ET_SetStrob = lib['ET_SetStrob']
ET_MeasEnd = lib['ET_MeasEnd']
ET_MeasEnd.restype = c_
ET_SetADCMode = lib['ET_SetADCMode']
ET_SetScanMode = lib['ET_SetScanMode']
ET_SetAmplif = lib['ET_SetAmplif']
# ET_ErrMsg = lib['ET_ErrMsg']
# ET_ErrMsg.restype = c_char
'''

#ET_SetDeviceNumber = lib['ET_SetDeviceNumber']

'''
def WaitADC(t):
	start = time.clock()
	result = False
	dt = time.clock() - start
	while (not result and dt <= t / 1000.):
		result = ET_MeasEnd()
		dt = time.clock() - start
		#pr(dt, t / 1000., dt <= t / 1000., not result)
		# err = ET_ErrMsg()
		# if (err != ""): pr()
	return result
'''
class ET1255(object):

	def __init__(self):
		self.lib = cdll.LoadLibrary("et1255\libet1255.so")
		self.et = self.lib.ET1255_new()

	def ET_StartDrv(self):
		self.lib.ET1255_ET_StartDrv.restype = c_char_p
		return self.lib.ET1255_ET_StartDrv(self.et)

	def ET_SetStrob(self ):
		return self.lib.ET1255_ET_SetStrob(self.et )
	def ET_ReadADC(self ):
		self.lib.ET1255_ET_ReadADC.restype = c_float
		return self.lib.ET1255_ET_ReadADC(self.et )
	def ET_StopDrv(self):
		return self.lib.ET1255_ET_StopDrv(self.et )
	def ET_SetADCChnl(self, chnl):
		return self.lib.ET1255_ET_SetADCChnl(self.et, c_int(chnl))
	def ET_CodeToVolt(self, w):
		self.lib.ET1255_ET_CodeToVolt.restype = c_float
		return self.lib.ET1255_ET_CodeToVolt(self.et, c_int(w))
	def ET_SetScanMode(self, ChCount, ScanEnable):
		return self.lib.ET1255_ET_SetScanMode(self.et, c_int(ChCount),  c_bool(ScanEnable))
	def ET_SetADCMode(self, Frq, PrgrmStart,  Tackt,  MemEnable):
		return self.lib.ET1255_ET_SetADCMode(self.et, c_int(Frq),  c_bool(PrgrmStart),  c_bool(Tackt),  c_bool(MemEnable))
	def ET_SetAmplif(self,  Value):
		return self.lib.ET1255_ET_SetAmplif(self.et,  c_int(Value))
	def ET_MeasEnd(self):
		self.lib.ET1255_ET_MeasEnd.restype = c_int
		return self.lib.ET1255_ET_MeasEnd(self.et)
	def ET_WriteDGT(self,  Value):
		return self.lib.ET1255_ET_WriteDGT(self.et,  c_int(Value))
	def ET_StrobDataRead(self, port, dataFreq):
		return self.lib.ET1255_ET_StrobDataRead(self.et, c_char_p(port.encode('utf-8')), c_float(dataFreq))
	def ET_FStrobDataRead(self, port, fname, dataFreq):
		return self.lib.ET1255_ET_FStrobDataRead(self.et, c_char_p(port.encode('utf-8')), c_char_p(fname.encode('utf-8')), c_float(dataFreq))
	def ET_stopStrobData(self):
		return self.lib.ET1255_ET_stopStrobData(self.et)
	def getData(self):
		ch1 = c_float()
		ch2 = c_float()
		ch3 = c_float()
		ch4 = c_float()
		N = c_long()
		t = c_float()
		angle = c_float()
		self.lib.ET1255_getData(self.et, byref(N),byref(ch1), byref(ch2), byref(ch3), byref(ch4),  byref(t), byref(angle))
		return (N.value,ch1.value,ch2.value,ch3.value,ch4.value, t.value, angle.value)
	def openSerialPort(self, port):
		return self.lib.ET1255_openSerialPort(self.et,c_char_p(port.encode('utf-8')))
	def getAngle(self):
		return self.lib.ET1255_getAngle()
	def setStrobMode(self,  mode):
		return self.lib.ET1255_setStrobMode(self.et,  c_int(mode))

	#def delete(): 
	#	self.FunMath.del_MyMathFuncs()

if __name__ == "__main__":
	import time
	import threading
	et = ET1255()

	laserState = False

	data = []

	n = 0
	v = 0
	stopAll = False
	def laserStrob(delay):
		global laserState
		global stopAll
		print(stopAll)
		if laserState:
			et.ET_WriteDGT(1)
		else:
			et.ET_WriteDGT(0)
		laserState = not laserState
		if not stopAll:
			laserThread = threading.Timer(delay,laserStrob,[delay])
			laserThread.start()


	
	def dataRead(delay):
		global n
		global v
		global data
		global stopAll
		if et.ET_MeasEnd():
			et.ET_SetStrob()
		v = et.ET_ReadADC()+2.5
		data.append(v)
		n += 1
		if not stopAll:
			dataThread = threading.Timer(delay,dataRead,[delay])
			dataThread.start()
		#else: stopAll=True
		#time.sleep(1)

	print(et, c_char_p(et.ET_StartDrv()))
	et.ET_SetAmplif(3)
	print(et.ET_MeasEnd())
	
	et.ET_SetADCChnl(0)
	'''
	laserThread = threading.Timer(0.1,laserStrob, [0.1])
	laserThread.start()

	dataThread = threading.Timer(0.01,dataRead, [0.01])
	dataThread.start()
	
	while(n<100):
		print(n, v, stopAll)
	
	stopAll = True
		#

	print(data)
	'''
	et.openSerialPort("COM7")
	#for i in range(3):
	#print(str(i*10)+"  "+"="*10)
	#f = lambda: et.ET_StrobDataRead(1000)
	f = lambda: et.ET_FStrobDataRead('test.dat', 1000)
	threading.Thread(target=f).start()
	time.sleep(5)
	
	r = et.getData()
	print(r)
	et.ET_stopStrobData()