import sys
import supervisor

if supervisor.runtime.serial_connected:
    print("Welcome to MAE-156A!")
    print("Refer to github for all code used with this project:")
    print("https://github.com/ucsd-mae/mae156a-motor-circuitpython")
    print("\n")
    print(f"Running CircuitPython version: {sys.version}")