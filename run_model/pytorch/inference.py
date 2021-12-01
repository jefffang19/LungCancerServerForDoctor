import sys
import os
import cv2
import time

if __name__ == '__main__':
    if len(sys.argv) == 1:  # no cases to take care of
        exit()

    # each argv is a image file path
    file_path = sys.argv[1]

    # read image
    img = cv2.imread(file_path, 0)  # read as graysacle

    cv2.imwrite('test.png', img)
