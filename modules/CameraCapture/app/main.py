# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import os
import random
from re import A
import sys
import time

#import iothub_client
# pylint: disable=E0611
# Disabling linting that is not supported by Pylint for C extensions such as iothub_client. See issue https://github.com/PyCQA/pylint/issues/1955
#from iothub_client import (IoTHubModuleClient, IoTHubClientError, IoTHubError,
#                           IoTHubMessage, IoTHubMessageDispositionResult,
#                           IoTHubTransportProvider)

# from azure.iot.device import IoTHubModuleClient, Message

import CameraCapture
from CameraCapture import CameraCapture


# global counters
SEND_CALLBACKS = 0



def main(
        videoPath,
        imageProcessingEndpoint="",
        imageProcessingParams="",
        showVideo=False,
        verbose=False,
        loopVideo=True,
        convertToGray=False,
        resizeWidth=0,
        resizeHeight=0,
        annotate=False,
        fps=0,
        AZURE_STORAGE_BLOB="",
        AZURE_STORAGE_CONNECTION_STRING="",
        AZURE_STORAGE_CONTAINER="",
        IMAGEWIDTH=0,
        IMAGEHEIGHT=0,
        ROI1="0,0,0,0",
        ROI2="0,0,0,0",
        ROI3="0,0,0,0",
        ROI4="0,0,0,0",
        genral_rotation="0",
        roi1_rotation="0",
        roi2_rotation="0",
        roi3_rotation="0",
        roi4_rotation="0",
        roi1a="0,0,0,0",
        roi1b="0,0,0,0",
        roi1c="0,0,0,0",
        rpo1d="0,0,0,0"
        ):
    '''
    Capture a camera feed, send it to processing and forward outputs to EdgeHub

    :param int videoPath: camera device path such as /dev/video0 or a test video file such as /TestAssets/myvideo.avi. Mandatory.
    :param str imageProcessingEndpoint: service endpoint to send the frames to for processing. Example: "http://face-detect-service:8080". Leave empty when no external processing is needed (Default). Optional.
    :param str imageProcessingParams: query parameters to send to the processing service. Example: "'returnLabels': 'true'". Empty by default. Optional.
    :param bool showVideo: show the video in a windows. False by default. Optional.
    :param bool verbose: show detailed logs and perf timers. False by default. Optional.
    :param bool loopVideo: when reading from a video file, it will loop this video. True by default. Optional.
    :param bool convertToGray: convert to gray before sending to external service for processing. False by default. Optional.
    :param int resizeWidth: resize frame width before sending to external service for processing. Does not resize by default (0). Optional.
    :param int resizeHeight: resize frame width before sending to external service for processing. Does not resize by default (0). Optional.ion(
    :param bool annotate: when showing the video in a window, it will annotate the frames with rectangles given by the image processing service. False by default. Optional. Rectangles should be passed in a json blob with a key containing the string rectangle, and a top left corner + bottom right corner or top left corner with width and height.
    :param int fps: frames per second to send to the external service for processing. 0 by default, which means no throttling. Optional.
    :param str AZURE_STORAGE_BLOB: Azure Storage Blob name. Optional.
    :param str AZURE_STORAGE_CONNECTION_STRING: Azure Storage Connection String. Optional.
    :param str AZURE_STORAGE_CONTAINER: Azure Storage Container name. Optional.
    '''
    try:
        print("\nPython %s\n" % sys.version)
        with CameraCapture(videoPath, imageProcessingEndpoint, imageProcessingParams, showVideo, verbose, loopVideo, convertToGray, resizeWidth, resizeHeight, annotate,fps,AZURE_STORAGE_BLOB,AZURE_STORAGE_CONNECTION_STRING,AZURE_STORAGE_CONTAINER,IMAGEWIDTH,IMAGEHEIGHT,
                           ROI1,ROI2,ROI3,ROI4,genral_rotation,roi1_rotation,roi2_rotation,roi3_rotation,roi4_rotation,roi1a,roi2a,roi3a,roi4a) as cameraCapture:
            cameraCapture.start()
    except KeyboardInterrupt:
        print("Camera capture module stopped")


def __convertStringToBool(env):
    if env in ['True', 'TRUE', '1', 'y', 'YES', 'Y', 'Yes']:
        return True
    elif env in ['False', 'FALSE', '0', 'n', 'NO', 'N', 'No']:
        return False
    else:
        raise ValueError('Could not convert string to bool.')


