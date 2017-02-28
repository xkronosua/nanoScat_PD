# -*- coding: utf-8 -*-
import ctypes# give location of dll
from ctypes import c_int, c_bool, c_float, c_double, c_char,  c_ulong, byref
libDLL = ctypes.windll.LoadLibrary("SMD004.dll")

"""  Открыть Com-порт 
function SMD_OpenComPort(AComNmbr: integer): boolean; stdcall; 
Функция открывает COM-порт, и устанавливает заданный номер порта. 
Вход:  AComNmbr - номер COM-порта. Целое число > 0. 
Выход:  TRUE – если операция выполнена, FALSE – еслиимеются ошибки. 
"""

SMD_OpenComPort = libDLL['SMD_OpenComPort']
SMD_OpenComPort.restype = ctypes.c_bool
SMD_OpenComPort.argtypes = (ctypes.c_int,)

"""  Закрыть Com-порт 
function SMD_CloseComPort: boolean; stdcall; 
Выход: TRUE – если операция выполнена, FALSE – еслиимеются ошибки.
"""

SMD_CloseComPort = libDLL['SMD_CloseComPort']
SMD_CloseComPort.restype = ctypes.c_bool

"""  Получить номер COM-порта 
function SMD_GetPortNumber: integer;stdcall; 
Выход:  установленный номер COM-порта.
"""

SMD_GetPortNumber = libDLL['SMD_GetPortNumber']
SMD_GetPortNumber.restype = ctypes.c_int

"""  Установить номер COM-порта 
procedure SMD_SetPortNumber(const Value: integer);stdcall; 
Вход:  Value - номер COM-порта.
"""

SMD_SetPortNumber = libDLL['SMD_SetPortNumber']
SMD_SetPortNumber.restype = ctypes.c_int
SMD_SetPortNumber.argtypes = (c_int, )
"""  Сообщение об ошибке 
function SMD_ErrMsg: PChar; 
Выход:  сообщение об ошибке. Еcли ошибок нет, возвращается пустая строка. 
Рекомендуется  проверять  сообщение  об  ошибке  после  каждого  обращения  к  процедурам  и 
функциям библиотеки.
"""

SMD_ErrMsg = libDLL['SMD_ErrMsg']
SMD_ErrMsg.restype = ctypes.c_char_p

""" Старт двигателя (команда $00) 
function SMD_OnSHD(ATrtAddr: byte; ANumber: integer): boolean; stdcall; 
Вход:  ATrtAddr – адрес модуля SMD-004; 
 ANumber – номер двигателя (0 или 1). 
Выход:  TRUE – если операция выполнена, FALSE – еслиимеются ошибки
"""

SMD_OnSHD = libDLL['SMD_OnSHD']
SMD_OnSHD.restype = c_bool
SMD_OnSHD.argtypes = (c_int, c_int)
"""  Остановка двигателя (команда $01)
function SMD_OffSHD(ATrtAddr: byte; ANumber: integer): boolean; stdcall; 
Вход:  ATrtAddr – адрес модуля SMD-004; 
 ANumber – номер двигателя (0 или 1). 
Выход:  TRUE – если операция выполнена, FALSE – еслиимеются ошибки.
"""

SMD_OffSHD = libDLL['SMD_OffSHD']
SMD_OffSHD.restype = c_bool
SMD_OffSHD.argtypes = (c_int, c_int)


"""  Установка режима вращения (команда $02) 
function SMD_SetMoveParam(ATrtAddr: byte; ANumber: integer; 
AStop, ADirR: boolean; 
AStepCount: longword): boolean; stdcall; 
Вход:  ATrtAddr – адрес модуля SMD-004; 
ANumber – номер двигателя (0 или 1); 
AStop – TRUE - вращение до концевого выключателя или команды СТОП; 
ADirR – TRUE – вращение в прямом направлении, FALSE– в обратном; 
AStepCount – количество шагов (число в диапазоне от1 до 65535). 
Выход:  TRUE – если операция выполнена, FALSE – еслиимеются ошибки.
"""
SMD_SetMoveParam = libDLL['SMD_SetMoveParam']
SMD_SetMoveParam.restype = ctypes.c_bool
SMD_SetMoveParam.argtypes = (c_int, c_int, c_bool, c_bool, c_ulong)

""" Установка тактовой частоты (команда $03) 
function SMD_WriteTactFreq(ATrtAddr: byte; ANumber, Value: integer): boolean; 
stdcall; 
Вход:  ATrtAddr – адрес модуля SMD-004; 
ANumber – номер двигателя (0 или 1); 
Value  –  множитель  полупериода  (число  в  диапазоне  от 1  до  255).  Это  значение 
передается модулю без изменений. 
Выход:  TRUE – если операция выполнена, FALSE – еслиимеются ошибки. 
"""
SMD_WriteTactFreq = libDLL['SMD_WriteTactFreq']
SMD_WriteTactFreq.restype = ctypes.c_bool
SMD_WriteTactFreq.argtypes = (c_int, c_int, c_int)


