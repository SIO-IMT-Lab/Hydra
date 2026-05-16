from gpiozero import Button, OutputDevice
from signal import pause


HEARTBEAT_PIN      = 13
RPI_MASTER_PIN     = 17
STARLINK_PIN       = 10

HEARTBEAT_TIMEOUT  = 60   # seconds, duration until considering RPi Master dead
POWER_CUT_DURATION = 60   # seconds, duration to turn off power to RPi Master
BOOT_WAIT          = 60   # seconds, duration to wait for the RPi Master to boot
STARLINK_BRINGUP   = 60   # seconds, duration after powering up StarLink to try to connect 
MAX_RETRIES        = 3    # number of power cycles before sending SOS via Starlink

heartbeat    = Button(HEARTBEAT_PIN, pull_up=False)
rpi_master   = OutputDevice(RPI_MASTER_PIN) # Set HIGH to turn off RPi master
starlink     = OutputDevice(STARLINK_PIN)


last_heartbeat = time.time()

def on_heartbeat():
    global last_heartbeat
    last_heartbeat = time.time()

heartbeat.when_pressed = on_heartbeat

def activate_starlink():
    """Activate Starlink"""
    starlink.on()
    time.sleep(STARLINK_BRINGUP)

def send_alert():
    """Confrim Starlink connection is established, send out the SOS message"""
    pass

def power_cycle():
    """Perform a power cycle on the RPi Master"""
    rpi_master.on()
    time.sleep(POWER_CUT_DURATION)
    rpi_master.off()

def main():
    attempts = 0

    try:
        while True:
            cur_time = time.time()
            elapsed = cur_time - last_heartbeat

            if elapsed > HEARTBEAT_TIMEOUT:
                if attempts < MAX_RETRIES:
                    print(f"Heartbeat lost. Attempt {attempts + 1} of {MAX_RETRIES}")
                    power_cycle()
                    time.sleep(BOOT_WAIT)
                    attempts += 1
                else:
                    print("Max retries reached, sending SOS...")
                    activate_starlink()
                    send_alert()
                    attempts = 0
            else:
                attempts = 0

            time.sleep(1)

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
