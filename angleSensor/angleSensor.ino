#include <ps2.h>

/*
 * an arduino sketch to interface with a ps/2 mouse.
 * Also uses serial protocol to talk back to the host
 * and report what it finds.
 */

/*
 * Pin 5 is the mouse data pin, pin 6 is the clock pin
 * Feel free to use whatever pins are convenient.
 */
PS2 mouse(6, 5);

/*
 * initialize the mouse. Reset it, and place it into remote
 * mode, so we can get the encoder data on demand.
 */
void mouse_init()
{
  mouse.write(0xff);  // reset
  mouse.read();  // ack byte
  mouse.read();  // blank */
  mouse.read();  // blank */
  mouse.write(0xf0);  // remote mode
  mouse.read();  // ack
  delayMicroseconds(100);
}

int angle=0, prev_angle=0;
int ledState = LOW;             // ledState used to set the LED

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;        // will store last time LED was updated

// constants won't change :
long interval = 100;  
 const int ledPin =  2;      // the number of the LED pin
 const int ledPinOut =  3; 
 
String inputString = ""; 
boolean stringComplete = false;
void setup()
{
  inputString.reserve(200);
  pinMode(ledPin, OUTPUT);
  pinMode(ledPinOut, OUTPUT);
  Serial.begin(19200);
  mouse_init();
}

/*
 * get a reading from the mouse and report it back to the
 * host via the serial line.
 */
void loop()
{
  char mstat;
  char mx;
  char my;


  mouse.write(0xeb);  // give me data!
  mouse.read();      // ignore ack
  mstat = mouse.read();
  mx = mouse.read();
  my = mouse.read();

 
  if ((int)mstat==9){
    angle=0;
    }
    
  //Serial.print((int)mstat);
  //Serial.print("\tX=");
  //Serial.print(mx, DEC);
  angle+=my;
  //Serial.print("\tang=");
 // if (angle!=prev_angle){
  //  Serial.println(angle);
 //   prev_angle = angle;
  //}
  
  //Serial.println();
  
   unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    previousMillis = currentMillis;
    //if(interval>=500) Serial.println(angle);
    // if the LED is off turn it on and vice-versa:
    if (ledState == LOW) {
      ledState = HIGH;
    } else {
      ledState = LOW;
    }

    // set the LED with the ledState of the variable:
    digitalWrite(ledPin, ledState);
    digitalWrite(ledPinOut, ledState);
  }

  if (stringComplete) {
    Serial.println(inputString);
    // clear the string:
    if (inputString[0]=='f'){
      interval = (inputString.substring(1)).toInt();
      }
    inputString = "";
    stringComplete = false;
  }
  delay(0.1);  /* twiddle */
}


/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    if (inChar=='A'){
      stringComplete = true;
      inputString = (String)angle;
      }
    else {
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
    }
  }
}
