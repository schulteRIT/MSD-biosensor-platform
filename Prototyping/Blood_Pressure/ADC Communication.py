from machine import Pin, I2C
import time
import bluetooth
import ubluetooth
from ble_simple_peripheral import BLESimplePeripheral



# Define I2C pins (Pico default pins for I2C)
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)  # 400 kHz is a common I2C speed

# Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()

# Create an instance of the BLESimplePeripheral class with the BLE object
sp = BLESimplePeripheral(ble)

# Define the I2C address of the NAU7802KGI ADC
ADC_ADDRESS = 0x2A  # Default address for NAU7802KGI

def power_up():
    power_data = bytearray([0x06])  # Replace with your desired configuration
    i2c.writeto_mem(ADC_ADDRESS, 0x00, power_data)
    print('Power up successful')
    pwr = i2c.readfrom_mem(ADC_ADDRESS, 0, 1)
    print(pwr)
    #i2c.writeto(ADC_ADDRESS, bytes([0x10,0x00]))
    i2c.writeto(ADC_ADDRESS, bytes([0x07,0x80]))


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
#    print(f'Res[0] is {bin(result[0])}')
#    print(f'Res[1] is {bin(result[1])}')
#    print(f'Res[2] is {bin(result[2])}')
    return (result[0] << 16) | (result[1] << 8) | result[2]

def convert2BP(adc_val):
    Vs = 5
    R1 = 47
    R2 = 100
    adc_res = 16777215
    Vref = 3.3
    Vcal = 0.15 # Can adjust this to calibrate
    V_analog = adc_val * (Vref+Vcal)/adc_res
    # print(f"ADC Voltage: {V_analog}")
    V_BP = V_analog * (R2 + R1)/R2
    
    # print(f"BP Sensor Voltage: {V_BP}")
    
    pressure_kpa = ((V_BP/Vs)-0.04)/0.018
    pressure_mmHg = pressure_kpa * 7.50062
    return pressure_mmHg
      

try:
    power_up() # Power on ADC
    
    # configure_adc()  # Configure the ADC before starting
    
    
    while True:
        if sp.is_connected():  # Check if a BLE connection is established
            print('Connected!')
            while sp.is_connected():
                adc_avg = 0
                avg = 5
                # start_conversion()  # Start a conversion
                for val in range(avg):
                    time.sleep(0.2)
                    # Wait for the conversion to complete (adjust based on datasheet)
                    # Read and print the converted ADC value
                    adc_value = read_adc_value()
                    BP_single = convert2BP(adc_value)
                    #print(f"ADC val is {adc_value}")
                    adc_avg = adc_avg + adc_value # Accumulating adc val 
                adc_avg = adc_avg/avg # Dividing by 10 to get average        
                BP_mmHg = convert2BP(adc_avg)
                # print(f"Converted ADC Value: {adc_avg}")
                
                msg = f"Converted Bp Value: {BP_mmHg}\n"
                print(msg)
                sp.send(msg)

                # Wait for 2 seconds before the next reading
                time.sleep(0.05)

except OSError as e:
    print("I2C communication error:", e)

except KeyboardInterrupt:
    print("Script terminated by user.")
    

