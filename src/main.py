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

def trigger(timer):
    my_queue.put(PC0pin.read())
    
my_queue = task_share.Queue('h', 1000, name="My Queue")

PC1pin = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
PC0pin = pyb.ADC(pyb.Pin.board.PC0)

n = 0

tim = pyb.Timer(1, freq=1000)

startFlag = False
waitTime = utime.ticks_ms()
dataList = []
flag = True

if __name__ == "__main__":
    while utime.ticks_diff(utime.ticks_ms(),waitTime) < 1000:
        PC1pin.high()
    PC1pin.low()
    tim.callback(trigger)
    print(my_queue)
    while flag:
        if my_queue.full():
            tim.deinit()
            while my_queue.any():
                dataList.append(my_queue.get())
            print(my_queue)
            my_queue.clear()
            print(my_queue)
            flag = False
    print(my_queue)