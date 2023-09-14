import machine
import utime

led = machine.Pin("LED", machine.Pin.OUT)
print("test")
while True:
    
    led.value(1)
    print("test")

