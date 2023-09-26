import machine
import time
from machine import Pin
from time import sleep

pin = Pin("LED", Pin.OUT)

# while True:
#     pin.toggle()
#     sleep(1)
    
# Initialize SPI
print("Initializing SPI")
spi = machine.SPI(0, baudrate=1000000, polarity=0, phase=0, sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
cs = machine.Pin(17, machine.Pin.OUT)
cs.high()

def read_mcp3008(channel):
    """
    Read data from MCP3008 ADC from a specific channel.
    """
    if channel > 7 or channel < 0:
        return -1  # Invalid channel
    
    # Create command byte
    command = 0b11 << 6  # Start bit + single-ended bit
    command |= (channel & 0x07) << 3  
    
    # Send & receive data
    cs.low() 
    response = bytearray(3)
    spi.write_readinto(command.to_bytes(1, 'big') + bytes([0, 0]), response)
    cs.high()
    
    
    # Extract ADC value from response
    adc_value = ((response[0] & 0x01) << 9) | (response[1] << 1) | (response[2] >> 7)
    
    return adc_value, f"{response}"


while True:
    value, str = read_mcp3008(0)
    print(f"ADC Value Ch 0: {value*3.3/1024}")
    time.sleep(1)
