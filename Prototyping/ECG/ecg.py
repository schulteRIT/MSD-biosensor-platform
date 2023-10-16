import machine
import time
from machine import Pin, SPI, Timer


# Global Constants
SAMPLE_FREQ = 1000  # Sampling frequency in Hz
NOTCH_FREQ = 60.0  # Frequency to be removed from signal [Hz]
Q = 30.0  # Quality factor

MAX_SAMPLES = SAMPLE_FREQ * 10  # Store 10 seconds of data

    
# Initialize SPI
print("Initializing SPI")
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs = Pin(17, Pin.OUT)
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

class LowPassFilter:
    def __init__(self, cutoff_freq, fs):
        self.cutoff_freq = cutoff_freq
        self.fs = fs
        self.b0, self.b1, self.a1 = self.calculate_coefficients()
        self.x1 = self.y1 = 0

    def calculate_coefficients(self):
        wc = 2 * 3.141592653589793 * self.cutoff_freq / self.fs
        b0 = wc / (wc + 1)
        b1 = b0
        a1 = (wc - 1) / (wc + 1)
        return b0, b1, a1

    def apply(self, x):
        y = self.b0 * x + self.b1 * self.x1 - self.a1 * self.y1
        self.x1 = x
        self.y1 = y
        return y

class NotchFilter:
    def __init__(self, notch_freq, Q, fs):
        self.notch_freq = notch_freq
        self.Q = Q
        self.fs = fs
        self.b0, self.b1, self.b2, self.a1, self.a2 = self.calculate_coefficients()
        self.x1 = self.x2 = self.y1 = self.y2 = 0

    def calculate_coefficients(self):
        w0 = 2 * 3.141592653589793 * self.notch_freq / self.fs
        alpha = (2 * 3.141592653589793 * self.notch_freq * 0.5) / self.Q
        
        b0 = 1
        b1 = -2 * (1 - 2**0.5) * (2**0.5) * (2**0.5 * 3.141592653589793 * self.notch_freq) / self.fs
        b2 = 1
        a0 = 1 + alpha
        a1 = -2 * (1 - 2**0.5) * (2**0.5) * (2**0.5 * 3.141592653589793 * self.notch_freq) / self.fs
        a2 = 1 - alpha
        
        # Normalize coefficients
        b0 /= a0
        b1 /= a0
        b2 /= a0
        a1 /= a0
        a2 /= a0
        
        return b0, b1, b2, a1, a2

    def apply(self, x):
        y = self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x2 = self.x1
        self.x1 = x
        self.y2 = self.y1
        self.y1 = y
        return y

# Initialize filters
notch_filter_60 = NotchFilter(60, Q, SAMPLE_FREQ)
notch_filter_120 = NotchFilter(120, Q, SAMPLE_FREQ)
notch_filter_180 = NotchFilter(180, Q, SAMPLE_FREQ)
low_pass_filter = LowPassFilter(200, SAMPLE_FREQ)


data = []
counter = 0

def read_adc(timer):
    global counter
    value, str = read_mcp3008(0)
    voltage = value*3.3/1024
    
    # Apply filters
    filtered_voltage = notch_filter_60.apply(voltage)
    filtered_voltage = notch_filter_120.apply(filtered_voltage)
    filtered_voltage = notch_filter_180.apply(filtered_voltage)
    filtered_voltage = low_pass_filter.apply(filtered_voltage)
    
    # Store data
    data.append((counter/SAMPLE_FREQ, filtered_voltage))
    counter += 1
    
    # Check if max samples reached
    if counter >= MAX_SAMPLES:
        timer.deinit()  # Stop the timer
        process_data()  # Process and graph the data

def process_data():
    # Implement your data processing and graphing code here
    print("Data collected:")
    for timestamp, value in data:
        print(f"{timestamp}s: {value}V")

# Set up timer
timer = Timer(freq=SAMPLE_FREQ)
timer.init(period=1000/SAMPLE_FREQ, mode=Timer.PERIODIC, callback=read_adc)
