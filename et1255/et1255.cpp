
#include "et1255.h"
#include <iostream>
#include <vector>
#include <sys\timeb.h>
#include <windows.h>								// for Windows APIs
#include <time.h>
#include <sstream>
#include <stdio.h>
#include <cstdlib>
#include <math.h> 
using namespace std;

ET1255::ET1255()
{
	hHandle = INVALID_HANDLE_VALUE;
	laserState = false;
	this->strobDataFlag = true;
	HIGH = 254;
	LOW = 252;
}

void ET1255::ET_StopDrv() {
	CloseHandle(hHandle);

}

char* ET1255::ET_StartDrv() {
	char *dwResult = "ET1255:";
//GUID MID;
//LPTSTR CLASS_STR = L"{20CBE45F-F6F7-4f4a-8F2F-DBB6BF82A46C}";
//UuidFromString((RPC_WSTR)CLASS_STR, &MID);
	cout << "Start...";

	HDEVINFO hDevInfo = SetupDiGetClassDevs( &_GUID_MID, NULL, 0, DIGCF_DEVICEINTERFACE | DIGCF_PRESENT | DIGCF_ALLCLASSES);
	if (hDevInfo == INVALID_HANDLE_VALUE)
	{
		return "ERR_FAIL";
	}

	std::vector<SP_INTERFACE_DEVICE_DATA> interfaces;

	for (DWORD i = 0; true; ++i)
	{
		SP_DEVINFO_DATA devInfo;
		devInfo.cbSize = sizeof(SP_DEVINFO_DATA);
		BOOL succ = SetupDiEnumDeviceInfo(hDevInfo, i, &devInfo);
		if (GetLastError() == ERROR_NO_MORE_ITEMS)
			break;
		if (!succ) continue;

		SP_INTERFACE_DEVICE_DATA ifInfo;
		ifInfo.cbSize = sizeof(SP_INTERFACE_DEVICE_DATA);
		if (TRUE != SetupDiEnumDeviceInterfaces(hDevInfo, &devInfo,	&(_GUID_MID), 0, &ifInfo))
		{
			if (GetLastError() != ERROR_NO_MORE_ITEMS)
				break;
		}
		interfaces.push_back(ifInfo);
	}

	std::vector<SP_INTERFACE_DEVICE_DETAIL_DATA*> devicePaths;
	for (size_t i = 0; i < interfaces.size(); ++i)
	{
		DWORD requiredSize = 0;
		SetupDiGetDeviceInterfaceDetail(hDevInfo, &(interfaces.at(i)), NULL, 0, &requiredSize, NULL);
		SP_INTERFACE_DEVICE_DETAIL_DATA* data = (SP_INTERFACE_DEVICE_DETAIL_DATA*) malloc(requiredSize);
		//Q_ASSERT(data);
		data->cbSize = sizeof(SP_INTERFACE_DEVICE_DETAIL_DATA);

		if (!SetupDiGetDeviceInterfaceDetail(hDevInfo, &(interfaces.at(i)), data, requiredSize, NULL, NULL))
		{
			continue;
		}
		devicePaths.push_back(data);
		//QString s;
		//TCHAR* t = data->DevicePath;
		//s = (LPSTR)(t);

		//cout<<"data: "<<t[1];
		hHandle = CreateFile(data->DevicePath,
		                     GENERIC_READ | GENERIC_WRITE,
		                     FILE_SHARE_READ | FILE_SHARE_WRITE,
		                     NULL,
		                     OPEN_EXISTING,
		                     FILE_ATTRIBUTE_NORMAL,
		                     0);
		if (hHandle == INVALID_HANDLE_VALUE) {
			cout << GetLastError();
			//return "ERR";
		}
		else {
			//	QString s = QString::fromWCharArray(data->DevicePath);
			//	cout<<s;
			break;
		}
	}

	//cout<<hHandle;
	return dwResult;
}
//void ET1255:Get_

