/*
 * ps2.h - a library to interface with ps2 devices. See comments in
 * ps2.cpp.
 * Written by Chris J. Kiick, January 2008.
 * Release into public domain.
 */

#ifndef ps2_h
#define ps2_h

#include "Arduino.h"
#include "Delay.h" 
#include <DirectIO.h>
class PS2
{
	public:
		PS2(int clk, int data);
		void write(unsigned char data);
		void write_(unsigned char data);
		unsigned char read(void);
		unsigned char read_(void);
		char get_y(void);
		NonBlockDelay_mc d;
		int counter;  
	private:
		int _ps2clk;
		int _ps2data;
		void golo(int pin);
		void gohi(int pin);
};

#endif /* ps2_h */

