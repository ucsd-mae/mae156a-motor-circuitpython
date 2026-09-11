"""
code.py -- example usage, mirrors the original quadrature_encoder.c main().
"""
import time
import board
import digitalio


# Set constants for our setup
motor_cpr = int(48) # 48 counts per revolution
encoder_pinA = board.GP16
encoder_pinB = board.GP17 
loop_rate = 10
sleep_seconds = 1/loop_rate # only compute this once



# Initialize Pin 1
encoderA = digitalio.DigitalInOut(encoder_pinA)
encoderA.switch_to_input(pull=digitalio.Pull.UP)

# Initialize Pin 2
encoderB = digitalio.DigitalInOut(encoder_pinB)
encoderB.switch_to_input(pull=digitalio.Pull.UP)

encoder_count = 0
encoder_count_prev = 0


# store state of pins as binary value 0b(pinA)(pinB)
# so if pinA is high (1) and pin B is low, value is 0b10
encoder_state_prev = (encoderA.value << 1) | encoderB.value 
print("Encoder state at startup: {:2b}".format(encoder_state_prev))
last_time = time.monotonic()

print("Basic encoder reading, loop rate: {:d}".format(loop_rate))
while True:
    # read encoder:   read pin A, shift over 1 bit, then read pin B
    encoder_state_new = (encoderA.value << 1) | encoderB.value
    # create a binary number holding the previous 2 encoder pin values and the most recent
    # encoder pin values. So if previous state was 01 and new state is 11, the combined
    # state is 0111
    if encoder_state_new != encoder_state_prev:
        # print("Encoder moved. New state: {:2b}".format(encoder_state_new))
        combined_state = encoder_state_prev << 2 | encoder_state_new # left shift previous state by 2 and combine
        if (combined_state == 0b1101 or combined_state == 0b0010 or combined_state == 0b0100 or combined_state == 0b1011):
            encoder_count += 1
        
        if (combined_state == 0b0111 or combined_state == 0b1110 or combined_state == 0b1000 or combined_state == 0b0001):
            encoder_count -= 1
        # update previous encoder state with new state
        encoder_state_prev = encoder_state_new

    # get current time
    new_time = time.monotonic()
    print("systime {:6f}, encoder count {:6d}".format(new_time,
                                                    encoder_count, 
                                                    ), 
                                                    )
    encoder_count_prev = encoder_count
    last_time = new_time
    time.sleep(sleep_seconds) # enforce the loop rate from constants
