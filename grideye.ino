#include <SparkFun_GridEYE_Arduino_Library.h>
#include <Wire.h>

// Use these values (in degrees C) to adjust the contrast
#define HOT 40
#define COLD 20

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

  // collect the values
  for(unsigned char i = 0; i < 64; i++){
    Serial.print(grideye.getPixelTemperature(i), 2);
    if (i != 63) Serial.print(" ");
    //if((i+1)%8 == 0) Serial.println();
  }
  Serial.println();

  delay(10);

}
