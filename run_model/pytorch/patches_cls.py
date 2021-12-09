import torch
import torch.nn as nn
import torchvision
import albumentations as albu
import numpy as np
from cv2 import cv2

from torchcam.cams import CAM
from torchcam.utils import overlay_mask
from torchvision.transforms.functional import to_pil_image


def get_cls_model(path):
    ENCODER = 'resnet34'
    ENCODER_WEIGHTS = 'imagenet'

    model = torchvision.models.resnet34(pretrained=True)
    model.fc = nn.Linear(in_features=512, out_features=2, bias=True)

    DEVICE = 'cpu'
    if torch.cuda.is_available():
        print('using gpu')
        DEVICE = 'cuda'
        model.cuda()
    else:
        print('using cpu')

    model.load_state_dict(torch.load(path, map_location=DEVICE))

    return model


def fit(model, patches):
    test_transform = [
        albu.PadIfNeeded(224, 224, always_apply=True,
                         border_mode=cv2.BORDER_CONSTANT, value=0)
    ]

    patches_square = []

    for p in patches:
        sample = albu.Compose(test_transform)(image=p)
        patches_square.append(np.moveaxis(sample['image'], -1, 0))

    # to tensor
    patches_square = torch.tensor(patches_square).float()

    # init cam
    cam = CAM(model, 'layer4', 'fc')

    print('input patch sizes: ', patches_square.shape)
    if torch.cuda.is_available():
        patches_square = patches_square.cuda()

    with torch.no_grad():
        # cam only support batch = 1
        cams_images = []

        for i in range(16):
            pred = model(patches_square[i].unsqueeze(0))

            pred = nn.Softmax(dim=1)(pred)

            activation_map = cam(class_idx=1)

            cam_result = overlay_mask(to_pil_image(patches[i]), to_pil_image(
                activation_map, mode='F'), alpha=0.5)

            cams_images.append(np.array(cam_result))

        # monkey patch the probability
        pred = model(patches_square)

        pred = nn.Softmax(dim=1)(pred)

        return pred.cpu().numpy(), cams_images
