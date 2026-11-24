#define BUZZER_PIN 13
#define BUTTON_START 5
#define BUTTON_COUNT 5

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
  for (int i = 0; i < BUTTON_COUNT; i++)
    pinMode(BUTTON_START + i, INPUT_PULLUP);
}

volatile bool b[5];
volatile unsigned char index = 0;

void loop() {
  if (index >= BUTTON_COUNT) index = 0;
  bool btn = digitalRead(BUTTON_START + index);
  
  if (!btn && b[index]) {
    unsigned short frequency;
    switch (index) {
      case 0:
        frequency = 784;
        break;
      case 1:
        frequency = 698;
        break;
      case 2:
        frequency = 659;
        break;
      case 3:
        frequency = 587;
        break;
      case 4:
        frequency = 523;
        break;
      default:
        frequency = 0;
        break;
    }
    if (frequency > 0)
      tone(BUZZER_PIN, frequency, 500);
  }
  
  b[index] = btn;
  index++;
}