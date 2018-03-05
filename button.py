import RPi.GPIO as GPIO
import time
class Button:

    def __init__(self, pin):
        self.pin=pin    
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        
        self.state = 1

    def pressed(self):
        if GPIO.input(self.pin) == 0:
            self.state = 0;
        elif self.state == 0:
            self.state = 1
            return True
        return False

def main():
    try:
        button = Button(pin=2)
        while True :
            print(button.pressed())
            time.sleep(0.1)

    except KeyboardInterrupt: # Ctrl-C to terminate the program
        GPIO.cleanup()


if __name__ == '__main__':
    main()


