"""
motor_and_encoder.py
Combines the basic motor control and PIO encoder
"""
import time
import board, sys, supervisor
import pwmio
from quadrature_encoder import QuadratureEncoder
from adafruit_motor import motor


# Set constants for encoder in our setup
motor_cpr = int(48) # 48 counts per revolution
encoder_pinA = board.GP16
encoder_pinB = board.GP17 # unused in code- just here to clarify pin is claimed
loop_rate = 250
sleep_seconds = 1/loop_rate # only compute this once instead of every loop
filter_alpha = 0.3 # low pass filter for RPM

# Base pin for phase A. Phase B must be wired to the next GPIO
# (here, the pin after board.GP10).
encoder = QuadratureEncoder(encoder_pinA)

# Set up motor
motor1_pwmA = board.GP8
motor1_pwmB = board.GP9

# set pins as PWM outputs
M1A = pwmio.PWMOut(motor1_pwmA, frequency=10000) # this pin is used to set PWM speed in fwd dir
M1B = pwmio.PWMOut(motor1_pwmB, frequency=10000) # this pin is used to set PWM speed in rev dir
# create motor object with PWM objects
motor1 = motor.DCMotor(M1A, M1B)


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
            return 0    # adafruit_motor.Motor class handles a throttle value of 0 as both outputs on: which shorts them on motor driver
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

print("Basic encoder reading, loop rate: {:d}".format(loop_rate))
print("To run motor, send throttle command between -1 and 1.")
print("\n example:\n> -1        # sets throttle to 100% reverse")
print("> -0.5      # sets throttle to 50% reverse")
print(">  1.0      # sets throttle to 100% forward")

# equivalent to "loop" in Arduino  
while True:
    new_time = time.monotonic_ns()
    new_value = encoder.count()
    delta_count = new_value - last_value
    delta_time = new_time - last_time 

    if new_value != last_value:
        print("systime {:5.5f}, throttle {:s}, encoder count {:8d}"
              .format(time.monotonic(),
                      str(motor1.throttle),
                      new_value
                      )
              )
        last_value = new_value
        last_time = new_time

    # check for new commands in serial buffer
    if supervisor.runtime.serial_bytes_available:
        user_input = sys.stdin.readline().strip()
        if user_input:
            motor1.throttle = parse_user_input(user_input)

    time.sleep(sleep_seconds) # slow down update loop, encoder counts unaffected, pwm output to motor unaffecte