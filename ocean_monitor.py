import RPi.GPIO as GPIO

from RPLCD import CharLCD
from rotary_encoder import RotaryEncoder
from button import Button
from sonic_sensor import SonicSensor

from filters import get_rolling_median_filtered
from smoothers import exponential_filter
from peaks import is_peak

import time
from collections import deque
import numpy as np

from constants import *




class OceanMonitor:

    def __init__(self):
        # hardcoded PINOUT
        self.sensor_left 	= SonicSensor(trig_pin=16, echo_pin=12, numbering_mode=GPIO.BCM)
        self.sensor_right 	= SonicSensor(trig_pin=18, echo_pin=24, numbering_mode=GPIO.BCM)
        self.lcd 		= CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=21, pin_e=20, pins_data=[5,7,8,25,26,19,13,6])
        self.rotary 		= RotaryEncoder(dt_pin=3, clk_pin=4, lower_limit=0, upper_limit=40)
        self.button 		= Button(pin=2)

        # hardcoded dsp parameters
        # self.interval	= ??	# 
        self.window 	= 30 	# for filters and running smoother
        self.threshold 	= 4  	# for filters
        self.weight 	= .3    # for exponential smoother
        self.iterations = 20    # for exponential smoother
        #self.lag        = 1 	# for peak detection. Probably not needed as using a simple peak detector
        
        self.raw_data_left  = deque(maxlen=self.window)
        self.raw_data_right = deque(maxlen=self.window)

        self.water_level = -1# man measured ance from past hour
        self.mean_measured_level = 0 	# man measured ance from past hour
        #self.sensor_spacing = # cm 

        # variables used shared across iterations
        self.prev_peak_dist     = -1 # save wave peak height
        self.prev_trough_dist   = -1 # save wave trough height
        self.counter            = 0  # used as unit of time


    def set_initial_ance(self):
        self.rotary.start()
        self.lcd.clear()
        while self.rotary.get_count() == 0:
            self.lcd.clear()
            self.lcd.write_string(u'Use dial to set  water level    ')
            time.sleep(2)
            
            self.lcd.clear()
            self.lcd.write_string(u'press button     when set')
            time.sleep(1.5)

        while True :
            if self.button.pressed():
                break
            self.lcd.clear()
            self.lcd.write_string(u'{} cm'.format(self.rotary.get_count()*10))
            time.sleep(0.1)
        
        self.rotary.stop()
        self.water_level = self.rotary.get_count()*10
        self.lcd.clear()
        self.lcd.write_string('Set level to     {} cm'.format(self.water_level))


    def clean_data(data):
        res = get_rolling_median_filtered(np.array(data), window=self.window, threshold=self.threshold, replace_with='last')
        res = exponential_filter(res, weight=self.weight, iterations=self.iterations)
        return res
    

    def iteration():
        # get data from left sensor
        self.data_left.append( self.sensor_left.get_ance() )
        clean_data_left = clean_data(self.data_left)

        # check if the previous was a peak
        was_previous_a_peak_left = is_peak(window-2, clean_data_left)
        
        if (was_previous_a_peak_left == -1):
            # it was a trough in the measurement then it is a wave peak
            self.prev_peak_dist = clean_data_left[0]
            # inform the world
            lcd.clear()
            lcd.write_string(u'Incoming Wave   {} m/s'.format(1))
        elif (was_previous_a_peak_left == 1):
            self.prev_trough_dist = clean_data_left[0]

        self.data_right.append( self.sensor_right.get_ance() )

        was_previous_a_peak_right = is_peak(window-2, self.left_right)

        if (was_previous_a_peak_right == previous_peak):
            previous_peak = was_previous_a_peak_left # save peak vs trough

            speed = speed()

            lcd.clear()
            lcd.write_string(u'Incoming Wave   {} m/s'.format(1)) 

        lcd.clear()
        lcd.write_string(u'%.1f cm'% 2)
        lcd.write_string(u'\n%.1f cm'% 1)


    def run(self):
        # initial ance setting
        self.set_initial_ance()
        
        # delay calibration
        delay = 3 #s
        for i in range(delay):
            self.lcd.clear()
            self.lcd.write_string('calibrating in {}'.format(delay-i))
            time.sleep(1)

        # fill the queues withdata
        self.lcd.clear()
        self.lcd.write_string('CALIBRATING:    ignore output')
        
        for i in range(self.window):
            iteration()
        
        self.lcd.clear()
        self.lcd.write_string('CALIBRATING:    Done!')

        # TODO: main event loop
        while True:
            break

        GPIO.cleanup()


if __name__ == '__main__':
    device = OceanMonitor()
    device.run()