if __name__ == '__main__':
    try:
        # VIDEO_PATH = os.environ['VIDEO_PATH']
        # IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT', "")
        # IMAGE_PROCESSING_PARAMS = os.getenv('IMAGE_PROCESSING_PARAMS', "")
        # SHOW_VIDEO = __convertStringToBool(os.getenv('SHOW_VIDEO', 'False'))
        # VERBOSE = __convertStringToBool(os.getenv('VERBOSE', 'False'))
        # LOOP_VIDEO = __convertStringToBool(os.getenv('LOOP_VIDEO', 'True'))
        # CONVERT_TO_GRAY = __convertStringToBool(
        #     os.getenv('CONVERT_TO_GRAY', 'False')),
        # RESIZE_WIDTH = int(os.getenv('RESIZE_WIDTH', 0))
        # RESIZE_HEIGHT = int(os.getenv('RESIZE_HEIGHT', 0))
        # FPS = int(os.getenv("FPS",0)),
        # AZURE_STORAGE_BLOB = os.getenv("AZURE_STORAGE_BLOB",""),
        # AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING",""),
        # AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER",""),
        # ANNOTATE = __convertStringToBool(os.getenv('ANNOTATE', 'False')),
        # IMAGEWIDTH = int(os.getenv('IMAGEWIDTH', 0)),
        # IMAGEHEIGHT = int(os.getenv('IMAGEHEIGHT', 0)),
        # ROI1 = os.getenv('ROI1', ""),
        # ROI2 = os.getenv('ROI2', ""),
        # ROI3 = os.getenv('ROI3', ""),
        # ROI4 = os.getenv('ROI4', ""),
        # genral_rotation = os.getenv('genral_rotation', ""),
        # roi1_rotation = os.getenv('roi1_rotation', ""),
        # roi2_rotation = os.getenv('roi2_rotation', ""),
        # roi3_rotation = os.getenv('roi3_rotation', ""),
        # roi4_rotation = os.getenv('roi4_rotation', ""),
        # roi1a = os.getenv('roi1a', ""),
        # roi2a = os.getenv('roi2a', ""),
        # roi3a = os.getenv('roi3a', ""),
        # roi4a = os.getenv('roi4a', ""),
        VIDEO_PATH = "rtsp://admin:S0lskin1234!@10.10.50.102:554",
        IMAGE_PROCESSING_ENDPOINT = "",
        IMAGE_PROCESSING_PARAMS = os.getenv('IMAGE_PROCESSING_PARAMS', "")
        SHOW_VIDEO = True,
        VERBOSE = False,
        LOOP_VIDEO = __convertStringToBool(os.getenv('LOOP_VIDEO', 'True'))
        CONVERT_TO_GRAY = __convertStringToBool(
            os.getenv('CONVERT_TO_GRAY', 'False')),
        RESIZE_WIDTH = 0,
        RESIZE_HEIGHT = 0,
        FPS = 10,
        AZURE_STORAGE_BLOB = "fiberdefectstest",
        AZURE_STORAGE_CONNECTION_STRING ="DefaultEndpointsProtocol",
        AZURE_STORAGE_CONTAINER = "camerataggingmodulecloud",
        ANNOTATE = __convertStringToBool(os.getenv('ANNOTATE', 'False')),
        IMAGEWIDTH =1980,
        IMAGEHEIGHT = 1080,
        ROI1 = "1120,200,370,1750",
        ROI2 = "1600,200,370,1750",
        ROI3 = "2090,200,370,1750",
        ROI4 = "2600,200,370,1750",
        genral_rotation = "355",
        roi1_rotation = "358.5",
        roi2_rotation = "360",
        roi3_rotation = "360",
        roi4_rotation = "362.5",
        roi1a = "9,100,303,1750",
        roi2a = "15,100,316,1750",
        roi3a = "30,100,320,1750",
        roi4a = "30,100,325,1750",
    except ValueError as error:
        print(error)
        sys.exit(1)

    main(VIDEO_PATH, IMAGE_PROCESSING_ENDPOINT, IMAGE_PROCESSING_PARAMS, SHOW_VIDEO,
         VERBOSE, LOOP_VIDEO, CONVERT_TO_GRAY, RESIZE_WIDTH, RESIZE_HEIGHT, ANNOTATE,
         FPS,AZURE_STORAGE_BLOB,AZURE_STORAGE_CONNECTION_STRING,AZURE_STORAGE_CONTAINER,
         IMAGEWIDTH,IMAGEHEIGHT,ROI1,ROI2,ROI3,ROI4,genral_rotation,roi1_rotation,roi2_rotation,
         roi3_rotation,roi4_rotation,roi1a,roi2a,roi3a,roi4a)