void ET1255::ET_SetStrob() {
	DWORD BytesReturned = 0;
	int result = 0;
	result =	DeviceIoControl(hHandle, ioctl_ADC_STROB,
	                            NULL, 0, NULL, 0,
	                            &BytesReturned,
	                            (LPOVERLAPPED)NULL);
	if (!result)
		cout << "Error in <ET_SetStrob> =" << GetLastError();

}

float ET1255::ET_ReadADC() {
	int rdata;
	DWORD BytesReturned;

	if (!DeviceIoControl(hHandle, ioctl_ADC_READ, NULL, 0, &rdata, sizeof(rdata), &BytesReturned, (LPOVERLAPPED)NULL))
	{
		cout << "Error in <ET_ReadADC> =" << GetLastError();
		// return 0;
	}
	else {
		//cout<<rdata<<" "<<BytesReturned;
		return CodeToVolt(rdata & 0x0FFF);//(rdata[0]+rdata[1] >> 8) & 0x0FFF;

	}
}
/*var
	ioctlCode, BytesReturned: cardinal;
	rdata: array[0..1] of byte;
begin
	ioctlCode:=Get_CTL_CODE($804);
	DeviceIoControl(hHandle, ioctlCode, nil, 0, @rdata, sizeof(rdata), BytesReturned, nil);
	Result := (rdata[0] + rdata[1] shl 8) and $0FFF;
end;
Здесь: Result
*/
float ET1255::ET_ReadMem() {
	int rdata;
	DWORD BytesReturned;

	if (!DeviceIoControl(hHandle, ioctl_SCAN_READ, NULL, 0, &rdata, sizeof(rdata), &BytesReturned, (LPOVERLAPPED)NULL))
	{
		cout << "Error in <ET_ReadMem> =" << GetLastError();
		// return 0;
	}
	else {
		//cout<<rdata<<" "<<BytesReturned;
		return CodeToVolt(rdata & 0x0FFF);
	}
}



float ET1255::ET_ReadADC(int n) {
	float res = 0;
	for (int i = 0; i < n; i++) {
		res += this->ET_ReadADC();
	}
	return res / n;
}


void ET1255::ET_SetAddr(int wdata) {
	DWORD BytesReturned = 0;
	int result = 0;
	result =	DeviceIoControl(hHandle, ioctl_MEM_START_WRITE, &(wdata), sizeof(wdata), NULL, 0, &BytesReturned,	(LPOVERLAPPED)NULL);
	if ( !result)	cout << "Error in <ET_SetAddr> =" << GetLastError();

}


void ET1255::ET_SetADCChnl(int chnl) {
	DWORD BytesReturned = 0;
	int result = 0;
	result =	DeviceIoControl(hHandle, ioctl_ADC_WRITE, &(chnl), sizeof(chnl), NULL, 0, &BytesReturned,	(LPOVERLAPPED)NULL);
	if ( !result)	cout << "Error in <ET_SetADCChnl> =" << GetLastError();

}


float ET1255::CodeToVolt(int w) {

	float result = 1;
	int p = 0;
	for (int i = 0; i < 11; i++) {

		p = 11 - 2 * i;
		if (p > 0) result = result + ((w & (1 << i)) << p);
		else		 result = result + ((w & (1 << i)) >> abs(p));
	}
	result = (float)(-2.5 + 5 * result / 0xFFF);
	return result;
}

void ET1255::ET_SetScanMode(int ChCount, bool ScanEnable) {

	DWORD BytesReturned = 0;
	int wdata;

	if (ChCount > 16) ChCount = 16;
	wdata = ChCount;
	if (ScanEnable) wdata = wdata | 0x20;
	if (!DeviceIoControl(hHandle, ioctl_SCAN_WRITE, &wdata, sizeof(wdata), NULL, 0, &BytesReturned, (LPOVERLAPPED)NULL)) {
		cout << "Error in <ET_SetScanMode> =" << GetLastError();
	}

}

