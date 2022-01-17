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


def main(filename):
    # Initialising necessary variables.
    df = pd.read_csv(filename, header=None)
    fgbg = cv.createBackgroundSubtractorMOG2()
    left_to_right = np.zeros(shape=(3, ), dtype=bool)
    right_to_left = np.zeros(shape=(3, ), dtype=bool)
    # Loop that goes through each frame.
    for i in range(len(df)):
        frame = np.array(df.iloc[i]).reshape((8, 8))
        # Create an image to see the sensor output.
        frame3 = arr_to_img(np.transpose(frame))

        # Create an image for the algorithm to work on.
        temp_frame = arr_to_img2(np.transpose(frame))
        fgmask = fgbg.apply(temp_frame)
        frame2 = arr_to_img(fgmask)

        # Brain of the algorithm.

        # Returns the sum of pixel values of the left half and the right half of the image.
        pixel_halves = sum_pixel_vals(fgmask)
        temps = sum_temps(frame)
        print(temps)
        print(np.abs(temps[0] - temps[1]))

        # Checking all the conditions for people going left to right.
        if pixel_halves[1] < pixel_halves[0] and pixel_halves[0] > 765 and not right_to_left[0]:
            left_to_right[0] = True
            right_to_left.fill(False)
        if pixel_halves[1] > pixel_halves[0] and left_to_right[0] and not right_to_left[0]:
            left_to_right[1] = True
        if left_to_right[1] and left_to_right[0] and pixel_halves[1] < 765 and not right_to_left[0]:
            left_to_right[2] = True

        # Checking all the conditions for people going right to left.
        if pixel_halves[0] < pixel_halves[1] and pixel_halves[1] > 765 and not left_to_right[0]:
            right_to_left[0] = True
            left_to_right.fill(False)
        if pixel_halves[0] > pixel_halves[1] and right_to_left[0] and not left_to_right[0]:
            right_to_left[1] = True
        if right_to_left[1] and right_to_left[0] and pixel_halves[0] < 765 and not left_to_right[0]:
            right_to_left[2] = True

        # Displaying information
        if all(left_to_right):
            print("Someone has just entered the room!")
            left_to_right.fill(False)
        if all(right_to_left):
            print("Someone has just left the room!")
            right_to_left.fill(False)
        cv.imshow("Frame", frame2)
        cv.imshow("Frame2", frame3)
        cv.waitKey(80)
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

def read_and_write_port():
    serial_connection = Serial(arduino_port1, baudrate=115200, timeout=2)


<<<<<<< HEAD
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
=======
if __name__ == "__main__":
    # display_from_file('program_output3.csv')
    display_from_port()
    # write_to_file(10, 3)
    # main_algorithm_with_no_specified_name_for_the_time_being()
>>>>>>> 9a82be4a4b4604c0bf7cfd121f8f5281806ce560


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
    main('program_output2.csv')
