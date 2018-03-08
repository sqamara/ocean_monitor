import RPi.GPIO as GPIO

from RPLCD import CharLCD
from rotary_encoder import RotaryEncoder
from button import Button
from sonic_sensor import SonicSensor

from filters import rolling_median_filter_last_point
from smoothers import exponential_filter
from peaks import recent_peak

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
        self.window 	= 30    # for filters and running smoother
        self.threshold 	= 3  	# for filters
        self.weight 	= .3    # for exponential smoother
        self.iterations = 3    # for exponential smoother
        self.lag        = 10 	# for peak detection. Probably not needed as using a simple peak detector
        
        # memory for both sensors
        self.raw_data_left  = deque([-1]*self.window, maxlen=self.window)
        self.raw_data_right = deque([-1]*self.window, maxlen=self.window)
        self.data_left  = deque([-1]*self.window, maxlen=self.window)
        self.data_right = deque([-1]*self.window, maxlen=self.window)


        # parameters and variables for tide
        self.initial_water_level        = -1    # mean measured from past hour
        self.initial_median_dist        = 0     # man measured distance from past readings
        self.current_median_dist        = 0     # 
        self.tide_window                = 1001
        self.points_for_median_dist     = deque(maxlen=self.tide_window)   # used for adding points to running average
        
        # parameters and variables for speed
        self.sensor_spacing     = 10    # cm 
        self.delay              = .3    # time to do one iteration
        self.prev_peak_dist     = -1    # save wave peak height
        self.prev_trough_dist   = -1    # save wave trough height
        self.counter            = -1    # used as unit of time

        # misc
        self.calibration_delay = 0  # s   time used after setting water level to move sensor into place
        self.line2 = u'Wave: None'

    
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
        self.initial_water_level = self.rotary.get_count()*10
        self.lcd.clear()
        self.lcd.write_string('Set level to     {} cm'.format(self.initial_water_level))


    '''
    a function that uses dsp on the collected data to filter outliers and smooth points
    '''
    
    '''
    Uses the number of iterations, spacing and delay of iteration to get the speed between two detected peaks
    '''
    def __calc_speed(self):
        return self.sensor_spacing / (self.counter*self.delay) # cm/s
    
    '''
    maintains a current water level using a windowed average
    '''
    def __update_median_dist(self, point1, point2):
        self.points_for_median_dist.append(point1)
        self.points_for_median_dist.append(point2)
        self.current_median_dist = np.median(self.points_for_median_dist)
    '''
    calulates the tide form the initial water level and the current mean
    '''
    def __get_tide(self):
        print(self.initial_water_level , self.initial_median_dist , self.current_median_dist)

        return self.initial_water_level + self.initial_median_dist - self.current_median_dist
    
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
    def __iteration(self):
        # if there are no current waves detected then report tide

    
        # get data from left sensor
        self.raw_data_left.append( self.sensor_left.get_distance() )
        # perform outlier check
        self.data_left.append( rolling_median_filter_last_point(np.array(self.raw_data_left), threshold=self.threshold, replace_with=self.data_left[-1]) )
        # smooth on checked data
        clean_data_left = exponential_filter(self.data_left, weight=self.weight, iterations=self.iterations)

        # check if the previous was a peak
        was_previous_a_peak_left = recent_peak(clean_data_left, lag=self.lag)
        print was_previous_a_peak_left, 
        print self.raw_data_left[-1],
        print self.data_left[-1], clean_data_left[-1],
        print np.median(clean_data_left), self.current_median_dist
        #print (np.std(clean_data_left), clean_data_left[-2], np.median(clean_data_left))
        #for d in clean_data_left:
        #    print '{0:.2f},'.format(d),
        #print
           
        line1 = u'Tide: {0:5.1f} cm  '.format(self.__get_tide())

        if (was_previous_a_peak_left == -1):
            # it was a trough in the measurement then it is a wave peak
            if abs(clean_data_left[-self.lag-1]-self.current_median_dist) > 5:
                for d in clean_data_left:
                    print '{0:.2f},'.format(d),
                print
           
                self.prev_peak_dist = clean_data_left[-2]
                # inform the world
                self.line2 = u'Wave: {0:5.1f} cm'.format(self.current_median_dist-clean_data_left[-self.lag-1])
                self.counter = 0
            else:
                pass #wave was too small, probably not a real wave
        self.lcd.clear()
        self.lcd.write_string(line1+self.line2)

        #print('trough {}, peak {}'.format(self.prev_trough_dist,self.prev_peak_dist))

        # get data from right sensor
        self.raw_data_right.append( self.sensor_right.get_distance() )
        # perform outlier check
        self.data_right.append( rolling_median_filter_last_point(np.array(self.raw_data_right), threshold=self.threshold, replace_with=self.data_right[-1]))
        clean_data_right = exponential_filter(self.data_right, weight=self.weight, iterations=self.iterations)

        #was_previous_a_peak_right = is_peak(self.window-1-self.lag, clean_data_right)
        #if (was_previous_a_peak_left == -1):
        #    # it was a trough in the measurement then it is a wave peak
        #    # height = self.prev_trough_dist - clean_data_right[-1-self.lag] # height of the wave is trough less most recent read of wave peak
        #    speed = self.__calc_speed()
        #    # inform the world
        #    self.lcd.clear()
        #    self.lcd.write_string(u'Incoming Wave     Speed: {0:.1f}'.format(speed))
        #    self.counter = -1
    
        self.__update_median_dist(clean_data_left[-1], clean_data_right[-1])
        self.counter += 1


    '''
    setups and runs the the sensor
    '''
    def run(self):
        try:
            # initial distance setting
            print('setting initial distance')
            self.set_initial_distance()
            
            # delay calibration
            print('delaying calibration')
            for i in range(self.calibration_delay):
                self.lcd.clear()
                self.lcd.write_string('calibrating in {}'.format(self.calibration_delay-i))
                time.sleep(1)

            # fill the queues withdata
            print('calibrating')
            self.lcd.clear()
            self.lcd.write_string('CALIBRATING:    ignore LCD out')
            time.sleep(1)
            
            for i in range(100):
                self.__iteration()

            self.initial_median_dist = self.current_median_dist

            self.lcd.clear()
            self.lcd.write_string('CALIBRATING:    Done!')
            self.line2 = u'Wave: None'
            time.sleep(1)

            # run main event loop
            print('running')
            while True:
                self.__iteration()
                #time.sleep(1)
        
        except KeyboardInterrupt:
            pass

        GPIO.cleanup()


if __name__ == '__main__':
    device = OceanMonitor()
    device.run()

