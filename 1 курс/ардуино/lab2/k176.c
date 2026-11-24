#define CLK_U 8
#define RST_U 9
#define CLK_T 10
#define RST_T 11
unsigned int v = 0;                  // член последовательности A006995
unsigned long last = 0;
void pulse(byte pin) { digitalWrite(pin, HIGH); digitalWrite(pin, LOW); }
void show(byte rst, byte clk, byte d) {
  pulse(rst);
  for (byte i = 0; i < d; i++) pulse(clk);
}
bool isBinPal(unsigned int x) {      // палиндром в двоичной записи
  unsigned int r = 0;
  for (unsigned int t = x; t > 0; t >>= 1) r = (r << 1) | (t & 1);
  return r == x;
}
void next() {                        // следующий двоично-десятичный палиндром
  do { v++; } while (!isBinPal(v));
  if (v > 99) v = 0;                 // два разряда: 0..99, затем сброс
}
void show2() { show(RST_T, CLK_T, v / 10); show(RST_U, CLK_U, v % 10); }
void setup() {
  Serial.begin(9600);
  for (byte p = 8; p <= 11; p++) pinMode(p, OUTPUT);
  show2();
}
void loop() {
  if (millis() - last >= 1000) {     // секундомер: смена раза в секунду
    last = millis();
    next();
    show2();
    Serial.println(v);
  }
}
