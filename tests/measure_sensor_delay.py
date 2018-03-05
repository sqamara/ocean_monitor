import time
import RPi.GPIO as GPIO
from sonic_sensor import SonicSensor

sensor = SonicSensor(trig_pin=18, echo_pin=24, numbering_mode=GPIO.BCM)

iterations = 10000
#
#for i in range(10):
#    StartTime = time.time()
#    
#    for i in range(iterations):
#        sensor.get_distance()
#                
#    
#    StopTime = time.time()
#
#print((StopTime-StartTime)/iterations)

from RPLCD import CharLCD
lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=21, pin_e=20, pins_data=[26,19,13,6, 5, 11, 9, 10])
dist1 = 25.6
dist2 = 24.5

iterations = 100
for i in range(3):
    StartTime = time.time()

    for i in range(iterations):
        lcd.clear()
        lcd.write_string(u'12345678901234567890123456789012')
        #lcd.write_string(u'\n%.1f cm'% dist1)

    StopTime = time.time()
print((StopTime-StartTime)/iterations)
