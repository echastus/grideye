import numpy as np
import pandas as pd
import cv2 as cv
import time
import playsound
import os

from serial import Serial

# Variables needed for loading the data from the serial link to Arduino Board.
arduino_port1 = '/dev/cu.usbmodem14101'
arduino_port2 = '/dev/cu.usbmodem14201'
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
            new_frame[(64 * i):(64 * i) + 64, (64 * j):(64 * j) + 64, :] = frame[i, j] / 80 * 255
    return new_frame


def arr_to_img2(frame):
    new_frame = np.zeros(shape=(8, 8, 3), dtype=np.uint8)
    for i, row in enumerate(frame):
        for j, column in enumerate(row):
            new_frame[i, j, :] = frame[i, j] / 80 * 255
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


def detect_motion(filename):
    # Initialising necessary variables.
    df = pd.read_csv(filename, header=None)
    fgbg = cv.createBackgroundSubtractorMOG2()
    bools = np.zeros(shape=(3, ), dtype=bool)
    # Loop that goes through each frame.
    for i in range(len(df)):
        frame = np.array(df.iloc[i]).reshape((8, 8))

        # Create an image to see the sensor output.
        frame2 = arr_to_img(np.transpose(frame))

        # Create an image for the algorithm to work on.
        frame = arr_to_img2(np.transpose(frame))
        fgmask = fgbg.apply(frame)

        # Brain of the algorithm.

        # Returns the sum of pixel values of the left half and the right half of the image.
        temp = sum_halves(fgmask)
        if temp[1] < temp[0]:
            bools[0] = True
        if temp[1] > temp[0] and bools[0]:
            bools[1] = True
        if bools[1] and bools[0] and temp[1] < 765:
            bools[2] = True

        if all(bools):
            print("Someone just went from left to right!")
            bools.fill(False)
        cv.imshow("Frame", frame2)
        cv.waitKey(100)
        cv.destroyAllWindows()


def display_from_port():
    serial_connection = Serial(arduino_port1, baudrate=115200, timeout=2)
    while True:
        try:
            data = serial_connection.readline().decode('ascii')
            frame = data.split(" ")[:-1]
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


def sum_halves(x):
    temp1 = 0
    temp2 = 0
    for i in range(8):
        for j in range(8):
            if j < 4:
                temp1 += x[i][j]
            else:
                temp2 += x[i][j]
    return tuple((temp1, temp2))


if __name__ == "__main__":
    # display_from_file('program_output5.csv')
    # display_from_port()
    # write_to_file(10, 10, 4)
    # main_algorithm_with_no_specified_name_for_the_time_being()
    detect_motion('program_output5.csv')

    # x0 = np.zeros(shape=(8, 8), dtype=np.uint8)
    # x1 = np.zeros(shape=(8, 8), dtype=np.uint8)
    # x1[0][0] = 255
    # x1[1][0] = 255
    # x1[1][1] = 255
    # x1[2][1] = 255
    # x1[2][2] = 255
    # x1[3][2] = 255
    #
    # x2 = np.zeros(shape=(8, 8), dtype=np.uint8)
    # x2[7][7] = 255
    # x2[7][6] = 255
    # x2[6][6] = 255
    # x2[5][6] = 255
    # x2[4][5] = 255
    # x3 = np.zeros(shape=(8, 8), dtype=np.uint8)
    # #765
    # print(x1)
    # print(x2)
    # bools = np.zeros(shape=(3, ), dtype=bool)
    # temps0 = sum_halves(x0)
    # temps1 = sum_halves(x1)
    # temps2 = sum_halves(x2)
    # temps3 = sum_halves(x3)
    # print(temps0)
    # print(temps1)
    # print(temps2)
    # print(temps3)
    #
    # temps = [temps0, temps1, temps2, temps3]
    #
    # for temp in temps:
    #     if temp[0] >= 765 and temp[1] < temp[0]:
    #         bools[0] = True
    #     if temp[1] > temp[0] and temp[1] >= 765:
    #         bools[1] = True
    #     if bools[1] and bools[0] and temp[1] < 765:
    #         bools[2] = True
    #
    # if all(bools):
    #     print("Someone just went from left to right")
