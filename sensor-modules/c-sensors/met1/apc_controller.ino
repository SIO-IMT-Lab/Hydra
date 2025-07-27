//======================================================================
// Hydra - MET1 Air Particle Counter Controller
//
// Controls pumps and valves on the Feather microcontroller.
// Configuration values are declared at the top so the sketch can be
// adapted without modifying the main logic.
//======================================================================

// Pin assignments
constexpr int ON_PIN       = 13;  // LOW = off, HIGH = on
constexpr int VALVE_PIN    = 9;   // HIGH = allow air in
constexpr int SAMPLE_PIN   = 10;  // HIGH = sampling motor active
constexpr int FLUSH_PIN    = 5;   // HIGH = flushing motor active

// Seawater switch (SWSW) pins
constexpr int SWSW_POWER_1 = 11;
constexpr int SWSW_DATA_1  = A3;
constexpr int SWSW_POWER_2 = 12;
constexpr int SWSW_DATA_2  = A2;

// Tunable parameters
constexpr int NUM_READINGS   = 100;  // samples for range calculation
constexpr int SWSW_THRESHOLD = 100;  // threshold to detect water
constexpr int SWSW_PWM_LEVEL = 200;  // PWM level supplied to the SWSWs

// Globals
int swswData1[NUM_READINGS];
int swswData2[NUM_READINGS];
int sampleIndex = 0;

enum State {
  STATE_IDLE,
  STATE_SAMPLE,
  STATE_FLUSH,
};

State currentState = STATE_IDLE;

void setup() {
  Serial.begin(9600);

  pinMode(ON_PIN, OUTPUT);
  pinMode(VALVE_PIN, OUTPUT);
  pinMode(SAMPLE_PIN, OUTPUT);
  pinMode(FLUSH_PIN, OUTPUT);

  pinMode(SWSW_POWER_1, OUTPUT);
  pinMode(SWSW_DATA_1, INPUT);
  pinMode(SWSW_POWER_2, OUTPUT);
  pinMode(SWSW_DATA_2, INPUT);
}

void loop() {
  // Power the seawater switches
  analogWrite(SWSW_POWER_1, SWSW_PWM_LEVEL);
  analogWrite(SWSW_POWER_2, SWSW_PWM_LEVEL);

  // Record readings in circular buffers
  swswData1[sampleIndex] = analogRead(SWSW_DATA_1);
  swswData2[sampleIndex] = analogRead(SWSW_DATA_2);
  sampleIndex = (sampleIndex + 1) % NUM_READINGS;

  // Calculate range for each switch
  int max1 = swswData1[0];
  int min1 = swswData1[0];
  int max2 = swswData2[0];
  int min2 = swswData2[0];

  for (int i = 1; i < NUM_READINGS; ++i) {
    if (swswData1[i] < min1) min1 = swswData1[i];
    if (swswData1[i] > max1) max1 = swswData1[i];
    if (swswData2[i] < min2) min2 = swswData2[i];
    if (swswData2[i] > max2) max2 = swswData2[i];
  }

  int range1 = max1 - min1;
  int range2 = max2 - min2;

  // Determine state
  if (range1 > SWSW_THRESHOLD || range2 > SWSW_THRESHOLD) {
    currentState = STATE_FLUSH;
  } else {
    currentState = STATE_SAMPLE;
  }

  if (range1 > SWSW_THRESHOLD) Serial.println("SWSW 1 Shorted");
  if (range2 > SWSW_THRESHOLD) Serial.println("SWSW 2 Shorted");

  // Execute state action
  switch (currentState) {
    case STATE_IDLE:
      handleIdle();
      break;
    case STATE_SAMPLE:
      handleSample();
      break;
    case STATE_FLUSH:
      handleFlush();
      break;
  }
}

void handleIdle() {
  digitalWrite(ON_PIN, LOW);
  digitalWrite(VALVE_PIN, LOW);
  digitalWrite(SAMPLE_PIN, LOW);
  digitalWrite(FLUSH_PIN, LOW);
}

void handleSample() {
  digitalWrite(ON_PIN, HIGH);
  digitalWrite(VALVE_PIN, HIGH);
  digitalWrite(SAMPLE_PIN, HIGH);
  digitalWrite(FLUSH_PIN, LOW);
}

void handleFlush() {
  digitalWrite(ON_PIN, LOW);
  digitalWrite(VALVE_PIN, LOW);
  digitalWrite(SAMPLE_PIN, LOW);
  digitalWrite(FLUSH_PIN, HIGH);
}
