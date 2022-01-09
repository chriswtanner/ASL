//Written by Thomas Fouts 3/12/21


//Define the analog pins for each of the muscle sensors
#define RightEMG1 A0 
#define RightEMG2 A1 
#define RightEMG3 A2 
#define RightEMG4 A3 
#define RightEMG5 A4 

#define LeftEMG1 A8
#define LeftEMG2 A9 
#define LeftEMG3 A10 
#define LeftEMG4 A11 
#define LeftEMG5 A12



// Include Wire for I2C for Gyroscope
#include <Wire.h>

//Declare variables for Right Hand Gyroscope
const int RightMPU = 0x68; // DefMPU6050 I2C address
float RightAccX, RightAccY, RightAccZ;
float RightGyroX, RightGyroY, RightGyroZ;
float RightAccAngleX, RightAccAngleY, RightGyroAngleX, RightGyroAngleY, RightGyroAngleZ;
float RightElapsedTime, RightCurrentTime, RightPreviousTime;

//Declare variables for the Left Hand Gyroscope
const int LeftMPU = 0x69; // MPU6050 Address with 3.3V connected
float LeftAccX, LeftAccY, LeftAccZ;
float LeftGyroX, LeftGyroY, LeftGyroZ;
float LeftAccAngleX, LeftAccAngleY, LeftGyroAngleX, LeftGyroAngleY, LeftGyroAngleZ;
float LeftElapsedTime, LeftCurrentTime, LeftPreviousTime;
int timeIndex=0; 


String currentWord; //Declare currentWord for word being signed 


//Declare variables for the instantanous reading of each muscle sensor

int RightFinalReading1;
int RightFinalReading2;
int RightFinalReading3;
int RightFinalReading4;
int RightFinalReading5;

int LeftFinalReading1;
int LeftFinalReading2;
int LeftFinalReading3;
int LeftFinalReading4;
int LeftFinalReading5;


bool Signing = false; //Declare variable to control when we collect data

//Foot Pedal
int buttonStatus = 0; 
int count;
int signNumber= 12; //Set how many signs we want to record

int LED = 12;


void setup(){ 
  Serial.begin(115200); 

  pinMode(2, INPUT_PULLUP); //Foot Petal 

  pinMode(LED, OUTPUT); //LED



  newWord(); 
  count=0; 

   Wire.begin();                            // Initialize comunication
   Wire.beginTransmission(RightMPU);        // Start communication with MPU6050 // MPU=0x68
   Wire.write(0x6B);                        // Talk to the register 6B
   Wire.write(0x00);                        // Make reset - place a 0 into the 6B register
   Wire.endTransmission(true);              //end the transmission

   Wire.begin();                            // Initialize comunication
   Wire.beginTransmission(LeftMPU);        // Start communication with MPU6050 // MPU=0x68
   Wire.write(0x6B);                        // Talk to the register 6B
   Wire.write(0x00);                        // Make reset - place a 0 into the 6B register
   Wire.endTransmission(true);              //end the transmission



  
}

void loop(){
   if (count< signNumber+1){ 
    getFootPedal(); 
    while(Signing){
     getRightEMGData();
     getLeftEMGData(); 
     getRightGyroData(); 
     getLeftGyroData();
     getFootPedal();
     delay(65); 
    }
   }
   if(count == signNumber+1){ //Stop collecting data once the target number is hit
    stopCode();
   }
   if(count > signNumber+2){ //Start collecting data for next word
    newWord();
   }
  delay (50);
}

void getRightEMGData(){

   RightFinalReading1 = analogRead(RightEMG1);
   RightFinalReading2 = analogRead(RightEMG2);
   RightFinalReading3 = analogRead(RightEMG3);
   RightFinalReading4 = analogRead(RightEMG4);
   RightFinalReading5 = analogRead(RightEMG5);
   

   Serial.print(RightFinalReading1);Serial.print(",");//RightFinalReading1;
   Serial.print(RightFinalReading2);Serial.print(",");//RightFinalReading2;
   Serial.print(RightFinalReading3);Serial.print(",");//RightFinalReading3;
   Serial.print(RightFinalReading4);Serial.print(",");//RightFinalReading4;
   Serial.print(RightFinalReading5);Serial.print(",");//RightFinalReading5;


}