void	ET1255::ET_SetADCMode(int Frq, bool PrgrmStart, bool IntTackt, bool MemEnable) {
	DWORD BytesReturned = 0;
	WORD wdata = 0;

	if (Frq > 3) Frq = 3;
	wdata = Frq;
	if (!PrgrmStart) wdata = wdata | 0x04;
	if (!IntTackt)	 wdata = wdata | 0x08;
	if (!MemEnable)	wdata = wdata | 0x10;

	if (!DeviceIoControl(hHandle, ioctl_CTRL_WRITE, &wdata, sizeof(wdata), NULL, 0, &BytesReturned, (LPOVERLAPPED)NULL)) {
		cout << "Error in <ET_SetADCMode> =" << GetLastError();
	}
}

void ET1255::ET_SetAmplif(int Value) {
	this->amplif = Value;
	DWORD BytesReturned = 0;
	if (Value > 15) Value = 15;
	if (!DeviceIoControl(hHandle, ioctl_AMPL_SET, &Value, sizeof(Value), NULL, 0, &BytesReturned, (LPOVERLAPPED)NULL)) {
		cout << "Error in <ET_SetAmplif> =" << GetLastError();
	}
}

void ET1255::ET_WriteDGT(int Value) {
	DWORD BytesReturned = 0;

	if (!DeviceIoControl(hHandle, ioctl_DGT_WRITE, &Value, sizeof(Value), NULL, 0, &BytesReturned, (LPOVERLAPPED)NULL)) {
		cout << "Error in <ET_WriteDGT> =" << GetLastError();
	}
}


int ET1255::ET_ReadDGT() {
	DWORD BytesReturned = 0;
	int rdata;
	if (!DeviceIoControl(hHandle, ioctl_DGT_READ, NULL, 0, &rdata, sizeof(rdata), &BytesReturned, (LPOVERLAPPED)NULL)) {
		cout << "Error in <ET_ReadDGT> =" << GetLastError();
		return -1;
	}
	else return rdata & 0xFF;
}



int ET1255::ET_MeasEnd() {
	DWORD BytesReturned = 0;
	int rdata;



	if (!DeviceIoControl(hHandle, ioctl_CTRL_READ, NULL, 0, &rdata, sizeof(rdata), &BytesReturned, (LPOVERLAPPED)NULL)) {
		cout << "Error in <ET_MeasEnd> =" << GetLastError();
		return -1;
	}
	else return (rdata & 0x0001) == 0x0001;
}

void ET1255::getData(float *ch1, float *ch2, float *ch3, float *ch4, long *N, double *t, float* angle) {
	*ch1 = this->chVal[0];
	*ch2 = this->chVal[1];
	*ch3 = this->chVal[2];
	*ch4 = this->chVal[3];

	*N = this->counter;
	*t = this->lastUpdateTime;
	*angle = this->currentAngle;
	this->lastUpdateTime = 0;
	printf("\n%.4f\t%.4f\t%.4f\t%.4f\t%d\t%.4f\t%.4f\n",*ch1,*ch2,  *ch3,*ch4, *N, *t, *angle);
}

void ET1255::getData_(float *ch1, float *ch2, float *ch3, float *ch4,float *SNRch1, float *SNRch2, float *SNRch3, float *SNRch4, long *N, double *t, float* angle) {
	*ch1 = this->chVal[0];
	*ch2 = this->chVal[1];
	*ch3 = this->chVal[2];
	*ch4 = this->chVal[3];

	*SNRch1 = this->SNR[0];
	*SNRch2 = this->SNR[1];
	*SNRch3 = this->SNR[2];
	*SNRch4 = this->SNR[3];

	*N = this->counter;
	*t = this->lastUpdateTime;
	*angle = getAngle();
	printf("\n%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%d\t%.4f\t%.4f\n",*ch1,*ch2,  *ch3,*ch4, *SNRch1,  *SNRch2,  *SNRch3, *SNRch4, *N, *t, *angle);
	this->lastUpdateTime = 0;
}

