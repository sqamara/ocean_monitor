import RPi.GPIO as GPIO
import time
from constants import SPEED_OF_SOUND

class SonicSensor:
	
	def __init__(self, trig_pin, echo_pin, numbering_mode):
		self.trig_pin = trig_pin
		self.echo_pin = echo_pin
		self.numbering_mode = numbering_mode
		
		GPIO.setmode(numbering_mode)
		#set GPIO direction (IN / OUT)
		GPIO.setup(trig_pin, GPIO.OUT)
		GPIO.setup(echo_pin, GPIO.IN)

	def get_distance(self):
		# set Trigger to HIGH
	    GPIO.output(self.trig_pin, True)
	    
	    # set Trigger after 0.01ms to LOW
	    time.sleep(0.00001)
	    GPIO.output(self.trig_pin, False)
	    
	    StartTime = time.time()
	    StopTime = time.time()
	    
	    # save StartTime
	    while GPIO.input(self.echo_pin) == 0:
	        StartTime = time.time()
	    
	    # save time of arrival
	    while GPIO.input(self.echo_pin) == 1:
	        StopTime = time.time()
	    
	    # time difference between start and arrival
	    TimeElapsed = StopTime - StartTime
	    # multiply with the sonic speed (34300 cm/s)
	    # and divide by 2, because there and back
	    distance = (TimeElapsed * SPEED_OF_SOUND) / 2

	    return distance
