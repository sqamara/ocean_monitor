import RPi.GPIO as GPIO
from RPLCD import CharLCD
import time
from sonic_sensor import SonicSensor

from constants import *




class OceanMonitor:

	def __init__(self):
		# hardcoded PINOUT
	    self.sensor_right = SonicSensor(trig_pin=18, echo_pin=24, numbering_mode=GPIO.BCM)
	    self.sensor_left = SonicSensor(trig_pin=16, echo_pin=12, numbering_mode=GPIO.BCM)
	    lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=21, pin_e=20, pins_data=[26,19,13,6])

		interval = ??
		window = 30     # for filters and running smoother
		threshold = 4   # for filters
		weight = .3     # for exponential smoother
		lag = 1 		# for 



	def run():
	    try:
	    	while True:
	            dist1 = sensor1.get_distance()
	            dist2 = sensor2.get_distance()
	            
	            results1.append(dist1)
	            results2.append(dist2)
	            
	            lcd.write_string(u'%.1f cm'% dist2)
	            lcd.write_string(u'\n%.1f cm'% dist1)
	            
	            time.sleep(interval)
	            lcd.clear()

	    except KeyboardInterrupt:
	        pass

	    GPIO.cleanup()


if __name__ == '__main__':
    device = OceanMonitor()
    device.run()

