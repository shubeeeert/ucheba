#include <LedControl.h>
LedControl lc(11, 13, 10, 1);
const byte frames[3][8] = {
  {0x8E, 0x70, 0x50, 0x68, 0x96, 0x8C, 0x88, 0x00}, 
  {0x80, 0x7E, 0x50, 0x68, 0x56, 0x4C, 0x48, 0x00},  
  {0x8E, 0x70, 0x50, 0x68, 0x96, 0x8C, 0x88, 0x00}  
};
byte f = 0;
unsigned long last = 0;

void draw(byte n) {       
  for (byte r = 0; r < 8; r++) lc.setRow(0, r, frames[n][r]);
}
void setup() {
  Serial.begin(9600);
  lc.shutdown(0, false);            
  lc.setIntensity(0, 4);
  lc.clearDisplay(0);
  draw(0);
}
void loop() {
  if (millis() - last >= 500) {       
    last = millis();
    f = (f + 1) % 3;
    draw(f);
    Serial.println(f);
  }
}