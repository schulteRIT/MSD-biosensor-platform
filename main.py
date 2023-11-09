import pyRTOS
import machine
# import ecg_sensor
# import blood_pressure_sensor
# import temperature_sensor
# import spo2_sensor
import network
import time
import socket
import json
import random


class ECGSensor:
    def __init__(self):
        self.last_value = 80  # Starting value, typical resting heart rate

    def read(self):
        new_component = random.uniform(-1, 1)  # Small change
        self.last_value = self.last_value * 0.9 + new_component * 0.1
        return max(50, min(120, int(self.last_value)))  # Clamp the value to a realistic range

class BloodPressureSensor:
    def __init__(self):
        self.last_systolic = 120
        self.last_diastolic = 80

    def read(self):
        systolic_change = random.uniform(-1, 1)
        diastolic_change = random.uniform(-0.5, 0.5)
        self.last_systolic = self.last_systolic * 0.9 + systolic_change * 0.1
        self.last_diastolic = self.last_diastolic * 0.9 + diastolic_change * 0.1
        return (
            max(90, min(140, int(self.last_systolic))),
            max(60, min(90, int(self.last_diastolic)))
        )

class TemperatureSensor:
    def __init__(self):
        self.last_temp = 37.0  # Average human body temperature in Celsius

    def read(self):
        change = random.uniform(-0.05, 0.05)
        self.last_temp = self.last_temp * 0.9 + change * 0.1
        return round(max(36.5, min(37.5, self.last_temp)), 1)

class SpO2Sensor:
    def __init__(self):
        self.last_spo2 = 98  # Starting value, typical SpO2 level

    def read(self):
        change = random.uniform(-0.1, 0.1)
        self.last_spo2 = self.last_spo2 * 0.9 + change * 0.1
        return max(95, min(100, int(self.last_spo2)))

ecg_sensor = ECGSensor()
blood_pressure_sensor = BloodPressureSensor()
temperature_sensor = TemperatureSensor()
spo2_sensor = SpO2Sensor()

# Global dictionary to store sensor data
sensor_data = {
    'ecg': 'No Data',
    'bp': 'No Data',
    'temp': 'No Data',
    'spo2': 'No Data'
}

ecg_rtos_task = None
bp_rtos_task = None
temp_rtos_task = None
spo2_rtos_task = None
server_rtos_task = None
led_rtos_task = None

def ecg_task(self):
    print("Initializing ECG task...")
    global sensor_data
    yield
    print("Starting ECG task...")
    while True:
        ecg_data = ecg_sensor.read()
        sensor_data['ecg'] = ecg_data  
        print("ECG Data:", ecg_data)
        yield [pyRTOS.timeout(1)]

def blood_pressure_task(self):
    print("Initializing blood pressure task...")
    global sensor_data
    yield
    print("Starting blood pressure task...")
    while True:
        bp_data = blood_pressure_sensor.read()
        sensor_data['bp'] = f"{bp_data[0]}/{bp_data[1]}"  # Format as "systolic/diastolic"
        print("Blood Pressure Data:", bp_data)
        yield [pyRTOS.timeout(2)]

def temperature_task(self):
    print("Initializing temperature task...")
    global sensor_data
    yield
    print("Starting temperature task...")
    while True:
        temp_data = temperature_sensor.read()
        sensor_data['temp'] = temp_data
        print("Temperature Data:", temp_data)
        yield [pyRTOS.timeout(5)]

def spo2_task(self):
    print("Initializing SpO2 task...")
    global sensor_data
    yield
    print("Starting SpO2 task...")
    while True:
        spo2_data = spo2_sensor.read()
        sensor_data['spo2'] = spo2_data
        print("SPO2 Data:", spo2_data)
        yield [pyRTOS.timeout(3)]
        
def toggle_led_task(self):
    print("Initializing LED task...")
    led = machine.Pin("LED", machine.Pin.OUT)
    yield
    print("Starting LED task...")
    while True:
        led.value(not led.value())
        yield [pyRTOS.timeout(0.5)]



