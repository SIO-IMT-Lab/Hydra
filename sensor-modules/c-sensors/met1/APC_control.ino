//========================================================================
// IMT Lab - Hydra
// Arduino Code to control the pumps and valves in the air particle counter
// By default, the air valve (leading in to the particle counter) is shut

// Written by: Girish Krishnan
//========================================================================

// PINS
const int onPin = 13; // LOW ==> shuts off the APC, HIGH ==> turns it on
const int valvePin = 9; // HIGH ==> air can enter PC
const int samplePin = 10;  // HIGH ==> the motor that draws air into the PC is turned on
const int flushPin = 5; // HIGH ==> the motor that flushes air (and possibly water) out of the tubes is turned on
const int SWSWPower_1 = 11; // provide pulse width modulated signal for SWSW
const int SWSWData_1 = A3; // pin to read in analog data from SWSW
const int SWSWPower_2 = 12; // another SWSW pin
const int SWSWData_2 = A2; // another SWSW pin

const int NUM_READINGS = 100;
int SWSWDataArray_1[NUM_READINGS];
int SWSWDataArray_2[NUM_READINGS];
int i = 0;

// STATES
enum States {
  STATE_IDLE,
  STATE_SAMPLE,
  STATE_FLUSH,
};

States currentState = STATE_IDLE;

void setup() {
  Serial.begin(9600);
  pinMode(onPin, OUTPUT);
  pinMode(valvePin, OUTPUT);
  pinMode(samplePin, OUTPUT);
  pinMode(flushPin, OUTPUT);
  pinMode(SWSWPower_1, OUTPUT);
  pinMode(SWSWData_1, INPUT);
  pinMode(SWSWPower_2, OUTPUT);
  pinMode(SWSWData_2, INPUT);
}

void loop() {

  // // Seawater Switch
  analogWrite(SWSWPower_1, 200);
  analogWrite(SWSWPower_2, 200);

  // Fill arrays with SWSW readings
  int SWSWreading_1 = analogRead(SWSWData_1);
  int SWSWreading_2 = analogRead(SWSWData_2);
  SWSWDataArray_1[i] = SWSWreading_1;
  SWSWDataArray_2[i] = SWSWreading_2;
  
  i++;
  if (i == NUM_READINGS) i = 0;

  // Logic to update state based on min and max reading
  int max_reading_1 = SWSWDataArray_1[0];
  int min_reading_1 = SWSWDataArray_1[0];

  int max_reading_2 = SWSWDataArray_2[0];
  int min_reading_2 = SWSWDataArray_2[0];

  for(int j = 0; j < NUM_READINGS; j++) {
      if (SWSWDataArray_1[j] < min_reading_1) min_reading_1 = SWSWDataArray_1[j];
      if (SWSWDataArray_1[j] > max_reading_1) max_reading_1 = SWSWDataArray_1[j];

      if (SWSWDataArray_2[j] < min_reading_2) min_reading_2 = SWSWDataArray_2[j];
      if (SWSWDataArray_2[j] > max_reading_2) max_reading_2 = SWSWDataArray_2[j];
  }

  int range_1 = max_reading_1 - min_reading_1;
  int range_2 = max_reading_2 - min_reading_2;

  // Use the SWSW reading to determine SAMPLE or FLUSH
  if((range_1 > 100) || (range_2 > 100)) currentState = STATE_FLUSH;
  else currentState = STATE_SAMPLE;
  
  if(range_1 > 100) Serial.println("SWSW 1 Shorted");
  if(range_2 > 100) Serial.println("SWSW 2 Shorted");

  // Handling different states of the pump
  switch(currentState) {
    case STATE_IDLE:
      idleStateHandler();
      break;
    case STATE_SAMPLE:
      sampleStateHandler();
      break;
    case STATE_FLUSH:
      flushStateHandler();
      break;
  }  
}

// Functionality for each state
void idleStateHandler() {
  /*When the board is reset, keep motors off*/
  digitalWrite(onPin, LOW); // turn off APC
  digitalWrite(valvePin, LOW); // nothing enters PC

  // Keep motors off at the start
  digitalWrite(samplePin, LOW);
  digitalWrite(flushPin, LOW);
}

void sampleStateHandler() {
  /*When air enters the particle counter*/
  digitalWrite(onPin, HIGH); // turn on APC
  digitalWrite(valvePin, HIGH); // open valve to start sampling
  digitalWrite(samplePin, HIGH); // start pulling air pin
  digitalWrite(flushPin, LOW); // don't flush while sampling
}

void flushStateHandler() {
  /*If water is detected, flush*/
  digitalWrite(onPin, LOW); // turn off APC
  digitalWrite(valvePin, LOW); // don't let water into the APC
  digitalWrite(samplePin, LOW); // stop pulling air in
  digitalWrite(flushPin, HIGH); // begin flushing out
}

