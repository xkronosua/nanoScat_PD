
#include <SevSeg.h>

#include <ps2.h>
#include <EEPROM.h>
#include <DirectIO.h>
//#include <string.h>
/*
 * Pin 5 is the mouse data pin, pin 6 is the clock pin
 * Feel free to use whatever pins are convenient.
 */
PS2 mouse(10, 11);

/*
 * initialize the mouse. Reset it, and place it into remote
 * mode, so we can get the encoder data on demand.
 */

void mouse_init()
{/*
  mouse.write(0xff);  // reset
  mouse.read();  // ack byte
  mouse.write(0xf0);  // remote mode
  mouse.read();  // ack
  delayMicroseconds(100);
  mouse.write(0xf3);  // Set Sample Rate 
  mouse.read();  // ack
  mouse.write(0xc8);  // 200 sampl/s
  mouse.read();  // ack
  mouse.write(0xe8);  // Set Resolution 
  mouse.read();  // ack
  mouse.write(0x03);  //  8 counts/mm
  mouse.read();  // ack*/
  mouse.write(0xff);  // reset
  mouse.read();  // ack byte
  mouse.read();  // blank */
  mouse.read();  // blank */
  mouse.write(0xf0);  // remote mode
  mouse.read();  // ack
  
}

typedef union{
  float f;
  byte b[4];
  } floatByte;

int val = 0;
int buttonValue = 0; 
byte optVal = 0;
int dt_max = 0;
int angleCounter = 0;
float currentAngle = 0;
int ltN=0;
int viewDelay = 5;
char displayChar[3];
int button1Pressed=0, button2Pressed=0;
int displayUpdateTime = 100;
int refreshCounter = 0;
bool boostMode = false;
bool viewLock = false;
bool changeMode = false;
int prevPressedButton = -1;
int boostCounter = 0;
bool robustRemoteMode = false;
float calibrCoef = 0.5036; // deg
int buttonsLRReader(int pressedButton){
  int add=0;
  viewLock=true;
  if (pressedButton == prevPressedButton && pressedButton != -1 ){ boostCounter++;}
  else {boostCounter = 0;
  boostMode = false;
  }
  if (boostCounter>10) {boostMode = true;}
  prevPressedButton = pressedButton;
  if(pressedButton==1){
      add--;
      button1Pressed++;
      button2Pressed=0;
     }

  if(pressedButton==2){
    add++;
    button1Pressed=0;
    button2Pressed++;
    }
    if(boostMode) add*=10;
   
   return add;
  }

SevSeg sevseg; //Instantiate a seven segment controller object
const int buttonsReader = A6;
static unsigned long timer = 0;
static unsigned long timerAngSensor = 0;
int laserHighTime = 20, laserLowTime = 20;
static unsigned long laserTimer = 0;
static unsigned long loopTime = 0, maxLoopTime=0;
bool laserState = LOW;

unsigned long t=0;
InputPin optEndstop(13);
OutputPin laserStrober(12);
//InputPin laserTrigger(12);
InputPin filtersWheelSensor(7);
OutputPin laserStateSender(9);
bool laserStateSenderMode = LOW;
byte displayMode = 0;

int inByte = 0;         // incoming serial byte
void establishContact() {
  while (Serial.available() <= 0) {
    Serial.print('A');   // send a capital A
    delay(300);
  }
}

void setup() {
  Serial.begin(19200);
  //while (!Serial) {
  //  ; // wait for serial port to connect. Needed for native USB port only
  //}
  mouse_init();

  
  byte numDigits = 3;   
  byte digitPins[] = {8, 17, 18};
  byte segmentPins[] = {15, 19, 3, 5, 6, 16, 2, 4};
  bool resistorsOnSegments = true; // Use 'true' if on digit pins
  byte hardwareConfig = COMMON_CATHODE; // See README.md for options
  
  sevseg.begin(hardwareConfig, numDigits, digitPins, segmentPins, resistorsOnSegments);
  sevseg.setBrightness(0);
  timer = millis();
  //pinMode(19,INPUT);
  //pinMode(optEndstop, INPUT);
  //pinMode(laserStrober, OUTPUT);
  //pinMode(laserStateSender, OUTPUT);
  laserTimer = millis();


     laserHighTime=word(EEPROM.read(0),EEPROM.read(1));
     if (laserHighTime<1 || laserHighTime> 999) laserHighTime = 500;
     laserLowTime=word(EEPROM.read(2),EEPROM.read(3));
     if (laserLowTime<1 || laserLowTime> 999) laserLowTime = 500;
     angleCounter=word(EEPROM.read(4),EEPROM.read(5));
     if (angleCounter<-999 || angleCounter> 999) angleCounter = 0;
     //EEPROM.get(6,calibrCoef);
 // establishContact();  // send a byte to establish contact until receiver responds
}



