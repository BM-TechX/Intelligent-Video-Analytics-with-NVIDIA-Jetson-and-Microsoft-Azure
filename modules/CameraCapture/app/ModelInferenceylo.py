"""
load yolov5 model
and run inference
"""

import sys
sys.path.append('yolov5')
from IPython.core.display import ProgressBar
import argparse
import os
import platform
from pathlib import Path
import torch
import torch.nn.functional as F
from models.common import DetectMultiBackend
from utils.augmentations import classify_transforms
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadScreenshots, LoadStreams
from utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, print_args, strip_optimizer)
from utils.plots import Annotator
from utils.torch_utils import select_device, smart_inference_mode

class ModelInference:
    def __init__(self, weights, imgsz=(224,224), half=False, dnn=False, device='', bs=1, vid_stride=1):
        self.weights = weights
        self.imgsz = imgsz
        self.half = half
        self.dnn = dnn
        self.device = device
        self.bs = bs
        self.vid_stride = vid_stride
        self.device = select_device(self.device)
        ROOT = 'yolov5'
        data=ROOT
        self.model = DetectMultiBackend(self.weights, device=self.device, dnn=self.dnn, data=data, fp16=self.half)
        self.stride, self.names, self.pt = self.model.stride, self.model.names, self.model.pt
        self.imgsz = check_img_size(self.imgsz, s=self.stride)  # check image size

        self.vid_path, self.vid_writer = [None] * self.bs, [None] * self.bs
    def warmup(self):
        # Warmup
        self.model.warmup(imgsz=(1 if self.pt else self.bs, 3, *self.imgsz))
        
    def run_inference(self,frame):
        # Run inference
        seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
        torch_transforms= classify_transforms(self.imgsz[0])
        im = torch_transforms(image)
        im = torch.Tensor(im).to(self.model.device)
        im = im.half() if self.model.fp16 else im.float()
        if len(im.shape)==3:
            im=im[None]
        results = self.model(im)

        pred = F.softmax(results, dim=1)  # probabilities
        for i, prob in enumerate(pred):
            top5i = prob.argsort(0,descending=True).tolist()
            for x in top5i:
                print( self.names[top5i[x]] + ":" + str(prob.tolist()[top5i[x]]))

