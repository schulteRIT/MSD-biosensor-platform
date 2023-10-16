import Max30100
from machine import Timer, Pin
from time import sleep
MODE_HR = 0x02
MODE_SPO2 = 0x03
led = machine.Pin('LED', machine.Pin.OUT) #configure LED Pin as an output pin and create and led object for Pin class
timeInterval = 0 # global variable
lastTimeInterval = 0 # global variable

def interruption_handler(pin):
    global timeInterval
    timeInterval += 1

def adjO2():
    a=[]
    mx30.set_mode(MODE_SPO2)  # Trigger an initial temperature read.

    for i in range(0, 250):
        mx30.read_sensor()
        if(mx30.red!=0 and mx30.ir!=0):
            b=mx30.ir/mx30.red
            a.append(b);
    if(len(a)!=0):
        avg = sum(a)/len(a)
        if(avg>=1):
            avg=1
        print("average SPO2 in 1/500000 of a second: " + str(avg))
        a.clear()
    else:
        print ("no SPO2 detected please insert finger")
        
if __name__ == "__main__":
    data=[]
    soft_timer = Timer(mode=Timer.PERIODIC, period=1, callback=interruption_handler)
    mx30 = Max30100.MAX30100()
    d=0
    mx30.set_mode(MODE_HR)  # Trigger an initial temperature
    y=0
    z=[]
    rising=falling=False
    state=0
    while False:
        mx30.read_sensor()
        print(mx30.ir)
    if(True):
        while True:
            #adjO2()
            #time.sleep(1)
            for i in range(50):
                mx30.read_sensor()
                a=mx30.ir
            mx30.read_sensor()
            if(mx30.ir>a and state ==0):
                timeInterval=0
                rising = True
                state=1
            elif (state==0):
                timeInterval=0
                state=1
                falling=True
                
            if(rising and mx30.ir<a):
                bpm = 60000/timeInterval
                if(bpm<120):
                    print("bpm : " + str(60000/timeInterval))
                    led.value(True)  #turn on the LED
                    

                    data.append(timeInterval)
                    timeInterval=0
                    if(len(data)!=0):
                        s=sorted(data)
                        median = s[(len(data)//2)-1]
                        
                        print("bpm ave:" +str(60000/median))


            elif(falling and mx30.ir>a):
                bpm = 60000/timeInterval
                if(bpm<120):
                    print("bpm : " + str(60000/timeInterval))
                    led.value(True)  #turn on the LED

                    data.append(timeInterval)
                    timeInterval=0
                
                    if(len(data)!=0):
                        s=sorted(data)
                        median = s[(len(data)//2)-1]
                        
                        print("bpm ave:" +str(60000/median))


            a=0
            c=0
            
            #time.sleep(1)
            led.value(False)  #turn on the LED

        


