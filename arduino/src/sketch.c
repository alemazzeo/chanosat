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
// Servo motor
/*#define SERVO_CONTROL 10*/
#define SERVO_INIT 60
#define LC_PIN 10 // Laser power control pin corresponds to timer1

// Initiate variables
SerialCommand sCmd; // Rename command
AccelStepper stepper1(1, STEPPER1_STEP_PIN, STEPPER1_DIR_PIN);
AccelStepper stepper2(1, STEPPER2_STEP_PIN, STEPPER2_DIR_PIN);
AccelStepper stepper3(4, STEPPER3_PIN1, STEPPER3_PIN2, STEPPER3_PIN3, STEPPER3_PIN4);
/*Servo myservo;  // create servo object to control a servo*/
/*float servo_pos_now = SERVO_INIT;
float servo_pos_uset = SERVO_INIT;*/
float servo_step = 0.1;
// Flag to check if the stepper is moving
bool stepper_moving = false;

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
    /*pinMode(STEPPER1_ENABLE, OUTPUT);*/
    stepper1.setEnablePin(STEPPER1_ENABLE);
    stepper1.setPinsInverted(true, true, true);
    stepper1.enableOutputs();
    stepper3.setPinsInverted(true, true, true);
    //pinMode(LC_PIN, OUTPUT);
    digitalWrite(MS1, HIGH);
    digitalWrite(MS2, HIGH);
    digitalWrite(MS3, LOW);
    /*digitalWrite(STEPPER1_ENABLE, HIGH); // Off*/
  //Change these to suit your stepper if you want
    set_stepper_parameters(&stepper1, 2000, 1200);
    set_stepper_parameters(&stepper2, 20000, 8000);
    set_stepper_parameters(&stepper3, 150, 100);

    //myservo.attach(SERVO_CONTROL);
    //myservo.write(SERVO_INIT);
    //// Setup callbacks for SerialCommand commands
    sCmd.addCommand("STMOV", rotate); // Rotates the amount of steps stated in the argument
    /*sCmd.addCommand("SVMOV", move_servo); // Rotates the amount of steps stated in the argument*/
    sCmd.addCommand("LPOW", laser_power);
    sCmd.addCommand("STRES", step_reset); // sets the initial position of the steppers
    sCmd.addDefaultHandler(unrecognized); // Handler for command that isn't matched  (says "What?")
    // Start serial port communication with corresponding baud rate
    Serial.begin(BAUD_RATE);
    Serial.println("Ready");
}


void loop(){
	while (Serial.available() > 0 & (stepper1.distanceToGo()==0 & stepper2.distanceToGo()==0)) {
		sCmd.readSerial();    // Process serial commands if new serial is available
	}
    stepper3.run();
    stepper2.run();
    if(!stepper1.distanceToGo()){
        stepper1.disableOutputs();
        stepper_moving = false;
    }
    else if(!stepper_moving){
        stepper1.enableOutputs();
        stepper_moving = true;
    }
    stepper1.run();
    /*if(servo_pos_now != servo_pos_uset){
        servo_pos_now < servo_pos_uset ? servo_pos_now+=servo_step : servo_pos_now-=servo_step ;
        myservo.write(servo_pos_now);
    }*/
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
    //MoveEffector(Steps, Motor); // Caller for move executer function
    if(stepper == 1){
        stepper1.moveTo(int(pos));
    }
    else if(stepper == 2) {
        stepper2.moveTo(int(pos));
    }
    else if(stepper == 3) {
        stepper3.moveTo(int(pos));
    }
    else {
        Serial.println("Available options for MOT are 1 or 2 OR 3.");
        return;
    }
    Serial.println("0");
}

/*void move_servo(){
  // Validation
    char *arg;
    arg = sCmd.next();
    if (arg == NULL) {
        Serial.println("No stepper selected.");
        return;
    }
    int pos = atoi(arg); // Setting first argument as the desired amount of positions. Accepts negative steps
    // myservo.write(pos);
    servo_pos_uset = pos;
    Serial.println("0");
}*/

void laser_power(){
    char *arg;
    arg = sCmd.next();
    if (arg == NULL) {
        Serial.println("No power set.");
        return;
    }
    int power = atoi(arg);
    analogWrite(LC_PIN, power);
    Serial.println("0");
}

// Not working properly
void step_reset(){
    char *arg;
    arg = sCmd.next();
    if (arg == NULL) {
        Serial.println("No power set.");
        return;
    }
    int stepper = atoi(arg);

    if(stepper == 1){
        stepper1.setCurrentPosition(0);
        set_stepper_parameters(&stepper1, 5000, 20000);
        Serial.print(stepper2.currentPosition());
    }
    else if(stepper == 2) {
        stepper2.setCurrentPosition(0);
        set_stepper_parameters(&stepper2, 1000, 20000);
    }
    else {
        Serial.println("Available options for MOT are 1 or 2.");
        return;
    }
}

void set_stepper_parameters(AccelStepper * stepper, int maxspeed, int accel){
    stepper->setMaxSpeed(maxspeed);
    stepper->setAcceleration(accel);
    // stepper->setCurrentPosition(curpos); // To move a predefined number of steps
}

// Private function that actually executes the steps
//void MoveEffector(int steps, int motor){
//  stepper.moveTo(steps);
  //Serial.println("HERE");
//}
// This gets set as the default handler, and gets called when no other command matches.
void unrecognized() {
    Serial.println("Invalid Command");
}
