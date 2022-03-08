import RPi.GPIO as GPIO
import spidev
import time
import os
import statistics
import heapq
from datetime import datetime

Debug = True
X = ""

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
    adc = spi.xfer2([ 6 | (channel&4) >> 2, (channel&3)<<6, 0])
    #print(adc)
    #time.sleep(0.10)
    data = ((adc[1]&15) << 8) + adc[2]
    return data

# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data, places):
    volts = (data * 3.3) / float(4095)
    volts = round(volts, places)
    return volts

def setmediandata(data):
    #pushing additional math here testing:
    #get top 500 results from 60hz grab
    #start = datetime.today().timestamp()
    _temp = heapq.nlargest(4000, data)
    #end = datetime.today().timestamp()
    #print(f"seek time for top 500 was {end - start} seconds")
    #median the _temp (top 500) results from here.
    #print(f" measured input index count: {len(data)}")
    time.sleep(0.5)
    return statistics.median(_temp)

try:
    while Debug == False:
        #Itterate through Channels (0-7)
        for i in range(8):
            if (X == ""):
                print(f"channel: {i} returning {ConvertVolts(ReadChannel(i), 4)}")
            else:
                print(f"channel: {X} returning {ConvertVolts(ReadChannel(X), 4)}")
            #time.sleep(1)
        # Wait before repeating loop
        time.sleep(1)
        #print(spi)

    while Debug == True:
        measuredinput = []
        if (X == ""):
            for i in range(8):
                start = datetime.today().timestamp()
                end = datetime.today().timestamp()
                while ((end - start) <= 1):
                    measuredinput.append(ConvertVolts(ReadChannel(i), 4))
                    end = datetime.today().timestamp()
                print(f"Channel: {i} returning Median Value without AC correction: {setmediandata(measuredinput)}")
                measuredinput.clear()

        else:
            start = datetime.today().timestamp()
            end = datetime.today().timestamp()
            while ((end - start) <= 1):
                measuredinput.append(ConvertVolts(ReadChannel(X), 4))
                end = datetime.today().timestamp()
            print(f"Channel: {X} returning Median Value without AC correction: {setmediandata(measuredinput)}")


except KeyboardInterrupt:
    print("User Exit")
