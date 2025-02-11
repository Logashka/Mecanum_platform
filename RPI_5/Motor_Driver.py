import serial, time

class MotorDriver:
    def __init__(self, port: str, bod: int):
        
        self.runTime = 60
        self.toggleInt = 1
        dataInt = 1.5
        self.dataTimeOut = 5
        
        self.sport = serial.Serial(port, bod)
        print(self.sport)

    
    
    def sendData(self, messeg: str):
        print("Sending:",messeg)
        data=messeg.encode('UTF-8')
        self.sport.write(data)
        time.sleep(0.02)
        


    def receiveData(self) -> str:
        # Wait for data or time out
        timeOut=time.time() + self.dataTimeOut
        dataIn="Error_timeout"
        
        while (time.time() < timeOut):
            if(self.sport.in_waiting>0):
                # There is data
                #print("There is data waiting")
                rawIn = bytearray()
                while (self.sport.in_waiting > 0):
                    # Read until line ending
                    rawIn += self.sport.read_until()
                    #print('.',end='')
                    
                # Raw data is a byte stream, convert
                # Need to use a try/except as control characters may cause an issue
                try:
                    dataIn = rawIn.decode('utf-8').strip()
                    #print("  Incoming :", dataIn)
                except:
                    dataIn = "Error_decode"
                # We got something, drop out of loop
                #print("Data received")
                break
        # End of while loop, if a timeout then dataIn will be unchanged
        return dataIn



    def getCount(self, motorPort: str) -> int:
        self.sendData(f"motor{motorPort.upper()}.get_count()\n")
        return int(self.receiveData())



    def resetCount(self, motorPort: str):
        self.sendData(f"motor{motorPort.upper()}.reset_count()\n")



    def start(self, motorPorts: str, motorSpeeds: list):
        for i in range(len(motorSpeeds)):
            self.sendData(f"motor{motorPorts[i].upper()}.start({motorSpeeds[i]})\n") if motorSpeeds[i] != 0 else self.stop(motorPorts[i], True)
            


    def stop(self, motorPort: str, type: bool):
        self.sendData(f"motor{motorPort.upper()}" + f".stop({'True' if type else 'False'})\n")



    def reverse(self, motorPort: str, move: bool, encoder: bool):
        self.sendData(f"motor{motorPort.upper()}.reverse(move={'True' if move else 'false'}, encoder={'True' if encoder else 'False'})\n")


    
    
