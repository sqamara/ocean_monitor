import time
from rotary_encoder import RotaryEncoder
from button import Button
import RPi.GPIO as GPIO
from RPLCD import CharLCD

def main():
    try:
        rotary = RotaryEncoder(dt_pin=3, clk_pin=4)
        button = Button(pin=2)
        lcd = CharLCD(numbering_mode=GPIO.BCM, cols=16, rows=2, pin_rs=21, pin_e=20, pins_data=[5,7,8,25,26,19,13,6])
        while True :
            if button.pressed():
                break
            lcd.clear()
            lcd.write_string(u'{}'.format(rotary.get_count()))
            time.sleep(0.1)

    except KeyboardInterrupt: # Ctrl-C to terminate the program
        pass

    print ("stopped at {}".format(rotary.get_count()))
    rotary.stop()
    GPIO.cleanup()


if __name__ == '__main__':
    main()
