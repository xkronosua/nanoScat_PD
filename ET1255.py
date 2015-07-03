__author__ = 'Admin'
from ctypes import *
import time

lib = WinDLL('C:\\WINDOWS\\ET1255.dll', use_last_error=True)
lib1 = WinDLL('C:\\WINDOWS\\Project2.dll', use_last_error=True)
# lib = ctypes.WinDLL('full/path/to/mylibrary.dll')

ET_SetADCChnl = lib['ET_SetADCChnl']
ET_SetADCChnl.restype = c_int
ET_StartDrv = lib1['test1']
#ET_StartDrv.argtypes = []#c_wchar_p, c_int]  # lib['ET_StartDrv']#my func is double myFunc(double);
#ET_StartDrv.restype = c_long
ET_ReadADC = lib['ET_ReadADC']
ET_ReadADC.restype = c_float
# opt_flag = ctypes.c_char_p.in_dll(lib, "ET1255_DLL_Name")
ET_SetDeviceCount = lib['ET_SetDeviceCount']
ET_SetStrob = lib['ET_SetStrob']
ET_MeasEnd = lib['ET_MeasEnd']
ET_MeasEnd.restype = c_bool
ET_SetADCMode = lib['ET_SetADCMode']
ET_SetScanMode = lib['ET_SetScanMode']
ET_SetAmplif = lib['ET_SetAmplif']
# ET_ErrMsg = lib['ET_ErrMsg']
# ET_ErrMsg.restype = c_char


ET_SetDeviceNumber = lib['ET_SetDeviceNumber']


def WaitADC(t):
    start = time.clock()
    result = False
    dt = time.clock() - start
    while (not result and dt <= t / 1000.):
        result = ET_MeasEnd()
        dt = time.clock() - start
        #print(dt, t / 1000., dt <= t / 1000., not result)
        # err = ET_ErrMsg()
        # if (err != ""): print()
    return result