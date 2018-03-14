from __future__ import print_function
from __future__ import division

from di_sensors.temp_hum_press import TempHumPress

import datetime
import os
import sys
import time
import grovepi
from urllib import urlencode
from grove_rgb_lcd import *
import urllib2


# timeinterval 1.0
# https://github.com/srevenant/timeinterval
import timeinterval

import SI1145 #grove_i2c_sunlight_sensor

from config import Config

# ============================================================================
# Constants
# ============================================================================
# specifies how often to measure values from the Sense HAT (in minutes)
MEASUREMENT_INTERVAL = 10  # minutes
# Set to False when testing the code and/or hardware
# Set to True to enable upload of weather data to Weather Underground
WEATHER_UPLOAD = True
# the weather underground URL used to upload weather data
WU_URL = "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"
SINGLE_HASH = "#"
HASHES = "########################################"
SLASH_N = "\n"

air_sensor = 0
temp_hum_pr = TempHumPress() # Temprasure Humidity Pressure Sensor API
grovepi.pinMode(air_sensor, 'INPUT')
ir_uv_sensor = SI1145.SI1145()
setRGB(0, 179, 255)


def main():
    global last_temp

    # initialize the lastMinute variable to the current time to start
    last_minute = datetime.datetime.now().minute
    # on startup, just use the previous minute as lastMinute
    last_minute -= 1
    if last_minute == 0:
        last_minute = 59

    # infinite loop to continuously check weather values
    while 1:
        # on frequent measurements, so we'll take measurements every 5 seconds
        # but only upload on measurement_interval
        current_second = datetime.datetime.now().second
        # are we at the top of the minute or at a 5 second interval?
        if (current_second == 0) or ((current_second % 5) == 0):

            # Read the temperature
            temp_f = temp_hum_pr.get_temperature_fahrenheit()
            # Read the relative humidity
            humidity = temp_hum_pr.get_humidity()
            # Read the pressure
            pressure = temp_hum_pr.get_pressure()

            # Get sensor value
            air_sensor_value = grovepi.analogRead(air_sensor)
            if air_sensor_value > 700:
                print ('High pollution')
            elif air_sensor_value > 300:
                print ('Low pollution')
            else:
                print ('Air fresh')

            readVisible = ir_uv_sensor.readVisible()
            IR = sensor.readIR()
            UV = sensor.readUV()
            uvIndex = UV / 100.0

            setText('Temp: {:5.3f} Hum: {:5.3f} Pres: {:5.3f}'.format(temp_f, humidity, pressure))
            setText('\nAir: {:5.3f}, IR: {:5.3f}, UV: {:5.3f}, UV Index: {:5.3f}'.format(air_sensor_value, IR, UV, uvIndex))

            # get the current minute
            current_minute = datetime.datetime.now().minute
            # is it the same minute as the last time we checked?
            if current_minute != last_minute:
                # reset last_minute to the current_minute
                last_minute = current_minute
                # is minute zero, or divisible by 10?
                # we're only going to take measurements every MEASUREMENT_INTERVAL minutes
                if (current_minute == 0) or ((current_minute % MEASUREMENT_INTERVAL) == 0):
                    # get the reading timestamp
                    now = datetime.datetime.now()
                    print("\n%d minute mark (%d @ %s)" % (MEASUREMENT_INTERVAL, current_minute, str(now)))
                    # did the temperature go up or down?
                    if last_temp != temp_f:
                        if last_temp > temp_f:
                            # display a blue, down arrow
                            setRGB(0, 154, 255)
                        else:
                            # display a red, up arrow
                            setRGB(255, 0, 0)
                    else:
                        # temperature stayed the same
                        # display red and blue bars
                        setRGB(145, 0, 255)
                    # set last_temp to the current temperature before we measure again
                    last_temp = temp_f

                    # ========================================================
                    # Upload the weather data to Weather Underground
                    # ========================================================
                    # is weather upload enabled (True)?
                    if WEATHER_UPLOAD:
                        # From http://wiki.wunderground.com/index.php/PWS_-_Upload_Protocol
                        print("Uploading data to Weather Underground")
                        # build a weather data object
                        google_spreadsheet_data = {
                            'id': wu_station_id,
                            'date': datetime.datetime.now(),
                            'temp': str(temp_f),
                            'humidity': str(humidity),
                            'air': str(air_sensor_value),
                            'ir': str(IR),
                            'uv': str(UV),
                            'uv_index': str(uvIndex),
                        }

                        weather_data = {
                            "action": "updateraw",
                            "ID": wu_station_id,
                            "PASSWORD": wu_station_key,
                            "dateutc": "now",
                            "tempf": str(temp_f),
                            "humidity": str(humidity),
                            "baromin": str(pressure),
                        }
                        try:
                            upload_url = WU_URL + "?" + urlencode(weather_data)
                            response = urllib2.urlopen(upload_url)
                            html = response.read()
                            print("Server response:", html)
                            # do something
                            response.close()  # best practice to close the file

                            google_sheet_url = 'https://script.google.com/macros/s/AKfycbw7j2UB76OLKf6mvwnKJTK4JP1HZCKxGnhxb_4d1ezK-mnQS_yw/exec' + '?' + urlencode(google_spreadsheet_data)
                            res = urllib2.urlopen(google_sheet_url)
                            res_html = res.read()
                            print("Server response:", res_html)
                            res.close()
                        except:
                            print('Exception:', sys.exc_info()[0], SLASH_N)
                    else:
                        print('Skipping Weather Underground upload')

        # wait a second then check again
        # You can always increase the sleep value below to check less often
        time.sleep(1)  # this should never happen since the above is an infinite loop

    print('Leaving main()')

# ============================================================================
# here's where we start doing stuff
# ============================================================================
print(SLASH_N + HASHES)
print(SINGLE_HASH, 'Pi Weather Station                  ', SINGLE_HASH)
print(SINGLE_HASH, 'By Fernando Garcia                  ', SINGLE_HASH)
print(HASHES)

# make sure we don't have a MEASUREMENT_INTERVAL > 60
if (MEASUREMENT_INTERVAL is None) or (MEASUREMENT_INTERVAL > 60):
    print('The application\'s \'MEASUREMENT_INTERVAL\' cannot be empty or greater than 60')
    sys.exit(1)

# ============================================================================
#  Read Weather Underground Configuration Parameters
# ============================================================================
print('\nInitializing Weather Underground configuration')
wu_station_id = Config.STATION_ID
wu_station_key = Config.STATION_KEY
if (wu_station_id is None) or (wu_station_key is None):
    print('Missing values from the Weather Underground configuration file\n')
    sys.exit(1)

# we made it this far, so it must have worked...
print('Successfully read Weather Underground configuration values')
print('Station ID:', wu_station_id)
# print("Station key:", wu_station_key)

# ============================================================================
# initialize the Sense HAT object
# ============================================================================
try:
    setText('Initializing Weather App')
    last_temp = temp_hum_pr.get_temperature_fahrenheit()
    setText('Current temperature reading: ' + str(last_temp))
except:
    print('Unable to initialize Weather App', sys.exc_info()[0])
    sys.exit(1)

setText('Initialization complete!')

# Now see what we're supposed to do next
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        setText('\nExiting application\n')
        sys.exit(0)
