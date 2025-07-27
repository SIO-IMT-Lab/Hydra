from ..sensor import Sensor

import serial
import time
from threading import Timer

class Sita(Sensor):
	"""
    Sita class which inherits from Sensor
	
    Attributes
    ----------
    
    ser: Serial
	measureTimeLimit: int
	measureInterval: int
	timer: Timer

    Methods
    -------
    
    power_on()
  		turns on the SITA by making a serial connection
	power_off()
  		turn off the SITA by closing serial connection
	write_data()
  		write sensor data to a text file in the same folder
	collect_data()
  		collect data and call write_data()
	start_collection_workflow()
  		start the data collection workflow by calling collect_data() every 30 minutes

	TODO: 
		- explore sleep times for powering and data collection/writing
		- implement logging module
    """

	# Initialize Member Variables
	def __init__(self, measureTimeLimit, measureInterval, baud_rate, port, timeout):
		self.ser = serial.Serial(port, baud_rate, timeout)
		self.measureTimeLimit = measureTimeLimit
		self.measureInterval = measureInterval

	def power_on(self):
		""" Power on the SITA using the serial connection """
		# powerup
		self.ser.write('\r\n:020605000100F2\r\n'.encode('utf-8'))
		time.sleep(1)
        # no cal
		self.ser.write('\r\n:020601000600F1\r\n'.encode('utf-8'))
		time.sleep(3)
        # sample
		self.ser.write('\r\n:020601000B00EC\r\n'.encode('utf-8'))
		time.sleep(1)

	def power_off(self):
		""" Power off the SITA using the serial connection """
		self.ser.write('\r\n:020605000000F3\r\n'.encode('utf-8'))
		time.sleep(0.2)
		self.ser.write('\r\n:020618000000E0\r\n'.encode('utf-8'))
		self.ser.close()
		time.sleep(2)

	def write_data(self, line, fdata):
		""" Write sensor SITA data to sita_log.txt in the same folder """
		fdata.write(time.ctime(now)+' @ '+line+'\r\n')
		
	def collect_data(self):
		""" Collect data from the SITA every 30 minutes and write it by calling write_data() """
		fdata = open('sita_log.txt','at')   
		sampled = False
		measureStart = time.time()
		while not sampled:
            # query
			self.ser.write('\r\n:020618000500DB\r\n'.encode('utf-8'))
			time.sleep(0.04)
			if self.ser.in_waiting > 0:
    			line = self.ser.readline().decode('utf-8').rstrip()
                now = time.time()
                if len(line) > 20:
                    print(time.ctime(now)+' @ '+line+'\r\n')
					# call of write_data()
					self.write_data(line, fdata)
                    sampled = True
                else:
                    if now > measureStart + self.measureTimeLimit:
                        print(time.ctime(now)+' @ SITA measurement timeout\r\n')
                        fdata.write(time.ctime(now)+' @ SITA measurement timeout\r\n')                     
                        sampled = True		
	
	def start_collection_workflow(self):
		""" Start the data collection workflow by calling collect_data() every 30 minutes """

		# sanity check of serial connection
		self.ser.flush()
		if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').rstrip()
            print(line)

		# setup timer
		self.timer = Timer(self.measureInterval, self.collect_data)
		self.timer.start()