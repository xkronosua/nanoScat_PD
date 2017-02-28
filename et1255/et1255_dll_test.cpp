#include <iostream>
#include "et1255.h"
#include <windows.h>
using namespace std;
int main(int argc, char* argv[] )
{
  	char port[4] = "COM";
  	port[3] = argv[1][0];
  	printf("|%s|\n",port);
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
    //delay(5000);
    int strob=0;
    int j=0;
    bool state=false;
   // for (int i=0;i<1000;i++){
    //	printf("%d\n",et.ET_ReadDGT());
   // }
    //et.ET_WriteDGT(3);
   // et.openSerialPort(port);

    //printf("\n%f\n",et.getAngle());
      
    //et.ET_StrobDataRead(port, 500);
    et.ET_FStrobDataRead(port,"test.dat",500);
        return 0;
}