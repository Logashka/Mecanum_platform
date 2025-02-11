
from machine import Pin
import machine
import time
import _thread
import random
import json

class SerialPico:

    def __init__(self, uartPin: int, bod: int) -> None:
        self.port = uartPin
        self.uart = machine.UART(self.port, bod)

    def sendData(self, line: str):
        # Sends data over the serial UART
        # Add new line to terminate string
        #print("Sending: ", str)
        self.uart.write(line+'\n')
    
        
    def receiveData(self) -> str:
        dataIn = ""

        while self.uart.any():
            # In a fast enough loop, this may be called before the string
            # has completed sending. This loop will continue until the incoming
            # data has completed. On exception it will send what string it has
            # so far
            rawIn = self.uart.readline()
            #print(rawIn)
            # Raw data is as a byte stream. Convert
            # Need to use a try/except as control characters may cause an issue
            try:
                dataIn += str(rawIn.decode('utf-8').strip())
                #print("Incoming :", dataIn)
            except:
                pass
        return dataIn
