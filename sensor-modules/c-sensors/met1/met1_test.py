import serial
from datetime import datetime

# comm port is the virtual comm port (in /dev) which holds the connection to this serial device
# baud rate has to do with bit transfer rate. change this depending on the serial device's spec.
def create_serial_connection(com_port, baud_rate=9600, timeout=1):
    try:
        ser = serial.Serial(com_port, baud_rate, timeout=timeout)
        return ser
    except Exception as e:
        print('Error creating serial object', e)
        return None

if __name__ == '__main__':
    # USB2 gave information
    com_port = '/dev/ttyUSB2'

    # create serial connection
    ser = create_serial_connection(com_port)
    print(ser.flush())

    while True:
        with open('met1_data.csv', 'a') as data_file:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)

