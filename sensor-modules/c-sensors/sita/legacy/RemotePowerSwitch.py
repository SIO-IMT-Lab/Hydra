# See https://roboticsbackend.com/raspberry-pi-arduino-serial-communication/

import serial
import time

if __name__ == '__main__':
    packet = bytearray();
    packet.append(0x02)
    packet.append(0x18)
    packet.append(0x18)
    packet.append(0x02)
    packet.append(0x18)
    packet.append(0x18)
    packet.append(0x30)
    packet.append(0x3F)
    packet.append(0x0D)
    print('Opening /dev/ttyUSB1')
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
    ser.flush()   
    ser.write(packet)
    time.sleep(0.5)
    line = ser.readline().decode('utf-8')
    print(line)
    
    packet = bytearray();
    packet.append(0x02)
    packet.append(0x18)
    packet.append(0x18)
    packet.append(0x02)
    packet.append(0x18)
    packet.append(0x18)
    packet.append(0x30)
    packet.append(0x31)
    packet.append(0x0D)
    print('Opening /dev/ttyUSB1')
    ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
    ser.flush()   
    ser.write(packet)
    time.sleep(0.5)
    line = ser.readline().decode('utf-8')
    print(line)
    