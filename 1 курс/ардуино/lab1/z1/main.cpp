const int LED = 7, L = 3, R = 2;

void setup() {
  pinMode(LED, OUTPUT);
  pinMode(L, INPUT_PULLUP);
  pinMode(R, INPUT_PULLUP);
}

bool ledOn = false, wait = false, leftFirst = false;
unsigned long t = 0;

void loop() {
  static bool lastL = 1, lastR = 1;
  bool currL = digitalRead(L), currR = digitalRead(R);

  if (lastL && !currL) {
    if (ledOn) { ledOn = false;  wait = false;} 
    else if (wait && !leftFirst) { ledOn = true; wait = false; } 
    else if (!wait) { wait = true; leftFirst = true; t = millis(); }
  }

  if (lastR && !currR) {
    if (ledOn) { }
    else if (wait && leftFirst) { ledOn = true; wait = false; } 
    else if (!wait) {wait = true; leftFirst = false; t = millis(); }
  }
  
  digitalWrite(LED, ledOn);
  lastL = currL; 
  lastR = currR;
}
