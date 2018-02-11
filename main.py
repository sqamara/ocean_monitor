import RPi.GPIO as GPIO
from RPLCD import CharLCD
import time
from sonic_sensor import SonicSensor
import pickle

def main():

    iterations = 300 
    interval = 0.05
    print("starting {} second collection".format(iterations*interval))


    sensor1 = SonicSensor(trig_pin=18, echo_pin=24, numbering_mode=GPIO.BCM)
    sensor2 = SonicSensor(trig_pin=16, echo_pin=12, numbering_mode=GPIO.BCM)
    lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=21, pin_e=20, pins_data=[26,19,13,6])

    results1 = []
    results2 = []

    try:
        for i in range(iterations):
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

    with open('results.pickle', 'wb') as file:
        pickle.dump((results1,results2), file)


if __name__ == '__main__':
    main()
