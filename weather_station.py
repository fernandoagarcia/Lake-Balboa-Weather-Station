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
# some string constants
SINGLE_HASH = "#"
HASHES = "########################################"
SLASH_N = "\n"

interval_count = 0
air_sensor = 0
temp_hum_pr = TempHumPress() # Temprasure Humidity Pressure Sensor API
grovepi.pinMode(air_sensor, 'INPUT')
ir_uv_sensor = SI1145.SI1145()
setRGB(0,179,255)

def testme
    setText('I love you Negar ' + interval_count + ' times')
    interval_count++

timer = timeinterval.start(1000, testme)
