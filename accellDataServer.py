#!/usr/bin/python

import smbus
import math
import time
import socket
import sys
import json

#### Model to send to Unity
class accellGyro:
    def __init__(self, accelX, accelY, accelZ, gyroX, gyroY, gyroZ, rotX, rotY):
        self.AccelX = accelX
        self.AccelY = accelY
        self.AccelZ = accelZ
        self.GyroX = gyroX
        self.GyroY = gyroY
        self.GyroZ = gyroZ
        self.RotX = rotX
        self.RotY = rotY


####### Socket Server Setup

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('192.168.8.107', 27015)

print 'starting up on %s port %s' % server_address
sock.bind(server_address)

sock.listen(1)

###Accel/Gyro Stuffs
# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)





while True:
    print 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print 'connection from', client_address

        #receive data in chunks
        while True:
            data = connection.recv(16)
            print 'received "%s"' % data

            if data:
                print 'Got some data'



                while True:
                    print "gyro data"
                    print "---------"

                    gyro_xout = read_word_2c(0x43)
                    gyro_yout = read_word_2c(0x45)
                    gyro_zout = read_word_2c(0x47)

                    print "gyro_xout: ", gyro_xout, " scaled: ", (gyro_xout / 131)
                    print "gyro_yout: ", gyro_yout, " scaled: ", (gyro_yout / 131)
                    print "gyro_zout: ", gyro_zout, " scaled: ", (gyro_zout / 131)

                    print
                    print "accelerometer data"
                    print "------------------"

                    accel_xout = read_word_2c(0x3b)
                    accel_yout = read_word_2c(0x3d)
                    accel_zout = read_word_2c(0x3f)

                    accel_xout_scaled = accel_xout / 16384.0
                    accel_yout_scaled = accel_yout / 16384.0
                    accel_zout_scaled = accel_zout / 16384.0

                    print "accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled
                    print "accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled
                    print "accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled

                    print "x rotation: " , get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
                    print "y rotation: " , get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
                    

                    axs = accel_xout_scaled
                    ays = accel_yout_scaled
                    azs = accel_zout_scaled
                    gxs = gyro_xout / 131
                    gys = gyro_yout / 131
                    gzs = gyro_zout / 131
                    rox = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
                    roy = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

                    accellGyroData = accellGyro(axs, ays, azs, gxs, gys, gzs, rox, roy )

                    ##jsonStr = json.dumps( accellGyroData.__dict__ )
                    jsonStr = str(axs) + "," + str(ays) + "," + str(azs) + "," + str(gxs) + "," + str(gys) + "," + str(gzs) + "," + str(rox) + "," + str(roy)

                    connection.sendall(   jsonStr   )
                    
                    time.sleep(0.1)


                
                
            else:
                print 'no more data from', client_address
                break
    finally:
        connection.close()



