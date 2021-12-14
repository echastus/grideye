import numpy as np
import pandas as pd
import cv2 as cv

from serial import Serial


def to_csv(file):
    with open(file, "r") as f:
        for line in f:
            if len(line) > 1:
                values = np.array(line.split(" ")[:-1])
                values.resize((8, 8))
                print(values)


def main():
    # to_csv("sensorOutput")
    # port_name = '/dev/cu.usbmodem14101'
    with open("sensorOutput", "r") as f:
        lines = [np.array(line.split(" ")[:-1]).reshape((8, 8)) for line in f if len(line) > 1]
        print("GITHUB CHANGE")


if __name__ == "__main__":
    main()
