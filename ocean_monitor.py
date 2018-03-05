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

        # parameters for filtering and smoothing
        # self.interval	= ??	# 
        self.window 	= 30 	# for filters and running smoother
        self.threshold 	= 4  	# for filters
        self.weight 	= .3    # for exponential smoother
        self.iterations = 20    # for exponential smoother
        self.lag        = 1 	# for peak detection. Probably not needed as using a simple peak detector
        
        # memory for both sensors
        self.raw_data_left  = deque(maxlen=self.window)
        self.raw_data_right = deque(maxlen=self.window)

        # parameters and variables for tide
        self.initial_water_level    = -1    # mean measured from past hour
        self.initial_mean_dist      = 0     # man measured ance from past hour #TODO
        self.current_mean_dist      = 0     # 
        self.points_for_mean_dist   = 100   # used for adding points to running average
        
        # parameters and variables for speed
        self.sensor_spacing     = 10    # cm 
        self.delay              = .3    # time to do one iteration
        self.prev_peak_dist     = -1 # save wave peak height
        self.prev_trough_dist   = -1 # save wave trough height
        self.counter            = -1  # used as unit of time

    
    '''
    A control loop in which user uses the rotary encoder to set the initial water level
    '''
    def set_initial_distance(self):
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


    '''
    a function that uses dsp on the collected data to filter outliers and smooth points
    '''
    def clean_data(data):
        res = get_rolling_median_filtered(np.array(data), window=self.window, threshold=self.threshold, replace_with='last')
        res = exponential_filter(res, weight=self.weight, iterations=self.iterations)
        return res
    
    '''
    Uses the number of iterations, spacing and delay of iteration to get the speed between two detected peaks
    '''
    def calc_speed():
        return self.sensor_spacing / (self.counter*self.delay) # cm/s
    
    '''
    maintains a current water leven using a weighted average
    '''
    def update_mean_dist(point1, point2):
        self.current_mean_dist = ((self.points_for_mean_dist-2)*self.current_mean_dist + point1 + point2) / self.points_for_mean_dist

    '''
    calulates the tide form the initial water level and the current mean
    '''
    def get_tide():
        return self.initial_water_level + self.initial_mean_dist - self.current_mean_dist
    
    '''
    An iteration of the main control loop.
    
    Samples both sensors and reports 
        if a wave has been detected
        the speed of an earlier detected wave
        or the tide as no waves have been detected

    ASSUMPUTIONS MADE: 
        a wave travels from left to right
        a waves peak and trough will not both pass the left sensor before the first passes the right sensor
    '''

'''
    TODO:
    spin loops for synchronus behavior:
        max delay before left read
        max delay for read
        max delay before right read
        max delay for read
        max delay after right read
'''
    def iteration():
        # if there are no current waves detected then report tide
        if self.counter == -1;
            lcd.clear()
            lcd.write_string(u'Tide             Height: {} cm'.format(get_tide()))

    
        # get data from left sensor
        self.data_left.append( self.sensor_left.get_distance() )
        clean_data_left = clean_data(self.data_left)

        # check if the previous was a peak
        was_previous_a_peak_left = is_peak(window-1-self.lag, clean_data_left)
        
        if (was_previous_a_peak_left == -1):
            # it was a trough in the measurement then it is a wave peak
            self.prev_peak_dist = clean_data_left[1]
            # inform the world
            lcd.clear()
            lcd.write_string(u'Incoming Wave     Height: {} cm'.format(self.prev_trough_dist-self.prev_peak_dist))
            self.counter = .5;

        elif (was_previous_a_peak_left == 1):
            self.prev_trough_dist = clean_data_left[1]
        

        # get data from left sensor
        self.data_right.append( self.sensor_right.get_distance() )
        clean_data_right = clean_data(self.data_right)

        was_previous_a_peak_right = is_peak(window-1-self.lag, clean_data_right)
        if (was_previous_a_peak_left == -1):
            # it was a trough in the measurement then it is a wave peak
            # height = self.prev_trough_dist - clean_data_right[-1-self.lag] # height of the wave is trough less most recent read of wave peak
            speed = calc_speed()
            # inform the world
            lcd.clear()
            lcd.write_string(u'Incoming Wave     Speed: {} cm/s'.format(speed))
            self.counter = -1


        update_mean_dist(clean_data_left[-1], clean_data_right[-1])
        self.counter += 1


    '''
    setups and runs the the sensor
    '''
    def run(self):
        try:
            # initial distance setting
            self.set_initial_distance()
            
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

            self.intial_mean_dist = (np.mean(clean_data(self.data_left)) + np.mean(clean_data(self.data_left))) / 2
            self.current_mean_dist = self.intial_mean_dist

            self.lcd.clear()
            self.lcd.write_string('CALIBRATING:    Done!')

            # run main event loop
            while True:
                iteration()
        
        except KeyboardInterrupt:
            pass

        GPIO.cleanup()


if __name__ == '__main__':
    device = OceanMonitor()
    device.run()