void ET1255::ET_stopStrobData()
{
	this->strobDataFlag = false;
	this->arduino->~SerialPort();
}


int ET1255::ET_FStrobDataRead(char *port, char *fname, float dataFreq) {
	openSerialPort(port);
	FILE * pFile;
	pFile = fopen(fname, "a+");
	printf("%s\n", fname);
	LARGE_INTEGER frequency;				// ticks per second
	LARGE_INTEGER t_prevLaser, t_prevData, t_now, t0;					 // ticks
	LARGE_INTEGER angleUpdateTimer;
	double diff = 0, diff_angle=0, laserPeriod = 0;
	QueryPerformanceFrequency(&frequency);
	QueryPerformanceCounter(&t_prevLaser);
	QueryPerformanceCounter(&t_prevData);
	QueryPerformanceCounter(&angleUpdateTimer);
	t0 = angleUpdateTimer = t_prevData;
	//double timeshift = (1 / laserFreq) * phaseshift / 360.;
	float r = 0, SNR = 0;

	int n = 0, m = 0, k = 0;
	float pos[4] = {0, 0, 0, 0};
	float neg[4] = {0, 0, 0, 0};
	this->strobDataFlag = true;

	bool prevState = this->laserState;
	int cyclesToRefresh = 2;
	int nStrobs = 0;
	this->counter = 0;
	fprintf(pFile,"#dataFreq=%.3fHz;\n#ch1\tch2\tch3\tch4\tN\tlastUpdate_time\tlaser_dt\tangle\n",  dataFreq);
	
	while (isStrobDataActive()) {
		QueryPerformanceCounter(&t_now);
		//QueryPerformanceCounter(&angleUpdateTimer);
		diff = (t_now.QuadPart - t_prevData.QuadPart) * 1e3 / frequency.QuadPart;
		diff_angle = (t_now.QuadPart - angleUpdateTimer.QuadPart) * 1e3 / frequency.QuadPart;


		if (diff  >= 1000 / dataFreq) {
			int dgtState = ET_ReadDGT();


			if (dgtState == HIGH) {
				this->laserState = true;
			}
			else {
				this->laserState = false;
			}

			for (int ch = 0; ch < 4; ch++) {
				ET_SetADCChnl(ch);
				r = ET_ReadADC() + 2.5;
				if (this->laserState) {
					n++;
					pos[ch] += (r - pos[ch]) / n;

				}
				else {
					m++;
					r < neg[ch] ? neg[ch]=r: r;
					//neg[ch] += (r - neg[ch]) / m;
				}

				if (ET_MeasEnd()) ET_SetStrob();
			}



			t_prevData = t_now;


			if (this->laserState != prevState) {
				nStrobs++;
				prevState = this->laserState;
				laserPeriod =(t_now.QuadPart - t0.QuadPart) * 1e3 / frequency.QuadPart;
				//timeshift = laserPeriod * phaseshift / 360.;
				if (nStrobs >= cyclesToRefresh) {
					nStrobs = 0; 
					//ET_WriteDGT(0);
					for (int ch = 0; ch < 4; ch++) {
						r = pos[ch] - neg[ch];
						SNR = pow(pos[ch]/neg[ch],2.0);
						if ( this->lastUpdateTime != 0 || k >= 100) {
							k++;
							this->chVal[ch] += (r - this->chVal[ch]) / k ;
							this->SNR[ch] = SNR;
						}
						else {
							k = 0;
							this->chVal[ch] = r;
							this->SNR[ch] = SNR;
						}
						fprintf(pFile,"%.6f\t", r/this->amplif);
						pos[ch] = neg[ch] = 0;

					}
					//printf("%.4f\n",this->currentAngle );
					n = m = 0;
					this->counter++;
					//cout<<"dgt" <<ET_ReadDGT()<<"dgt\n";
					//(t_now.QuadPart) * 1e3 / frequency.QuadPart;
					//this->currentAngle = getAngle();
					fprintf(pFile, "%d\t%.2f\t%f\t%.1f\n", this->counter, this->lastUpdateTime, laserPeriod, getAngle(diff_angle));
					this->lastUpdateTime = 0;
				}
				t_prevLaser = t_now;
				if(diff_angle>3) angleUpdateTimer = t_now;
			}
			else {

			}

			//t_prevData = t_now;
		}
	}


	fclose (pFile);
	return 0;
}
int ET1255::ET_StrobDataRead(char *port,  float dataFreq) {
	openSerialPort(port);
	//FILE * pFile;
	//pFile = fopen(fname, "a+");
	//printf("%s\n", fname);
	LARGE_INTEGER frequency;				// ticks per second
	LARGE_INTEGER t_prevLaser, t_prevData, t_now, t0;					 // ticks
	LARGE_INTEGER angleUpdateTimer;
	double diff = 0, diff_angle=0, laserPeriod = 0;
	QueryPerformanceFrequency(&frequency);
	QueryPerformanceCounter(&t_prevLaser);
	QueryPerformanceCounter(&t_prevData);
	QueryPerformanceCounter(&angleUpdateTimer);
	t0 = angleUpdateTimer = t_prevData;
	//double timeshift = (1 / laserFreq) * phaseshift / 360.;
	float r = 0, SNR = 0;

	int n = 0, m = 0, k = 0;
	float pos[4] = {0, 0, 0, 0};
	float neg[4] = {0, 0, 0, 0};
	this->strobDataFlag = true;

	bool prevState = this->laserState;
	int cyclesToRefresh = 2;
	int nStrobs = 0;
	this->counter = 0;
	printf("#dataFreq=%.3fHz;\n#ch1\tch2\tch3\tch4\tN\tlastUpdate_time\tlaser_dt\tangle\n",  dataFreq);
	
	while (isStrobDataActive()) {
		QueryPerformanceCounter(&t_now);
		//QueryPerformanceCounter(&angleUpdateTimer);
		diff = (t_now.QuadPart - t_prevData.QuadPart) * 1e3 / frequency.QuadPart;
		diff_angle = (t_now.QuadPart - angleUpdateTimer.QuadPart) * 1e3 / frequency.QuadPart;


		if (diff  >= 1000 / dataFreq) {
			int dgtState = ET_ReadDGT();


			if (dgtState == HIGH) {
				this->laserState = true;
			}
			else {
				this->laserState = false;
			}

			for (int ch = 0; ch < 4; ch++) {
				ET_SetADCChnl(ch);
				r = ET_ReadADC() + 2.5;
				if (this->laserState) {
					n++;
					pos[ch] += (r - pos[ch]) / n;

				}
				else {
					m++;
					r < neg[ch]? neg[ch]=r: r;
					//neg[ch] += (r - neg[ch]) / m;
				}

				if (ET_MeasEnd()) ET_SetStrob();
			}



			t_prevData = t_now;


			if (this->laserState != prevState) {
				nStrobs++;
				prevState = this->laserState;
				laserPeriod =(t_now.QuadPart - t0.QuadPart) * 1e3 / frequency.QuadPart;
				//timeshift = laserPeriod * phaseshift / 360.;
				if (nStrobs >= cyclesToRefresh) {
					nStrobs = 0; 
					//ET_WriteDGT(0);
					for (int ch = 0; ch < 4; ch++) {
						r = pos[ch] - neg[ch];
						SNR = pow(pos[ch]/neg[ch],2.0);
						if ( this->lastUpdateTime != 0 || k >= 100) {
							k++;
							this->chVal[ch] += (r - this->chVal[ch]) / k;
							this->SNR[ch] = SNR;
						}
						else {
							k = 0;
							this->chVal[ch] = r;
							this->SNR[ch] = SNR;
						}
						printf("%.6f\t", r/this->amplif);
						pos[ch] = neg[ch] = 0;

					}
					n = m = 0;
					this->counter++;
					//cout<<"dgt" <<ET_ReadDGT()<<"dgt\n";
					//(t_now.QuadPart) * 1e3 / frequency.QuadPart;
					//this->currentAngle = getAngle();
					printf("%d\t%.2f\t%f\t%.1f\n", this->counter, this->lastUpdateTime, laserPeriod, getAngle(diff_angle));
					this->lastUpdateTime = 0;
				}
				t_prevLaser = t_now;
				if(diff_angle>3) angleUpdateTimer = t_now;
			}
			else {

			}

			//t_prevData = t_now;
		}
	}


	//fclose (pFile);
	return 0;
}

