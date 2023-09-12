## I2C set up for NAU ADC used with Blood Pressure and Body Temp
## Created by Dustin Grant 4/25/23

import machine
import utime

## Function: setup_adc
## Args: none
## Returns: I2C interface object
## Desc: Configures I2C1 inteface on Pico and Powers on the NAU ADC
def setup_adc():

    sdaPIN=machine.Pin(2)
    sclPIN=machine.Pin(3)
    addrBP = 42
    i2c = machine.I2C(1,sda=sdaPIN, scl=sclPIN, freq=400000)
    utime.sleep_ms(100) # Might not need delay

    # Power On ADC
    i2c.writeto_mem(addrBP, 0x00, b'\x06')
    utime.sleep_ms(100) # Might not need delay
    pwr = i2c.readfrom_mem(addrBP,0,1) # Checking if power on was sucessful
    if pwr == 0:
        print("ADC is not on!")
        return -1
    i2c.writeto_mem(addrBP, 0x01, b'\x01') # Setting programmable gain to x2
    return i2c

## Function: get_sample
## Args: I2C interface object
## Returns: 3 byte array of converted sample
## Desc: Reads the most recent converted sample from the ADC's registers
def get_sample(i2c):

    addrBP = 42
    sample_val = bytearray(3) # Allocating 3 bytes for the converted sample

    pwr = i2c.readfrom_mem(addrBP,0x00,b'\x01') # Checking if power on was sucessful
    if pwr == 0:
        print("ADC is not on!")
        return -1
    i2c.readfrom_mem_into(addrBP,0x12,sample_val) #Reading in the three bytes of data
    return sample_val
 
setup_adc()
