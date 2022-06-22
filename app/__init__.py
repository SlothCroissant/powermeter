
import os
import re
import math
import statistics
from datetime import datetime
import RPi.GPIO as GPIO
import spidev
import logging
from flask import Flask, jsonify

########################
# Env Vars
########################

# CT Count
CT_COUNT = 0
print('Parsing provided Environment Variables:')
myPattern = re.compile(r'^ct[0-9]_[0-9]$')
for key, val in os.environ.items():
    if myPattern.match(key):
        print(f'{key}={val}')
        CT_COUNT += 1
mux_channel_count = int(math.ceil(CT_COUNT / 8))
print('Found ' + str(CT_COUNT) + " CTs across " + str(mux_channel_count) + " Mux channels")

# Build dict of CTs and their Amp rating
ct_amps = {}
for mux_channel in range(mux_channel_count):
    for i in range(8):
        KEY = str("ct" + str(mux_channel) + "_" + str(i))
        ct_amps[KEY] = float(os.environ.get("ct" + str(mux_channel) + "_" + str(i)))

########################
# Hardware & Math
########################
# Open SPI bus
print("Opening SPI bus...")
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000


# Function to read SPI data from MCP3008 / MCP3208 chip
# Channel must be an integer 0-7
def read_raw_data(ct):
    adc = spi.xfer2([6 | (ct & 4) >> 2, (ct & 3) << 6, 0])
    data = ((adc[1] & 15) << 8) + adc[2]
    return data


# Configure GPIO and Mode
print("Setting GPIO Mode...")
GPIO.setmode(GPIO.BOARD)
shiftpins = [15, 13, 11]  # This order is important - based on hardware traces.
addresses = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]]
for pin in shiftpins:
    print("Setting GPIO Pin " + str(pin) + "...")
    GPIO.setup(pin, GPIO.OUT)

print("Pins set.")


# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def get_voltage_reading(ct):
    places = 4
    volts = (read_raw_data(ct) * 3.3) / float(4095)
    volts = round(volts, places)
    return volts


def process_ct(ct, mux_channel):
    arr = []
    # We want 10 sine wave "upside" cycles to ensure good data
    while len(arr) < 10:
        measuredinput = []
        # Until we get 50 readings on a single upside, keep checking
        reading = 1
        # Get initial reading - if > 0 (top half of the sine wave), wait till we get back to 0.
        while reading > 0:
            reading = get_voltage_reading(ct)
        # Now that we're back to 0 (bottom half of the sine wave), let's wait till we get back to the top half so we can take a reading
        n = 0
        while reading == 0:
            reading = get_voltage_reading(ct)
            n += 1
            # But if we get to 100 readings without anything, we should assume this CT is actually reading zeroes.
            if n > 100:
                for _ in range(5):
                    measuredinput.append(0.0)
                break
        # Now that the CT is reading > 0, add all the values to measuredinput array so we can calculate off of them.
        while reading > 0:
            reading = get_voltage_reading(ct)
            if reading > 0:
                measuredinput.append(reading)
        # Now that the reading is now back below zero, check to see if we have "enough" readings to make a decision (basically, exclude any readings that didn't have 4 consecutive values above 0):
        if len(measuredinput) >= 4:
            arr.append(statistics.mean(measuredinput))
        measuredinput.clear()
    str_ct = "ct" + str(mux_channel) + "_" + str(ct)
    str_val = round(120 * statistics.mean(arr) * ct_amps["ct" + str(mux_channel) + "_" + str(ct)], 2)
    return({"ct_name": str_ct, "ct_value_watts": str_val})


########################
# Do Work
########################
def query_records():
    values_arr = []
    for mux_channel in range(mux_channel_count):
        # Set MUX BIT registers for ADC selection.
        for _ in range(3):  # range to be expanded (HW Limitation).
            GPIO.output(shiftpins[_], addresses[mux_channel][_])
        # Logging for selected ADC (each ADC is hard-coded to 8 channels at this point)
        for _ in range(8):
            values_arr.append(process_ct(_, mux_channel))
    return values_arr


########################
# Python Flask
########################

def create_app():
    app = Flask(__name__)
    
    @app.route('/', methods=['GET'])

    def index():
        start = datetime.now()
        records = query_records()
        timestamp = datetime.today().timestamp()
        end = datetime.now()
        timediff = (end - start).total_seconds() * 1000
        return jsonify(timestamp=timestamp, records=records, elapsed_time=timediff)

    return app
