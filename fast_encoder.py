"""
code.py -- example usage, mirrors the original quadrature_encoder.c main().
"""
import time
import board
from quadrature_encoder import QuadratureEncoder

# Set constants for encoder in our setup
motor_cpr = int(48) # 48 counts per revolution
encoder_pinA = board.GP16
encoder_pinB = board.GP17 # unused in code- just here to clarify pin is claimed

# Base pin for phase A. Phase B must be wired to the next GPIO
# (here: GPIO16 and GPIO17).
# create encoder object to read encoder via PIO
encoder = QuadratureEncoder(encoder_pinA)


loop_rate = 100
sleep_seconds = 1/loop_rate # only compute this once
filter_alpha = 0.1 # low pass filter for RPM

last_value = encoder.count()
last_time = time.monotonic_ns()

print("Basic encoder reading, loop rate: {:d}".format(loop_rate))
while True:
    new_time = time.monotonic_ns()
    new_value = encoder.count()
    delta_count = new_value - last_value
    delta_time = new_time - last_time 

    
    print("systime {:6f}, encoder count {:6d}".format(new_time, new_value))
    last_value = new_value
    last_time = new_time

    time.sleep(sleep_seconds)
