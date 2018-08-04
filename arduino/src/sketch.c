/* commands
ROT STEPPER POS rotates the stepper STEPPER to the position POS defined as an absolute position in microstep units
*/

// Import libraries
#include <SoftwareSerial.h>   // We need this even if we're not using a SoftwareSerial object
#include <SerialCommand.h>
#include <AccelStepper.h>
#include <Servo.h>


#define COM2A0 6
#define COM2B1 5
#define WGM21 1
#define WGM20 0
#define WGM22 0
#define CS22 2


// Defines for pinout
#define BAUD_RATE 9600
#define MOTOR_PINS 2 //Number of pins per motor
// Pololus DIR and STEP pins for both motors
#define STEPPER3_PIN1 A5
#define STEPPER3_PIN2 A3
#define STEPPER3_PIN3 A4
#define STEPPER3_PIN4 A2

#define STEPPER2_DIR_PIN 8 //
#define STEPPER2_STEP_PIN 9
#define STEPPER1_DIR_PIN 4 // CHECK
#define STEPPER1_STEP_PIN 2 //CHECKstr(i)
#define STEPPER1_ENABLE 7 // Just motor 1 has an enable pin
// Microstep pins for both motors
#define MS1 3
#define MS2 12
#define MS3 13

// Initiate variables
SerialCommand sCmd; // Rename command
AccelStepper stepper1(1, STEPPER1_STEP_PIN, STEPPER1_DIR_PIN);
AccelStepper stepper2(1, STEPPER2_STEP_PIN, STEPPER2_DIR_PIN);
AccelStepper stepper3(4, STEPPER3_PIN1, STEPPER3_PIN2, STEPPER3_PIN3, STEPPER3_PIN4);

void setup()
{
    // Prescaler for faster pwm
    TCCR1A = _BV(COM2A0) | _BV(COM2B1) | _BV(WGM21) | _BV(WGM20);
    TCCR1B = _BV(WGM22) | _BV(CS22);
    TCCR1B = TCCR1B & 0b11111000 | 0x01;
    OCR1B = 255;
    //
    pinMode(MS1,OUTPUT);
    pinMode(MS2,OUTPUT);
    pinMode(MS3,OUTPUT);
    stepper1.setEnablePin(STEPPER1_ENABLE);
    stepper1.setPinsInverted(true, true, true);
    stepper1.enableOutputs();
    stepper3.setPinsInverted(true, true, true);

    digitalWrite(MS1, HIGH);
    digitalWrite(MS2, HIGH);
    digitalWrite(MS3, LOW);
  //Change these to suit your stepper if you want
    set_stepper_parameters(&stepper1, 2000, 1200);
    set_stepper_parameters(&stepper2, 20000, 8000);
    set_stepper_parameters(&stepper3, 150, 100);

    //// Setup callbacks for SerialCommand commands
    sCmd.addCommand("STMOV", rotate); // Rotates the amount of steps stated in the argument
    sCmd.addDefaultHandler(unrecognized); // Handler for command that isn't matched  (says "What?")

    // Start serial port communication with corresponding baud rate
    Serial.begin(BAUD_RATE);
    Serial.println("Ready");
}


void loop(){
	while (Serial.available() > 0 ) {
		sCmd.readSerial();    // Process serial commands if new serial is available
	}
}

// Moving a user specified amount of positions function
void rotate() {
  // Validation
    char *arg;
    arg = sCmd.next();
    if (arg == NULL) {
        Serial.println("No stepper selected.");
        return;
    }
    int stepper = atoi(arg); // Setting first argument as the desired amount of positions. Accepts negative steps
    arg = sCmd.next();
    if (arg == NULL) {
        Serial.println("No position selected.");
        return;
    }
    int pos = atoi(arg); // Setting first argument as the desired amount of positions. Accepts negative steps

    if(stepper == 1){
	stepper1.enableOutputs();
        stepper1.runToNewPosition(long(pos));
	stepper1.disableOutputs();
    }
    else if(stepper == 2) {
        stepper2.runToNewPosition(long(pos));
    }
    else if(stepper == 3) {
        stepper3.runToNewPosition(long(pos));
    }
    else {
        Serial.println("Available options for MOT are 1 or 2 OR 3.");
        return;
    }
    Serial.println("0");
}


void set_stepper_parameters(AccelStepper * stepper, int maxspeed, int accel){
    stepper->setMaxSpeed(maxspeed);
    stepper->setAcceleration(accel);
    // stepper->setCurrentPosition(curpos); // To move a predefined number of steps
}

void unrecognized() {
    Serial.println("Invalid Command");
}
