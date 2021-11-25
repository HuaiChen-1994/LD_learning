# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 10:22:09 2019

@author: Administrator
"""
import numpy as np
import random
import os
from PIL import Image
import torch
from torch.utils import data
import torchvision.transforms as transforms
def check_and_create_fold(path):
    if not os.path.exists(path):
        os.makedirs(path)
class AverageMeter(object):
    """Computes and stores the average and current value""" 
    def __init__(self):
        self.reset()
                   
    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0 

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count        

class MyDataset(data.Dataset):
    '''
    Data generater
    Args:
        total_num (int): The data number of one epoch.
        data_list (list or array): The list of data.
        data_path (str): The path where the data is.
        if_rot_90 (bool): If True, images will be randomly rotated by 0, 90, 180 or 270.
        if_flip (bool): If True, images will by flipped.
        if_mixup (bool): If True, returns the mixup images.
        transform_list: The list of transformation operations. 
                        It consists three part, respectively for augmenting, generating similar paris and normalization. 
    Returns:
        img1_1,img1_2,img2_1,img2_2 are two similar pairs ().
        img1_2_flip,img1_2_rot,img2_2_flip,img2_2_rot are corresponding augmentation operations of flip and rotation for img1_2 and img2_2.
        img3,img1_weight are mixup image and corresponding fusion weights and only will be returned if if_mixup is True.
    '''
    
    def __init__(self,
                 total_num,
                 data_list,
                 data_path,
                 if_rot_90=True,
                 if_flip=True,
                 if_mixup=True,
                 transform_list=None):
       self.data_list=data_list
       self.data_path=data_path
       self.transform_list=transform_list
       self.if_mixup=if_mixup
       self.if_flip=if_flip
       self.if_rot_90=if_rot_90
       self.total_num=total_num
    
    def __getitem__(self,idex):
        # Randomly choose two images
        choosen_index=random.randint(0, len(self.data_list)-1)
        img1=Image.open(os.path.join(self.data_path,self.data_list[choosen_index]))
        choosen_index=random.randint(0, len(self.data_list)-1)
        img2=Image.open(os.path.join(self.data_path,self.data_list[choosen_index]))
        img1=self.transform_list[0](img1)
        img2=self.transform_list[0](img2)
        
        # Generate similar pairs
        img1_1=self.transform_list[1](img1)
        img2_1=self.transform_list[1](img2)
        img1_2=self.transform_list[1](img1)
        img2_2=self.transform_list[1](img2)
        
        img1_2_flip=random.randint(0,1)
        img1_2_rot=random.randint(0,3)
        if self.if_flip:
            if img1_2_flip:
                img1_2=torch.flip(img1_2,dims=(1,2))
        if self.if_rot_90:
            if img1_2_rot:
                img1_2=torch.rot90(img1_2,k=img1_2_rot,dims=(1,2))
        
        img2_2_flip=random.randint(0,1)
        img2_2_rot=random.randint(0,3)
        if self.if_flip:
            if img2_2_flip:
                img2_2=torch.flip(img2_2,dims=(1,2))
        if self.if_rot_90:
            if img2_2_rot:
                img2_2=torch.rot90(img2_2,k=img2_2_rot,dims=(1,2))
            
        
        if self.if_mixup:
            # IF if_mixup is True, mixup images will be created.
            img1_weight=random.random()*0.6+0.2
            img3=img1_weight*img1_1+(1-img1_weight)*img2_1    
            img3=self.transform_list[2](img3)
            img1_weight=torch.tensor(img1_weight)    
            
            img1_1=self.transform_list[2](img1_1)
            img1_2=self.transform_list[2](img1_2)
            img2_1=self.transform_list[2](img2_1)
            img2_2=self.transform_list[2](img2_2)
                
            return img1_1,img1_2,img2_1,img2_2,img3,img1_weight,img1_2_flip,img1_2_rot,img2_2_flip,img2_2_rot
        else:
            img1_1=self.transform_list[2](img1_1)
            img1_2=self.transform_list[2](img1_2)
            img2_1=self.transform_list[2](img2_1)
            img2_2=self.transform_list[2](img2_2)
                
            return img1_1,img1_2,img2_1,img2_2,img1_2_flip,img1_2_rot,img2_2_flip,img2_2_rot
            
    def __len__(self):
        return self.total_num