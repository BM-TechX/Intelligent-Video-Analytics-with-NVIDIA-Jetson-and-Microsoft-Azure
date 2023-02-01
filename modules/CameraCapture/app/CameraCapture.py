#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import
from cmath import log

#Imports
from datetime import datetime, timedelta
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
import BufferLess
from BufferLess import BufferLess
import ImageServer
from ImageServer import ImageServer
from datetime import datetime
import ProcessFrame
from ProcessFrame import ProcessFrame
import ProcessFrameUSB
from ProcessFrameUSB import ProcessFrameUSB
import UndistortParser
from UndistortParser import UndistortParser
import torch_inference
from torch_inference import Infrence
import string
import random
import imutils
import UploadToAzure
from UploadToAzure import UploadToAzure
from datetime import datetime
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
        self.state = None
        self.timefrequency = 10
        print(videoPath)
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
        self.threshold=0.5
        self.nbOfPreprocessingSteps = 1
        self.autoRotate = False
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
        self.useFile=True
        self.displayFrame = None
        self.Lane1State = ""
        self.Lane2State = ""
        self.Lane3State = ""
        self.Lane4State = ""
        self.LaneStateUSB1 = ""
        self.LaneStateUSB2 = ""
        self.LaneStateUSB3 = ""
        self.LaneStateUSB4 = ""
        self.previousUSBFrame1 = None
        self.previousUSBFrame2 = None
        self.previousUSBFrame3 = None
        self.previousUSBFrame4 = None
        self.numpy_horizontal_concat_usb = None
        self.numpy_horizontal_concat_rtsp = None
        self.ALARM=0
        self.ALARMREPORTED=0
        self.table="FiberlineTest"
        self.connectionstring = "DefaultEndpointsProtocol=https;AccountName=camtagstoreaiem;AccountKey=TwURR9XUNY+jsvTvMzGdjUxb+x8q+MCSLiVxNwGBdg5vjwkBEP6q1DWUI+SId91AxHxJKIzOLjBq+ASt2YALow==;EndpointSuffix=core.windows.net"
        self.takePhotoFrequency=0
        self.takePhoto=False             
        self.threshold=0.5
        self.uploadToAzure=False
        self.activeLanes=[1,1,1,1]
        self.activeUSBLanes=[1,1,1,1]
        self.infrencerTop = Infrence(model_path='model_4.ckpt',config_path='config.yaml',device='cuda',visualization_mode='segmentation',task='segmentation')
        self.infrencerTopSeondary = Infrence(model_path='model_top_clas.ckpt',config_path='config_top_clas.yaml',device='cuda',visualization_mode='segmentation',task='classification')
        #test if we have a usb camera
        if self.useUSB == True:
            self.infrencerbuttom = Infrence(model_path='model_bottom.ckpt',config_path='config_bot.yaml',device='cuda',visualization_mode='segmentation',task='segmentation')
        
        print("booting up")
        if self.convertToGray:
            self.nbOfPreprocessingSteps +=1
        if self.resizeWidth != 0 or self.resizeHeight != 0:
            self.nbOfPreprocessingSteps +=1
            
        #############################Azure Storage############################################
        self.upload = UploadToAzure(self.connectionstring,self.table)
        try :
            self.upload.connectToAzure()
            self.upload.createTable(self.table)
            if(self.upload.test_con()):
                print("Connected to Azure")
            else:
                self.upload.intiateTable(self.table)
        except Exception as e:
            print("Error initCamera " + str(e))
        ######################################################################################
        
        if self.showVideo:
            self.imageServer = ImageServer(5012, self)
            self.imageServer.start()
   

    def check_clock(self):
        current_time = datetime.utcnow()
        if current_time.minute % self.timefrequency == 0 and current_time.second == 0:
            # perform action
           return True
        else:
            re

    def __uploadToAzure(self, filename, frame):
        try:
            print("uploading to azure" + filename)
            blob_service_client = BlobServiceClient.from_connection_string(self.connectionstring)
            local_file_name = filename +  ".jpg"
            _, img_encode = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 99])            
            try:
                blob_client = blob_service_client.get_blob_client(container=self.AZURE_STORAGE_BLOB[0], blob=local_file_name)
                blob_client.upload_blob(img_encode.tobytes(), overwrite=True)
            except Exception as e:
                print("error" + str(e))
        except Exception as e:
            print('__uploadToAzure Excpetion -' + str(e))
            return

    def restartrtsp(self):
        try:
            print("stopping rtsp")
            self.vs.stop()
            time.sleep(1.0)
            print("trying to restart rtsp")
            self.vs = BufferLess(self.videoPath,id="rtsp")
        except Exception as e:
            print("error" + str(e))
            time.sleep(1.0)
            self.retyr(1)
            
    def __displayTimeDifferenceInMs(self, endTime, startTime):
        return str(int((endTime-startTime) * 1000)) + " ms"

    def __enter__(self):
        if self.isWebcam:
            #The VideoStream class always gives us the latest frame from the webcam. It uses another thread to read the frames.
            if self.isRTSP==False:
                self.vs = VideoStream(int(self.videoPath))
                self.vs.setSize(4032,3040)
            else:
                try:
                    print("connecting to rtsp")
                    time.sleep(4.0)
                    self.vs = BufferLess(self.videoPath,id="rtsp",setFPS=8)
                    print("trying to get frame")
                    frame = self.vs.read()
                except Exception as e:
                    print("error" + str(e))
                    time.sleep(1.0)
         
               
                #self.vs.setFPS(15)
                if self.useUSB ==True:
                    self.vscam1=ProcessFrameUSB(threshold=self.threshold,infrencerbuttom=self.infrencerbuttom,table=self.table,AZURE_STORAGE_BLOB=self.AZURE_STORAGE_BLOB)
                    self.vscam1.start_processing()

            ##self.vs.start()
            time.sleep(1.0)
            #needed to load at least one frame into the VideoStream class
            #self.capture = cv2.VideoCapture(int(self.videoPath))
        else:
            #In the case of a video file, we want to analyze all the frames of the video thus are not using VideoStream class
            self.capture = cv2.VideoCapture(self.videoPath)
        return self
    def retyr(self,count):
        time.sleep(2.0)
        if(count>10):
            return
        try:
            self.vs.stop()
            self.vs = BufferLess(self.videoPath,id="rtsp")
        except Exception as e:
            print("error" + str(e))
            self.retyr(count+1)
        
        
    def get_display_frame(self):
        return self.displayFrame   
    def get_LaneState(self):
        if (self.ALARM>100):
            self.ALARMREPORTED=1000
            self.ALARM=0
        if (self.ALARMREPORTED>1):
            self.ALARMREPORTED= self.ALARMREPORTED-1
            return "ALARM" +"|"+ "Lane1:"+str(self.Lane1State) + "Lane2:"+ str(self.Lane2State) + "Lane3:"+ str(self.Lane3State) + "Lane4"+ str(self.Lane4State)
        else :
            return "NORMAL"+"|"+ str(self.Lane1State) + str(self.Lane2State) + str(self.Lane3State) + str(self.Lane4State)
        

    def convertROIstringToTuple(self,roiString,read):
        if (read==0):
            roi = roiString[0].split(',')
        else:
            roi = roiString.split(',')
        return (int(roi[0]),int(roi[1]),int(roi[2]),int(roi[3]))
    def convertROIstringToTuple2(self,roiString):
        roi = roiString.split(',')
        return (int(roi[0]),int(roi[1]),int(roi[2]),int(roi[3]))
    def put_text(self, frame, text, position, color, font_scale, thickness):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, position, font, font_scale, color, thickness, cv2.LINE_AA)
        return frame

    def azUp(self,predictions,id,rowkey,url):
            try:
               
                #now.month, now.day, now.year, now.hour, now.minute, now.secon
                entity={
                    'PartitionKey': id,
                    'RowKey': rowkey,
                    'Prediction': predictions.pred_label,
                    'Score': str(predictions.pred_score),
                    'anomaly_map': str(predictions.anomaly_map),
                    'pred_mask': str(predictions.pred_mask),
                    'url': url
                    #'Timestamp': str(datetime.datetime.now())
                }
                if(self.upload.test_con()):
                    self.upload.uploadtoTable(entity)
                else:
                    self.upload.intiateTable(self.table)
                    self.upload.uploadtoTable(entity)
            except Exception as e:
                print("Error connecting to Azure " + str(e))

    def get_process_lane(self,rs,regioninner,rotation,frame,read):
        if read==0:
            region1= rs[0].split(",")
        else: 
            region1= rs.split(",")
        roi1=[int(region1[0]),int(region1[1]),int(region1[2]),int(region1[3])]
        frame_cropped= frame[int(roi1[1]):int(roi1[1]+roi1[3]), int(roi1[0]):int(roi1[0]+roi1[2])]
        frame_cropped_rotated=imutils.rotate(frame_cropped,rotation)
        frame_cropped_rotated_inner = frame_cropped_rotated[int(regioninner[1]):int(regioninner[1]+regioninner[3]), int(regioninner[0]):int(regioninner[0]+regioninner[2])]
        return frame_cropped_rotated_inner
    def classify_lane(self,frame,threshold):
        preroi_img_ot,predictions =self.infrencerTopSeondary.getInfrence(frame)
        LaneState = predictions.pred_label + " " + str(round(predictions.pred_score,2))
        return LaneState
        
    def process_lane(self,frame,threshold,id):
        preroi_img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        preroi_img_ot,predictions =self.infrencerTop.getInfrence(preroi_img)
        LaneState = predictions.pred_label + " " + str(round(predictions.pred_score,2))
        now = datetime.now()
        rowkey = str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second) + str(now.microsecond)
        url = ""
        if(self.check_clock):
            if(self.uploadToAzure==1):
                self.__uploadToAzure(filename=rowkey+id +"_Clock",frame=preroi_img)
           
        if(predictions.pred_score>threshold):
            try:
                height, width, channels = preroi_img_ot.shape
                start_point = (0,0)
                end_point = (width, height)
                color = (0,0,255)
                thickness = 8
                try:
                    predictions.pred_label = predictions.pred_label + ":" + self.classify_lane(preroi_img_ot,threshold)
                except Exception as e:
                    print("something went wrong while classifying lane" + str(e))
                preroi_img_ot = cv2.rectangle(preroi_img_ot, start_point, end_point, color, thickness)
                if(self.uploadToAzure==1):
                    self.__uploadToAzure(filename=rowkey+id,frame=preroi_img)
                    url = "https://camtagstoreaiem.blob.core.windows.net/fiberdefectstest/"+rowkey+id+ ".jpg"
                self.ALARM = self.ALARM + 1
            except Exception as e:
                    print("something went wrong while uploading to azure")
        else:
            LaneState = "Normal" + " " + str(round(predictions.pred_score,2))
        if(self.uploadToAzure==1):
            self.azUp(predictions,id,rowkey,url)
        cv2.putText(preroi_img_ot, LaneState, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        return preroi_img_ot,LaneState
        
    def read_json(self):
        try:
            print("Reading config file")
            with open('config.json') as json_file:
                data = json.load(json_file)
                self.ROI1 = data['roi1']
                self.ROI2 = data['roi2']
                self.ROI3 = data['roi3']
                self.ROI4 = data['roi4']
                self.genral_rotation=data['genral_rotation']
                self.roi1_rotation=data['roi1_rotation']
                self.roi2_rotation=data['roi2_rotation']
                self.roi3_rotation=data['roi3_rotation']
                self.roi4_rotation=data['roi4_rotation']
                self.roi1a=data['roi1a']
                self.roi2a=data['roi2a']
                self.roi3a=data['roi3a']
                self.roi4a=data['roi4a']
                self.timefrequency=int(data['timefrequency'])
                self.takePhotoFrequency=int(data["takePhotoFrequency"])
                self.takePhoto= data["takePhoto"]
                self.uploadToAzure= int(data["uploadToAzure"])        
                # self.useUSB = self.strtobool(data['useUSB'])
                self.threshold=float(data['threshold'])
                activelanes=  data['activeLanes'].split(",")
                self.activeLanes=[int(activelanes[0]),int(activelanes[1]),int(activelanes[2]),int(activelanes[3])]
                activeUSB=  data['activeUSB'].split(",")
                self.activeUSBLanes=[int(activeUSB[0]),int(activeUSB[1]),int(activeUSB[2]),int(activeUSB[3])]
                return data
        except Exception as e:
            print("Error reading config file " + str(e))

        
    def strtobool (val):
        val = val.lower()
        if val in ('y', 'yes', 't', 'true', 'on', '1'):
            return True
        elif val in ('n', 'no', 'f', 'false', 'off', '0'):
            return False
        else:
            raise ValueError("invalid truth value %r" % (val,))
  
    def start(self):
        infrenceCounter = 0
        perfForOneFrameInMs = None
        cnt = 0
        # Default imageProcessing interval in seconds
        count = 0
        usberror = 0
        usbreuse = 0
       
        while True:
            if self.isWebcam:
                frame = self.vs.read() 
            #Pre-process locally
            try:
                preprocessedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            except:
                count = count + 1
                if count > 4:
                    print("trying to restart rtsp")
                    try:
                        self.restartrtsp()
                        time.sleep(3.0)
                    except:
                        print("rtsp restart failed")
                        time.sleep(1.0)
                print("frame size is 0")
                time.sleep(1.0)
                

            if self.showVideo:
                try:
                    read =1
                    if(self.useFile):
                        self.read_json()
                        self.vscam1.uploadToAzure = self.uploadToAzure
                    
                    genral_rotation = float(self.genral_rotation)
                
                    roi1_rotation=float(self.roi1_rotation)
                 
                    roi2_rotation=float(self.roi2_rotation)
              
                    roi3_rotation=float(self.roi3_rotation)
          
                    roi4_rotation=float(self.roi4_rotation)
                    roi1a =self.convertROIstringToTuple(self.roi1a,read)
                    roi2a =self.convertROIstringToTuple(self.roi2a,read) 
                    roi3a =self.convertROIstringToTuple(self.roi3a,read)
                    roi4a =self.convertROIstringToTuple(self.roi4a,read)
                    try:
                        preprocessedFrame = self.UndistortParserInstance.undistortImage(preprocessedFrame)
                    except Exception as e:
                        print("Error undistorting frame " + str(e))

                    preprocessedFrame=imutils.rotate(preprocessedFrame,genral_rotation)
                    threshold = self.threshold
                    numpy_horizontal_concat = None
                    if(self.activeLanes[0]==1):
                        preroi1 = self.get_process_lane(self.ROI1,roi1a,roi1_rotation,preprocessedFrame,read)
                        preroi1_img_ot,self.Lane1State = self.process_lane(preroi1,threshold,"Lane1Top")
                        numpy_horizontal_concat = preroi1_img_ot
                    if(self.activeLanes[1]==1):
                        preroi2 = self.get_process_lane(self.ROI2,roi2a,roi2_rotation,preprocessedFrame,read)
                        preroi2_img_ot,self.Lane2State = self.process_lane(preroi2,threshold,"Lane2Top")
                        if(numpy_horizontal_concat is not None):
                            numpy_horizontal_concat = np.concatenate((numpy_horizontal_concat, preroi2_img_ot), axis=1)
                        else:
                            numpy_horizontal_concat = preroi2_img_ot
                    if(self.activeLanes[2]==1):
                        preroi3 = self.get_process_lane(self.ROI3,roi3a,roi3_rotation,preprocessedFrame,read)
                        preroi3_img_ot,self.Lane3State = self.process_lane(preroi3,threshold,"Lane3Top")
                        if(numpy_horizontal_concat is not None):
                            numpy_horizontal_concat = np.concatenate((numpy_horizontal_concat, preroi3_img_ot), axis=1)
                        else:
                            numpy_horizontal_concat = preroi3_img_ot
                    if(self.activeLanes[3]==1):
                        preroi4 = self.get_process_lane(self.ROI4,roi4a,roi4_rotation,preprocessedFrame,read)
                        preroi4_img_ot,self.Lane4State = self.process_lane(preroi4,threshold,"Lane4Top")  
                        if(numpy_horizontal_concat is not None):
                            numpy_horizontal_concat = np.concatenate((numpy_horizontal_concat, preroi4_img_ot), axis=1)
                        else:
                            numpy_horizontal_concat = preroi4_img_ot
                    state = "NORMAL"
                    print("got to here")
                    
                    #####################COMBINE IMAGES#####################
                    print ("RTSP" + self.Lane1State + " " + self.Lane2State + " " + self.Lane3State + " " + self.Lane4State)
                   
                            
                    self.numpy_horizontal_concat_rtsp= numpy_horizontal_concat
                    width, height, channels = numpy_horizontal_concat.shape
                    width = int(width/2)
                    height = int(height/2)
                    if (self.numpy_horizontal_concat_usb is not None):
                        numpy_horizontal_concat = np.concatenate((numpy_horizontal_concat,self.numpy_horizontal_concat_usb), axis=1)
                        self.displayFrame = cv2.imencode('.jpg', numpy_horizontal_concat)[1].tobytes()
                    else:
                        self.displayFrame = cv2.imencode('.jpg', numpy_horizontal_concat)[1].tobytes()
                    if self.useUSB==True:
                        print("useUSb = true")
                        if (usberror > 50):
                            try:
                                self.vscam1.stop_processing()
                                self.vscam1=ProcessFrameUSB(threshold=self.threshold,infrencerbuttom=self.infrencerbuttom,table=self.table,AZURE_STORAGE_BLOB=self.AZURE_STORAGE_BLOB)
                                self.vscam1.start_processing()
                            except:
                                print("usb restart failed")
                            usberror=0
                        if (usbreuse > 400):
                            try:
                                self.vscam1.stop_processing()
                                self.vscam1=ProcessFrameUSB(threshold=self.threshold,infrencerbuttom=self.infrencerbuttom,table=self.table,AZURE_STORAGE_BLOB=self.AZURE_STORAGE_BLOB)
                                self.vscam1.start_processing()
                            except:
                                print("usb restart failed")
                            usbreuse=0
                        try:
                            numpy_horizontal_concat = cv2.resize(numpy_horizontal_concat, dsize=(height*2, width*2))
                        except:
                            print("resize error")
                        try:
                            if(self.activeUSBLanes[0]==1):
                                if(self.vscam1.frame1_ready):
                                    self.LaneStateUSB1,frame1=self.vscam1.getframe("0")
                                    frame1_resized = cv2.resize(frame1, dsize=(height, width))
                                    self.previousUSBFrame1 = frame1_resized
                                    print("freshframe")
                                elif (self.previousUSBFrame1 is not None):
                                    frame1_resized = self.previousUSBFrame1
                                    usbreuse=usbreuse+1
                                    print("reuse usb1")
                                else:
                                    frame1_resized = np.zeros((width,height,3), dtype=np.uint8)
                                    self.LaneStateUSB1=None
                                    usberror=usberror+1
                                    print("created zero")
                            else:
                                frame1_resized = np.zeros((width,height,3), dtype=np.uint8)
                                self.LaneStateUSB1=None
                                print("USBlane1 not active")
                           
                        except:
                            print("frame1 error")
                            frame1_resized = np.zeros((width,height,3), dtype=np.uint8)
                        try:
                            if(self.activeUSBLanes[1]==1):
                                if(self.vscam1.frame2_ready):
                                    self.LaneStateUSB2,frame2 = self.vscam1.getframe("1")
                                    frame2_resized = cv2.resize(frame2, dsize=(height, width))
                                    self.previousUSBFrame2 = frame2_resized
                                elif (self.previousUSBFrame2 is not None):
                                    frame2_resized = self.previousUSBFrame2
                                    usbreuse=usbreuse+1
                                else:
                                    frame2_resized = np.zeros((width,height,3), dtype=np.uint8)
                                    self.LaneStateUSB2=None
                                    usberror=usberror+1
                            else:
                                frame2_resized = np.zeros((width,height,3), dtype=np.uint8)
                                self.LaneStateUSB2=None
                                print("USBlane2 not active")
                        except:
                            print("frame2 error")
                            frame2_resized = np.zeros((width,height,3), dtype=np.uint8)
                        try:
                            if(self.activeUSBLanes[2]==1):
                                if(self.vscam1.frame3_ready):
                                    self.LaneStateUSB3,frame3 = self.vscam1.getframe("2")
                                    frame3_resized = cv2.resize(frame3, dsize=(height, width))
                                    self.previousUSBFrame3 = frame3_resized
                                elif (self.previousUSBFrame3 is not None):
                                    frame3_resized = self.previousUSBFrame3
                                    usbreuse=usbreuse+1
                                else:
                                    frame3_resized = np.zeros((width,height,3), dtype=np.uint8)
                                    self.LaneStateUSB3=None
                                    usberror=usberror+1
                            else:
                                frame3_resized = np.zeros((width,height,3), dtype=np.uint8)
                                self.LaneStateUSB3=None
                                print("USBlane3 not active")
                        except:
                            print("frame3 error")
                            frame3_resized = np.zeros((width,height,3), dtype=np.uint8)
                        try:
                            if(self.activeUSBLanes[3]==1):
                                if(self.vscam1.frame4_ready):
                                    self.LaneStateUSB4,frame4= self.vscam1.getframe("3")
                                    frame4_resized = cv2.resize(frame4, dsize=(height, width))
                                    self.previousUSBFrame4 = frame4_resized
                                elif (self.previousUSBFrame4 is not None):
                                    frame4_resized = self.previousUSBFrame4
                                    usbreuse=usbreuse+1
                                else:
                                    frame4_resized = np.zeros((width,height,3), dtype=np.uint8)
                                    self.LaneStateUSB4=None
                                    usberror=usberror+1
                            else:
                                frame4_resized = np.zeros((width,height,3), dtype=np.uint8)
                                self.LaneStateUSB4=None
                                print("USBlane4 not active")

                        except Exception as e:
                            frame4_resized = np.zeros((width,height,3), dtype=np.uint8)
                            usberror=usberror+1
                            print("Error in frame4: " + str(e))
                        try:
                                            
                            print ("USB" + self.LaneStateUSB1 + " " + self.LaneStateUSB2 + " " + self.LaneStateUSB3 + " " + self.LaneStateUSB4)
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