from numpy.lib.type_check import imag
import serial
import numpy as np
import cv2 as cv

def translate(frame): #maps a range of degrees (init) to 8-bit colour values (result)
    initMin = 20
    initMax = 60
    resultMin = 0
    resultMax = 254

    initSpan = initMax - initMin
    resultSpan = resultMax - resultMin
    
    for i in range(len(frame)):
        value = float(frame[i])
        newValue = max(0, float(value - initMin) / float(initSpan)) # max(0, x) doesnt allow newValue to be negative
        frame[i] = np.uint8(resultMin + (newValue * resultSpan))
        
def frameToImage(frame):
    sideSize = 64
    image = np.zeros((sideSize*8, sideSize*8, 3), np.uint8)         

    translate(frame)

    for t in range(64):
        y = t // 8
        x = t % 8

        for p in range(y*sideSize, (y+1)*sideSize):
            for r in range(x*sideSize, (x+1)*sideSize):
                image[r, p, 1] = frame[t] #sadly, full rbg colours slows the imshow() function

    return image

# main

unoPort = 'COM7'
serialport = serial.Serial(unoPort, baudrate = 115200, timeout = 2)
output = open('sensorOutput', 'a')

while(1):
    try:
        data = serialport.readline().decode('ascii')
        frame = data.split(" ")

        if len(frame) == 64:
            # output.write(data)
            cv.imshow('grideye output', frameToImage(frame))
            k = cv.waitKey(1) & 0xFF
            if k == ord('q'):
                break

    except UnicodeDecodeError: #mistake in serial stream encoding?
        continue

output.close()