def web_page(data):
    html = f"""<!DOCTYPE html>
<html>
<head><title>Sensor Data</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>
function requestData() {{
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {{
        if (this.readyState == 4 && this.status == 200) {{
            var data = JSON.parse(this.responseText);
            document.getElementById("ecg").innerHTML = data.ecg;
            document.getElementById("bp").innerHTML = data.bp;
            document.getElementById("temp").innerHTML = data.temp;
            document.getElementById("spo2").innerHTML = data.spo2;
        }}
    }};
    xhttp.open("GET", "sensors", true);
    xhttp.send();
}}
setInterval(requestData, 1000); // Request data every 1000 ms
</script>
</head>
<body>
<h1>Sensor Data</h1>
<p>ECG: <span id="ecg">{data.get('ecg', 'N/A')}</span></p>
<p>Blood Pressure: <span id="bp">{data.get('bp', 'N/A')}</span></p>
<p>Temperature: <span id="temp">{data.get('temp', 'N/A')}</span></p>
<p>SPO2: <span id="spo2">{data.get('spo2', 'N/A')}</span></p>
</body>
</html>
"""
    return html

def ap_mode(ssid, password):
    """
        Description: This is a function to activate AP mode
        
        Parameters:
        
        ssid[str]: The name of your internet connection
        password[str]: Password for your internet connection
        
        Returns: None
    """
    # Just setting up our access point
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)
    
    while not ap.active():
        pass
    print('AP Mode is active. You can now connect.')
    print('IP Address to connect to: ' + ap.ifconfig()[0])

def sensor_server_task(self):
    print("Initializing sensor server task...")
    try:
        print("Initializing AP mode...")
        ap_mode('P17448_BIOSENSOR', 'PASSWORD')  
    except Exception as e:
        print("Failed to initialize AP mode:", e)
        return  # Exit the task if AP mode fails to start

    # Server socket setup should be outside the try block or in its own try block to not catch exceptions from ap_mode
    try:
        print("Initializing socket...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 80))
        s.listen(5)
        s.setblocking(False)
    except Exception as e:
        print("Socket creation/bind/listen failed:", e)
        return  # Exit the task if socket setup fails

    yield  
    print("Sensor server task started. Waiting for connections...")
    while True:
        try:
            conn, addr = s.accept()
            print(f"Connection accepted from {addr}")
        except OSError as e:
            if e.errno == 11:
                yield [pyRTOS.timeout(0.1)]  # Yield control back to scheduler with a small timeout
                continue
            else:
                raise  # Re-raise the exception if it's not a blocking error


        try:
            # Process incoming connection
            request = conn.recv(1024)
            request = request.decode('utf-8')
            print('Received request:', request)

            # Respond to the sensors path
            if 'GET /sensors' in request:
                response = json.dumps(sensor_data)
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: application/json\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response.encode())
            else:
                # Respond with the main page
                response = web_page(sensor_data)
                conn.sendall('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n'.encode() + response.encode())

            conn.close()
        except Exception as e:
            print("Error handling the connection:", e)
        finally:
            # Ensure the connection is closed in case of error
            if conn:
                conn.close()

        yield


if __name__ == "__main__":
    
    ecg_rtos_task = pyRTOS.Task(ecg_task, name='ECG_Task')
    bp_rtos_task = pyRTOS.Task(blood_pressure_task, name='BP_Task')
    temp_rtos_task = pyRTOS.Task(temperature_task, name='Temp_Task')
    spo2_rtos_task = pyRTOS.Task(spo2_task, name='SpO2_Task')
    server_rtos_task = pyRTOS.Task(sensor_server_task, name='Server_Task')
    led_rtos_task = pyRTOS.Task(toggle_led_task, name='LED_Task')
    
    pyRTOS.add_task(ecg_rtos_task)
    pyRTOS.add_task(bp_rtos_task)
    pyRTOS.add_task(temp_rtos_task)
    pyRTOS.add_task(spo2_rtos_task)
    pyRTOS.add_task(server_rtos_task)
    pyRTOS.add_task(led_rtos_task)
    
    pyRTOS.start()