void getLeftEMGData(){

   LeftFinalReading1 = analogRead(LeftEMG1);
   LeftFinalReading2 = analogRead(LeftEMG2);
   LeftFinalReading3 = analogRead(LeftEMG3);
   LeftFinalReading4 = analogRead(LeftEMG4);
   LeftFinalReading5 = analogRead(LeftEMG5);
   

   Serial.print(LeftFinalReading1);Serial.print(",");//LeftFinalReading1;
   Serial.print(LeftFinalReading2);Serial.print(",");//LeftFinalReading2;
   Serial.print(LeftFinalReading3);Serial.print(",");//LeftFinalReading3;
   Serial.print(LeftFinalReading4);Serial.print(",");//LeftFinalReading4;
   Serial.print(LeftFinalReading5);Serial.print(",");//LeftFinalReading5;

   
   
  
}
void getRightGyroData(){

  Wire.beginTransmission(RightMPU);
  Wire.write(0x3B);               // Start with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(RightMPU, 6, true);   // Read 6 registers total, each axis value is stored in 2 registers
  
  RightAccX = (Wire.read() << 8 | Wire.read()) / 16384.0;    // X-axis value
  RightAccY = (Wire.read() << 8 | Wire.read()) / 16384.0;    // Y-axis value
  RightAccZ = (Wire.read() << 8 | Wire.read()) / 16384.0;    // Z-axis value
  
  // Calculating Roll and Pitch from the accelerometer data and account for the errors on the data sheet 
  RightAccAngleX = (atan(RightAccY / sqrt(pow(RightAccX, 2) + pow(RightAccZ, 2))) * 180 / PI) - 0.58;         // AccErrorX ~(0.58) 
  RightAccAngleY = (atan(-1 * RightAccX / sqrt(pow(RightAccY, 2) + pow(RightAccZ, 2))) * 180 / PI) + 1.58;    // AccErrorY ~(-1.58)

  // === Read gyroscope data === //
  RightPreviousTime = RightCurrentTime;        // Previous time is stored before the actual time read
  RightCurrentTime = millis();            // Current time actual time read
  RightElapsedTime = (RightCurrentTime - RightPreviousTime) / 1000; // Divide by 1000 to get seconds
  Wire.beginTransmission(RightMPU);
  Wire.write(0x43);                 // Gyro data first register address 0x43
  Wire.endTransmission(false);
  Wire.requestFrom(RightMPU, 6, true);   // Read 4 registers total, each axis value is stored in 2 registers
  RightGyroX = (Wire.read() << 8 | Wire.read()) / 131.0; //Save the values of value in radians 
  RightGyroY = (Wire.read() << 8 | Wire.read()) / 131.0;
  RightGyroZ = (Wire.read() << 8 | Wire.read()) / 131.0;
  
  // Correct the outputs with the calculated error values
  RightGyroX = RightGyroX + 0.56;   // GyroErrorX ~(-0.56)
  RightGyroY = RightGyroY - 2;      // GyroErrorY ~(2)
  RightGyroZ = RightGyroZ + 0.79;   // GyroErrorZ ~ (-0.8)

  // Gyro values are measured deg/s, so we multiply by s to get the angle in degrees (deg/s * s = deg)
  RightGyroAngleX = RightGyroAngleX + RightGyroX * RightElapsedTime; 
  RightGyroAngleY = RightGyroAngleY + RightGyroY * RightElapsedTime;

  Serial.print(RightAccX); Serial.print(",");//RightAccX;  //Acceleration in X plane
  Serial.print(RightAccY); Serial.print(",");//RightAccY;  //Acceleration in the Y plane
  Serial.print(RightAccZ); Serial.print(",");//RightAccZ;  //Acceleration in the Z plane
  Serial.print(RightAccAngleX); Serial.print(",");//RightAccAngleX;  
  Serial.print(RightAccAngleY); Serial.print(",");//RightAccAngleY;
  Serial.print(RightGyroX); Serial.print(",");//RightGyroX;
  Serial.print(RightGyroY); Serial.print(",");//RightGyroY;
  Serial.print(RightGyroZ); Serial.print(",");//RightGyroZ;
  Serial.print(RightGyroAngleX); Serial.print(",");//RightGyroAngleX;
  Serial.print(RightGyroAngleY); Serial.print(",");//RightGyroAngleY; 
  
 
}
void getLeftGyroData(){

  Wire.beginTransmission(LeftMPU);
  Wire.write(0x3B);               // Start with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(LeftMPU, 6, true);   // Read 6 registers total, each axis value is stored in 2 registers
  
  LeftAccX = (Wire.read() << 8 | Wire.read()) / 16384.0;    // X-axis value
  LeftAccY = (Wire.read() << 8 | Wire.read()) / 16384.0;    // Y-axis value
  LeftAccZ = (Wire.read() << 8 | Wire.read()) / 16384.0;    // Z-axis value
  
  // Calculating Roll and Pitch from the accelerometer data and account for the errors on the data sheet 
  LeftAccAngleX = (atan(LeftAccY / sqrt(pow(LeftAccX, 2) + pow(LeftAccZ, 2))) * 180 / PI) - 0.58;         // AccErrorX ~(0.58) 
  LeftAccAngleY = (atan(-1 * LeftAccX / sqrt(pow(LeftAccY, 2) + pow(LeftAccZ, 2))) * 180 / PI) + 1.58;    // AccErrorY ~(-1.58)

  // === Read gyroscope data === //
  LeftPreviousTime = LeftCurrentTime;        // Previous time is stored before the actual time read
  LeftCurrentTime = millis();            // Current time actual time read
  LeftElapsedTime = (LeftCurrentTime - LeftPreviousTime) / 1000; // Divide by 1000 to get seconds
  Wire.beginTransmission(LeftMPU);
  Wire.write(0x43);                 // Gyro data first register address 0x43
  Wire.endTransmission(false);
  Wire.requestFrom(LeftMPU, 6, true);   // Read 4 registers total, each axis value is stored in 2 registers
  LeftGyroX = (Wire.read() << 8 | Wire.read()) / 131.0; 
  LeftGyroY = (Wire.read() << 8 | Wire.read()) / 131.0;
  LeftGyroZ = (Wire.read() << 8 | Wire.read()) / 131.0;
  
  // Correct the outputs with the calculated error values
  LeftGyroX = LeftGyroX + 0.56;   // GyroErrorX ~(-0.56)
  LeftGyroY = LeftGyroY - 2;      // GyroErrorY ~(2)
  LeftGyroZ = LeftGyroZ + 0.79;   // GyroErrorZ ~ (-0.8)

  // Gyro values are measured deg/s, so we multiply by s to get the angle in degrees (deg/s * s = deg)
  LeftGyroAngleX = LeftGyroAngleX + LeftGyroX * LeftElapsedTime; 
  LeftGyroAngleY = LeftGyroAngleY + LeftGyroY * LeftElapsedTime;

  Serial.print(LeftAccX); Serial.print(",");//LeftAccX;
  Serial.print(LeftAccY); Serial.print(",");//LeftAccY;
  Serial.print(LeftAccZ); Serial.print(",");//LeftAccZ;
  Serial.print(LeftAccAngleX); Serial.print(",");//LeftAccAngleX;
  Serial.print(LeftAccAngleY); Serial.print(",");//LeftAccAngleY;
  Serial.print(LeftGyroX); Serial.print(",");//LeftGyroX;
  Serial.print(LeftGyroY); Serial.print(",");//LeftGyroY;
  Serial.print(LeftGyroZ); Serial.print(",");//LeftGyroZ;
  Serial.print(LeftGyroAngleX); Serial.print(",");//LeftGyroAngleX;
  Serial.print(LeftGyroAngleY); Serial.println("");//LeftGyroAngleY; 
}