"""
Установка множителя полупериода тактовой частоты (команда $06)
function SMD_WriteMulty(ATrtAddr: byte;ANumber, Value: integer): boolean; stdcall;
Вход:   ATrtAddr  – адрес модуля SMD004;
ANumber  – номер двигателя (0 или 1);
Value     – множитель  полупериода  (число  в  диапазоне  от  1  до  255).  Это  значение
передается модулю без изменений.
Выход:  TRUE     – если операция выполнена, FALSE – если имеются ошибки.
"""

SMD_WriteMulty = libDLL["SMD_WriteMulty"]
SMD_WriteMulty.restype = c_bool
SMD_WriteMulty.argtypes = (c_int, c_int, c_int)

"""
Установка маршевого тока и тока удержания (команда $07) 
function SMD_WriteMarchIHoldICode(ATrtAddr: byte;
ANumber, AMarchI, AHoldI: integer): boolean; 
stdcall;
Вход:  ATrtAddr  – адрес модуля SMD-004; 
ANumber  – номер двигателя (0 или 1); 
AMarchI  – маршевый ток (код от 0 до 7); 
AHoldI  – ток удержания (код от 0 до 7). 
Код  Ток, A 
0  0 
1  0,4 
2  0,8 
3  1,2 
4  1,6 
5  2,0 
6  2,5 
7  3,0 
Выход: TRUE – если операция выполнена, FALSE – если имеются ошибки. 
"""
SMD_WriteMarchIHoldICode = libDLL['SMD_WriteMarchIHoldICode']
SMD_WriteMarchIHoldICode.restype = ctypes.c_bool
SMD_WriteMarchIHoldICode.argtypes = (c_int, c_int, c_int, c_int)


SMD_GetAddr = libDLL['SMD_GetAddr']
SMD_GetAddr.restype = ctypes.c_int

'''
function SMD_GetState(ATrtAddr: byte;
	var SHDOn1, EndSensor1_0, EndSensor1_8: boolean;
	var Dir1: byte;
	var StepCount1: integer;
	var SHDOn2, EndSensor2_0, EndSensor2_8: boolean;
	var Dir2: byte;
	var StepCount2: integer): boolean; stdcall;
		Вход: ATrtAddr – адрес модуля SMD-004.
		Выход:
		SHDOn1 – TRUE – вращается двигатель, подключенный к каналу 1;
		EndSensor1_0 – TRUE – сработал концевой выключатель для 1-го канала, для прямого
		направления;
		EndSensor1_8 – TRUE – сработал концевой выключатель для 1-го канала, для обратного
		направления;
		Dir1 – 0 – двигатель на 1м канале вращается в прямом направлении, другое
		значение – в обратном;
		StepCount1 - количество шагов, выполненных двигателем на 1м канале;
		SHDOn2 – TRUE – вращается двигатель, подключенный к каналу 2;
		EndSensor2_0 – TRUE – сработал концевой выключатель для 2-го канала, для прямого
		направления;
		EndSensor2_8 – TRUE – сработал концевой выключатель для 2-го канала, для обратного
		направления;
		Dir2 – 0 – двигатель на 2м канале вращается в прямом направлении;
		StepCount2 - количество шагов, выполненных двигателем на 2-м канале.
'''
SMD_GetState = libDLL['SMD_GetState']
SMD_GetState.restype = ctypes.c_bool
SMD_GetState.argtypes = (c_int, ctypes.POINTER(c_int), ctypes.POINTER(c_int), ctypes.POINTER(c_int),
                         ctypes.POINTER(c_int), ctypes.POINTER(c_int),
                         ctypes.POINTER(c_int), ctypes.POINTER(c_int), ctypes.POINTER(c_int),
                         ctypes.POINTER(c_int), ctypes.POINTER(c_int),)


SMD_ClearStep = libDLL['SMD_ClearStep']
SMD_ClearStep.argtypes = (c_int,)
SMD_ClearStep.restype = c_bool

SMD_ResetSHD = libDLL["SMD_ResetSHD"]
SMD_ResetSHD.argtypes = (c_int, c_bool, c_bool)
SMD_ResetSHD.restype = c_bool
'''
function SMD_WritePhaseMode(ATrtAddr: byte; ANumber, Value: integer): boolean
; stdcall;
Вход:   ATrtAddr   – адрес модуля SMD004;
	ANumber  – номер двигателя (0 или 1);
Value     – режим возбуждения фаз двигателя:
00 – волновой режим полного шага;
01 – нормальный режим полного шаг;
10 – половинный шаг.
Выход:  TRUE – если операция выполнена, FALSE – если
 имеются ошибки.  '''
