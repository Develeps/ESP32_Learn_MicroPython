#include <SoftwareSerial.h>

SoftwareSerial Serial_2(11, 12); // RX, TX

String str = "";
int p = 13;
void setup()
{
  Serial.begin(9600); // стандартный
  Serial_2.begin(9600);
  pinMode(p, OUTPUT);
}


void loop()
{
  if (Serial_2.available() > 0) {
    char c = Serial_2.read();
    str += c;
    Serial.println(Serial_2.available());
  }
  else {
    if (str != "") {
      Serial.println(str);
      if (!Serial_2.available()) {

        if (str == "on") {
          digitalWrite(p, LOW);
          
          Serial_2.write("yes i");
        }
        if (str == "off") {
          digitalWrite(p, HIGH);
        }

        str = "";
      }
    }
  }
}

