#define COIL_PIN 9  // PWM for current control
#define HALL_PIN A0
#define LCR_TX 8
#define LCR_RX 9
SoftwareSerial lcrSerial(LCR_RX, LCR_TX);

void setup() {
  pinMode(COIL_PIN, OUTPUT);
  pinMode(HALL_PIN, INPUT);
  lcrSerial.begin(9600);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'H') analogWrite(COIL_PIN, 255);  // High field
    else if (cmd == 'L') analogWrite(COIL_PIN, 128);  // Low
    else if (cmd == 'O') analogWrite(COIL_PIN, 0);  // Off
  }

  int hallValue = analogRead(HALL_PIN);
  float magneticField = (hallValue - 512) * 0.00488;

  lcrSerial.println("L?");  // Read inductance
  delay(100);
  String lcrData = lcrSerial.readStringUntil('\n');

  Serial.print("HALL:"); Serial.print(magneticField); Serial.print(",LCR:"); Serial.println(lcrData);

  delay(500);
}