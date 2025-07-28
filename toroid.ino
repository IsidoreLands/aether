#define HELIX1_PIN 9  // PWM for first helix
#define HELIX2_PIN 10 // Second helix
#define HALL_PIN A0
#define LCR_TX 8
#define LCR_RX 9
SoftwareSerial lcrSerial(LCR_RX, LCR_TX);

void setup() {
  pinMode(HELIX1_PIN, OUTPUT);
  pinMode(HELIX2_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);
  lcrSerial.begin(9600);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'D') {  // Dipole mode (opposing currents)
      analogWrite(HELIX1_PIN, 255);
      analogWrite(HELIX2_PIN, 0);
    } else if (cmd == 'A') {  // Aligned mode
      analogWrite(HELIX1_PIN, 128);
      analogWrite(HELIX2_PIN, 128);
    } else if (cmd == 'O') {
      analogWrite(HELIX1_PIN, 0);
      analogWrite(HELIX2_PIN, 0);
    }
  }

  int hallValue = analogRead(HALL_PIN);
  float magneticField = (hallValue - 512) * 0.00488;

  lcrSerial.println("L?");  // Read inductance
  delay(100);
  String lcrData = lcrSerial.readStringUntil('\n');

  Serial.print("HALL:"); Serial.print(magneticField); Serial.print(",LCR:"); Serial.println(lcrData);

  delay(500);
}