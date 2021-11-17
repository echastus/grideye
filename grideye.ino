#include <SparkFun_GridEYE_Arduino_Library.h>
#include <Wire.h>

int knob = 0;

// Temperatures are reported by the library as floats
int pixelTable[64];

GridEYE grideye;

void setup() {

  // Start your preferred I2C object 
  Wire.begin();
  // Library assumes "Wire" for I2C but you can pass something else with begin() if you like
  grideye.begin();
  // Pour a bowl of serial
  Serial.begin(115200);

}

void loop() {

  knob = analogRead(0);
  knob = map(knob, 0, 1023, 0, 25);

  // collect the values from sensor
  for(unsigned char i = 0; i < 64; i++){
    Serial.print(grideye.getPixelTemperature(i), 2);
    Serial.print(" ");
  }
  Serial.print(knob);
  Serial.println();

  delay(10);

}
