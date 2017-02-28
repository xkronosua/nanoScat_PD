#include "Delay.h"
void NonBlockDelay::Delay (unsigned long t)
{
  iTimeout = millis() + t;
  return;
};
bool NonBlockDelay::Timeout (void)
{
  return (iTimeout < millis());
}
unsigned long NonBlockDelay::Time(void)
 {
   return iTimeout;
 }


void NonBlockDelay_mc::Delay (unsigned long t)
{
  iTimeout = micros() + t;
  return;
};
bool NonBlockDelay_mc::Timeout (void)
{
  return (iTimeout < micros());
}
unsigned long NonBlockDelay_mc::Time(void)
 {
   return iTimeout;
 }

