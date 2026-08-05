"""
motor_and_encoder.py
Combines the basic motor control and PIO encoder
"""
import time
import board, sys, supervisor
import pwmio, analogio
from quadrature_encoder import QuadratureEncoder
from adafruit_motor import motor


# Set constants for encoder in our setup
motor_cpr = int(48) # 48 counts per revolution
encoder_pinA = board.GP16
encoder_pinB = board.GP17 # unused in code- just here to clarify pin is claimed
loop_rate = 10000
sleep_seconds = 1/loop_rate # only compute this once instead of every loop
filter_alpha = 0.3 # low pass filter for RPM

# Base pin for phase A. Phase B must be wired to the next GPIO
# (here, the pin after board.GP10).
encoder = QuadratureEncoder(encoder_pinA)


# Set up motor
motor1_pwmA = board.GP8
motor1_pwmB = board.GP9

# current sense
adc_pin_1 = analogio.AnalogIn(board.GP26)
adc_pin_2 = analogio.AnalogIn(board.GP27)
resistor_value = 1.8 # ohms

# set pins as PWM outputs
M1A = pwmio.PWMOut(motor1_pwmA, frequency=10000) # this pin is used to set PWM speed in fwd dir
M1B = pwmio.PWMOut(motor1_pwmB, frequency=10000) # this pin is used to set PWM speed in rev dir
# create motor object with PWM objects
motor1 = motor.DCMotor(M1A, M1B)

def measure_current(adc_pin_1, adc_pin_2, resistor_value):
    # note, the pico ADC is only 12 bit (4096 discrete values), 
    # but circuitpython scales value to 16 bit because 16 bit is defacto resolution of boards in 
    # circuitpython/micropython, similar to how 8 bit is defacto resolution in arduino
    return 2 * (adc_pin_1.value - adc_pin_2.value) * (adc_pin_1.reference_voltage / 65535) / resistor_value

def rolling_ema_filter(alpha, raw_val, filtered_val):
    # simple filter: https://en.wikipedia.org/wiki/Exponential_smoothing
    return alpha * raw_val + (1 - alpha) * filtered_val

def parse_user_input(input_string):
    """
    parses user input to control motor. Available commands:
    throttle [-1.0, 1.0] - sets PWM as % of full scale in fwd or rev
    stop                 - sets motor driver to off, with braking (motor terminals shorted)
    coast                - sets motor driver to off, no braking   (motor terminals open)
    """ 
    try:
        command = input_string.lower()
        if command in ["off", "stop", "0"]:
            return 0    # adafruit_motor.Motor class handles a throttle value of 0 as both 
                        # outputs on: which shorts them on motor driver
        elif command in ["coast", None]:
            return None # sets motor to coast
        else:
            result = float(input_string)
            if result >  1.0: result =  1.0
            if result < -1.0: result = -1.0
            return result

    except:
        print("Invalid command. Accepted commands are:\nthrottle [-1.0 to 1.0]\nstop\n\ncommand received was: *{:s}*"\
              .format(input_string))
        return None


# initialize state of some objects, similar to "setup" function in arduino
last_value = encoder.count()
last_time = time.monotonic_ns()
filtered_rpm = 0
filtered_current = 0

print("Basic encoder reading, loop rate: {:d}".format(loop_rate))

# equivalent to "loop" in Arduino  
while True:
    new_time = time.monotonic_ns()
    new_value = encoder.count()
    delta_count = new_value - last_value
    delta_time = new_time - last_time 
    rpm = delta_count / motor_cpr / delta_time * 60e9
    filtered_rpm = rolling_ema_filter(filter_alpha, rpm, filtered_rpm)
    current = measure_current(adc_pin_1, adc_pin_2, resistor_value)
    filtered_current = rolling_ema_filter(filter_alpha, current, filtered_current)

    if new_value != last_value:
        print("systime {:5.5f}, throttle {:s}, encoder count {:8d}, delta encoder {:3d}, delta t(s) {:1.7f}, raw rpm {:4.0f}, filtered rpm {:4.0f}, filtered current {:1.3f}"\
              .format(time.monotonic(),
                        str(motor1.throttle),
                        new_value, 
                        delta_count, 
                        delta_time/1e9, 
                        rpm,
                        filtered_rpm,
                        filtered_current))
        last_value = new_value
        last_time = new_time

    # check for new commands in serial buffer
    if supervisor.runtime.serial_bytes_available:
        user_input = sys.stdin.readline().strip()
        if user_input:
            motor1.throttle = parse_user_input(user_input)

    time.sleep(sleep_seconds) # slow down update loop, encoder counts unaffected, pwm output to motor unaffecte