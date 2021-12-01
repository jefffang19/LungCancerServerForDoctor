# +
from skimage.measure import label, regionprops
import math
from tqdm import tqdm
import torch
import torch.nn as nn
import numpy as np
import segmentation_models_pytorch as smp

from utils import image_resize


# -

def ratio_keep_resize(image, size=224):
    # resize
    if image.shape[0] >= image.shape[1]:
        image=image_resize(image, height = size)
    else:
        image=image_resize(image, width = size)
        
    return image


# +
# lung segment model

def lung_segmentor(path):
    ENCODER = 'densenet161'
    ENCODER_WEIGHTS = 'imagenet'
    DEVICE = 'cpu'
    
    if torch.cuda.is_available():
        DEVICE = 'cuda'
        print('using cuda')
    else:
        print('using cpu')
    
    # segment lung
    lung_seg = smp.Unet(
        encoder_name='densenet161',        # choose encoder, e.g. mobilenet_v2 or efficientnet-b7
        encoder_weights=None,     # use `imagenet` pretreined weights for encoder initialization
        in_channels=3,                  # model input channels (1 for grayscale images, 3 for RGB, etc.)
        classes=1,                      # model output channels (number of classes in your dataset)
    )

    lung_seg.load_state_dict(torch.load(path, map_location=DEVICE))
    lung_seg.eval().to(DEVICE)
    print('eval mode')
    
    return lung_seg


