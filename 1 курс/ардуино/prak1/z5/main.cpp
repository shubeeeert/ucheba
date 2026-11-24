#define BUZZER_PIN 3
#define LDR_PIN A0
  
void setup(){
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
}

int N[] = {261, 293, 329, 349, 392, 440, 494};

void loop(){
  int val, frequency;
  val = analogRead(LDR_PIN);
  frequency = map(val, 969, 49, 6, 0);
  tone(BUZZER_PIN, N[frequency], 20);
  Serial.println(N[frequency]);
}