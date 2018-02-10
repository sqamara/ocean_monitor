from RPLCD import CharLCD
import RPi.GPIO as GPIO
lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=21, pin_e=20, pins_data=[26,19,13,6])
lcd.write_string(u'Hello world!')
