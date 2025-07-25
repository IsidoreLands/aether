#include <FastLED.h>

#define LED_PIN     6  // Data pin for WS2812B
#define NUM_LEDS    400  // 20x20 array
#define LED_TYPE    WS2812B
#define COLOR_ORDER GRB
#define BRIGHTNESS  64  // 0-255, adjust for power/heat

CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  Serial.begin(9600);  // For commands from Raspberry Pi/AetherOS
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'B') {  // Blue agitation mode
      blueAgitate();
    } else if (command == 'R') {  // Red stabilization mode
      redStabilize();
    } else if (command == 'O') {  // Off
      fill_solid(leds, NUM_LEDS, CRGB::Black);
      FastLED.show();
    }
  }
  delay(100);  // Throttle for stability
}

void blueAgitate() {
  // Flashing blue pattern for high-energy agitation
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB(0, 0, 255);  // Full blue
  }
  FastLED.show();
  delay(500);
  fill_solid(leds, NUM_LEDS, CRGB::Black);
  FastLED.show();
  delay(500);
}

void redStabilize() {
  // Steady red glow for stabilization
  fill_solid(leds, NUM_LEDS, CRGB(255, 0, 0));  // Full red
  FastLED.show();
}