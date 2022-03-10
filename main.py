from audioop import avg
import os
import RPi.GPIO as GPIO
import spidev
import time
import statistics
import heapq
from datetime import datetime
import mysql.connector

########################
# Env Vars
########################
debug = True
# CT Amp Ratings
ct_count = 8

# Build dict of CTs and their Amp rating
ct_amps = {}
for i in range(ct_count):
    key=str("ct"+str(i))
    ct_amps[key]=float(os.environ.get("ct"+str(i)))

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
    _temp = heapq.nlargest(10, data)
    #end = datetime.today().timestamp()
    #print(f"seek time for top 500 was {end - start} seconds")
    #median the _temp (top 500) results from here.
    #print(f" measured input index count: {len(data)}")
    # time.sleep(0.5)
    return statistics.median(_temp)

try:
    # "debug" loop
    arr = []
    while debug == True:
        for i in range(8):
            while (len(arr) < 10):
                measuredinput = []
                reading = 1
                while (reading > 0):
                    reading = ConvertVolts(ReadChannel(i), 4)
                while (reading == 0): # TO DO: What if a CT never goes above zero?
                    reading = ConvertVolts(ReadChannel(i), 4)
                start = datetime.today().timestamp()
                while (reading > 0):
                    reading = ConvertVolts(ReadChannel(i), 4)
                    if (reading > 0):
                        measuredinput.append(reading)
                end = datetime.today().timestamp()
                if (len(measuredinput) > 50):
                    #print(f"Channel: {i} | count: " + str(len(measuredinput)) + ' | time: ' + str(round((end-start)*1000,2)) + 'ms | min: ' + str(min(measuredinput)) + " | max: " + str(max(measuredinput)) + " | mean: " + str(statistics.mean(measuredinput)) + " | stdev: " + str(statistics.stdev(measuredinput)))
                    arr.append(statistics.mean(measuredinput))
                measuredinput.clear()
            print("ct: "+ str(i) + " | ct_amps: " + str(ct_amps["ct"+str(i)]) + " | watts: " + str(120 * statistics.mean(arr) * ct_amps["ct"+str(i)]) + " | stdev: " + str(statistics.stdev(arr)))
            arr.clear()

    # "Prod" loop
    while debug == False:
        measuredinput = []
        for i in range(8):
            start = datetime.today().timestamp()
            while (len(measuredinput) < 10000):
                measuredinput.append(ConvertVolts(ReadChannel(7), 4))
            end = datetime.today().timestamp()
            volts = setmediandata(measuredinput)
            print(f"Channel {i} Time Elapsed: {round((end-start)*1000,2)}")
            print(f"           volts: {volts}")
            print(f"           watts: " + str(120 * volts * ct_amps["ct"+str(i)]))
            print(f"           count: " + str(len(measuredinput)))
            print(f"           stdev: " + str(statistics.stdev(measuredinput)))
            measuredinput.clear()

except KeyboardInterrupt:
    print("User Exit")
