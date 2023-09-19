from machine import Pin, I2C
import time

# Define I2C pins (Pico default pins for I2C)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)  # 400 kHz is a common I2C speed

# Define the I2C address of the NAU7802KGI ADC
ADC_ADDRESS = 0x2A  # Default address for NAU7802KGI

def power_up():
    power_data = bytearray([0x06])  # Replace with your desired configuration
    i2c.writeto_mem(ADC_ADDRESS, 0x00, power_data)
    print('Power up successful')
    pwr = i2c.readfrom_mem(ADC_ADDRESS, 0, 1)
    print(pwr)

# Function to configure the ADC
"""def configure_adc():
    # Configure the ADC here
    # Example: Set gain = 1 and continuous conversion mode
    config_data = bytearray([0x00])  # Replace with your desired configuration
    i2c.writeto(ADC_ADDRESS, config_data)
    print('Configure Sucessful')
"""
# Function to start a conversion
"""def start_conversion():
    i2c.writeto(ADC_ADDRESS, bytearray([0x50]))  # Send command to start a conversion
"""

# Function to read the ADC value
def read_adc_value():
        # Read the status register
        #status = i2c.readfrom(ADC_ADDRESS, 1)[0]
        #print(status)
        #result = i2c.readfrom(ADC_ADDRESS, 3)  # Read 24-bit ADC data
        #print(result)
        #time.sleep(0.1)  # Wait for a short time (adjust as needed)
        #print('stat&8:', status & 0x80)
        #if status & 0x80:  # Check if conversion is complete
            #break
        
    result = bytearray(3)
    i2c.readfrom_mem_into(ADC_ADDRESS, 0x12, result)  # Read 24-bit ADC data
    
    return (result[0] << 16) | (result[1] << 8) | result[2]

try:
    power_up() # Power on ADC
    
    # configure_adc()  # Configure the ADC before starting
    
    
    while True:
        
        # start_conversion()  # Start a conversion

        # Wait for the conversion to complete (adjust based on datasheet)
        time.sleep(0.1)

        # Read and print the converted ADC value
        adc_value = read_adc_value()
        print(f"Converted ADC Value: {adc_value}")

        # Wait for 2 seconds before the next reading
        time.sleep(2)

except OSError as e:
    print("I2C communication error:", e)

except KeyboardInterrupt:
    print("Script terminated by user.")