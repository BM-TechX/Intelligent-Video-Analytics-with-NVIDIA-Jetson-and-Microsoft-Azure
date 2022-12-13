#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import
from cmath import log

#Imports
from datetime import datetime
import sklearn
import numpy as np
import sys
if sys.version_info[0] < 3:#e.g python version <3
    import cv2
else:
    import cv2
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955 
import numpy
import requests
import json
import time
import io
import os
from azure.storage.blob import BlobServiceClient, PublicAccess
import VideoStream
from VideoStream import VideoStream
import FreshestFrame
from FreshestFrame import FreshestFrame
import BufferLess
from BufferLess import BufferLess
import ImageServer
from ImageServer import ImageServer
from datetime import datetime
import ProcessFrame
from ProcessFrame import ProcessFrame
import UndistortParser
from UndistortParser import UndistortParser
import torch_inference
from torch_inference import Infrence
import string
import random
import imutils


class CameraCapture(object):

    def __IsInt(self,string):
        print("try to convert to int")
        try: 
            int(string)
            return True
        except ValueError:
            return False
    
    def __init__(
            self,
            videoPath,
            imageProcessingEndpoint = "",
            imageProcessingParams = "", 
            showVideo = False, 
            verbose = False,
            loopVideo = True,
            convertToGray = False,
            resizeWidth = 0,
            resizeHeight = 0,
            annotate = False,
            sendToHubCallback = None,
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
            roi2a="0,0,0,0",
            roi3a="0,0,0,0",
            roi4a="0,0,0,0",
            NUMBERFRAME=20,
            ):
        self.videoPath = videoPath
        self.isRTSP = False
        self.vscam1 = None
        self.vscam2= None
        self.vscam3 = None
        self.vscam4 = None
        if self.__IsInt(videoPath):
            #case of a usb camera (usually mounted at /dev/video* where * is an int)
            self.isWebcam = True
        else:
            #case of a video file
            print(videoPath)
            if (videoPath.startswith("rtsps://") or videoPath.startswith("rtsp://")):
                self.isWebcam = True
                self.isRTSP = True
            else:
                self.isWebcam = False
                self.isRTSP=False
        self.imageProcessingEndpoint = imageProcessingEndpoint
        if imageProcessingParams == "":
            self.imageProcessingParams = "" 
        else:
            self.imageProcessingParams = json.loads(imageProcessingParams)
        self.showVideo = showVideo
        self.verbose = verbose
        self.loopVideo = loopVideo
        self.convertToGray = convertToGray
        self.resizeWidth = resizeWidth
        self.resizeHeight = resizeHeight
        #self.annotate = (self.imageProcessingEndpoint != "") and self.showVideo & annotate
        self.nbOfPreprocessingSteps = 0
        self.autoRotate = False
        self.sendToHubCallback = sendToHubCallback
        self.fps = fps
        self.AZURE_STORAGE_BLOB = AZURE_STORAGE_BLOB
        self.AZURE_STORAGE_CONNECTION_STRING = AZURE_STORAGE_CONNECTION_STRING
        self.AZURE_STORAGE_CONTAINER = AZURE_STORAGE_CONTAINER
        self.ROI1 = ROI1
        self.ROI2 = ROI2
        self.ROI3 = ROI3
        self.ROI4 = ROI4
        self.genral_rotation=genral_rotation
        self.roi1_rotation=roi1_rotation
        self.roi2_rotation=roi2_rotation
        self.roi3_rotation=roi3_rotation
        self.roi4_rotation=roi4_rotation
        self.roi1a=roi1a
        self.roi2a=roi2a
        self.roi3a=roi3a
        self.roi4a=roi4a
        self.UndistortParserInstance = UndistortParser()
        self.vs = None
        self.useUSB=True
        self.displayFrame = None
        self.Lane1State = None
        self.Lane2State = None
        self.Lane3State = None
        self.Lane4State = None
        self.numpy_horizontal_concat_usb = None
        self.numpy_horizontal_concat_rtsp = None
        self.infrencerTop = Infrence(model_path='model_3.ckpt',config_path='config.yaml',device='cuda',visualization_mode='segmentation',task='segmentation')
        if self.useUSB == True:
            self.infrencerbuttom = Infrence(model_path='model_bottom.ckpt',config_path='config_bot.yaml',device='cuda',visualization_mode='segmentation',task='segmentation')
        
        print("booting up")
        if self.convertToGray:
            self.nbOfPreprocessingSteps +=1
        if self.resizeWidth != 0 or self.resizeHeight != 0:
            self.nbOfPreprocessingSteps +=1
        if self.verbose:
            print("Initialising the camera capture with the following parameters: ")
            print("   - Video path: " + self.videoPath)
            print("   - Image processing endpoint: " + self.imageProcessingEndpoint)
            print("   - Image processing params: " + json.dumps(self.imageProcessingParams))
            print("   - Show video: " + str(self.showVideo))
            print("   - Loop video: " + str(self.loopVideo))
            print("   - Convert to gray: " + str(self.convertToGray))
            print("   - Resize width: " + str(self.resizeWidth))
            print("   - Resize height: " + str(self.resizeHeight))
            #print("   - Annotate: " + str(self.annotate))
            print("   - Send processing results to hub: " + str(self.sendToHubCallback is not None))
            print()
        

        
        if self.showVideo:
            self.imageServer = ImageServer(5012, self)
            self.imageServer.start()
    def __uploadToAzure(self, counter, frame):
        try:
            print("uploading to azure")
            # blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=camtagstoreaiem;AccountKey=TwURR9XUNY+jsvTvMzGdjUxb+x8q+MCSLiVxNwGBdg5vjwkBEP6q1DWUI+SId91AxHxJKIzOLjBq+ASt2YALow==;EndpointSuffix=core.windows.net")
            # local_file_name = str(counter) +  ".jpg"
            # _, img_encode = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 99])            
            # try:
            #     blob_client = blob_service_client.get_blob_client(container=self.AZURE_STORAGE_BLOB[0], blob=local_file_name)
            #     blob_client.upload_blob(img_encode.tobytes(), overwrite=True)
            # except:
            #     print("error")
        except Exception as e:
            print('__uploadToAzure Excpetion -' + str(e))
            return


    def __displayTimeDifferenceInMs(self, endTime, startTime):
        return str(int((endTime-startTime) * 1000)) + " ms"

    def __enter__(self):
        if self.isWebcam:
            #The VideoStream class always gives us the latest frame from the webcam. It uses another thread to read the frames.
            if self.isRTSP==False:
                self.vs = VideoStream(int(self.videoPath))
                self.vs.setSize(4032,3040)
            else:
                #self.vs = VideoStream(self.videoPath)
                #cap = cv2.VideoCapture(self.videoPath)
                ##cap.set(cv2.CAP_PROP_FPS, 10)
                ##self.vs = cap
                # wrap it
                self.vs = BufferLess(self.videoPath,id="rtsp")
               
                #self.vs.setFPS(15)
                if self.useUSB ==True:
                    ##self.vscam1=BufferLess(0,10,4032,3040)
                    print("init cam1")
                    self.vscam1=ProcessFrame(BufferLess(0,id="0"),0.5,infrencerbuttom=self.infrencerbuttom)
                    time.sleep(5.0)
                    if (self.vscam1.start_processing() == False):
                        print("error")
                    
                    print("init over cam1")
                    #self.vscam2=BufferLess(1,10,4032,3040)
                    print("init cam2")
                    self.vscam2=ProcessFrame(BufferLess(1,id="0"),0.5,infrencerbuttom=self.infrencerbuttom)
                    time.sleep(5.0)
                    if (self.vscam2.start_processing() == False):
                        print("error")
                    
                    #self.vscam2=BufferLess(1,id="1")
                    #time.sleep(1)
                    print("init over cam2")
                    #self.vscam2= VideoStream(1)
                    #self.vscam2.start()
    
                    #self.vscam3=BufferLess(2,10,4032,3040)
                    print("init cam3")
                    self.vscam3=BufferLess(2,id="2")
                    time.sleep(1)
                    print("init over cam3")
                    #self.vscam3 = VideoStream(2)
                    #self.vscam3.start()
                    #self.vscam4=BufferLess(3,10,4032,3040)
                    print("init cam4")
                    self.vscam4=BufferLess(3,id="3")
                    time.sleep(1)
                    print("init over cam4")
                    #self.vscam4 = VideoStream(3)
                    #self.vscam4.start()
                    
                    
            ##self.vs.start()
            time.sleep(1.0)
            #needed to load at least one frame into the VideoStream class
            #self.capture = cv2.VideoCapture(int(self.videoPath))
        else:
            #In the case of a video file, we want to analyze all the frames of the video thus are not using VideoStream class
            self.capture = cv2.VideoCapture(self.videoPath)
        return self

    def get_display_frame(self):
        return self.displayFrame   
    def get_LaneState(self):
        return self.Lane1State + self.Lane2State + self.Lane3State + self.Lane4State
    
    def put_text(self, frame, text, position, color, font_scale, thickness):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)
        return frame
    
    def get_process_lane(self,rs,regioninner,rotation,frame):
        region1= rs[0].split(",")
        roi1=[int(region1[0]),int(region1[1]),int(region1[2]),int(region1[3])]
        frame_cropped= frame[int(roi1[1]):int(roi1[1]+roi1[3]), int(roi1[0]):int(roi1[0]+roi1[2])]
        frame_cropped_rotated=imutils.rotate(frame_cropped,rotation)
        frame_cropped_rotated_inner = frame_cropped_rotated[int(regioninner[1]):int(regioninner[1]+regioninner[3]), int(regioninner[0]):int(regioninner[0]+regioninner[2])]
        return frame_cropped_rotated_inner
    def process_lane(self,frame,threshold):
        preroi_img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        preroi_img_ot,predictions =self.infrencerTop.getInfrence(preroi_img)
        LaneState = predictions.pred_label + " " + str(round(predictions.pred_score,2))
        if(predictions.pred_score>threshold):
            try:
                self.__uploadToAzure(str(datetime.date)+".jpg",frame=preroi_img)
                state="ALARM"
            except Exception as e:
                    print("something went wrong while uploading to azure")
        cv2.putText(preroi_img_ot, LaneState, (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        return preroi_img_ot,LaneState
    def process_lane_bottom(self,frame,threshold):
        preroi_img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        preroi_img_ot,predictions =self.infrencerbuttom.getInfrence(preroi_img)
        LaneState = predictions.pred_label + " " + str(round(predictions.pred_score,2))
        if(predictions.pred_score>threshold):
            try:
                self.__uploadToAzure(str(datetime.date)+".jpg",frame=preroi_img)
                state="ALARM"
            except Exception as e:
                    print("something went wrong while uploading to azure")
        cv2.putText(preroi_img_ot, LaneState, (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        return preroi_img_ot,LaneState
        
        
        
    def start(self):
        infrenceCounter = 0
        perfForOneFrameInMs = None
        cnt = 0
        # Default imageProcessing interval in seconds
        
        while True:
            if self.isWebcam:
                ##frame = self.vs.read()
                frame = self.vs.read()     
                print("frame read")
            #succes,frame = self.vs.read()           
            if self.useUSB ==True:
                #try:
                    #frame1 = self.vscam1.read()
                #except Exception as e:
                #    print("error in reading camera 1")
                # try:
                #     frame2 = self.vscam2.read()
                # except Exception as e:
                #     print("error in reading camera 2")
                try:
                    frame3 = self.vscam3.read()
                except Exception as e:
                    print("error in reading camera 3")
                try:
                    frame4 = self.vscam4.read()
                except Exception as e:
                    print("error in reading camera 4")
            #Loop video
            #Pre-process locally
            print("frame starting preprocessing")
            if self.nbOfPreprocessingSteps == 1 and self.convertToGray:
                preprocessedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
            
            if self.nbOfPreprocessingSteps == 1 and (self.resizeWidth != 0 or self.resizeHeight != 0):
                preprocessedFrame = cv2.resize(frame, (self.resizeWidth, self.resizeHeight))

            print ("frame processed")

            if self.showVideo:
                try:
                    genral_rotation = 358.5
                    roi1_rotation=360.1
                    roi2_rotation=359.8
                    roi3_rotation=359.25
                    roi4_rotation=358.7
                    roi1a = [9,100,303,1750]
                    roi2a = [15,100,316,1750]
                    roi3a = [30,100,320,1750]
                    roi4a = [30,100,325,1750]
                    print("roi4a :" + self.roi4a[0])
                    
                    preprocessedFrame = self.UndistortParserInstance.undistortImage(preprocessedFrame)
                    print("Frame undistorted")
                    
                    preprocessedFrame=imutils.rotate(preprocessedFrame,genral_rotation)
                    preroi1 = self.get_process_lane(self.ROI1,roi1a,roi1_rotation,preprocessedFrame)
                    preroi2 = self.get_process_lane(self.ROI2,roi2a,roi2_rotation,preprocessedFrame)
                    preroi3 = self.get_process_lane(self.ROI3,roi3a,roi3_rotation,preprocessedFrame)
                    preroi4 = self.get_process_lane(self.ROI4,roi4a,roi4_rotation,preprocessedFrame)
                    threshold = 0.5
                    state = "NORMAL"
                    # #########LANE 1
                    preroi1_img_ot,self.Lane1State = self.process_lane(preroi1,threshold)
                    # #########LANE 2
                    preroi2_img_ot,self.Lane2State = self.process_lane(preroi2,threshold)
                    # ###########LANE 3
                    preroi3_img_ot,self.Lane3State = self.process_lane(preroi3,threshold)
                    # ###########LANE 4
                    preroi4_img_ot,self.Lane4State = self.process_lane(preroi4,threshold)
                    # preroi1_gray = cv2.cvtColor(preroi1, cv2.COLOR_BGR2GRAY)
                    # preroi1_img_ot,predictions =self.infrencerTop.getInfrence(preroi1_gray)
                    # preroi2_gray = cv2.cvtColor(preroi2, cv2.COLOR_BGR2GRAY)
                    # preroi2_img_ot,predictions =self.infrencerTop.getInfrence(preroi2_gray)
                    # preroi3_gray = cv2.cvtColor(preroi3, cv2.COLOR_BGR2GRAY)
                    # preroi3_img_ot,predictions =self.infrencerTop.getInfrence(preroi3_gray)
                    # preroi4_gray = cv2.cvtColor(preroi4, cv2.COLOR_BGR2GRAY)
                    # preroi4_img_ot,predictions =self.infrencerTop.getInfrence(preroi4_gray)
                    
                    #LaneState = predictions.pred_label + " " + str(round(predictions.pred_score,2))

                    #####################COMBINE
                    print("før combine")
                    print (self.Lane1State + " " + self.Lane2State + " " + self.Lane3State + " " + self.Lane4State)
                    numpy_horizontal_concat = np.concatenate((preroi1_img_ot, preroi2_img_ot, preroi3_img_ot, preroi4_img_ot), axis=1)
                    self.numpy_horizontal_concat_rtsp= numpy_horizontal_concat
                    width, height, channels = numpy_horizontal_concat.shape
                    width = int(width/2)
                    height = int(height/2)
                    if (self.numpy_horizontal_concat_usb is not None):
                        numpy_horizontal_concat = np.concatenate((numpy_horizontal_concat,self.numpy_horizontal_concat_usb), axis=1)
                        self.displayFrame = cv2.imencode('.jpg', numpy_horizontal_concat)[1].tobytes()# +"|"+state
                    if self.useUSB==True:
                        try:
                            numpy_horizontal_concat = cv2.resize(numpy_horizontal_concat, dsize=(height*2, width*2))
                        except:
                            print("resize error")
                            
                        try:
                            #frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                            #frame1,self.Lane4State = self.process_lane_bottom(frame1,threshold)
                            #frame1_resized = cv2.resize(frame1, dsize=(height, width))
                            if(self.vscam1.frame_ready):
                                frame1= self.vscam1.getframe()
                                frame1_resized = cv2.resize(frame1, dsize=(height, width))
                            else:
                                frame1_resized = np.zeros((width,height,3), dtype=np.uint8)
                        except:
                            print("frame1 error")
                            frame1_resized = np.zeros((width,height,3), dtype=np.uint8)
                        try:
                            # frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                            # frame2,self.Lane4State = self.process_lane_bottom(frame2,threshold)
                            # frame2_resized = cv2.resize(frame2, dsize=(height, width))
                            if(self.vscam2.frame_ready):
                                frame2= self.vscam2.getframe()
                                frame2_resized = cv2.resize(frame2, dsize=(height, width))
                            else:
                                frame1_resized = np.zeros((width,height,3), dtype=np.uint8)
                        except:
                            print("frame2 error")
                            frame2_resized = np.zeros((width,height,3), dtype=np.uint8)
                        try:
                            frame3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)
                            frame3,self.Lane4State = self.process_lane_bottom(frame3,threshold)
                            frame3_resized = cv2.resize(frame3, dsize=(height, width))
                        except:
                            print("frame3 error")
                            frame3_resized = np.zeros((width,height,3), dtype=np.uint8)
                        try:
                            frame4 = cv2.cvtColor(frame4, cv2.COLOR_BGR2GRAY)
                            frame4,self.Lane4State = self.process_lane_bottom(frame4,threshold)
                            frame4_resized = cv2.resize(frame4, dsize=(height, width))
                        except Exception as e:
                            frame4_resized = np.zeros((width,height,3), dtype=np.uint8)
                            print("Error in frame4: " + str(e))
                    try:
                        numpy_horizontal_concat_usb_top = np.concatenate((frame1_resized, frame2_resized), axis=1)
                        numpy_horizontal_concat_usb_bottom = np.concatenate((frame3_resized, frame4_resized), axis=1)
                        numpy_horizontal_concat_usb = np.concatenate((numpy_horizontal_concat_usb_top, numpy_horizontal_concat_usb_bottom), axis=0)
                        self.numpy_horizontal_concat_usb = numpy_horizontal_concat_usb
                        numpy_horizontal_concat = np.concatenate((self.numpy_horizontal_concat_rtsp , numpy_horizontal_concat_usb), axis=1)
                        self.displayFrame = cv2.imencode('.jpg', numpy_horizontal_concat)[1].tobytes()# +"|"+state
                    except Exception as e:
                        print("Error in concat: " + str(e))
                except Exception as e:
                    print("Could not display the video to a web browser.") 
                    print('Excpetion -' + str(e))
                   

    def __exit__(self, exception_type, exception_value, traceback):
        if not self.isWebcam:
            self.capture.release()
        if self.showVideo:
            self.imageServer.close()
            cv2.destroyAllWindows()