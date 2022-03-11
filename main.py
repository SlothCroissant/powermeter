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
db_host = os.environ.get("db_host")
db_port = os.environ.get("db_port")
db_user = os.environ.get("db_user")
db_pass = os.environ.get("db_pass")

# Build dict of CTs and their Amp rating
ct_amps = {}
for i in range(ct_count):
    key=str("ct"+str(i))
    ct_amps[key]=float(os.environ.get("ct"+str(i)))

########################
# MySQL
########################
def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False

# Establish DB connection
mydb = mysql.connector.connect(
  host=db_host,
  user=db_user,
  password=db_pass
)
print("Connected to database: " + db_host + ":" + str(db_port))
print("Checking if \"powermeter\" table exists...")
print(checkTableExists(mydb, "powermeter"))

########################
# Hardware & Math
########################
# Open SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def read_raw_data(ct):
    adc = spi.xfer2([ 6 | (ct&4) >> 2, (ct&3)<<6, 0])
    data = ((adc[1]&15) << 8) + adc[2]
    return data

# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def get_voltage_reading(ct):
    places = 4
    volts = (read_raw_data(ct) * 3.3) / float(4095)
    volts = round(volts, places)
    return volts

########################
# Do Work
########################

try:
    # "debug" loop
    while debug == True:
        for i in range(8):
            arr = []
            while (len(arr) < 10):
                measuredinput = []
                reading = 1
                while (reading > 0):
                    reading = get_voltage_reading(i)
                n=0
                while (reading == 0):
                    reading = get_voltage_reading(i)
                    n+=1
                    if (n>100):
                        for int in range(51):
                            measuredinput.append(reading)
                        break
                start = datetime.today().timestamp()
                while (reading > 0):
                    reading = get_voltage_reading(i)
                    if (reading > 0):
                        measuredinput.append(reading)
                end = datetime.today().timestamp()
                if (len(measuredinput) > 50):
                    arr.append(statistics.mean(measuredinput))
                measuredinput.clear()
            print("time: " + str(end) + " | ct: "+ str(i) + " | ct_amps: " + str(ct_amps["ct"+str(i)]) + " | watts: " + str(round(120 * statistics.mean(arr) * ct_amps["ct"+str(i)],2)) + " | stdev: " + str(statistics.stdev(arr)))
            arr.clear()

except KeyboardInterrupt:
    print("User Exit")
