#include <SparkFun_GridEYE_Arduino_Library.h>
#include <Wire.h>
#include <LiquidCrystal.h>

//== LCD
LiquidCrystal lcd(2, 3, 4, 5, 6, 7);
unsigned RED_LED = 12;
unsigned BLUE_LED = 11;


//== SERIAL
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

boolean newData = false;

unsigned DIRECTION = 0;
unsigned PERSON_NUMBER = 0;

//== GRIDEYE
int pixelTable[64];
GridEYE grideye;

void readPrintTemperature() {
  for(unsigned char i = 0; i < 64; i++){
    Serial.print(grideye.getPixelTemperature(i), 2);
    Serial.print(" ");
  }

  Serial.println();
}

void buzzerLed(unsigned ms, unsigned power, unsigned loop) {
  for(int i = 0; i < loop*2; i++){
    if(DIRECTION == 1){
      analogWrite(RED_LED, power*((i+1)%2));
    } else {
      analogWrite(BLUE_LED, power*((i+1)%2));
    }
    delay(ms/2);
  }
}

void printPeopleLcd() {
  lcd.setCursor(5, 2);
  lcd.print("PEOPLE: ");
  lcd.setCursor(13, 2);
  lcd.print(PERSON_NUMBER);
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void parseData() {      // split the data into its parts
    char * strtokIndx; // this is used by strtok() as an index
    
    strtokIndx = strtok(tempChars, ",");
    DIRECTION = atoi(strtokIndx);  
    
    strtokIndx = strtok(NULL, ",");
    PERSON_NUMBER = atof(strtokIndx);     // convert this part to a float
}

void setup() {
  // Library assumes "Wire" for I2C but you can pass something else with begin() if you like
  grideye.begin();
  
  // LCD startup
  lcd.begin(16,2);
  printPeopleLcd();
  
  // Start your preferred I2C object 
  Wire.begin();

  // Pour a bowl of serial
  Serial.begin(115200);
}

void loop() {
  readPrintTemperature();
  delay(500);
  
  recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
          buzzerLed(200, 150, 2);
  printPeopleLcd();
        newData = false;
    }
}
