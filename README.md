# mae156a-motor-circuitpython
## Requirements
These scripts are only intended to run on Raspberry Pi Pico/ Raspberry Pi Pico 2 boards running [CircuitPython 10](https://circuitpython.org/board/raspberry_pi_pico2_w/) or higher. 

## Getting Started
These scripts require two libraries from the [circuitpython library bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20260718/adafruit-circuitpython-bundle-10.x-mpy-20260718.zip):
- adafruit_pioasm
- adafruit_motor

Copy each of these libraries to your `CIRCUITPY/lib` folder.

Additionally, the quadrature_encoder.py file contains the QuadratureEncoder class used to read a quadrature encoder via PIO on RP2040/RP2350 boards. The quadrature_encoder.py file should always be placed on the CIRCUITPY drive