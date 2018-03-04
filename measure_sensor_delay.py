import time
import RPi.GPIO as GPIO
from sonic_sensor import SonicSensor

sensor = SonicSensor(trig_pin=18, echo_pin=24, numbering_mode=GPIO.BCM)

iterations = 10000

for i in range(10):
    StartTime = time.time()
    
    for i in range(iterations):
        sensor.get_distance()
                
    
    StopTime = time.time()

print((StopTime-StartTime)/iterations)
