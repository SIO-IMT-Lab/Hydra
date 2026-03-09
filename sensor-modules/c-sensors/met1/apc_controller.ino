//=============================================================================
// Hydra - MET1 Air Particle Counter Controller
//
// Controls pumps and valves on the Feather microcontroller.
//=============================================================================

// Pin assignments
// TODO: Confirm with Bill these comments
constexpr uint8_t STATUS_PIN = 1; // Sample State = HIGH (Green LED), Flush State = LOW (Red LED)
constexpr uint8_t FLUSH_PIN = 5;  // HIGH = flushing motor active
constexpr uint8_t SAMPLE_PIN = 6; // HIGH = sampling motor active
constexpr uint8_t VALVE_PIN = 9;  // HIGH = allow air in
constexpr uint8_t ON_PIN = 13;    // LOW = APC On, HIGH = APC Off

// Seawater switch (SWSW) pins
constexpr uint8_t SWSW_POWER_1 = 11;
constexpr uint8_t SWSW_DATA_1 = A3;
constexpr uint8_t SWSW_POWER_2 = 12;
constexpr uint8_t SWSW_DATA_2 = A2;

// Timing parameters (ms)
constexpr unsigned long WET_ENTRY_DELAY_MS = 2000;
constexpr unsigned long WET_RECHECK_DELAY_MS = 3000;
constexpr unsigned long DRY_CONFIRM_DELAY_MS = 500;
constexpr unsigned long WET_LOOP_DELAY_MS = 10;
constexpr unsigned long DRY_LOOP_DELAY_MS = 10;
constexpr unsigned long SWSW_DISCHARGE_DELAY_MS = 1;
constexpr unsigned long SWSW_SAMPLE_DELAY_MS = 1;

// Thresholds
constexpr int SWSW_THRESHOLD = 150;

void setup()
{
  Serial.begin(9600);

  pinMode(STATUS_PIN, OUTPUT);
  pinMode(FLUSH_PIN, OUTPUT);
  pinMode(SAMPLE_PIN, OUTPUT);
  pinMode(VALVE_PIN, OUTPUT);
  pinMode(ON_PIN, OUTPUT);

  pinMode(SWSW_POWER_1, OUTPUT);
  pinMode(SWSW_DATA_1, INPUT);
  pinMode(SWSW_POWER_2, OUTPUT);
  pinMode(SWSW_DATA_2, INPUT);
}

void loop()
{
  if (isWet())
  {
    handleWetCondition();
  }
  else
  {
    setDryMode();
    delay(DRY_LOOP_DELAY_MS);
  }
}

void handleWetCondition()
{
  setWetModeBase();
  digitalWrite(FLUSH_PIN, HIGH);
  delay(WET_ENTRY_DELAY_MS);

  // Remain in wet recovery until dryness is confirmed
  do
  {
    do
    {
      digitalWrite(FLUSH_PIN, LOW);
      delay(WET_LOOP_DELAY_MS);
    } while (isWet());
    delay(WET_RECHECK_DELAY_MS);

    // Briefly switch flush state, then re-check for wetness
    digitalWrite(FLUSH_PIN, HIGH);
    delay(DRY_CONFIRM_DELAY_MS);
    digitalWrite(FLUSH_PIN, LOW);

  } while (isWet());
}

bool isWet()
{
  digitalWrite(SWSW_POWER_1, LOW);
  digitalWrite(SWSW_POWER_2, LOW);
  pinMode(SWSW_DATA_1, OUTPUT);
  pinMode(SWSW_DATA_2, OUTPUT);
  digitalWrite(SWSW_DATA_1, LOW);
  digitalWrite(SWSW_DATA_2, LOW);

  // Allow sensing node capacitance to discharge to GND
  delay(SWSW_DISCHARGE_DELAY_MS);

  pinMode(SWSW_DATA_1, INPUT);
  pinMode(SWSW_DATA_2, INPUT);
  digitalWrite(SWSW_POWER_1, HIGH);
  digitalWrite(SWSW_POWER_2, HIGH);

  // Sample the capacitor voltage while it's rising, before it reaches steady state
  delay(SWSW_SAMPLE_DELAY_MS);

  int switch1 = analogRead(SWSW_DATA_1);
  int switch2 = analogRead(SWSW_DATA_2);

  digitalWrite(SWSW_POWER_1, LOW);
  digitalWrite(SWSW_POWER_2, LOW);

  if (switch1 > SWSW_THRESHOLD)
    Serial.println("SWSW 1 Shorted");
  if (switch2 > SWSW_THRESHOLD)
    Serial.println("SWSW 2 Shorted");

  return (switch1 > SWSW_THRESHOLD) || (switch2 > SWSW_THRESHOLD);
}

void setWetModeBase()
{
  digitalWrite(STATUS_PIN, LOW);
  digitalWrite(SAMPLE_PIN, LOW);
  digitalWrite(VALVE_PIN, HIGH);
  digitalWrite(ON_PIN, LOW); // APC always be on
}

void setDryMode()
{
  digitalWrite(STATUS_PIN, HIGH);
  digitalWrite(FLUSH_PIN, LOW);
  digitalWrite(SAMPLE_PIN, HIGH);
  digitalWrite(VALVE_PIN, LOW);
  digitalWrite(ON_PIN, LOW);
}