SMD_WritePhaseMode = libDLL["SMD_WritePhaseMode"]
SMD_WritePhaseMode.restype = ctypes.c_bool
SMD_WritePhaseMode.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_int)
##############################################################################
################
ATrtAddr = ctypes.c_int(255)
ANumber = [ctypes.c_int(0), ctypes.c_int(1)]#[::-1]

def getState(ATrtAddr=255, verb=0, wait=True, timeoff=1000):
	SHDOn1 = ctypes.c_int()
	EndSensor1_0 = ctypes.c_int()
	EndSensor1_8 = ctypes.c_int()
	Dir1 = ctypes.c_int()
	StepCount1 = ctypes.c_int()
	SHDOn2 = ctypes.c_int()
	EndSensor2_0 = ctypes.c_int()
	EndSensor2_8 = ctypes.c_int()
	Dir2 = ctypes.c_int()
	StepCount2 = ctypes.c_int()
	if wait:
		prevVal = 0
		for i in range(timeoff):
			SMD_GetState(ATrtAddr, SHDOn1, EndSensor1_0, EndSensor1_8, Dir1, StepCount1,
					SHDOn2, EndSensor2_0, EndSensor2_8, Dir2, StepCount2)
			if StepCount1.value == prevVal:
				break
			else:
				prevVal = StepCount1.value
	else:
		print(SMD_GetState(ATrtAddr, SHDOn1, EndSensor1_0, EndSensor1_8, Dir1, StepCount1,
					SHDOn2, EndSensor2_0, EndSensor2_8, Dir2, StepCount2))
	
	if verb:
		print("On1: %d\tEnd1_0: %d\tEnd1_8: %d\tDir1: %d\tStep1: %d\nOn2: %d\tEnd2_0: %d\tEnd2_8: %d\tDir2: %d\tStep2: %d"%
		      (SHDOn1.value, EndSensor1_0.value, EndSensor1_8.value, Dir1.value, StepCount1.value,
						  SHDOn2.value, EndSensor2_0.value, EndSensor2_8.value, Dir2.value, StepCount2.value))

	return SHDOn1, EndSensor1_0, EndSensor1_8, Dir1, StepCount1, SHDOn2, EndSensor2_0, EndSensor2_8, Dir2, StepCount2


if __name__ == "__main__":
	ATrtAddr = 255
	print(SMD_GetAddr())
	ANumber = [0, 1]#[::-1]
	steps = 0
	COMPortNumber = None
	print(SMD_CloseComPort())
	for i in range(7):
		state = SMD_OpenComPort(i)
		if state:
			print(state)
			COMPortNumber = i
			break


	print(SMD_GetPortNumber())
	print(SMD_SetPortNumber(COMPortNumber),"---")
	#SMD_ClearStep(ATrtAddr)

	print(SMD_GetAddr())
	print(str(SMD_ErrMsg()))
	#print(SMD_OnSHD(ATrtAddr, ANumber[0]))

	print(SMD_ClearStep(ATrtAddr))
	#print(SMD_ResetSHD(ATrtAddr, 1, 1))
	print(SMD_WriteTactFreq(ATrtAddr, ANumber[0],80))
	print(SMD_WriteMarchIHoldICode(ATrtAddr, ANumber[0], 1, 0))
	steps+=1000
	print(SMD_SetMoveParam(ATrtAddr, ANumber[0], 0, 0, 2000))

	print(SMD_OnSHD(ATrtAddr, ANumber[0]))
	SHDOn1, EndSensor1_0, EndSensor1_8, Dir1, StepCount1, SHDOn2, EndSensor2_0, EndSensor2_8, Dir2, StepCount2 = getState(ATrtAddr,1)

	'''
	print(SMD_SetPortNumber(ctypes.c_int32(COMPortNumber)))

	
	print(SMD_WriteTactFreq(ATrtAddr, ANumber[0], ctypes.c_int32(100)))
	print(SMD_WriteMarchIHoldICode(ATrtAddr, ANumber[0], ctypes.c_int(1), ctypes.c_int(0)))
	steps-=50
	print(SMD_SetMoveParam(ATrtAddr, ANumber[0], ctypes.c_int(0), ctypes.c_bool(1), ctypes.c_int32(steps)))
	'''
	n = 0
	import time
	SMD_ClearStep(ATrtAddr)
	getState(ATrtAddr, 1)
	for i in range(10):
		print("Start")
		print(SMD_OnSHD(ATrtAddr, ANumber[0]), n)
		a = 1

		while a:
			state = getState(ATrtAddr, 1)
			SMD_ClearStep(ATrtAddr)
			print(time.time())
			ss = [i.value for i in state]
			if sum(ss)!= 0:
				a = state[0]
			else:
				a = True
			#time.sleep(0.5)
		print("Done")


		n += 1

	getState(ATrtAddr, 1)
	print(SMD_CloseComPort())
