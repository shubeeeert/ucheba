#define CLK_U 8 
#define RST_U 9
#define CLK_T 10   
#define RST_T 11
unsigned int n = 0, k = 0, v = 1;  
unsigned long last = 0;
void pulse(byte pin) { digitalWrite(pin, HIGH); digitalWrite(pin, LOW); }
void show(byte rst, byte clk, byte d) { 
  pulse(rst);
  for (byte i = 0; i < d; i++) pulse(clk);
}
void next() {                         
  if (k < n) { v = v * (n - k) / (k + 1); k++; }  
  else { n++; k = 0; v = 1; }           
  if (v > 99) { n = 0; k = 0; v = 1; }  
}
void show2() { show(RST_T, CLK_T, v / 10); show(RST_U, CLK_U, v % 10); }
void setup() {
  Serial.begin(9600);
  for (byte p = 8; p <= 11; p++) pinMode(p, OUTPUT);
  show2();
}
void loop() {
  if (millis() - last >= 1000) {        
    last = millis();
    next();
    show2();
    Serial.println(v);
  }
}