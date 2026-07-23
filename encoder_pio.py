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
loop_rate = 1000
sleep_seconds = 1/loop_rate # only compute this once
filter_alpha = 0.1 # low pass filter for RPM

def rolling_ema_filter(alpha, raw_val, filtered_val):
    # simple filter: https://en.wikipedia.org/wiki/Exponential_smoothing
    return alpha * raw_val + (1 - alpha) * filtered_val

# Base pin for phase A. Phase B must be wired to the next GPIO
# (here: GPIO16 and GPIO17).
encoder = QuadratureEncoder(encoder_pinA)

last_value = encoder.count()
last_time = time.monotonic_ns()
filtered_rpm = 0

print("Basic encoder reading, loop rate: {:d}".format(loop_rate))
while True:
    new_time = time.monotonic_ns()
    new_value = encoder.count()
    delta_count = new_value - last_value
    delta_time = new_time - last_time 
    rpm = delta_count / motor_cpr / delta_time * 60e9
    filtered_rpm = rolling_ema_filter(filter_alpha, rpm, filtered_rpm)

    if new_value != last_value:
        print("encoder count {:8d}, delta encoder {:6d}, delta t(s) {:.7f}, raw rpm {:.0f}, filtered rpm {:.0f}".format(new_value, 
                                                                                                                  delta_count, 
                                                                                                                  delta_time/1e9, 
                                                                                                                  rpm,
                                                                                                                  filtered_rpm))
        last_value = new_value
        last_time = new_time

    time.sleep(sleep_seconds)
