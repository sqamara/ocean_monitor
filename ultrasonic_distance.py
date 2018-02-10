#Libraries
import RPi.GPIO as GPIO
import time
from RPLCD import CharLCD

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    
    return distance

if __name__ == '__main__':
    lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=21, pin_e=20, pins_data=[26,19,13,6])
    try:
        while True:
            dist = distance()
            print ("Measured Distance = %.1f cm" % dist)
            lcd.write_string(u'%.1f cm'% dist)
            lcd.write_string(u'\n%.1f cm'% dist)
            time.sleep(1)
            lcd.clear()
    
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
