#define LED_PIN 11
#define LDR_PIN A0 
int light = 0;
void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
}
void loop() {
  light = analogRead(LDR_PIN);
  light = map(light, 160, 1018, 0, 255);
  if (light < 0) light = 0;
  analogWrite(LED_PIN, light);
  Serial.println(light);
}