int ET1255::openSerialPort(char *port) {
	(this->arduino) = new SerialPort(port);
	if (this->arduino->isConnected()) {cout << "Connection Established" << endl;
	this->arduino->writeSerialPort("RM\n",4);
	}
	else cout << "ERROR, check port name";

	return 0;
}

float ET1255::getAngle() {
	if (this->arduino->isConnected()) {
			char incomingData[4];
			this->arduino->writeSerialPort("3",1);
			
			DWORD read_result = this->arduino->readSerialPort(incomingData, 4);
			//DWORD read_result = this->arduino->readSerialPort(incomingData, 4);
			float ang = atof(incomingData);
			//cout<<"\nID"<<incomingData<<"\n";
			//printf("\nA=%f\n",ang);
			
			
			char s[1];
			read_result = this->arduino->readSerialPort(s, 1);
			int cs = 0;
			UStuff f;
			//printf("\n");
			for (int i=0;i<4;i++) {
				cs+=incomingData[i];
				f.c[i] = incomingData[i];
				//printf("0x%02x ", incomingData[i]);
			}
			this->currentAngle = f.f;
			//printf("\nA:%f\n",this->currentAngle );
			return f.f;
			//cs = abs(cs);
			//printf("%f\t%d\t%d\n", f.f, cs, ord(s));
			//if (cs>255) cs-=255;
			//if (cs==abs(incomingData[4])){
			//	this->currentAngle = f.f;
				//return f.f;

			//}
			//else {
			//	this->currentAngle = f.f;
			//	return f.f;
			//}
		}
		else return 0;
}

