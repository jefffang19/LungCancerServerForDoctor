import sys
import os
import cv2
import numpy as np
import time
from seg_patches import *
from patches_cls import get_cls_model, fit
import requests
from dotenv import load_dotenv


if __name__ == '__main__':
    if len(sys.argv) == 1:  # no cases to take care of
        exit()

    load_dotenv()
    PORT = os.getenv("PORT")

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
    prd, cam_img = fit(cls_model, patches)
    results = prd[:, 1]

    # save cam
    for i in range(16):
        cv2.imwrite(os.path.join('run_model/static/run_model/patches', file_name,
                                 'h{}.png'.format(i)), cv2.cvtColor(cam_img[i], cv2.COLOR_RGB2BGR))

    print('model predict : ', results)

    # now post the result to db
    client = requests.session()

    # get csrf token
    # https://stackoverflow.com/questions/13567507/passing-csrftoken-with-python-requests
    # Retrieve the CSRF token first
    # sets cookie
    client.get('http://127.0.0.1:{}/run_model/get_csrf_token'.format(PORT))

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

    URL = 'http://127.0.0.1:{}/run_model/update_query'.format(PORT)
    r = client.post(URL, data=post_data, headers=dict(Referer=URL))

    print('model query request result: ', r)

    # POST the confidence of prediction to model predict
    post_data = {'case_id': case_id, 'path': os.path.join('run_model/static/run_model/patches', file_name),
                 'p0': results[0], 'p1': results[1], 'p2': results[2], 'p3': results[3], 'p4': results[4], 'p5': results[5], 'p6': results[6], 'p7': results[7],
                 'p8': results[8], 'p9': results[9], 'p10': results[10], 'p11': results[11], 'p12': results[12], 'p13': results[13], 'p14': results[14], 'p15': results[15],
                 'csrfmiddlewaretoken': csrftoken}

    URL = 'http://127.0.0.1:{}/run_model/save_result'.format(PORT)
    r = client.post(URL, data=post_data, headers=dict(Referer=URL))

    print(PORT)

    print('model predict request result: ', r)
