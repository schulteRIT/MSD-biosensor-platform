import Max30100
from sys import exit
import utime
import machine
import time

MODE_HR = 0x02
MODE_SPO2 = 0x03


mx30 = Max30100.MAX30100()
utime.sleep_ms(1000)
startTime,endTime,maxIR,ir=0,0,0,0
rising, falling = False, False
c=False
counter=0
threshold=800
bpm_range=[40,200]
last_bpm, last_beat_time = 0,0
mx30.set_mode(Max30100.MODE_SPO2)
def get_pulse():
    global last_bpm, last_beat_time

    # Read the analog value from the pulse sensor
    sensor_value = mx30.ir

    # Check if a beat is detected
    if sensor_value > threshold:
        current_time = time.ticks_ms()
        time_since_last_beat = current_time - last_beat_time

        # Calculate heart rate in beats per minute (BPM)
        bpm = 60000 / time_since_last_beat
        print ("bpm "+str(bpm))
        # Check if the BPM is within a reasonable range
        if bpm > bpm_range[0] and bpm < bpm_range[1]:
            last_bpm = bpm
            last_beat_time = current_time

    return last_bpm

c=0
while True:
    mx30.set_mode(MODE_SPO2)  # Trigger an initial temperature read.
    mx30.read_sensor()
    if(mx30.ir!=0):
        O2Saturation = mx30.red/mx30.ir
        O2Saturation_adj = O2Saturation-.1

        print("SPO2:" + str(O2Saturation_adj))
        #time.sleep(1)

# The latest values are now available via .ir and .red
    print("ir " + str(mx30.ir))
    print("red " + str(mx30.red))
    mx30.set_mode(MODE_HR)  # Trigger an initial temperature read.
    mx30.read_sensor()

    heart_rate = get_pulse()
    print("Heart Rate: {:.1f} BPM".format(heart_rate))

    mx30.refresh_temperature()
    temperature = mx30.get_temperature()
    temperature_adj = temperature+.6
    print("Temperature :"+str(temperature_adj))
    c+=1
    if(c>=10):
        time.sleep(5)
        c=0

    


