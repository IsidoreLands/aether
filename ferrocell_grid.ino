#include <FastLED.h>
#include <SoftwareSerial.h>  // For LCR if serial

// Pins
#define LED_PIN 6  // WS2812B data
#define NUM_LEDS 900  // Approx for 18x18" at 15mm spacing (~30x30)
CRGB leds[NUM_LEDS];
#define HALL_PIN A0  // SS49E analog
#define LCR_TX 8  // LCR module serial TX (if using GY-LCR)
#define LCR_RX 9  // RX
SoftwareSerial lcrSerial(LCR_RX, LCR_TX);

// Setup
void setup() {
  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, NUM_LEDS);
  FastLED.setBrightness(64);
  pinMode(HALL_PIN, INPUT);
  lcrSerial.begin(9600);  // LCR baud
  Serial.begin(9600);  // To RPi
}

// Loop: Read sensors, control LEDs
void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'B') blueAgitate();  // Blue mode
    else if (cmd == 'R') redStabilize();  // Red mode
    else if (cmd == 'O') FastLED.clear(true);  // Off
  }

  // Read Hall
  int hallValue = analogRead(HALL_PIN);
  float magneticField = (hallValue - 512) * 0.00488;  // Approx mV to Gauss (calibrate)

  // Read LCR (example for capacitance; adapt for full)
  lcrSerial.println("C?");  // Command to read capacitance
  delay(100);
  String lcrData = lcrSerial.readStringUntil('\n');  // Parse response

  // Send to RPi
  Serial.print("HALL:"); Serial.print(magneticField); Serial.print(",LCR:"); Serial.println(lcrData);

  delay(500);
}

// LED Functions
void blueAgitate() {
  fill_solid(leds, NUM_LEDS, CRGB::Blue);
  FastLED.show();
  delay(500);
  FastLED.clear(true);
  delay(500);
}

void redStabilize() {
  fill_solid(leds, NUM_LEDS, CRGB::Red);
  FastLED.show();
}