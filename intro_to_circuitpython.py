"""
Welcome to circuitpython! This program is intended to introduce python
on microcontrollers through the primary means of interaction:
     - Interactions between computer and microcontroller
    - Code running on the microcontroller
    - Interacactons between the microcontroller and the physical world
        - Digital Output
        - Digital Input
        - Analog Input
"""
# --------------------------------------------------------------------------------
#                           The basics of circuitpython
# --------------------------------------------------------------------------------
# interacting between the microcontroller and the computer
# Since we are writing code on the computer, our most valuable method of 
# writing and debugging code is our ability to communicate back and forth 
# between the microcontroller and the computer. 


print("Hello world!")
                        # the print() function allows the microcontroller to write
                        # text to the computer. 
                        # but what if we want to write to the microcontroller?
user_input = input("What's your name?")
                        # the input() function has the microcontroller wait until
                        # the computer writes text to the microcontroller
print("Hello "+ user_input + "!")

# --------------------------------------------------------------------------------
#                               importing modules
# --------------------------------------------------------------------------------
# modules are groups of code that expose functions and objects 
# that allow us to organize complicated actions in short, simple
# code statements. When we write complex code, we encapsulate it in a module
# so that it doesn't clutter up our main code.
# there are many built in modules that allow us to do important things, like 
# check the time

import time             
                        # time is the built in python module that lets us do
                        # timing related stuff. Knowing how much time has elapsed
                        # or waiting a specific amount of time is essential for
                        # interacting with the world as a microcontroller
print(time.time())
                        # prints the elapsed time since boot
                        # in seconds as a floating point number

# --------------------------------------------------------------------------------
#                               Data types in python
# --------------------------------------------------------------------------------
# python is an interpreted langauge, which means it can handle the data type of a 
# variable changing. This allows for operations that mix both floating point numbers
# and integers
current_time_seconds = time.time()
                        # current time in seconds as float
current_time_minutes = current_time_seconds / 60
                        # divide current time by 60 (int)
                        # resultant value is also a float
print("Current time in seconds: " + str(current_time_seconds))
                        # can't combine a string and number without casting
                        # number to string
print("Current time in minutes: " + str(current_time_minutes))


# --------------------------------------------------------------------------------
#        Interactions between the microcontroller and the physical world
# --------------------------------------------------------------------------------
import board            
                        # board is a module that lets us interact
                        # with the physical pins of our microcontroller
                        # this abstraction helps our code run on different hardware 
import digitalio        
                        # digitalio is a module that lets us control 
                        # the digital input/output of our pins

led = digitalio.DigitalInOut(board.LED) 
                        # here we have created a digital input/output object
                        # that is tied to the board.LED pin.
                        # now we can control this pin as a digital input/output
                        # in our code

led.direction = digitalio.Direction.OUTPUT
                        # set the direction property of the led DigitalInOut
                        # object as an output
                        # the LED is now ready to be turned on or off

led.value = True
                        # we set the output by setting the value property
time.sleep(0.5)
                        # tell microcontroller to wait (sleep) for 0.5 seconds
                        # so that we can achieve blinking
led.value = False
                        # turn the led off by setting the value to false
time.sleep(0.5)
                        # need a wait on both the on and off half cycles 
led.value = 1
                        # instead of True/False we can also use 1 and 0
time.sleep(0.5)
led.value = 0

# --------------------------------------------------------------------------------
#                                    Loop Forever
# --------------------------------------------------------------------------------
# generally we want our microcontroller to run forever, either doing a task over 
# and over, or waiting for user input from the physical world (button press, sensor 
# value) or input from a computer. The main encapsulation of this "forever" behavior
# will be a loop. If you've used arduino, this happens in the loop() function that
# is required in every arduino program. In circuit python, the same effect is achieved
# using a while loop. The simplest version of this is just a while True statement.
# more advanced applications will use architectures like state machines to enable
# more sophisticated and branching behavior.

while True:
    led.value = True

    time.sleep(0.5)

    led.value = False

    time.sleep(0.5)
                        # don't forget the second sleep statement!
