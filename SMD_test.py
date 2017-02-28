import serial
import time
import codecs
import base64
import threading
import traceback

class SMD004():
	ser = None
	def __init__(self, parent=None):
		self.eInit()
		ser = None
	def eInit(self):
		pass
		#self.ser = serial.Serial("COM3", baudrate=19200, timeout=0.05, bytesize=serial.EIGHTBITS)
		#print(self.write_(b'\xFF\x07\x03\x01\x04\x01'))#b"FF0703010101")
		#print(self.write_(b'\xFF\x06\x02\x01\x01'))#b"FF06020101")
		#print(self.write_(b'\xFF\x03\x05\x01\x60\x00\x00\x00'))#b"FF03050132000000")
		#print(self.write_(b"\xFF\x04\x00"))
		#print(self.write_(b"\xFF\x08\x02\x01\x01"))

	def eOpenCOMPort(self,port=1):
		self.ser = serial.Serial("COM"+str(port), baudrate=19200, timeout=0.05, bytesize=serial.EIGHTBITS)
	def eStop(self, stepper=3):
		'''
		Назначение: стоп вращения двигателя.
		Байт		1-й		2-й		3-й		4-й											5-й
		Значение	Адрес	01 hex	01 hex	01 hex – стоп 1-го двигателя
											02 hex – стоп 2-го двигателя
											03 hex – стоп двух двигателей одновременно	Контроль¬ная сумма
		Ответ модуля: возвращает принятые байты без изменений.
		'''
		#self.write(b"FF010101")
		self.write(b"FF01010"+ str(stepper).encode())

	
	def eStart(self, stepper=1):	
		'''
		Назначение: старт вращения двигателя.
		Байт		1-й		2-й		3-й		4-й								5-й
		Значение	Адрес	00 hex	01 hex	01 hex – старт 1-го двигателя	Контроль¬ная сумма
											02 hex – старт 2-го двигателя
											03 hex – старт двух двигателей одновременно	
		Ответ модуля: возвращает принятые байты без изменений.
		'''
		self.write(b"FF00010" + str(stepper).encode())

	def eSetParams(self,stepper=1,mode='ccw_step',steps=0):
		'''
		Назначение: установка режима вращения двигателя.
		Байт		1-й		2-й		3-й		4-й		5-й
		Значение	Адрес	02 hex	04 hex	Номер двигателя	00 hex – вращение до кон¬це¬во-го выклю¬ча¬теля или ко¬манды "Стоп"
															01 hex – вращение на заданное количество шагов
															80 hex и 81 hex – то же, но в обратную сторону

		Байт		6-й							7-й							8-ой
		Значение	Младший байт числа шагов	Старший байт числа шагов	Контроль¬ная сумма
		Ответ модуля: возвращает принятые байты без изменений.     

		'''
		m = {'ccw_step' : b'\x01',
			 'ccw2stop' : b'\x00',
			 'cw_step'  : b'\x81',
			 'cw2stop'  : b'\x80',

		}
		s = bytearray(self.int2B(steps))#[str(i) for i in int(steps).to_bytes(2,'little')]
		
		#if len(s)<4:
		#	if len(s[0])<len(s[1]): s[0] = '0'+s[0]
		#	elif len(s[0])>len(s[1]): s[1] = '0'+s[1]
		
		self.write_(b"\xFF\x02\x04"+bytearray([stepper]) + m[mode]+s)
	def eSetTactFreq(self, stepper=1, freq=68):
		'''
		Назначение: установка скорости вращения двигателя.
		Байт		1-й		2-й		3-й		4-й				5-й	6-й	7-й	8-й																								9-й
		Значение	Адрес	03 hex	05 hex	Номер двигателя	Длительность полу-периода тактовой частоты дви¬га¬теля в десятках микро¬се-кунд (млад¬шим байтом впе¬ред)	Контроль¬ная сумма
		Ответ модуля: возвращает принятые байты без изменений
		'''
		print(self.write_(b'\xFF\x03\x05'+bytearray([stepper])+(freq).to_bytes(4,'little')))

	def isConnected(self):
		try:
			self.ser.inWaiting()
			return 1
		except:
			print ("Lost connection!")
			return 0
	def eClearStep(self, stepper=3):
		'''
		Назначение: обнуление счетчика шагов.
		Байт		1-й		2-й		3-й		4-й											5-й
		Значение	Адрес	05 hex	01 hex	01 hex – для 1-го двигателя
											02 hex – для 2-го двигателя
											03 hex – для двух двигателей одновременно	Контроль¬ная сумма
		Ответ модуля: возвращает принятые байты без изменений.

		'''
		print(self.write_(b'\xFF\x05\x01'+bytearray([stepper])))
	def eSetMulty(self,stepper=1, multy=1):
		'''
		Назначение: установка множителя полупериода тактовой частоты двигателя.
		Байт		1-й		2-й		3-й		4-й					5-й					6-й
		Значение	Адрес	06 hex	02 hex	Номер дви¬га-те¬ля	Множитель (1…255)	Контроль¬ная сумма
		Ответ модуля: возвращает принятые байты без изменений.
		Примечание к команде 6.
		Фактическая длительность полупериода тактовой частоты равна величине, заданной командой 3, умноженной на величину множителя, заданную данной командой.
		'''
		print(self.write_(b'\xFF\x06\x02'+bytearray([stepper])+bytearray([multy])))
	def eSetMarchIHoldICode(self,stepper, Im=0, Is=0):
		'''
		Назначение: установка маршевого тока и тока удержания двигателей.
		Байт		1-й		2-й		3-й		4-й					5-й					6-й						7-й
		Значение	Адрес	07 hex	03 hex	Номер дви¬га¬те¬ля	Марше-вый ток (0…7)	Ток удер-жа¬ния (0…7)	Контроль¬ная сумма
		Ответ модуля: возвращает принятые байты без изменений.
		Зависимость тока от передаваемого данной командой номера ступени:
		Ступень	Ток, A
		0	0
		1	0,4
		2	0,8
		3	1,2
		4	1,6
		5	2,0
		6	2,5
		7	3,0
		Примечание к команде 7.
		Следует помнить, что ток обмоток двигателя ограничивается также их омическим сопротивлением.
		Например, для двигателя, имеющего сопротивление обмоток 10 Ом при напряжении питания 12 В,
		 будет иметь влияние только установка ступеней с 0 по 3. Установка ступеней с 4 по 
		 7 не будет оказывать влияние, т.к. ток будет ограничен сопротивлением обмоток на уровне 
		 1,2 А. Изменить значения ступеней регулирования тока можно только изменением номиналов электронных 
		 компонентов внутри модуля.
		'''
		print(self.write_(b'\xFF\x07\x03'+bytearray([stepper])+bytearray([Im])+bytearray([Is])))
	def eSetPhaseMode(self, stepper, mode='1x'):
		'''
		•	Команда 8.
		Назначение: задание режима возбуждения фаз двигателя.
		Байт	1-й	2-й	3-й	4-й	5-й	6-й
		Значение	Адрес	08 hex	02 hex	Номер дви¬га¬те¬ля	Режим	Контроль¬ная сумма
		Ответ модуля: возвращает принятые байты без изменений.
		Режим кодируется 2 младшими битами байта 5:
		00 – волновой режим полного шага (в каждый момент времени включена только 1 фаза);
		01 – нормальный режим полного шаг (в каждый момент времени включены одновременно 2 смежные фазы);
		1х – половинный шаг.
		Примечание к команде 8.
		Задание любого из режимов полного шага возможно только из режима половинного шага.
		Подача команды на переключение одного режима полного шага в другой режим полного шага
		без промежуточного выхода в режим половинного шага не даст никакого эффекта. По умолчанию,
		после включения питания, модуль инициализируется в режим половинного шага.
		'''
		#m = {'00':}
		print(self.write_(b'\xFF\x08\x02'+bytearray([stepper])+b'\x10'))
		print(self.write_(b'\xFF\x08\x02'+bytearray([stepper])+bytearray([mode])))
	def makeStepCCW(self, stepper=1, steps=0, waitUntilReady=True):
		
		state = self.eGetState(0.02)
		print('State', state)
		def f():
			self.eSetParams(1,'ccw_step',steps)
			self.eStart(1)
		if state[3] == 0:
			f()
		else:
			threading.Timer(1, f).start()

	def makeStepCW(self, stepper=1, steps=0, waitUntilReady=True):
		state = self.eGetState(0.02)

		print('State', state)
		def f():
			self.eSetParams(1,'cw_step',steps)
			self.eStart(1)
		if state[3] == 0:
			f()
		else:
			threading.Timer(1, f).start()
			
	def moveCCW(self, stepper=1, steps=0):
		self.eSetParams(1,'ccw2stop',steps)
		self.eStart(1)
	def moveCW(self, stepper=1, steps=0):
		self.eSetParams(1,'cw2stop',steps)
		self.eStart(1)

	def eGetState(self,delay=0.01):
		'''
		Назначение: запрос состояния двигателей.
		Байт	1-й	2-й	3-й	4-й
		Значение	Адрес	04 hex	00 hex	Контроль¬ная сумма
		Ответ модуля:
		Байт	1-й	2-й	3-й	4-й	5-й	6-й	7-й
		Значение	Адрес	04 hex	08 hex	Текущее со¬стояние двигателей	Режим дви¬га¬те-ля №1	Счетчик шагов дви-га¬те¬ля №1 (млад¬шим бай¬том впе¬ред)

		Байт	8-й	9-й	10-й	11-й	12 -ой
		Значение	Режим дви¬га¬те-ля №2	Счетчик шагов дви-га¬те¬ля №2 (млад¬шим бай¬том впе¬ред)	Состояние концевых выключателей	Контроль¬ная сумма
		Байт текущего состояния двигателей:
		00 hex – оба двигателя остановлены;
		01 hex – вращается 1-й двигатель, второй остановлен;
		02 hex – вращается 2-й двигатель, первый остановлен;
		03 hex – оба двигателя вращаются.
		Байты режима двигателей – так же, как и в команде 2, 5-й байт.
		Состояние концевых выключателей:
		Байт состояния концевых выключателей
		Бит 7	Бит 6	Бит 5	Бит 4	Бит 3	Бит 2	Бит 1	Бит 0
		K2.2	K2.1	K1.2	K1.1	x	x	x	x
		Младшие 4 бита – незначащие.
		Примечание к команде 4.
		Счетчики шагов двигателей – счетчики количества шагов с учетом направления вращения, с момента включения питания модуля или последнего обнуления счетчика (командой 5). Емкость счетчиков – 2 байта. Пример 1. После включения питания модуля двигатель сделал 200 шагов в прямом направлении и 50 – обратном. Значение счетчика шагов составит 150.
		Пример 2. После включения питания модуля двигатель сделал 100 шагов в обратном направлении. Значение счетчика шагов составит 65436 (т.е. 65536 –100).

		'''
		r = self.write(b"FF0400",delay)
		#time.sleep(0.5)
		#r = self.ser.readline(12)
		return r

	def write(self, data,sleep=0.01):
		s = data
		s = self.cSum(s)
	
		# s = s.replace('\x','')
		
		print( data, s, self.str2hex(s),type(s), '='*10)
		#s = bytes(s, 'utf-8')
		#self.ser.baudrate = 19200
		self.ser.parity = serial.PARITY_MARK
		#self.ser.bytesize = serial.EIGHTBITS
		self.ser.stopbits = serial.STOPBITS_ONE
		self.ser.write(s[:2])
		print(self.str2hex(s[:2]))
		
		#self.ser.baudrate = 19200
		self.ser.parity = serial.PARITY_SPACE
		#self.ser.bytesize = serial.EIGHTBITS
		self.ser.stopbits = serial.STOPBITS_ONE
		self.ser.write(s[2:])
		print(self.str2hex(s[2:]))
		#self.ser.read() 
		time.sleep(sleep)
		r = self.ser.readline(12)
		print(">"*10,codecs.encode(r,'hex'), r)
		return r
	def write_(self, data,sleep=0.01):
		s = data
		s = self.cSum(s,bytesA=True)
	
		# s = s.replace('\x','')
		
		print( data, s, self.str2hex(s),type(s), '='*10)
		#s = bytes(s, 'utf-8')
		#self.ser.baudrate = 19200
		self.ser.parity = serial.PARITY_MARK
		#self.ser.bytesize = serial.EIGHTBITS
		self.ser.stopbits = serial.STOPBITS_ONE
		self.ser.write(s[:2])
		print(self.str2hex(s[:2]))
		
		#self.ser.baudrate = 19200
		self.ser.parity = serial.PARITY_SPACE
		#self.ser.bytesize = serial.EIGHTBITS
		self.ser.stopbits = serial.STOPBITS_ONE
		self.ser.write(s[2:])
		print(self.str2hex(s[2:]))
		#self.ser.read() 
		time.sleep(sleep)
		r = self.ser.readline(12)
		print(">"*10,codecs.encode(r,'hex'), r)
		return r
	def int2B(self, b):
		return (b&0xff, (b&0xff00)>>8)


	def str2hex(self, InputString):
		InputString = base64.b16encode(InputString)
		return InputString#''.join('{:02x}'.format(ord(c)) for c in InputString)
	
	def cSum(self, string, bytesA=False):
		if not bytesA:
			bb = base64.b16decode(string)
		else: bb = string
		s = sum(bb[:-1])
		print(s)
		if s > 255:
			s = bytearray((s).to_bytes(2, 'little'))[1]
		string = bb + chr(s).encode('utf-8')

		return string


if __name__ == "__main__":
	e = SMD004()
	e.eOpenCOMPort(3)
	print(e.str2hex(b"Hello"))
	print(e.str2hex(b"\n\r"))
	#print(''.join('{:02x}'.format(ord(c)) for c in 'Hello'))
	
	try:
		#e.eStartLeft()
		#f = lambda : e.eStop()
		import time
		#time.sleep(2)
		#e.eStop()
		e.eSetTactFreq(1,50)
		e.eClearStep(3)
		e.eSetMulty(1,10)
		#e.makeStepCCW(steps=600)
		#e.makeStepCW(steps=300)
		#e.eStartLeft()
		#time.sleep(4)
		#e.makeStepCW(steps=600)

		#e.eStartRight()
		#e.eGetState()
		#time.sleep(2)
		#e.eStop()
		e.eGetState()
		print('+'*10,e.isConnected())
		e.eSetMarchIHoldICode(1,1,0)
		e.eSetPhaseMode(1,1)
		e.moveCCW(1)
		#threading.Timer(f,10)
		time.sleep(4)
		e.eStop()
	except:
		traceback.print_exc()
		e.ser.close()	
	e.ser.close()
	print(e.isConnected())

