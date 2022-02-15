'''!
@file       Lab4FrontEnd.py
@brief      Activates a step response for an RC circuit and plots the data and time constant.
@details    Sends characters to a Nucleo set up for an RC step response test, then reads
            the data and plots it. Additionally, calculates the time constant of the circuit
            according to the rule that in 1 second, the response from an RC circuit will have
            36.8% voltage remaining from its initial charge (aka, 1/e).
@author     Jakob Frabosilio, Ayden Carbaugh, Cesar Santana
@date       02/14/2022
'''

import time
import serial
import matplotlib.pyplot as myPlot

def sendChar():
    '''! Triggers an input command that sends an ASCII character through the serial bus
    @return     Returns the uppercase variant of the inputted character.
    '''
    inv = input('Input: ')
    if inv.upper() != 'H':                      # If H, display help command and don't send 
        ser.write(str(inv).encode('ascii'))     # Otherwise, send over serial
    return inv.upper()

def cmdsMsg():
    '''! Prints the list of possible inputs
    '''
    print('\n-----')
    print('CHARACTER | ACTION')
    print('  G / g   | Activate a step response and plot the data')
    print('  S / s   | Stop this program')
    print('  H / h   | Show this message again')
    print('-----')

## Serial communication object
ser = serial.Serial(port='COM8',baudrate=115273,timeout=1)

## Start time tracker (used for UI / time tracking)
startTime = time.time()

## State-tracking variable
state = 0

## String that holds incoming data values
dataVals = ''

## Maximum value of data to scale everything to percentage
scaleVal = 0

## List that holds all data value strings
splitVals = []

## Generated list for plotting yVals against time
xVals = []

## List that holds all data value floats
yVals = []

## Flag that turns True when Tau <= 0.368 is found
tauFlag = False

## Value of Tau (ms)
tauX = 0

if __name__ == "__main__":
    cmdsMsg()                                                         # Prints commands message
    while True:
        
# ----- WAITING STATE -----

        if state == 0:
            if time.time() - startTime > 1 and ser.in_waiting == 0:   # Artificial 1s delay for UX
                myChar = sendChar()                                   # Asks user for input
                if myChar == 'G':
                    state = 1
                    print('Step response activating.')
                elif myChar == 'H':
                    cmdsMsg()
                elif myChar == 'S':                                   # Used for debugging purposes
                    break
                else:
                    print('Invalid character!')
                startTime = time.time()
            elif ser.in_waiting != 0:                                 # Decodes any incoming messages
                print(ser.readline().decode('ascii'))

# ----- LISTENING STATE -----

        elif state == 1:
            if time.time() - startTime > 2.5:                         # Artificial 2.5s delay for data collection
                while ser.in_waiting != 0:
                    dataVals += ser.read().decode()                   # Appends any data to a string
                if ser.in_waiting == 0:
                    state = 2                                         # If no data waiting, send to state 2
                    print('Plotting data.\n-----')
                startTime = time.time()
                
# ----- DATA HANDLING STATE -----

        elif state == 2:
            splitVals = dataVals.split(',')                           # Splits data string into list
            splitVals.pop()                                           # Removes last (intentionally blank) value
            scaleVal = float(splitVals[0])                            # Assumes maximum value is the first value
            for vals in splitVals:
                yVals.append(float(vals)/scaleVal)                    # Scales and appends float values to list
                if float(vals)/scaleVal <= 0.368 and not tauFlag:     # If first value below 0.368, saves length
                    tauX = len(yVals)                                 # of list at current time (used to plot Tau)
                    tauFlag = True
            dataVals = ''                                             # After handling data, reset string and list
            splitVals = []
            state = 3

# ----- PLOTTING STATE -----

        elif state == 3:
            xVals = [*range(0, len(yVals), 1)]                        # Creates a list from zero to the length of data
            if yVals != []:
                fig, ax = myPlot.subplots(1, 1)
                ax.plot(xVals, yVals, ls = '-', color = 'k', label = 'Step Response')
                ax.plot([tauX, tauX], [0, 1], color = 'r', ls = ':', label = 'Time Constant')
                myPlot.xlabel('Time (ms)')                            # Sets axes labels
                myPlot.ylabel('Voltage (percentage of max)')
                ax.annotate('Tau = ' + str(tauX) + ' ms', [tauX+10, 0.75])
                myPlot.legend()                                       # Turns on legend
                myPlot.show()
                xVals = []                                            # Reset lists and variables
                yVals = []
                tauX = 0
                tauFlag = False
            startTime = time.time()
            state = 0
