import sys
import os
import cv2
import numpy as np
import time
from seg_patches import *
from patches_cls import get_cls_model, fit


if __name__ == '__main__':
    if len(sys.argv) == 1:  # no cases to take care of
        exit()

    # each argv is a image file path
    file_path = sys.argv[1]

    # read image
    img = cv2.imread(file_path)  # read

    # get lung segmentation model
    lung_seg = lung_segmentor('run_model/pytorch/weights/seg_lung.pth')

    # get classification model
    cls_model = get_cls_model('run_model/pytorch/weights/cls_model.pth')

    # segment into patches
    patches, coord = into_patches(lung_seg, img)

    # save patches
    file_name = file_path.split('/')[-1].split('.')[0]
    os.mkdir(os.path.join('run_model/static/run_model/patches', file_name))
    for i in range(16):
        cv2.imwrite(os.path.join('run_model/static/run_model/patches', file_name,
                                 'x{}.png'.format(i)), cv2.cvtColor(patches[i], cv2.COLOR_RGB2BGR))

    # predict
    prd = fit(cls_model, patches)
    results = prd[:, 1]

    print(results)