float ET1255::getAngle(double diff) {
	//printf("\nDiff%f\n",diff);
	if (diff  >= 3) {
		if (this->arduino->isConnected()) {
			char incomingData[4];
			this->arduino->writeSerialPort("3",1);
			
			DWORD read_result = this->arduino->readSerialPort(incomingData, 4);
			//DWORD read_result = this->arduino->readSerialPort(incomingData, 4);
			float ang = atof(incomingData);
			//cout<<"\nID"<<incomingData<<"\n";
			//printf("\nA=%f\n",ang);
			
			
			char s[1];
			read_result = this->arduino->readSerialPort(s, 1);
			int cs = 0;
			UStuff f;
			//printf("\n");
			for (int i=0;i<4;i++) {
				cs+=incomingData[i];
				f.c[i] = incomingData[i];
				//printf("0x%02x ", incomingData[i]);
			}
			this->currentAngle = f.f;
			//printf("\nA:%f\n",this->currentAngle );
			return f.f;
			//cs = abs(cs);
			//printf("%f\t%d\t%d\n", f.f, cs, ord(s));
			//if (cs>255) cs-=255;
			//if (cs==abs(incomingData[4])){
			//	this->currentAngle = f.f;
				//return f.f;

			//}
			//else {
			//	this->currentAngle = f.f;
			//	return f.f;
			//}
		}
		else return 0;

	}
	else{
		return this->currentAngle;
	}
}