/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int pressedButton = -1;
void loop() {
  loopTime = micros();
  
//if (millis() - timerAngSensor>100) {
   
  int r = mouse.get_y();
  angleCounter+=r;
 
 // timerAngSensor = millis();
//}

if(laserState){
  if(millis()-laserTimer>= laserHighTime){
    laserState = LOW;
    laserStrober = laserState;
    laserStateSender = !laserState;
    laserTimer = millis();
    }
  }
else{
  if(millis()-laserTimer >= laserLowTime){
    laserState = HIGH;
    laserStrober = laserState;
    laserStateSender = !laserState;
    laserTimer = millis();
    }
  }


  buttonValue = analogRead(buttonsReader);
  if(abs(buttonValue-537)<50)      pressedButton = 0;
  else if(abs(buttonValue-394)<50) pressedButton = 1;
  else if(abs(buttonValue)<10)     pressedButton = 2;
  else pressedButton = -1;
  
 // if (boostMode = true){
  //  displayUpdateTime=30;
    
 //   } 
  if (millis() - timer>displayUpdateTime) {
    viewDelay++;
  optVal = optEndstop.read();
  //if (optVal==1){angleCounter=0;}
  if(!robustRemoteMode){
  Serial.print("\tZ:");
  Serial.print(optVal);
  //Serial.print("\tLS:");
  //Serial.print(laserState);
  //Serial.print("\tFM");
  //Serial.print(laserHighTime);
  //Serial.print('x');
  //Serial.print(laserLowTime);
  Serial.print("\tA:");
  currentAngle = angleCounter*calibrCoef;
  Serial.print(currentAngle); 
  //Serial.print("\tb:");
  //Serial.print(pressedButton);
  //Serial.print("\tdM:");
  //Serial.print(displayMode);
 // Serial.print("\tcM:");
  //Serial.print(changeMode);
  //Serial.print("\tbC:");
  //Serial.print(boostCounter);
  Serial.print("\tFW:");
  byte fW = filtersWheelSensor.read();
  Serial.println(fW);
  //Serial.print("\tlt:");
  //Serial.println(maxLoopTime/ltN);
}
  ltN=0;
  maxLoopTime=0;

  
   
  if(abs(buttonValue-537)<50){
    displayMode++;
    if (displayMode>9) displayMode=0;
    viewDelay=0;
   // displayUpdateTime = 300;  
    boostMode = false; 
    changeMode = false;  
    }
    
  if(changeMode == false && pressedButton==2){changeMode = true;}


  int increment = buttonsLRReader(pressedButton);

  if(displayMode==0){
    sevseg.setNumber(int(angleCounter*calibrCoef), 0);
    }
  if(displayMode==1){
    if (changeMode == false)sevseg.setChars("LHI");
    else{
    
   if (laserHighTime+increment<=999 && laserHighTime+increment>=1){
    laserHighTime+=increment;
    }
    else{
      boostMode=false;
      }
      sevseg.setNumber(laserHighTime, 0);
   }
   
   }

 if(displayMode==2){
    if (!changeMode)sevseg.setChars("LLO");
    else{
   if (laserLowTime+increment<=999 && laserLowTime+increment>=1){
    laserLowTime+=increment;
    }
    else{
      boostMode=false;
      }
      sevseg.setNumber(laserLowTime, 0);
   }
  
   } /*
   if(displayMode==3){
    if (!changeMode)sevseg.setChars("ang");
    else{
   
      sevseg.setNumber(angleCounter, 0);
   }
   }*/
 /*  
 if(displayMode==4){
    if (!changeMode)sevseg.setChars("cal");
    else{
      sevseg.setChars("000");
      Serial.println("CAL");
      changeMode = false;
      
   
   }
   }*/
    if(displayMode==5){
    if (!changeMode)sevseg.setChars("s-c");
    else{
      EEPROM.write(0,highByte(laserHighTime));
      EEPROM.write(1,lowByte(laserHighTime));
       laserHighTime=word(EEPROM.read(0),EEPROM.read(1));
       Serial.println(laserHighTime);
      EEPROM.write(2,highByte(laserLowTime));
      EEPROM.write(3,lowByte(laserLowTime));
      EEPROM.write(4,highByte(angleCounter));
      EEPROM.write(5,lowByte(angleCounter));
      EEPROM.put(6,calibrCoef);
      changeMode = false;
      
     }
   }
   /*
   if(displayMode==6){
    if (!changeMode)sevseg.setChars("l-c");
    else{
     
     laserHighTime=word(EEPROM.read(0),EEPROM.read(1));
     if (laserHighTime<1 || laserHighTime> 999) laserHighTime = 500;
     laserLowTime=word(EEPROM.read(2),EEPROM.read(3));
     if (laserLowTime<1 || laserLowTime> 999) laserLowTime = 500;
     angleCounter=word(EEPROM.read(4),EEPROM.read(5));
     if (angleCounter<-999 || angleCounter> 999) angleCounter = 500;
     EEPROM.get(6,calibrCoef);
      
      changeMode = false;
     }
   }
   */
   



    
    //sevseg.setNumber(angleCounter, 1);
    timer=millis();
    refreshCounter++;
    if (refreshCounter>100){
      refreshCounter=0;
      displayUpdateTime=100;
      button1Pressed=button2Pressed=0;
      viewDelay=0;
      }
    
  }

if (Serial.available() > 0) {
    // get incoming byte:
    if (robustRemoteMode){
    inByte = Serial.read();
    //Serial.println(inByte);
    if(inByte == 49) {robustRemoteMode = false;}
    if(inByte == 50) {robustRemoteMode = true;  sevseg.setNumber(inByte, 2);}
    if(inByte == 51 ){
      
      //Serial.write(angleCounter);
      floatByte fb;
      fb.f = angleCounter*calibrCoef;
      int sum = 0;
      for(int i=0;i<4;i++) sum+=fb.b[i];
      sum = abs(sum);
      if (sum>255) sum-=255;
      Serial.write(fb.b, 4);
      Serial.write(sum);
      
      }}
      else{
        String inStr = Serial.readStringUntil('\n');
        Serial.println(inStr);
        if(inStr == "RM") robustRemoteMode = true;
        if(inStr.substring(0,2) == "CC") {
          if(inStr.length()==2) Serial.println(calibrCoef);
          else{
          calibrCoef = (inStr.substring(2)).toFloat();
        //EEPROM.put(6,calibrCoef);
      }
        }
        
        if(inStr.substring(0,2) == "FM") {
          if(inStr.length()==2) {
          Serial.print(laserHighTime);
          Serial.print("x");
          Serial.println(laserLowTime);
          }
          else{
            int commaIndex = inStr.indexOf('x');
            String sp = inStr.substring(2, commaIndex);
            int secondCommaIndex = inStr.indexOf(',', commaIndex + 1);
            laserHighTime = sp.toFloat();
            sp = inStr.substring(commaIndex + 1, secondCommaIndex);
            laserLowTime = sp.toFloat();
             EEPROM.write(0,highByte(laserHighTime));
             EEPROM.write(1,lowByte(laserHighTime));
            //char *h,*l, 
            //char *init;
            //inStr.toCharArray(&init, inStr.length());
            //sscanf(init,"FM%cx%c",&h, &l);
           
            
        //EEPROM.put(6,calibrCoef);
      }
        }
        if(inStr.substring(0,1) == "A") {
          if(inStr.length()==1) Serial.println(currentAngle);
          else{
          currentAngle = (inStr.substring(1)).toFloat();
          angleCounter = currentAngle/calibrCoef;
        //EEPROM.put(6,calibrCoef);
      }
        }
        
        }
      

  }
  
////////////////////////////////////////////////////////////////////////////////////////////////////////////
  
  if (displayMode!=7) sevseg.refreshDisplay(); // Must run repeatedly
  loopTime = micros()- loopTime;
  //if (loopTime>maxLoopTime) 
  maxLoopTime += loopTime;
  ltN++;
}
  





/// END ///