# +
# segment a xray into 6 patches
def into_patches(lung_seg, image, mask=None, size=224):
    '''
    lung_seg: lung segmentation model w input(3, 512, 512) imagenet pretrain weight
    image: numpy array of shape (512, 512, 3)
    mask: numpy array of shape (1, 512, 512)
    size: returned patch size
    returns : patches=[LUL, LML, LLL, RUL, RML, RLL], class_label=[LUL, LML, LLL, RUL, RML, RLL]
    '''
    # into tensor
    x = torch.tensor(np.moveaxis(image, -1, 0)).unsqueeze(0)
        
    # use imagenet normalization
    from torchvision import transforms

    transform = transforms.Compose([
      transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])

    x = transform(x/255)
    if np.any(mask):
        mask = mask.squeeze()

    
    # segment lung roi
    with torch.no_grad():
        if torch.cuda.is_available():
            x = x.cuda().float()
        else:
            x = x.float()
            
        lung_rois = lung_seg(x)
    
    # convert to numpy
    lung = lung_rois.squeeze().cpu().numpy()
    
    # thresholding
    lung = np.where(lung > 0.5, 1, 0)
    
    # get bbox
    label_img = label(lung)
    regions = regionprops(label_img)
    crop_rois = []

    for props in regions:
        minr, minc, maxr, maxc = props.bbox
        crop_rois.append([minr, minc, maxr, maxc])
        
    # decide which way is left
    # note left lung refers to the rightside in xray image
    left_lung = None
    left_lung_2 = None
    right_lung = None
    right_lung_2 = None
    # check image boundary
    # 
    #   ^
    #   | 0
    # <--
    #   1
    #                  2
    #                 -->
    #                 |
    #                \/ 3

    dist = [20, 20, 20, 20]
    
    # boundary condition
    if crop_rois[1][0]-dist[0] < 0:
        dist[0] = crop_rois[1][0]
    if crop_rois[1][1]-dist[1] < 0:
        dist[1] = crop_rois[1][1]
    if crop_rois[0][3]+dist[2] > image.shape[1]:
        dist[2] = image.shape[1]-crop_rois[0][3]
    if crop_rois[0][2]+dist[3] > image.shape[0]:
        dist[3] = image.shape[0]-crop_rois[0][2]
    # boundary condition
    if crop_rois[0][0]-dist[0] < 0:
        dist[0] = crop_rois[0][0]
    if crop_rois[0][1]-dist[1] < 0:
        dist[1] = crop_rois[0][1]
    if crop_rois[1][3]+dist[2] > image.shape[1]:
        dist[2] = image.shape[1]-crop_rois[1][3]
    if crop_rois[1][2]+dist[3] > image.shape[0]:
        dist[3] = image.shape[0]-crop_rois[1][2]
        
    # return the coordinate for patches
    coord = np.zeros((16, 4)) # (y_start, y_end, x_start, x_end)
    left_lung_coord = None
    left_lung_2_coord = None
    right_lung_coord = None
    right_lung_2_coord = None

    if crop_rois[0][1] - crop_rois[1][1] > 0:
        left_lung_coord = [crop_rois[0][0]-dist[0],crop_rois[0][2]+dist[3],crop_rois[0][1]-20,crop_rois[0][3]-35]
        right_lung_coord = [crop_rois[1][0]-dist[0],crop_rois[1][2]+dist[3],crop_rois[1][1]-dist[1],crop_rois[1][3]-35]
        left_lung_2_coord = [crop_rois[0][0]-dist[0],crop_rois[0][2]+dist[3],crop_rois[0][1]+35,crop_rois[0][3]+20]
        right_lung_2_coord = [crop_rois[1][0]-dist[0],crop_rois[1][2]+dist[3],crop_rois[1][1]+35,crop_rois[1][3]+dist[2]]
        
    else:  
        right_lung_coord = [crop_rois[0][0]-dist[0],crop_rois[0][2]+dist[3],crop_rois[0][1]-dist[1],crop_rois[0][3]-35]
        left_lung_coord = [crop_rois[1][0]-dist[0],crop_rois[1][2]+dist[3],crop_rois[1][1]-20,crop_rois[1][3]-35]
        right_lung_2_coord = [crop_rois[0][0]-dist[0],crop_rois[0][2]+dist[3],crop_rois[0][1]+35,crop_rois[0][3]+20]
        left_lung_2_coord = [crop_rois[1][0]-dist[0],crop_rois[1][2]+dist[3],crop_rois[1][1]+35,crop_rois[1][3]+dist[2]]
    
    # split lungs
    left_lung = image[left_lung_coord[0]:left_lung_coord[1], left_lung_coord[2]:left_lung_coord[3]]
    right_lung = image[right_lung_coord[0]:right_lung_coord[1], right_lung_coord[2]:right_lung_coord[3]]
    left_lung_2 = image[left_lung_2_coord[0]:left_lung_2_coord[1], left_lung_2_coord[2]:left_lung_2_coord[3]]
    right_lung_2 = image[right_lung_2_coord[0]:right_lung_2_coord[1], right_lung_2_coord[2]:right_lung_2_coord[3]]
    # set coordinates
    left_lung_y = left_lung_coord[1] - left_lung_coord[0]
    right_lung_y = right_lung_coord[1] - right_lung_coord[0]
    
    coord[0] = np.array([right_lung_coord[0],right_lung_coord[0]+round(right_lung_y*0.33),right_lung_coord[2],right_lung_coord[3]])
    coord[1] = np.array([right_lung_2_coord[0],right_lung_2_coord[0]+round(right_lung_y*0.33),right_lung_2_coord[2],right_lung_2_coord[3]])
    coord[2] = np.array([left_lung_coord[0],left_lung_coord[0]+round(left_lung_y*0.33),left_lung_coord[2],left_lung_coord[3]])
    coord[3] = np.array([left_lung_2_coord[0],left_lung_2_coord[0]+round(left_lung_y*0.33),left_lung_2_coord[2],left_lung_2_coord[3]])
    
    coord[4] = np.array([right_lung_coord[0]+round(right_lung_y*0.22),right_lung_coord[0]+round(right_lung_y*0.55),right_lung_coord[2],right_lung_coord[3]])
    coord[5] = np.array([right_lung_2_coord[0]+round(right_lung_y*0.22),right_lung_2_coord[0]+round(right_lung_y*0.55),right_lung_2_coord[2],right_lung_2_coord[3]])
    coord[6] = np.array([left_lung_coord[0]+round(left_lung_y*0.22),left_lung_coord[0]+round(left_lung_y*0.55),left_lung_coord[2],left_lung_coord[3]])
    coord[7] = np.array([left_lung_2_coord[0]+round(left_lung_y*0.22),left_lung_2_coord[0]+round(left_lung_y*0.55),left_lung_2_coord[2],left_lung_2_coord[3]])
    
    coord[8] = np.array([right_lung_coord[0]+round(right_lung_y*0.44),right_lung_coord[0]+round(right_lung_y*0.77),right_lung_coord[2],right_lung_coord[3]])
    coord[9] = np.array([right_lung_2_coord[0]+round(right_lung_y*0.44),right_lung_2_coord[0]+round(right_lung_y*0.77),right_lung_2_coord[2],right_lung_2_coord[3]])
    coord[10] = np.array([left_lung_coord[0]+round(left_lung_y*0.44),left_lung_coord[0]+round(left_lung_y*0.77),left_lung_coord[2],left_lung_coord[3]])
    coord[11] = np.array([left_lung_2_coord[0]+round(left_lung_y*0.44),left_lung_2_coord[0]+round(left_lung_y*0.77),left_lung_2_coord[2],left_lung_2_coord[3]])
    
    coord[12] = np.array([right_lung_coord[0]+round(right_lung_y*0.66),right_lung_coord[1],right_lung_coord[2],right_lung_coord[3]])
    coord[13] = np.array([right_lung_2_coord[0]+round(right_lung_y*0.66),right_lung_2_coord[1],right_lung_2_coord[2],right_lung_2_coord[3]])
    coord[14] = np.array([left_lung_coord[0]+round(left_lung_y*0.66),left_lung_coord[1],left_lung_coord[2],left_lung_coord[3]])
    coord[15] = np.array([left_lung_2_coord[0]+round(left_lung_y*0.66),left_lung_2_coord[1],left_lung_2_coord[2],left_lung_2_coord[3]])


        ######################################33
    # 0  1  2  3
    # 4  5  6  7
    # 8  9  10 11
    # 12 13 14 15
    
    coord = coord.astype('int')
    patches = []
    # cut 16 patches
    # image
    for i in range(16):
        patches.append(image[coord[i][0]:coord[i][1], coord[i][2]:coord[i][3]])
