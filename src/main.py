'''!
@file       main.py
@brief      
@details    
@author     Jakob Frabosilio
@date       02/08/2022
'''

import pyb
import utime
import task_share

def trigger():
    my_queue.put(PC0pin.read())
    
my_queue = task_share.Queue('h', 1000, name="My Queue")

PC1pin = pyb.Pin(pyb.Pin.board.PC1, Pin.OUT_PP)
PC0pin = pyb.ADC(pyb.Pin.board.PC0)
tim = pyb.Timer(1, freq=1000, callback=trigger())

startFlag = False
waitTime = utime.ticks_ms()
CSVlist = []

if __name__ == "__main__":
    PC1pin.high()
    while True:
        if my_queue.full():
            PC1pin.low()
            while my_queue.any():
                CSVlist.append(my_queue.get())
            my_queue.clear()
#             waitTime = utime.ticks_ms()
#             startFlag = True
            print(csvList)
            break
#         elif utime.ticks_diff(utime.ticks_ms,waitTime) > 500 and startFlag:
#             PC1pin.high()
#             startFlag = False