# +
# dataset number
# use to keep track of  which image from which dataset
# vbd = 0
#  jsrt = 1
# ncku = 2

# +
from torch.utils.data import DataLoader
from torch.utils.data import Dataset as BaseDataset
import pandas as pd
import os
import glob
import numpy as np
from cv2 import cv2
import albumentations as albu
from torch.utils.data import ConcatDataset
import segmentation_models_pytorch as smp
import pydicom

from utils import visualize, image_resize


# -

def get_csv(path):
    df = pd.read_csv(os.path.join(path, 'list_of_patient_with_both_ct_and_xray_cleaned.csv'))
    return df


def get_dcm_filename(df, data_path, idx):
    
    return glob.glob(os.path.join(data_path, '{}/xray/*/*.dcm'.format(df.iloc[idx]['patient_id'])))[0]


def get_dcm_img(df, data_path, idx):
    path = get_dcm_filename(df, data_path, idx)
    dcm = pydicom.dcmread(path)
    
    return dcm.pixel_array


class DatasetWholeSlide(BaseDataset):
    """
    Args:
        X, y (list of str): paths of images / labels
        clahe (bool): do clahe or not
        do_resize (tuple of ints): resize the image and mask, if None, DO NOT do resize
        augmentation (albumentations.Compose): data transfromation pipeline 
            (e.g. flip, scale, etc.)
        preprocessing (albumentations.Compose): data preprocessing 
            (e.g. noralization, shape manipulation, etc.)

    """

    def __init__(
            self,
            df,
            data_path,
            clahe=False,
            do_resize=(512, 512),
            augmentation=None,
            preprocessing=None,
    ):
        self.df = df
        self.data_path = data_path

        # check if do augmentation and preprocess
        self.augmentation = augmentation
        self.preprocessing = preprocessing

        self.do_resize = do_resize
        self.clahe = clahe

    def __getitem__(self, i):

        # read img
        highres = get_dcm_img(self.df, self.data_path, i)
        # normalize to 0~255
        highres = ((highres - highres.min()) / (highres.max() - highres.min()) * 255).astype(np.uint8)
        
        image = highres.copy()

        if self.clahe:
            # create a CLAHE object (Arguments are optional).
            clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
            image = clahe.apply(image)

        if self.do_resize:
            # resize
            if image.shape[0] >= image.shape[1]:
                image = image_resize(image, height=self.do_resize[0])
            else:
                image = image_resize(image, width=self.do_resize[1])

        # apply augmentations
        if self.augmentation:
            sample = self.augmentation(image=image)
            image = sample['image']

        # get origin image before normalization
        ori = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # image channel
        image = np.expand_dims(image, axis=-1)

        # apply preprocessing
        if self.preprocessing:
            sample = self.preprocessing(image=image)
            image = sample['image']

        return image, ori, highres, self.df.iloc[i]['patient_id']

    def __len__(self):
        return len(self.df)

# +


def get_validation_augmentation():
    """Add paddings to make image shape divisible by 32"""
    test_transform = [
        albu.PadIfNeeded(512, 512, always_apply=True,
                         border_mode=cv2.BORDER_CONSTANT, value=0)
    ]
    return albu.Compose(test_transform)


def to_tensor(x, **kwargs):
    return x.transpose(2, 0, 1).astype('float32')


def get_preprocessing(preprocessing_fn):
    """Construct preprocessing transform

    Args:
        preprocessing_fn (callbale): data normalization function 
            (can be specific for each pretrained neural network)
    Return:
        transform: albumentations.Compose

    """

    _transform = [
        albu.Lambda(image=preprocessing_fn),
        albu.Lambda(image=to_tensor, mask=to_tensor),
    ]
    return albu.Compose(_transform)


def get_preprocessing_no_pretrain():
    """Construct preprocessing transform

    Return:
        transform: albumentations.Compose

    """

    _transform = [
        albu.Lambda(image=to_tensor),
    ]
    return albu.Compose(_transform)


# -

# lazy person function
# a function return train, test datasets
def get_datasets(path):

    # define preprocessing function
    preprocessing_fn = smp.encoders.get_preprocessing_fn(
        'resnet34', 'imagenet')

    # set data csv
    df = get_csv(path)

    # create dataset
    dataset = DatasetWholeSlide(df, path,  augmentation=get_validation_augmentation(
    ), preprocessing=get_preprocessing(preprocessing_fn), do_resize=(512, 512), clahe=False)

    return dataset
