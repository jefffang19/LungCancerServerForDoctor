import sys
import os
import cv2
import time

if __name__ == '__main__':
    if len(sys.argv) == 1:  # no cases to take care of
        exit()

    time.sleep(5)
    # each argv is a image file path
    print(sys.argv[1])
