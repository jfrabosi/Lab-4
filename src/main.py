'''!
@file       main.py
@brief      Initiates a step response and sends data to MCU over USB VCP
@details    After recieving a character via USB VCP from an MCU (Nucleo),
            initiates a step response on an RC circuit as shown in Lab4
            instructions. Then, sends the data over USB VCP to the MCU
            for plotting and data handling.
@author     Jakob Frabosilio, Ayden Carbaugh, Cesar Santana
@date       02/14/2022
'''

import pyb
import utime
import task_share
from pyb import USB_VCP

def trigger(timer):
    '''! Puts the analog read value from PinC0 into a queue
    '''
    my_queue.put(PC0pin.read())
    
def nothing(timer):
    '''! Surprisingly, does nothing (used to replace trigger callback)
    '''
    pass

## Serial bus used to communicate with PC
myUSB = USB_VCP()

## Queue for callback-triggered data collection
my_queue = task_share.Queue('h', 1000, name="My Queue")

## Output pin object
PC1pin = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)

## Input pin object using analog to digital conversion
PC0pin = pyb.ADC(pyb.Pin.board.PC0)

## Timer object for callback function
tim = pyb.Timer(1, freq=1000)

## Variable that holds value of my_queue.get() temporarily
holderVar = 0

## State-tracking variable
state = 0

## Bool flag that keeps code in data-collection loop
queueFlag = True

if __name__ == "__main__":
    PC1pin.high()                                              # Sets output pin high to charge RC circuit
    while True:
        try:
            
# ----- WAITING STATE -----

            if state == 0:
                if myUSB.any():                                # Checks if any chars have been sent over USB
                    userInput = myUSB.read(1).decode()         # If so, reads char and assigns it to variable
                    
                    # Input G or g to start data collection
                    if userInput == 'g' or userInput == 'G':
                        state = 1
                      
# ----- STEP RESPONSE STATE -----

            elif state == 1:
                PC1pin.low()                                   # Sets output pin low to begin RC discharge
                tim.callback(trigger)                          # Assigns trigger callback function to timer
                while queueFlag:                               # Loops until data sending is done
                    if my_queue.full():                        # Initiates data sending once queue is full
                        tim.callback(nothing)                  # Turns off callback function for timer
                        while my_queue.any():
                            holderVar = str(my_queue.get())    # Assigns datapoint as string to holder variable
                            myUSB.write(holderVar.encode())    # Encodes and writes holder variable
                            myUSB.write(','.encode())          # Sends comma (for decoding/handling in frontend)
                        my_queue.clear()                       # Clears the queue
                        queueFlag = False                      # Once done, turns off queueFlag
                PC1pin.high()                                  # Sets output pin high to charge capacitor
                state = 0
                queueFlag = True
                
        except Exception as theError:
            tim.callback(nothing)                              # If error, turns off callback to avoid bricking the MCU
            print(theError)
            break