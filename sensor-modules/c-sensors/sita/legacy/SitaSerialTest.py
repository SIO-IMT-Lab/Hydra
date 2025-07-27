# See https://roboticsbackend.com/raspberry-pi-arduino-serial-communication/

import serial
import time

if __name__ == '__main__':
    fdata = open('SITA_testlog.txt','at')   
    for loopCount in range(30):
        print('Opening /dev/ttyUSB4')
        ser = serial.Serial('/dev/ttyUSB4', 57600, timeout=1)
        ser.flush()   
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
        print(loopCount)
        # powerup
        ser.write('\r\n:020605000100F2\r\n'.encode('utf-8'))
        time.sleep(1)
        # no cal
        ser.write('\r\n:020601000600F1\r\n'.encode('utf-8'))
        time.sleep(3)
        # sample
        ser.write('\r\n:020601000B00EC\r\n'.encode('utf-8'))
        time.sleep(1)
        # enter a timed measurement loop
        waitForSample = 0
        measureStart = time.time()
        measureTimeLimit = 20.0
        while waitForSample == 0:
            # query
            ser.write('\r\n:020618000500DB\r\n'.encode('utf-8'))
            time.sleep(0.04)
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                now = time.time()
                if len(line) > 20:
                    print(time.ctime(now)+' @ '+line+'\r\n')
                    fdata.write(time.ctime(now)+' @ '+line+'\r\n')
                    waitForSample = 1
                else:
                    if now > measureStart + measureTimeLimit:
                        print(time.ctime(now)+' @ SITA measurement timeout\r\n')
                        fdata.write(time.ctime(now)+' @ SITA measurement timeout\r\n')                     
                        waitForSample = 1
        ser.write('\r\n:020605000000F3\r\n'.encode('utf-8'))
        time.sleep(0.2)
        ser.write('\r\n:020618000000E0\r\n'.encode('utf-8'))
        ser.close()
        time.sleep(2)
    fdata.close()
