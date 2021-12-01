import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import numpy as np
from cv2 import cv2
from sklearn.model_selection import train_test_split
import albumentations as albu
import pandas as pd

import segmentation_models_pytorch as smp
import torch
import torch.nn as nn

from utils import visualize, image_resize
from get_data import get_datasets
from seg_patches import into_patches, lung_segmentor
from patches_cls import get_cls_model, fit


def run_inference(dcm_path, data_path, thresh=0.5, verbose=False):
    '''
    data_path : path of the dataset
    thresh : threshold for predict (confidence)
    '''
    dataset = get_datasets(path=dcm_path)
    if verbose:
        print('dataset len {}'.format(len(dataset)))

    # import lung segmentation model
    lung_seg = lung_segmentor('inference/weights/seg_lung.pth')

    # patchwise classification
    model = get_cls_model('inference/weights/cls_model.pth')
    classes = ['no', 'exist']

    # split the input image into patches
    idx = 0
    for image, ori, high_res, pat_id in dataset:
        os.mkdir(os.path.join(data_path, pat_id))
        os.mkdir(os.path.join(data_path, pat_id, 'wholeslide'))
        # save dicom into png
        cv2.imwrite(os.path.join(data_path, pat_id, 'wholeslide/wholeImg.png'), ori)
        cv2.imwrite(os.path.join(data_path, pat_id, 'wholeslide/wholeImg_highres.png'), high_res)

        # predict
        x, coord = into_patches(lung_seg, ori)

        # save patches
        os.mkdir(os.path.join(data_path, pat_id, 'patches'))
        
        for i in range(16):
            cv2.imwrite(os.path.join(data_path, pat_id,
                                     'patches', 'x{}.png'.format(i)), x[i])
            if verbose:
                print(coord[i])

        prd = fit(model, x)
        results = np.where(prd[:, 1] > thresh, 1, 0)

        if verbose:
            print('if nodule exist')
            print(results)
            print('confidence')
            print(prd[:, 1])

        # write model predict results
        y_start = [i[0] for i in coord]
        y_end = [i[1] for i in coord]
        x_start = [i[2] for i in coord]
        x_end = [i[3] for i in coord]
        pred_dict = {'confidence': prd[:, 1], 'nodule_exist': results,
                     'y_start': y_start, 'y_end': y_end, 'x_start': x_start, 'x_end': x_end}

        pred_df = pd.DataFrame(data=pred_dict)
        pred_df.to_csv(os.path.join(data_path, pat_id, 'predict.csv'))

        idx += 1


if __name__ == '__main__':
    run_inference('/home/parse_data/data', 'data_with_grad', thresh=0.7, verbose=True)
