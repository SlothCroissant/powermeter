from audioop import avg
import os
import RPi.GPIO as GPIO
import spidev
import statistics
from datetime import datetime
import mysql.connector
import traceback

########################
# Env Vars
########################
debug = True

# CT Count
ct_count = 8

# Build dict of CTs and their Amp rating
ct_amps = {}
for i in range(ct_count):
    key = str("ct" + str(i))
    ct_amps[key] = float(os.environ.get("ct" + str(i)))

# MySQL DB Info
db_host = os.environ.get("db_host")
db_port = os.environ.get("db_port")
db_database = os.environ.get("db_database")
db_table = os.environ.get("db_table")
db_user = os.environ.get("db_user")
db_pass = os.environ.get("db_pass")


########################
# MySQL
########################
def checkTableExists(db, tablename):
    print("Checking if \"" + db_table + "\" table exists...")
    dbcur = db.cursor()
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


def createTable(dbcon, tablename):
    return True


# Establish DB connection
def connect_db():
    print("Connecting to database: " + db_host + ":" + str(db_port))
    db = mysql.connector.connect(
        host=db_host,
        database=db_database,
        user=db_user,
        password=db_pass
    )
    checkTableExists(db, db_table)
    return db


# TO DO: Create DB if needed:
# CREATE TABLE `energymeter` (
#   `key` int(11) NOT NULL AUTO_INCREMENT,
#   `timestamp` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
#   `ct` int(11) NOT NULL,
#   `watts` float NOT NULL,
#   PRIMARY KEY (`key`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

def insert_data(db, value_arr):
    mycursor = db.cursor()
    sql = (f"INSERT INTO `{db_table}` (ct, watts) VALUES (%s, %s)")
    mycursor.executemany(sql, value_arr)
    db.commit()


########################
# Hardware & Math
########################
# Open SPI bus
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
GPIO.setmode(GPIO.BOARD)
shiftpins = [15, 13, 11]  # This order is important - based on hardware traces.
addresses = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1], [1, 0, 1], [0, 1, 1], [1, 1, 1]]
for pin in shiftpins:
    GPIO.setup(pin, GPIO.OUT)

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
key = 0
while debug == True:  # Loop forever
    try:
        # If the DB hasn't been instantiated yet, connect to it
        try:
            db
        except:
            db = connect_db()

        # Check to see that the DB has connectivity, and reconnect if needed
        db.ping(reconnect=True, attempts=10, delay=10)

        for mux_channel in range(2):
            # Set MUX BIT registers for ADC selection.
            for x in range(3): # range to be expanded (HW Limitation).
                GPIO.output(shiftpins[x], addresses[mux_channel][x])
            # Logging for selected ADC
            values_arr = []
            for i in range(8):
                arr = []
                while (len(arr) < 10):
                    measuredinput = []
                    reading = 1
                    while (reading > 0):
                        reading = get_voltage_reading(i)
                    n = 0
                    while (reading == 0):
                        reading = get_voltage_reading(i)
                        n += 1
                        if (n > 100):
                            for int in range(51):
                                measuredinput.append(reading)
                            break
                    # start = datetime.today().timestamp()
                    while (reading > 0):
                        reading = get_voltage_reading(i)
                        if (reading > 0):
                            measuredinput.append(reading)
                    # end = datetime.today().timestamp()
                    if (len(measuredinput) > 50):
                        arr.append(statistics.mean(measuredinput))
                    measuredinput.clear()
                # print("time: " + str(end) + " | ct: "+ str(i) + " | ct_amps: " + str(ct_amps["ct"+str(i)]) + " | watts: " + str(round(120 * statistics.mean(arr) * ct_amps["ct"+str(i)],2)))
                values_arr.append((i, round(120 * statistics.mean(arr) * ct_amps["ct" + str(i)], 2)))
                key += 1
                arr.clear()
            print(str(datetime.today().timestamp()) + " " + str(values_arr))
            insert_data(db, values_arr)

    except KeyboardInterrupt:
        print("User Exit")
        spi.close()
        GPIO.cleanup()
        exit()
    except Exception:
        print(traceback.format_exc())
        spi.close()
        GPIO.cleanup()
        continue
