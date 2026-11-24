#define CONTROL_PIN 9
int brightness = 255;
int k = 1;
void setup() {
	pinMode(CONTROL_PIN, OUTPUT);
  	Serial.begin(9600);
}
void loop() {
  brightness = brightness - 1;
  analogWrite(CONTROL_PIN, brightness); 
  if (brightness == 255/2*k or brightness == 0) {
    brightness = 255;
    k--;
    if (k == -1) k = 1;
  }
  Serial.println(brightness);
  delay(10); 
}