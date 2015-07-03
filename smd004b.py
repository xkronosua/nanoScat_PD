
import ctypes# give location of dll
libDLL = ctypes.WinDLL("C:\\Windows\\SMD004.dll")

"""  Открыть Com-порт 
function SMD_OpenComPort(AComNmbr: integer): boolean; stdcall; 
Функция открывает COM-порт, и устанавливает заданный номер порта. 
Вход:  AComNmbr - номер COM-порта. Целое число > 0. 
Выход:  TRUE – если операция выполнена, FALSE – еслиимеются ошибки. 
"""

SMD_OpenComPort = libDLL['SMD_OpenComPort']
SMD_OpenComPort.restype = ctypes.c_bool

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
SMD_GetPortNumber.restype = ctypes.c_int32

"""  Установить номер COM-порта 
procedure SMD_SetPortNumber(const Value: integer);stdcall; 
Вход:  Value - номер COM-порта.
"""

SMD_SetPortNumber = libDLL['SMD_SetPortNumber']
SMD_SetPortNumber.restype = ctypes.c_int

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
SMD_OnSHD.restype = ctypes.c_bool

"""  Остановка двигателя (команда $01) 
function SMD_OffSHD(ATrtAddr: byte; ANumber: integer): boolean; stdcall; 
Вход:  ATrtAddr – адрес модуля SMD-004; 
 ANumber – номер двигателя (0 или 1). 
Выход:  TRUE – если операция выполнена, FALSE – еслиимеются ошибки.
"""

SMD_OffSHD = libDLL['SMD_OffSHD']
SMD_OffSHD.restype = ctypes.c_bool


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

SMD_ClearStep = libDLL['SMD_ClearStep']

##############################################################################
################
ATrtAddr = ctypes.c_int(255)
ANumber = [ctypes.c_int(0), ctypes.c_int(1)]#[::-1]

def getState(verb=0):
        SHDOn1 = ctypes.c_int(0)
        EndSensor1_0 = ctypes.c_int(0)
        EndSensor1_8 = ctypes.c_int(0)
        Dir1 = ctypes.c_int(0)
        StepCount1 = ctypes.c_int(0)
        SHDOn2 = ctypes.c_int(0)
        EndSensor2_0 = ctypes.c_int(0)
        EndSensor2_8 = ctypes.c_int(0)
        Dir2 = ctypes.c_int(0)
        StepCount2 = ctypes.c_int(0)
        
        SMD_GetState(ATrtAddr, ctypes.byref(SHDOn1), ctypes.byref(EndSensor1_0), ctypes.byref(EndSensor1_8), ctypes.byref(Dir1), ctypes.byref(StepCount1),
        		       ctypes.byref(SHDOn2), ctypes.byref(EndSensor2_0), ctypes.byref(EndSensor2_8), ctypes.byref(Dir2), ctypes.byref(StepCount2))
        if verb:
               print((SHDOn1), (EndSensor1_0), (EndSensor1_8), (Dir1), (StepCount1),
						  (SHDOn2), (EndSensor2_0), (EndSensor2_8), (Dir2), (StepCount2))
        return SHDOn1, EndSensor1_0, EndSensor1_8, Dir1, StepCount1, SHDOn2, EndSensor2_0, EndSensor2_8, Dir2, StepCount2


if __name__ == "__main__":
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


	print(SMD_WriteTactFreq(ATrtAddr, ANumber[0], ctypes.c_int32(78)))
	print(SMD_WriteMarchIHoldICode(ATrtAddr, ANumber[0], ctypes.c_int(1), ctypes.c_int(0)))
	steps+=1000
	print(SMD_SetMoveParam(ATrtAddr, ANumber[0], ctypes.c_int(0), ctypes.c_bool(0), ctypes.c_int32(100)))
	SHDOn1 = ctypes.c_int(0)
	EndSensor1_0 = ctypes.c_int(0)
	EndSensor1_8 = ctypes.c_int(0)
	Dir1 = ctypes.c_int(0)
	StepCount1 = ctypes.c_int(0)
	SHDOn2 = ctypes.c_int(0)
	EndSensor2_0 = ctypes.c_int(0)
	EndSensor2_8 = ctypes.c_int(0)
	Dir2 = ctypes.c_int(0)
	StepCount2 = ctypes.c_int(0)
	print(SMD_OnSHD(ATrtAddr, ANumber[0]))
	SMD_GetState(ATrtAddr, ctypes.byref(SHDOn1), ctypes.byref(EndSensor1_0),
                     ctypes.byref(EndSensor1_8), ctypes.byref(Dir1), ctypes.byref(StepCount1),
						  ctypes.byref(SHDOn2), ctypes.byref(EndSensor2_0),
                     ctypes.byref(EndSensor2_8), ctypes.byref(Dir2), ctypes.byref(StepCount2))
	print((SHDOn1), (EndSensor1_0), (EndSensor1_8), (Dir1), (StepCount1),
						  (SHDOn2), (EndSensor2_0), (EndSensor2_8), (Dir2), (StepCount2))
	'''
	print(SMD_SetPortNumber(ctypes.c_int32(COMPortNumber)))

	
	print(SMD_WriteTactFreq(ATrtAddr, ANumber[0], ctypes.c_int32(100)))
	print(SMD_WriteMarchIHoldICode(ATrtAddr, ANumber[0], ctypes.c_int(1), ctypes.c_int(0)))
	steps-=50
	print(SMD_SetMoveParam(ATrtAddr, ANumber[0], ctypes.c_int(0), ctypes.c_bool(1), ctypes.c_int32(steps)))
	'''
	print(SMD_CloseComPort())
