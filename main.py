import RPi.GPIO as GPIO
import time
from sonic_sensor import SonicSensor
import pickle

def main():
	
	iteratrions = 60
    interval = 1


	sensor1 = SonicSensor(trig_pin=18, echo_pin=24, numbering_mode=GPIO.BCM)
	sensor1 = SonicSensor(trig_pin=16, echo_pin=12, numbering_mode=GPIO.BCM)


	results1 = []
	results2 = []

	try:
		for i in range(iteratrions)
			dist1 = sensor1.get_distance()
			dist2 = sensor2.get_distance()
			
			results1.append(dist1)
			results1.append(dist1)

			lcd.write_string(u'%.1f cm'% dist1)
			lcd.write_string(u'\n%.1f cm'% dist2)
			
			time.sleep(interval)
			lcd.clear()

	except KeyboardInterrupt:
		pass


	GPIO.cleanup()

	with open('results.pickle', 'wb') as file:
		pickle.dump((results1,results2), file)


if __name__ == '__main__':
	main()