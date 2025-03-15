from Motors import *
from Serial import *
from machine import Pin
from time import sleep
motorB = MotorB() # left_front_motor
motorA = MotorA() # left_back_motor
motorC = MotorC() # right_front_motor
motorD = MotorD() # right_back_motor 
led = Pin(25, Pin.OUT)
# right_back_motor.reverse(move=True, encoder=True)
# left_back_motor.reverse(move=True, encoder=True)
port = SerialPico(0, 115200)
print(port)
while True:
    led.value(0)
    if port.uart.any():
        msg=port.receiveData()
        led.value(1)
        print(f"Message received: \"{msg}\"")
        if(msg=="quit"):
            break
        elif(msg=="toggleLED"):
            port.sendData("ack")
        else:
            parts = msg.split(".")
            if parts[-1] == "get_count()":
                ans = 0
                if parts[0] == "motorA":
                    ans = motorA.get_count()
                if parts[0] == "motorB":
                    ans = motorB.get_count()
                if parts[0] == "motorC":
                    ans = motorC.get_count()
                if parts[0] == "motorD":
                    ans = motorD.get_count()
                print(f"Sending count: {ans}")
                port.sendData(str(ans))
            eval(msg)

