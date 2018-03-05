import RPi.GPIO as GPIO
from time import sleep

class RotaryEncoder:

    def __init__(self, dt_pin, clk_pin, lower_limit=-100, upper_limit=100):
        self.counter = lower_limit # starting point for the running directional counter
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

        # GPIO Ports
        self.Enc_A = dt_pin  # Encoder input A: input GPIO 23 (active high)
        self.Enc_B = clk_pin  # Encoder input B: input GPIO 24 (active high)

        GPIO.setwarnings(True)

        # Use the Raspberry Pi BCM pins
        GPIO.setmode(GPIO.BCM)

        # define the Encoder switch inputs
        GPIO.setup(self.Enc_A, GPIO.IN) # pull-ups are too weak, they introduce noise
        GPIO.setup(self.Enc_B, GPIO.IN)

    def get_count(self):
        return self.counter

    def rotation_decode(self, Enc_A):
        '''
        This function decodes the direction of a rotary encoder and in- or
        decrements a counter.

        The code works from the "early detection" principle that when turning the
        encoder clockwise, the A-switch gets activated before the B-switch.
        When the encoder is rotated anti-clockwise, the B-switch gets activated
        before the A-switch. The timing is depending on the mechanical design of
        the switch, and the rotational speed of the knob.

        This function gets activated when the A-switch goes high. The code then
        looks at the level of the B-switch. If the B switch is (still) low, then
        the direction must be clockwise. If the B input is (still) high, the
        direction must be anti-clockwise.

        All other conditions (both high, both low or A=0 and B=1) are filtered out.

        To complete the click-cycle, after the direction has been determined, the
        code waits for the full cycle (from indent to indent) to finish.

        '''


        sleep(0.002) # extra 2 mSec de-bounce time

        # read both of the switches
        Switch_A = GPIO.input(Enc_A)
        Switch_B = GPIO.input(self.Enc_B)

        if (Switch_A == 1) and (Switch_B == 0) : # A then B ->
            if self.counter+1 < self.upper_limit:
                self.counter += 1
            #print("direction -> ", self.counter)
            # at this point, B may still need to go high, wait for it
            while Switch_B == 0:
                Switch_B = GPIO.input(self.Enc_B)
            # now wait for B to drop to end the click cycle
            while Switch_B == 1:
                Switch_B = GPIO.input(self.Enc_B)
            return

        elif (Switch_A == 1) and (Switch_B == 1): # B then A <-
            if self.counter-1 >= self.lower_limit:
                self.counter -= 1
            #print("direction <- ", self.counter)
            # A is already high, wait for A to drop to end the click cycle
            while Switch_A == 1:
                Switch_A = GPIO.input(Enc_A)
            return

        else: # discard all other combinations
            return

    def start(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.add_event_detect( self.Enc_A, GPIO.RISING, callback=self.rotation_decode, bouncetime=2) # bouncetime in mSec

    def stop(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.remove_event_detect(self.Enc_A)



def main():
    try:
        rotary = RotaryEncoder(dt_pin=3, clk_pin=4)
        rotary.start()
        while True :
            #
            # wait for an encoder click
            sleep(1)

    except KeyboardInterrupt: # Ctrl-C to terminate the program
        print ("stopped at {}".format(rotary.get_count()))
        rotary.stop()
        GPIO.cleanup()


if __name__ == '__main__':
    main()
