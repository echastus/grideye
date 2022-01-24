import numpy as np
import pandas as pd
import cv2 as cv
from serial import Serial
import time

# Variables needed for loading the data from the serial link to Arduino Board.
arduino_port1 = '/dev/cu.usbmodem14101'
arduino_port2 = '/dev/cu.usbmodem14201'
based_port = 'COM7'
pixel_visibility_threshold = 24.0


# Convert a string of 64 values into an 8x8 array.
def str_to_arr(frame):
    if len(frame) == 64:
        frame = np.transpose(np.array(frame, dtype=np.float64).reshape(8, 8))
    return frame


# Scale an 8x8 array into 512x512 array and scale its values into range (0, 256),
# so that it can be displayed as an image.
def arr_to_img(frame):
    new_frame = np.zeros(shape=(8 * 64, 8 * 64, 3), dtype=np.uint8)
    for i, row in enumerate(frame):
        for j, column in enumerate(row):
            new_frame[(64 * i):(64 * i) + 64, (64 * j):(64 * j) + 64, :] = frame[i][j] / 80 * 255
    return new_frame


# Same as the previous function, but don't scale it to 512x512.
def arr_to_img2(frame):
    new_frame = np.zeros(shape=(8, 8, 3), dtype=np.uint8)
    for i, row in enumerate(frame):
        for j, column in enumerate(row):
            new_frame[i, j, :] = frame[i][j] / 80 * 255
    return new_frame


# Sum values of pixels from the first and second half of the image and return both values.
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


# Sum values of temperatures from the first and second half of the image and return both values.
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


# Display a short video from a .csv file.
def display_from_file(filename):
    df = pd.read_csv(filename, header=None)
    for i in range(len(df)):
        frame = np.array(df.iloc[i]).reshape((8, 8))
        frame = arr_to_img(np.transpose(frame))
        cv.imshow("Frame", frame)
        cv.waitKey(50)
    cv.destroyAllWindows()


# Display data directly from the Grid-EYE.
def display_from_port():
    serial_connection = Serial(based_port, baudrate=115200, timeout=1)
    while True:
        try:
            # Added 'ignore' to ignore mostly "codec can't decode byte" errors B).
            data = serial_connection.readline().decode('ascii', 'ignore')
            frame = data.split(" ")[:-1]
            # A lot of lines are cut because the connection is started in the middle of transfer.
            if (len(frame)) != 64:
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


# 'Record' short videos from the Grid-EYE.
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


# Main algorithm that determines, whether people go inside or outside.
def main(port, debug=False):
    # Initialising necessary variables.
    timer = 0
    num_of_people = 0
    framerate = 1
    fgbg = cv.createBackgroundSubtractorMOG2()
    ltr = np.zeros(shape=(3,), dtype=bool)
    rtl = np.zeros(shape=(3,), dtype=bool)
    serial_connection = Serial(port, baudrate=115200, timeout=2)
    # Loop that goes through each frame.
    while True:
        data = serial_connection.readline().decode('ascii', 'ignore')
        frame = data.split(" ")[:-1]
        if len(frame) != 64:
            continue
        frame = np.transpose(np.array(frame, dtype=np.float16).reshape(8, 8))

        # Created for different purposes.
        temp_frame = arr_to_img2(frame)
        fgmask = fgbg.apply(temp_frame)
        movement_detection = arr_to_img(fgmask)
        grideye_output = arr_to_img(frame)

        # Brain of the algorithm.
        pixels = sum_pixel_vals(fgmask)
        temps = sum_temps(frame)

        # Initialise thresholds.
        pixels_th = 1
        temps_th = 600

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


        # Display different information about the current frame for debugging purposes.
        if debug:
            print(f'pixels[0], temps[0]: {pixels[0]}, {temps[0]}')
            print(f'pixels[1], temps[1]: {pixels[1]}, {temps[1]}')
            print(f'Left to right: {ltr}')
            print(f'Right to left: {rtl}\n')

        # Displaying information and adjusting the num_of_people value.
        if all(ltr):
            num_of_people += 1
            print("Someone has just entered the room!")
            print(f'Current number of people inside: {num_of_people}')
            ltr.fill(False)
            rtl.fill(False)
            info = f'<{1},{num_of_people}>'
            serial_connection.write(info.encode())
        elif all(rtl):
            num_of_people -= 1
            print("Someone has just left the room!")
            print(f'Current number of people inside: {num_of_people}')
            rtl.fill(False)
            ltr.fill(False)
            info = f'<{0},{num_of_people}>'
            serial_connection.write(info.encode())

        # Displaying movement frame and the actual Grid-EYE output frame.
        cv.imshow("Movement detection", movement_detection)
        cv.imshow("Grid-EYE output", grideye_output)
        k = cv.waitKey(framerate)
        if k == ord('q'):
            break
    cv.destroyAllWindows()


if __name__ == "__main__":
    main(port=arduino_port2, debug=True)
# 5, 8
