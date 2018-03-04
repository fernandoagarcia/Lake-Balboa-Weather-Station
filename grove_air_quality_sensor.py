import time
import grovepi

# Connect the Grove Air Quality Sensor to analog port A0
# SIG,NC,VCC,GND
air_sensor = 0

grovepi.pinMode(air_sensor,"INPUT")

while True:
    try:
        # Get sensor value
        sensor_value = grovepi.analogRead(air_sensor)

        if sensor_value > 700:
            print "High pollution"
        elif sensor_value > 300:
            print "Low pollution"
        else:
            print "Air fresh"

        print "sensor_value =", sensor_value
        time.sleep(.5)

    except IOError:
        print "Error"