#     patches.append(right_lung[:round(right_lung.shape[0]*0.33),].copy())
#     patches.append(right_lung_2[:round(right_lung_2.shape[0]*0.33),].copy())
#     patches.append(left_lung[:round(left_lung.shape[0]*0.33),].copy())
#     patches.append(left_lung_2[:round(left_lung_2.shape[0]*0.33),].copy())
    
#     patches.append(right_lung[round(right_lung.shape[0]*0.22):round(right_lung.shape[0]*0.55),].copy())
#     patches.append(right_lung_2[round(right_lung_2.shape[0]*0.22):round(right_lung_2.shape[0]*0.55),].copy())
#     patches.append(left_lung[round(left_lung.shape[0]*0.22):round(left_lung.shape[0]*0.55),].copy())
#     patches.append(left_lung_2[round(left_lung.shape[0]*0.22):round(left_lung_2.shape[0]*0.55),].copy())
    
#     patches.append(right_lung[round(right_lung.shape[0]*0.44):round(right_lung.shape[0]*0.77),].copy())
#     patches.append(right_lung_2[round(right_lung_2.shape[0]*0.44):round(right_lung_2.shape[0]*0.77),].copy())
#     patches.append(left_lung[round(left_lung.shape[0]*0.44):round(left_lung.shape[0]*0.77),].copy())
#     patches.append(left_lung_2[round(left_lung_2.shape[0]*0.44):round(left_lung_2.shape[0]*0.77),].copy())
    
#     patches.append(right_lung[round(right_lung.shape[0]*0.66):,].copy())
#     patches.append(right_lung_2[round(right_lung_2.shape[0]*0.66):,].copy())
#     patches.append(left_lung[round(left_lung.shape[0]*0.66):,].copy())
#     patches.append(left_lung_2[round(left_lung_2.shape[0]*0.66):,].copy())

    # resize
    for i in range(16):
        patches[i] = ratio_keep_resize(patches[i])
        
    # reduce coord because we ignore cases in the boarder 20 pixels
#     for i in range(16):
#         coord[i][0] += 20 
#         coord[i][1] -= 20 
#         coord[i][2] += 20 
#         coord[i][3] -= 20 
    
    return patches, coord
# -






