import RPi.GPIO as GPIO

from RPLCD import CharLCD
from rotary_encoder import RotaryEncoder
from button import Button
from sonic_sensor import SonicSensor

import time
from collections import deque

from constants import *




class OceanMonitor:

	def __init__(self, initial_water_level):
		# hardcoded PINOUT
	    self.sensor_left 	= SonicSensor(trig_pin=16, echo_pin=12, numbering_mode=GPIO.BCM)
	    self.sensor_right 	= SonicSensor(trig_pin=18, echo_pin=24, numbering_mode=GPIO.BCM)
	    self.lcd 			= CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=21, pin_e=20, pins_data=[5,7,8,25,26,19,13,6])
        self.rotary 		= RotaryEncoder(dt_pin=3, clk_pin=4)
        self.button 		= Button(pin=2)

	    # hardcoded dsp parameters
		# self.interval	= ??	# 
		self.window 	= 30 	# for filters and running smoother
		self.threshold 	= 4  	# for filters
		self.weight 	= .3    # for exponential smoother
		self.lag 		= 1 	# for peak detection

		self.data_left  = deque(maxlen=self.window)
		self.data_right = deque(maxlen=self.window)

		self.water_level = initial_water_level 	# man measured distance from past hour
		self.mean_measured_level = 0 	# man measured distance from past hour
		self.sensor_spacing = # cm

		self.active = 1

		# initial distance setting
		self.set_initial_distance()


	def set_initial_distance(self):
		while True :
			if self.button.pressed():
				break
			lcd.clear()
			lcd.write_string(u'{}'.format(rotary.get_count()))
			time.sleep(0.1)

		print ("stopped at {}".format(rotary.get_count()))
		rotary.stop()

	def passive():
		pass

	def active():
        self.data_left.append( self.sensor_left.get_distance() )

        was_previous_a_peak_left = is_peak(window-2, self.left_data)
        
        if (was_previous_a_peak_left != 0)
        	previous_peak = was_previous_a_peak_left # save peak vs trough
           	
           	lcd.clear()
            lcd.write_string(u'Incoming Wave   {} m/s'.format(1))
        
        self.data_right.append( self.sensor_right.get_distance() )

        was_previous_a_peak_right = is_peak(window-2, self.left_right)

        if (was_previous_a_peak_right == previous_peak)
        	previous_peak = was_previous_a_peak_left # save peak vs trough
           	
        	speed = speed()

           	lcd.clear()
            lcd.write_string(u'Incoming Wave   {} m/s'.format(1)) 

        lcd.clear()
        lcd.write_string(u'%.1f cm'% dist2)
        lcd.write_string(u'\n%.1f cm'% dist1)
	            

	def run():
	    try:
	    	while True:
	    		#button LOGIC
	    		if self.active:
	    			active()
	    		else
	    			passive()

	    except KeyboardInterrupt:
	        pass

	    GPIO.cleanup()


if __name__ == '__main__':
    device = OceanMonitor()
    # device.run()

