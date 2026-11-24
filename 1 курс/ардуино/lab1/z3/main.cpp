#define BUZZER_PIN 0
#define FIRST_BAR_PIN 4
#define BAR_COUNT 14

volatile unsigned short score = 3 << 6;
volatile unsigned short count = 0;
void pushP1() {
  count++;
  if (count == 4) {
    score/=2; 
    count = 0;
  }
}
void pushP2() {
  count++;
  if (count == 4) {
    score*=2; 
    count = 0;
  }
}

void setup() {
	for (int i = 0; i < BAR_COUNT; ++i)
		pinMode(i + FIRST_BAR_PIN, OUTPUT);
	pinMode(BUZZER_PIN, OUTPUT);
	attachInterrupt(INT0, pushP1, RISING);
	attachInterrupt(INT1, pushP2, RISING);
}

void loop() {
    tone(BUZZER_PIN, 1000, 500);
    
    int center_left = (BAR_COUNT / 2) - 1;
    int center_right = BAR_COUNT / 2;
    
    while (score > 1 && score < (1 << 13)) {
        int current_pos = 0;
        int temp = score;
        while (temp > 1) {
            temp >>= 1;
            current_pos++;
        }
        
        int start_pos = min(center_left, current_pos);
        int end_pos = max(center_right, current_pos);
        
        for (int i = 0; i < BAR_COUNT; i++) {
            if (i >= start_pos && i <= end_pos) {
                digitalWrite(FIRST_BAR_PIN + i, HIGH);
            } else {
                digitalWrite(FIRST_BAR_PIN + i, LOW);
            }
        }
    }
    
    tone(BUZZER_PIN, 1000, 500);
    while (true) {}
}