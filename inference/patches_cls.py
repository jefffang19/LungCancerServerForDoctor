import torch
import torch.nn as nn
import torchvision
import albumentations as albu
import numpy as np
from cv2 import cv2


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
        albu.PadIfNeeded(224, 224, always_apply=True, border_mode=cv2.BORDER_CONSTANT, value=0)
    ]
    
    patches_square = []
    
    for p in patches:
        sample = albu.Compose(test_transform)(image=p)
        patches_square.append(np.moveaxis(sample['image'], -1, 0))
        
    # to tensor
    patches_square = torch.tensor(patches_square).float()
    if torch.cuda.is_available():
        patches_square = patches_square.cuda()
    
    with torch.no_grad():
        pred = model(patches_square)
        
        pred = nn.Softmax(dim=1)(pred)
        
        return pred.cpu().numpy()