using std::cout;
using std::endl;

SerialPort::SerialPort(char *portName)
{
	this->connected = false;

	this->handler = CreateFileA(static_cast<LPCSTR>(portName),
	                            GENERIC_READ | GENERIC_WRITE,
	                            0,
	                            NULL,
	                            OPEN_EXISTING,
	                            FILE_ATTRIBUTE_NORMAL,
	                            NULL);
	if (this->handler == INVALID_HANDLE_VALUE) {
		if (GetLastError() == ERROR_FILE_NOT_FOUND) {
			printf("ERROR: Handle was not attached. Reason: %s not available\n", portName);
		}
		else
		{
			printf("ERROR!!!");
		}
	}
	else {
		DCB dcbSerialParameters = {0};

		if (!GetCommState(this->handler, &dcbSerialParameters)) {
			printf("failed to get current serial parameters");
		}
		else {
			dcbSerialParameters.BaudRate = CBR_19200;
			dcbSerialParameters.ByteSize = 8;
			dcbSerialParameters.StopBits = ONESTOPBIT;
			dcbSerialParameters.Parity = NOPARITY;
			dcbSerialParameters.fDtrControl = DTR_CONTROL_DISABLE;

			if (!SetCommState(handler, &dcbSerialParameters))
			{
				printf("ALERT: could not set Serial port parameters\n");
			}
			else {
				this->connected = true;
				PurgeComm(this->handler, PURGE_RXCLEAR | PURGE_TXCLEAR);
				Sleep(ARDUINO_WAIT_TIME);
			}
		}
	}
}

SerialPort::~SerialPort()
{
	if (this->connected) {
		this->connected = false;
		CloseHandle(this->handler);
	}
}


int SerialPort::readSerialPort(char *buffer, unsigned int buf_size)
{
    DWORD bytesRead;
    unsigned int toRead;

    ClearCommError(this->handler, &this->errors, &this->status);

    if (this->status.cbInQue > 0){
        if (this->status.cbInQue > buf_size){
            toRead = buf_size;
        }
        else toRead = this->status.cbInQue;
    }

    if (ReadFile(this->handler, buffer, toRead, &bytesRead, NULL)) {
    	PurgeComm( this->handler, PURGE_TXABORT |
					   PURGE_RXABORT |
					   PURGE_TXCLEAR |
					   PURGE_RXCLEAR );	
    	return bytesRead;}

    return 0;
}

bool SerialPort::writeSerialPort(char *buffer, unsigned int buf_size)
{
	DWORD bytesSend;

	if (!WriteFile(this->handler, (void*) buffer, buf_size, &bytesSend, 0)) {
		ClearCommError(this->handler, &this->errors, &this->status);
		return false;
	}
	else return true;
}

bool SerialPort::isConnected()
{
	return this->connected;
}





/*
int main(int argc, char *argv[])
{
	 // QCoreApplication a(argc, argv);


	ET1255 et;
	char* aa = et.ET_StartDrv();


	cout<<"aaa<<"<<aa;
	et.ET_StopDrv();
	aa = et.ET_StartDrv();


	cout<<"aaa<<"<<aa;

	//et.ET_SetStrob();
	//et.ET_SetStrob();
	et.ET_SetADCChnl(0);
	et.ET_SetAmplif(5);
	et.ET_SetScanMode(0, false);
	et.ET_SetADCMode(0, 1, 1, 0);


	float r = 0;
	int ch = 1;
	 // delay(5000);
	int strob=0;
	for (int i=0; i<20; i++){
		//delay(5);
		for (ch=0;ch<1;ch++){
		et.ET_SetADCChnl(ch);
		r = et.ET_ReadADC();
		cout<<r;
		strob = et.ET_MeasEnd();
		if(strob) et.ET_SetStrob();
		}
	}
	et.ET_StopDrv();
	 // return a.exec();
}
*/