#include <LedControl.h>
LedControl lc(11, 13, 10, 1);
const byte frames[3][8] = {
  {0x44, 0xFE, 0xB6, 0xFE, 0x7C, 0x4C, 0x7C, 0x00},  // Im6
  {0x44, 0xFE, 0x92, 0xFE, 0x7C, 0x44, 0x7C, 0x00},  // Im7
  {0x44, 0xFE, 0xDA, 0xFE, 0x7C, 0x64, 0x7C, 0x00}   // Im8
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
