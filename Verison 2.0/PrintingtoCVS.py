import pandas as pd
import numpy as np
import time
import serial
from datetime import datetime
from datetime import date
import threading
from mpu9250_i2c import *

def startIMU():   ## starts IMU and gets data from the mpu9250_i2c.py file
    time.sleep(1) 
    print("Started IMU")  # lets me know IMU started okay
    try:
        while(True):
            try:
                startIMU.ax,startIMU.ay,startIMU.az,startIMU.wx,startIMU.wy,startIMU.wz = mpu6050_conv() #gets data from mpu9250_i2c.py 
                startIMU.mx,startIMU.my,startIMU.mz = AK8963_conv() #gets data from mpu9250_i2c.py
            except:
                continue	
    except KeyboardInterrupt:   # allows me to stop thread with control c
        sys.exit(0)

def convert_to_degrees(rawValue): # for gps convert data to degrees
    decimalValue = rawValue/100.00
    degrees = int(decimalValue)
    hold = (decimalValue - int(decimalValue))/0.6
    position = degrees + hold
    position = "%.4f" %(position)
    return position

def startGPS(): # starts the GPS
    device = (serial.Serial("/dev/ttyS0")) ## initializers
    startGPS.latitudeInDegrees = 0
    startGPS.longitudeInDegrees = 0
    startGPS.numStatellites = 0
    startGPS.Elivation = 0
    print("Started GPS") # lets me know GPS started okay
    try:
        while True:
            Data = (str)(device.readline()) # gets $GPGGA data               
            DataAvailable = Data.find("$GPGGA,") # finds the $GPGGA data                 
            if (DataAvailable>0):
                GPGGAString = Data.split("$GPGGA,",1)[1] 
                buffer = (GPGGAString.split(',')) # splits up $GPGGA data to array
                try:
                    nmea_latitude =  float(buffer[1])  # converts from string to float              
                    nmea_longitude = float(buffer[3])  # converts from string to float
                    startGPS.numStatellites = float(buffer[6]) # converts from string to float
                    startGPS.Elivation = float(buffer[8]) # converts from string to float
                    startGPS.latitudeInDegrees  = convert_to_degrees(nmea_latitude)    # converts from float raw data to degrees
                    startGPS.longitudeInDegrees = convert_to_degrees(nmea_longitude)   # converts from float raw data to degrees                 
                except ValueError:
                    print("connecting")   # prints conneceting when no connection                    
    except KeyboardInterrupt: # allows me to stop thread with control c
        sys.exit(0)

def timeAndDate():
    today = date.today()  # gets month/day/year
    timeAndDate.todaysDate = today.strftime("%d/%m/%Y")  # gets month/day/year
    now = datetime.now()  # gets hour/mintues/seconds
    timeAndDate.timeString = now.strftime("%H:%M:%S") # gets hour/mintues/seconds   

t1 = threading.Thread(target=startGPS) # allows GPS and IMU to run at the same time
t2 = threading.Thread(target=startIMU) # allows GPS and IMU to run at the same time
t1.start() #starts GPS
t2.start() #starts GPS
timeAndDate()  # calls time and date so it will be ready for array
time.sleep(2)  # waits just to make sure gps is ready
my_array = np.array ([[timeAndDate.todaysDate,timeAndDate.timeString,   ## array for pandas to cvs
                        startGPS.numStatellites, startGPS.latitudeInDegrees, startGPS.longitudeInDegrees, startGPS.Elivation,
                        startIMU.ax,startIMU.ay,startIMU.az,
                        startIMU.mx, startIMU.my,startIMU.mz,
                        startIMU.wx, startIMU.wy,startIMU.wz]])

df3 = pd.DataFrame(my_array, columns = ['Date','Time','Satelliates',  ## uses pandas for array to cvs 
                        'Latitude','Longitude','Elivation (m)','X Accel (m/s^2)',
                        'Y Accel (m/s^2)','Z Accel (m/s^2)','X Mag (uT)',
                        'Y Mag (uT)','Z Mag (uT)','X Gyro (rps)',
                        'Y Gyro (rps)','Z Gyro (rps)'])

while(1):
    my_array = np.array ([[timeAndDate.todaysDate, timeAndDate.timeString,  ## gets new data fopr array for pandas to cvs
                        startGPS.numStatellites, startGPS.latitudeInDegrees, startGPS.longitudeInDegrees, startGPS.Elivation,
                        startIMU.ax,startIMU.ay,startIMU.az,
                        startIMU.mx, startIMU.my,startIMU.mz,
                        startIMU.wx, startIMU.wy,startIMU.wz]])
    df = pd.DataFrame(my_array, columns = ['Date','Time','Satelliates',  ## makes template for addending data
                        'Latitude','Longitude','Elivation (m)','X Accel (m/s^2)',
                        'Y Accel (m/s^2)','Z Accel (m/s^2)','X Mag (uT)',
                        'Y Mag (uT)','Z Mag (uT)','X Gyro (rps)',
                        'Y Gyro (rps)','Z Gyro (rps)'])                  
    df3 = df3.append(df, ignore_index = True) ## appends data
    timeAndDate() ## calls time and date for next append
    time.sleep(.5) ## pauses for half a second so pi doesn't freeze 
    df3.to_csv('Data.csv') # outputs to Data.csv
    # add radio tranmitter

