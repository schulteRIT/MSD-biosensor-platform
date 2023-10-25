import pyRTOS
import machine
import ecg_sensor
import blood_pressure_sensor
import temperature_sensor
import spo2_sensor

def ecg_task():
    while True:
        ecg_data = ecg_sensor.read()
        print("ECG Data:", ecg_data)
        yield [pyRTOS.timeout(1)]  

def blood_pressure_task():
    while True:
        bp_data = blood_pressure_sensor.read()
        print("Blood Pressure Data:", bp_data)
        yield [pyRTOS.timeout(2)]  

def temperature_task():
    while True:
        temp_data = temperature_sensor.read()
        print("Temperature Data:", temp_data)
        yield [pyRTOS.timeout(5)]  

def spo2_task():
    while True:
        spo2_data = spo2_sensor.read()
        print("SPO2 Data:", spo2_data)
        yield [pyRTOS.timeout(3)]  # Delay for 3 seconds

def communication_task():
    while True:
        # Communication stuff goes here
        print("Communicating with server...")
        yield [pyRTOS.timeout(1)]  

if __name__ == "__main__":
    pyRTOS.add_task(pyRTOS.Task(ecg_task))
    pyRTOS.add_task(pyRTOS.Task(blood_pressure_task))
    pyRTOS.add_task(pyRTOS.Task(temperature_task))
    pyRTOS.add_task(pyRTOS.Task(spo2_task))
    pyRTOS.add_task(pyRTOS.Task(communication_task))
    pyRTOS.start()
