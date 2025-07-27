import serial
import os       # can only remove empty directories w os.remove(directory_as_string)
import shutil   # can be used to remove non-empty directories via shutil.rmtree()
import datetime
import signal   # for forcing gpio cleanup after ctrl-c encountered
import RPi.GPIO as GPIO # to process hardware interrupts
import sys
# interrupt info @ https://roboticsbackend.com/raspberry-pi-gpio-interrupts-tutorial/

GPS_DATA_DIR = '/home/pi/Desktop/IMT/gps_timestamps'
GPIO_PIN = 16

def init_logs():
   date = str(datetime.datetime.now().date())
   gps_log = date + '.txt'
   gps_log_path = os.path.join(GPS_DATA_DIR, date)

   # return date_path here so you can open file using 'with' operator in main
   return str(gps_log_path)

   '''
   if not os.path.exists(date_path):
       os.mkdir(date_path)
   '''

# ser is open serial port
# log_file is open file to write data to
# data is like a string buffer, only write to file when whole string is built since write ops are slow!!
def process_uart_char(ser, log_file, data):
    char = ser.read().decode(encoding='utf_8')

    # flush data to file once newline encountered
    if char == '\n':
        data = data + char

        #only write to disk if $GPRMC nmea string
        if "$GPRMC" in data:
            log_file.write(data)

        # reset data buffer
        return ''
    else:
        return data + char  # append the char to string being built

def one_pps_callback(channel):
    curr_time = datetime.datetime.now().isoformat()
    gps_log.write("Rising Edge @ " + curr_time + "\n")

def gpio_setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(GPIO_PIN, GPIO.RISING, callback=one_pps_callback)

def signal_handler(sig, frame):
    print("ending.........")
    gps_log.close()
    GPIO.cleanup()
    sys.exit(0)


if __name__ == '__main__':
    with serial.Serial('/dev/ttyACM0', baudrate=9600) as ser:
        # extract the path to the data log file
        gps_log_path = init_logs()

        # open the file w global scope so event callback can see it
        global gps_log
        gps_log = open(gps_log_path, "w")

        #perform gpio setup to set callback for interrupts
        gpio_setup()
        # signal setup for ctrl-c interrupt
        signal.signal(signal.SIGINT, signal_handler)

        # write header to log file
        gps_log.write('Hello World!\n\n')
        # init data to be empty
        data = ''
        while True:
            data = process_uart_char(ser, gps_log, data)
