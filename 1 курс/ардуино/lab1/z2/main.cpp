const byte led[] = {5, 6, 7};
const byte btn[] = {2, 3, 4};
bool last[] = {HIGH, HIGH, HIGH};
byte active = 255;

void setup() {
  for (byte i = 0; i < 3; i++) {
    pinMode(led[i], OUTPUT);
    pinMode(btn[i], INPUT_PULLUP);
    digitalWrite(led[i], LOW);
  }
}

void update() {
  for (byte i = 0; i < 3; i++) {
    digitalWrite(led[i], i == active);
  }
}

void loop() {
  for (byte i = 0; i < 3; i++) {
    bool cur = digitalRead(btn[i]);
    if (last[i] == LOW && cur == HIGH) {
      delay(20); 
      if (digitalRead(btn[i]) == HIGH) {
        if (active == i) active = 255;
        else active = i;
        update();
      }
    }
    last[i] = cur;
  }
}
