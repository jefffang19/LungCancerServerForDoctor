import sys
import os
import cv2
import numpy as np
import time
from seg_patches import *
from patches_cls import get_cls_model, fit
import requests


if __name__ == '__main__':
    if len(sys.argv) == 1:  # no cases to take care of
        exit()

    print('inference argv: ', sys.argv)

    # each argv : image_path, case_id
    file_path = sys.argv[1]
    case_id = sys.argv[2]

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

    print('model predict : ', results)

    # now post the result to db
    client = requests.session()

    # get csrf token
    # https://stackoverflow.com/questions/13567507/passing-csrftoken-with-python-requests
    # Retrieve the CSRF token first
    client.get('http://127.0.0.1:5757/run_model/get_csrf_token')  # sets cookie

    csrftoken = None
    if 'csrftoken' in client.cookies:
        # Django 1.6 and up
        csrftoken = client.cookies['csrftoken']
    else:
        print('cannot get csrf token')

    # print(csrftoken)

    # POST the complete state to model query
    post_data = {'case_id': case_id, 'state': 2,
                 'csrfmiddlewaretoken': csrftoken}

    URL = 'http://127.0.0.1:5757/run_model/update_query'
    r = client.post(URL, data=post_data, headers=dict(Referer=URL))

    print('request result: ', r)
