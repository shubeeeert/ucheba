#define FIRST_LED_PIN 2 
#define LAST_LED_PIN 11
int s = -1;
int s_pin = LAST_LED_PIN;
int i = 0;
void setup() {
  for (int pin = FIRST_LED_PIN; pin <= LAST_LED_PIN; ++pin)
  	pinMode(pin, OUTPUT); 
}
void loop() {
  unsigned int ms = millis(); 
  int pin = s_pin + (s*(i % 10)); 
  digitalWrite(pin, HIGH); 
  delay(120);
  digitalWrite(pin, LOW);
  if (pin == FIRST_LED_PIN) {
    s = 1;
    s_pin = FIRST_LED_PIN;
  }
  if (pin == LAST_LED_PIN) {
    s = -1;
    s_pin = LAST_LED_PIN;
  }
  i++;
}