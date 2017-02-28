/*
 * ps2.cpp - an interface library for ps2 devices.  Common devices are
 * mice, keyboard, barcode scanners etc.  See the examples for mouse and
 * keyboard interfacing.
 * limitations:
 *      we do not handle parity errors.
 *      The timing constants are hard coded from the spec. Data rate is
 *         not impressive.
 *      probably lots of room for optimization.
 */

#include "ps2.h"
 
/*
 * the clock and data pins can be wired directly to the clk and data pins
 * of the PS2 connector.  No external parts are needed.
 */
PS2::PS2(int clk, int data)
{
	_ps2clk = clk;
	_ps2data = data;
	gohi(_ps2clk);
	gohi(_ps2data);
	counter=0;
}

/*
 * according to some code I saw, these functions will
 * correctly set the clock and data pins for
 * various conditions.  It's done this way so you don't need
 * pullup resistors.
 */
void
PS2::gohi(int pin)
{
	//pinMode(pin, INPUT);
	//digitalWrite(pin, HIGH);
	InputPin Pin(pin);
	Pin = LOW;
}

void
PS2::golo(int pin)
{
	OutputPin Pin(pin);
	Pin = LOW;
}

/* write a byte to the PS2 device */
void
PS2::write(unsigned char data)
{
	unsigned char i;
	unsigned char parity = 1;
	
	gohi(_ps2data);
	gohi(_ps2clk);
	delayMicroseconds(300);
	golo(_ps2clk);
	delayMicroseconds(300);
	golo(_ps2data);
	delayMicroseconds(10);
	gohi(_ps2clk);	// start bit
	/* wait for device to take control of clock */
	while (digitalRead(_ps2clk) == HIGH)
		;	// this loop intentionally left blank
	// clear to send data
	for (i=0; i < 8; i++)
	{
		if (data & 0x01)
		{
			gohi(_ps2data);
		} else {
			golo(_ps2data);
		}
		// wait for clock
		while (digitalRead(_ps2clk) == LOW)
			;
		while (digitalRead(_ps2clk) == HIGH)
			;
		parity = parity ^ (data & 0x01);
		data = data >> 1;
	}
	// parity bit
	if (parity)
	{
		gohi(_ps2data);
	} else {
		golo(_ps2data);
	}
	// clock cycle - like ack.
	while (digitalRead(_ps2clk) == LOW)
		;
	while (digitalRead(_ps2clk) == HIGH)
		;
	// stop bit
	gohi(_ps2data);
	//delayMicroseconds(50);
	while (digitalRead(_ps2clk) == HIGH)
		;
	// mode switch
	while ((digitalRead(_ps2clk) == LOW) || (digitalRead(_ps2data) == LOW))
		;
	// hold up incoming data
	golo(_ps2clk);
}

/* write a byte to the PS2 device */
void
PS2::write_(unsigned char data)
{
	unsigned char i;
	unsigned char parity = 1;
	if(d.Timeout()){
		switch(counter){
			case 0:{
	gohi(_ps2data);
	gohi(_ps2clk);
	counter++;
	d.Delay(50);
	}break;
	case 1:{
	//delayMicroseconds(300);
	golo(_ps2clk);
	counter++;
	d.Delay(50);
	}break;
	case 2:{
	//delayMicroseconds(300);
	golo(_ps2data);
	
	counter++;
	d.Delay(5);
	}break;
	case 3:{
	//delayMicroseconds(10);
		gohi(_ps2clk);	// start bit

	/* wait for device to take control of clock */
	while (digitalRead(_ps2clk) == HIGH)
		;	// this loop intentionally left blank
	// clear to send data
	for (i=0; i < 8; i++)
	{
		if (data & 0x01)
		{
			gohi(_ps2data);
		} else {
			golo(_ps2data);
		}
		// wait for clock
		while (digitalRead(_ps2clk) == LOW)
			;
		while (digitalRead(_ps2clk) == HIGH)
			;
		parity = parity ^ (data & 0x01);
		data = data >> 1;
	}
	// parity bit
	if (parity)
	{
		gohi(_ps2data);
	} else {
		golo(_ps2data);
	}
	// clock cycle - like ack.
	while (digitalRead(_ps2clk) == LOW)
		;
	while (digitalRead(_ps2clk) == HIGH)
		;
	// stop bit
	gohi(_ps2data);
    //counter++;
	//d.Delay(50);
   // }break;
   // case 4:{
	//delayMicroseconds(50);
	while (digitalRead(_ps2clk) == HIGH)
		;
	// mode switch
	while ((digitalRead(_ps2clk) == LOW) || (digitalRead(_ps2data) == LOW))
		;
	// hold up incoming data
	golo(_ps2clk);
	counter++;
	d.Delay(0);
    }break;
}
}
}


/*
 * read a byte of data from the ps2 device.  Ignores parity.
 */
unsigned char
PS2::read(void)
{
	unsigned char data = 0x00;
	unsigned char i;
	unsigned char bit = 0x01;

	// start clock
	gohi(_ps2clk);
	gohi(_ps2data);
	//delayMicroseconds(25);
	while (digitalRead(_ps2clk) == HIGH)
		;
	//delayMicroseconds(5);	// not sure why.
	while (digitalRead(_ps2clk) == LOW)
		;	// eat start bit
	for (i=0; i < 8; i++)
	{
		while (digitalRead(_ps2clk) == HIGH)
			;
		if (digitalRead(_ps2data) == HIGH)
		{
			data = data | bit;
		}
		while (digitalRead(_ps2clk) == LOW)
			;
		bit = bit << 1;
	}
	
	// eat parity bit, ignore it.
	while (digitalRead(_ps2clk) == HIGH)
		;
	while (digitalRead(_ps2clk) == LOW)
		;
	// eat stop bit
	while (digitalRead(_ps2clk) == HIGH)
		;
	while (digitalRead(_ps2clk) == LOW)
		;
	golo(_ps2clk);	// hold incoming data

	return data;
}

unsigned char
PS2::read_(void)
{
	unsigned char data = 0x00;
	unsigned char i;
	unsigned char bit = 0x01;
	if(d.Timeout()){
		switch(counter){
			case 4 :{
	// start clock
	gohi(_ps2clk);
	gohi(_ps2data);
	counter++;
	d.Delay(25);
	}break;
	case 5 :{
	//delayMicroseconds(25);
	while (digitalRead(_ps2clk) == HIGH)
		;
	counter++;
	d.Delay(5);
	}break;
	case 6 :{
	//delayMicroseconds(5);	// not sure why.
	while (digitalRead(_ps2clk) == LOW)
		;	// eat start bit
	for (i=0; i < 8; i++)
	{
		while (digitalRead(_ps2clk) == HIGH)
			;
		if (digitalRead(_ps2data) == HIGH)
		{
			data = data | bit;
		}
		while (digitalRead(_ps2clk) == LOW)
			;
		bit = bit << 1;
	}
	
	// eat parity bit, ignore it.
	while (digitalRead(_ps2clk) == HIGH)
		;
	while (digitalRead(_ps2clk) == LOW)
		;
	// eat stop bit
	while (digitalRead(_ps2clk) == HIGH)
		;
	while (digitalRead(_ps2clk) == LOW)
		;
	golo(_ps2clk);	// hold incoming data

	return data;
	counter++;
	d.Delay(0);
    }break;
}}}

char
PS2::get_y(void){

  //this->counter=4;
  this->write_(0xeb);  // give me data!
  if (this->counter==4){
  this->read();      // ignore ack
  this->read();
  this->read();
  char r = this->read();
  this->counter = 0;
  return r;
}
  else return 0;
}