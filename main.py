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
    with open("sensorOutput", "r") as f:
        frames = [np.array(line.split(" ")[:-1]).reshape((8, 8)) for line in f if len(line) > 1]
        for frame in frames:
            frame = np.transpose(frame).astype(np.float32)
            new_frame = np.zeros((frame.shape[0] * 64, frame.shape[1] * 64, 3), dtype=np.uint8)
            for i, row in enumerate(frame):
                for j, column in enumerate(row):
                    temp = np.uint8(column / 100 * 255)
                    if temp > 60:
                        new_frame[(64 * i):(64 * i) + 64, (64 * j):(64 * j) + 64, 1] = temp
                    else:
                        new_frame[(64 * i):(64 * i) + 64, (64 * j):(64 * j) + 64, 1] = 0
            cv.imshow("frame", new_frame)
            cv.waitKey(50)

    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
