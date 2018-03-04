import time
from sonic_sensor import SonicSensor

sensor1 = SonicSensor(trig_pin=18, echo_pin=24, numbering_mode=GPIO.BCM)
