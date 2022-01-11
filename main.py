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
            new_frame[(64 * i):(64 * i) + 64, (64 * j):(64 * j) + 64, 0:2] = frame[i, j] / 80 * 255
    return new_frame


def main_algorithm_with_no_specified_name_for_the_time_being():
    # I want to dieeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!!!
    serial_connection = Serial(arduino_port1, baudrate=115200, timeout=2)
    tracker = np.zeros(shape=(8, 8), dtype=bool)
    # while True:
    data = serial_connection.readline().decode('ascii')
    data = data.split(" ")[:-1]
    frame = str_to_arr(data)
    # Base for the algorithm, basically it is supposed to check if the difference, between the current value and the
    # previous value is positive and bigger than 1 for example, that would indicate, that something is coming from the
    # right side, it is then supposed to change the value of tracke on the right edge to True, then it is going to treat
    # the second column from the right as the first column and do the same, if the whole process goes correctly it would
    # mean that someone has entered the room. The algorithm that checks if someone comes from the left will be written
    # later.
    for val, prev_val in zip(frame[:, -1], prev_frame[:, -1]):
        print(val - prev_val)



def display_from_file(filename):
    df = pd.read_csv(filename, header=None)
    for i in range(len(df)):
        frame = np.array(df.iloc[i]).reshape((8, 8))
        frame = arr_to_img(frame)
        cv.imshow("Frame", frame)
        cv.waitKey(100)
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
            k = cv.waitKey(50)
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


if __name__ == "__main__":
    # display_from_file('program_output3.csv')
    display_from_port()
    # write_to_file(10, 3)
    # main_algorithm_with_no_specified_name_for_the_time_being()

