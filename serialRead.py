import serial
import numpy as np
import cv2 as cv


def translate(frame):  # maps a range of degrees (init) to 8-bit colour values (result)
    initMin = int(frame[-1])  # last element of frame is value of potentiometer already in degrees
    initMax = 60
    resultMin = 0
    resultMax = 254

    initSpan = initMax - initMin
    resultSpan = resultMax - resultMin

    for i in range(64):
        value = float(frame[i])
        newValue = max(0.0, float(value - initMin) / float(initSpan))  # max(0, x) doesnt allow newValue to be negative
        frame[i] = np.uint8(resultMin + (newValue * resultSpan))


def frameToImage(frame):
    sideSize = 64
    image = np.zeros((sideSize * 8, sideSize * 8, 3), np.uint8)

    translate(frame)

    for t in range(64):
        y = t // 8
        x = t % 8

        for p in range(y * sideSize, (y + 1) * sideSize):
            for r in range(x * sideSize, (x + 1) * sideSize):
                image[r, p, 1] = frame[t]  # sadly, full rbg colours slows the imshow() function

    return image


# main
unoPort1 = 'COM7'
unoPort2 = '/dev/cu.usbmodem14101'
serialport = serial.Serial(unoPort2, baudrate=115200, timeout=2)

with open('sensorOutput', 'a'):

    while True:
        try:
            data = serialport.readline().decode('ascii')
            frame = data.split(" ")

            if len(frame) == 65:
                # output.write(data)
                cv.imshow('grideye output', frameToImage(frame))
                k = cv.waitKey(1) & 0xFF
                if k == ord('q'):
                    break

        except UnicodeDecodeError:  # mistake in serial stream encoding?
            continue
