import NaturalLanguage
import numpy as np
import pandas as pd
import cv2 as cv
import time
import playsound
import os
import threading


from serial import Serial

# Variables needed for loading the data from the serial link to Arduino Board.
arduino_port1 = '/dev/cu.usbmodem14101'
arduino_port2 = '/dev/cu.usbmodem14201'
based_port = 'COM7'
pixel_visibility_threshold = 24.0


# Convert a string of 64 values into an 8 by 8 numpy array
def str_to_arr(frame):
    if len(frame) == 64:
        frame = np.transpose(np.array(frame, dtype=np.float64).reshape(8, 8))
    return frame


def arr_to_img(frame):
    new_frame = np.zeros(shape=(8 * 64, 8 * 64, 3), dtype=np.uint8)
    for i, row in enumerate(frame):
        for j, column in enumerate(row):
            new_frame[(64 * i):(64 * i) + 64, (64 * j):(64 * j) + 64, :] = frame[i, j] / 100 * 255
    return new_frame


def arr_to_img2(frame):
    new_frame = np.zeros(shape=(8, 8, 3), dtype=np.uint8)
    for i, row in enumerate(frame):
        for j, column in enumerate(row):
            new_frame[i, j, :] = frame[i, j] / 100 * 255
    return new_frame


def display_from_file(filename):
    df = pd.read_csv(filename, header=None)
    fgbg = cv.createBackgroundSubtractorMOG2()
    for i in range(len(df)):
        frame = np.array(df.iloc[i]).reshape((8, 8))
        frame = arr_to_img(np.transpose(frame))
        fgmask = fgbg.apply(frame)
        cv.imshow("Frame", frame)
        cv.imshow("FG Frame", fgmask)
        cv.waitKey(10)
    cv.destroyAllWindows()


def main(filename, debug=False):
    # Initialising necessary variables.
    framerate = 50
    df = pd.read_csv(filename, header=None)
    fgbg = cv.createBackgroundSubtractorMOG2()
    ltr = np.zeros(shape=(3, ), dtype=bool)
    rtl = np.zeros(shape=(3, ), dtype=bool)
    # Loop that goes through each frame.
    for i in range(len(df)):
        frame = np.array(df.iloc[i]).reshape((8, 8))
        # Create an image to see the sensor output.
        frame3 = arr_to_img(np.transpose(frame))

        # Create an image for the algorithm to work on.
        temp_frame = arr_to_img2(np.transpose(frame))
        fgmask = fgbg.apply(temp_frame)
        for x, row in enumerate(fgmask):
            for y, column in enumerate(row):
                if fgmask[x][y] > 0:
                    fgmask[x][y] = 255
        frame2 = arr_to_img(fgmask)

        # Brain of the algorithm.

        # Returns the sum of pixel values of the left half and the right half of the image.
        pixels = sum_pixel_vals(fgmask)
        temps = sum_temps(frame)
        pixels_th = 765
        temps_th = 620

        # Checking all the conditions for people going left to right.
        if pixels[1] < pixels[0] and pixels[0] > pixels_th and not rtl[0]:
            if temps[1] < temps[0] and temps[0] > temps_th:
                ltr[0] = True
                rtl.fill(False)
        if pixels[1] > pixels[0] and ltr[0] and not rtl[0]:
            if temps[1] > temps[0]:
                ltr[1] = True
                rtl.fill(False)
        if ltr[1] and ltr[0] and pixels[1] < pixels_th and not rtl[0]:
            if temps[1] < temps_th:
                ltr[2] = True
            elif temps[0] > temps_th:
                ltr[1] = False

        # Checking all the conditions for people going right to left.
        if pixels[0] < pixels[1] and pixels[1] > pixels_th and not ltr[0]:
            if temps[0] < temps[1] and temps[1] > temps_th:
                rtl[0] = True
                ltr.fill(False)
        if pixels[0] > pixels[1] and rtl[0] and not ltr[0]:
            if temps[0] > temps[1]:
                ltr.fill(False)
                rtl[1] = True
        if rtl[1] and rtl[0] and pixels[0] < pixels_th and not ltr[0]:
            if temps[0] < temps_th:
                rtl[2] = True
            elif temps[1] > temps_th:
                rtl[1] = False

        if debug:
            print(f'pixels[0], temps[0]: {pixels[0]}, {temps[0]}')
            print(f'pixels[1], temps[1]: {pixels[1]}, {temps[1]}')
            print(f'Left to right: {ltr}')
            print(f'Right to left: {rtl}\n')
            framerate = 1

        # Displaying information
        if all(ltr):
            print("Someone has just entered the room!")
            ltr.fill(False)
            rtl.fill(False)
        if all(rtl):
            print("Someone has just left the room!")
            rtl.fill(False)
            ltr.fill(False)
        cv.imshow("Frame", frame2)
        cv.imshow("Frame2", frame3)
        cv.waitKey(framerate)
    cv.destroyAllWindows()


def display_from_port():
    serial_connection = Serial(based_port, baudrate=115200, timeout=1)
    while True:
        try:
            data = serial_connection.readline().decode('ascii', 'ignore') # added 'ignore' to ignore mostly "codec can't decode byte" errors B)
            frame = data.split(" ")[:-1]
            if (len(frame)) != 64: # a lot of lines are cut because the connection is started in the middle of transfer
                continue

            frame = str_to_arr(frame)
            frame = arr_to_img(frame)
            cv.imshow('grideye output', frame)
            k = cv.waitKey(1)
            if k == ord('q'):
                break

        except Exception as e:
            print(e)
            break
    cv.destroyAllWindows()


def write_to_file(video_length, num_of_vids, sleep_time=5.5):
    serial_connection = Serial(arduino_port1, baudrate=115200, timeout=2)
    for i in range(num_of_vids + 1):
        playsound.playsound('sound.mp3')
        if i == 0:
            filename = 'trashfile.csv'
        else:
            filename = f'program_output{i}.csv'
        print(f'Saving values to file no.{i}')
        t_end = time.time() + video_length
        with open(filename, 'w') as f:
            while time.time() < t_end:
                data = serial_connection.readline().decode('ascii')
                data = ",".join(data.split(" ")[:-1])
                if filename != 'trashfile.csv':
                    f.write(data + '\n')
        playsound.playsound('sound.mp3')
        time.sleep(sleep_time)
    os.remove('trashfile.csv')


def sum_pixel_vals(x):
    left = 0
    right = 0
    for i in range(8):
        for j in range(8):
            if j < 4:
                left += x[i][j]
            else:
                right += x[i][j]
    return tuple((left, right))


def sum_temps(x):
    left = 0
    right = 0
    for i in range(8):
        for j in range(8):
            if j < 4:
                left += x[i][j]
            else:
                right += x[i][j]
    return tuple((left, right))


if __name__ == "__main__":
    main('program_output5.csv', debug=True)
# 5, 8
