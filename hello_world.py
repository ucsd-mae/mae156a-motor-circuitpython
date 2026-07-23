import time
import board
import digitalio

led = digitalio.DigitalInOut(board.LED)  # The LED is actually connected to the wifi chip, not directly to a GPIO pin
led.direction = digitalio.Direction.OUTPUT

# print the canonical hello world
print("Hello world!")

while(True):
    # turn on LED
    led.value = True
    print("LED is on.")

    time.sleep(1)
    
    # turn off LED
    led.value = False
    print("LED is off")
    
    time.sleep(1)