void getFootPedal(){

  int pinValue= digitalRead(2); // Assigns the state of the footpedal to the measured state
  if (buttonStatus != pinValue){ // Determines when the pedal changes state
    buttonStatus = pinValue;
    if (buttonStatus ==1){
      digitalWrite(LED, HIGH);
      Signing = false;
        Serial.println("");
        Serial.println("");
        Serial.println("***RESTING***");
        Serial.println("");
        count ++;             //Index count variable to keep track of how many signs have been completed  
    }
    
    if (buttonStatus ==0){
      if(count<=signNumber){ 
        digitalWrite(LED, LOW);
        Signing = true; 
        Serial.println("");
        Serial.println("");
        Serial.print("SIGNING: ");Serial.print(currentWord);
        Serial.print("***Sign Number: ");Serial.print(count); Serial.println("***");
        Serial.println("");
       }
      }
  }
}


void stopCode(){ //Prints end statement and stops code from running
  Serial.print("***Thats "); Serial.print(signNumber); Serial.println(" Signs***");
  count +=5;
  }
  
void newWord(){ //Takes input from user and re-assigns the currentWord and restarts the code
  Serial.println("");
  Serial.println("");
  Serial.println("");

  Serial.println("What word is next?");
  Serial.println("");
  Serial.println("");
  
  while (Serial.available()==0){}   //Delays code until user gives serial input
  currentWord = Serial.readString(); //Sets the new word equal to the serial input
  Serial.println("**********"); 
  Serial.print(currentWord); 
  Serial.println("**********"); 
  Serial.println("");
  Serial.println("");
  Serial.println("");
 
  
  count = 1; //Reset the count variable so the data collection will restart
  delay(1500); 
}
