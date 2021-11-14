from numpy.lib.type_check import imag
import serial
import numpy as np
import cv2 as cv

def translate(frame):
    initMin = 0
    initMax = 60
    resultMin = 0
    resultMax = 254

    initSpan = initMax - initMin
    resultSpan = resultMax - resultMin

    newFrame = np.zeros(len(frame), np.uint8)
    
    for i in range(len(frame)):
        value = float(frame[i])
        newValue = float(value - initMin) / float(initSpan)
        newFrame[i] = np.uint8(resultMin + (newValue * resultSpan))

    return newFrame

def coolColors(value):
    color = (0, value, value/2)
    return color
        
def frameToImage(frame):
    sideSize = 64
    image = np.zeros((sideSize*8, sideSize*8, 3), np.uint8)
    
    translate(frame)            

    for t in range(64):
        color = coolColors(float(frame[t]))
        y = t // 8
        x = t % 8

        for p in range(y*sideSize, (y+1)*sideSize):
            for r in range(x*sideSize, (x+1)*sideSize):
                image[p, r] = color

    return image

# main

unoPort = 'COM7'

serialport = serial.Serial(unoPort, baudrate = 115200, timeout = 2)
output = open('sensorOutput', 'a')

while(1):
    data = serialport.readline().decode('ascii')
    frame = (data.split(" ")[:-1])

    if len(frame) == 64:
        output.write(data)
        cv.imshow('grideye output', frameToImage(frame))
        k = cv.waitKey(1) & 0xFF
        if k == ord('q'):
            break

output.close()