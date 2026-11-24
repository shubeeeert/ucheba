#define CLK_U 8                      
#define RST_U 9
#define CLK_T 10                     
#define RST_T 11
#define BTN 2
unsigned int n = 0, k = 0, v = 1;    
bool prev = HIGH;
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
  pinMode(BTN, INPUT_PULLUP);
  show2();
}
void loop() {
  bool now = digitalRead(BTN);
  if (prev == HIGH && now == LOW && millis() - last > 200) {
    last = millis();
    next();
    show2();
    Serial.println(v);
  }
  prev = now;
}