#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import
from cmath import log

#Imports
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
import AnnotationParser
from AnnotationParser import AnnotationParser
import ImageServer
from ImageServer import ImageServer
from datetime import datetime
import UndistortParser
from UndistortParser import UndistortParser

import string
import random

class CameraCapture(object):

    def __IsInt(self,string):
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
            ):
        self.videoPath = videoPath
        if self.__IsInt(videoPath):
            #case of a usb camera (usually mounted at /dev/video* where * is an int)
            self.isWebcam = True
        else:
            #case of a video file
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
        self.UndistortParserInstance = UndistortParser()
        self.vs = None

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
        
        self.displayFrame = None
        if self.showVideo:
            self.imageServer = ImageServer(5012, self)
            self.imageServer.start()
    def __uploadToAzure(self, counter, frame):
        try:
            
            blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=camtagstoreaiem;AccountKey=TwURR9XUNY+jsvTvMzGdjUxb+x8q+MCSLiVxNwGBdg5vjwkBEP6q1DWUI+SId91AxHxJKIzOLjBq+ASt2YALow==;EndpointSuffix=core.windows.net")
            #time = datetime.now.strftime("%m/%d/%Y-%H:%M:%S")
            local_file_name = "frame_261bu" + str(counter) +  ".jpg"
            _, img_encode = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 99])
            ##blob_client = blob_service_client.get_blob_client(container="nnpic3", blob=local_file_name)
            ##blob_client.upload_blob(img_encode.tobytes(), overwrite=True)
            
            try:
                blob_client = blob_service_client.get_blob_client(container=self.AZURE_STORAGE_BLOB[0], blob=local_file_name)
                blob_client.upload_blob(img_encode.tobytes(), overwrite=True)
            except:
                print("error")
        except Exception as e:
            print('__uploadToAzure Excpetion -' + str(e))
            return

    def __annotate(self, frame, response):
        AnnotationParserInstance = AnnotationParser()
        #TODO: Make the choice of the service configurable
        listOfRectanglesToDisplay = AnnotationParserInstance.getCV2RectanglesFromProcessingService1(response)
        for rectangle in listOfRectanglesToDisplay:
            cv2.rectangle(frame, (rectangle(0), rectangle(1)), (rectangle(2), rectangle(3)), (0,0,255),4)
        return
    def __undistort(self, frame):
        UndistortParserInstance = UndistortParser()
        
    def __sendFrameForProcessing(self, frame):
            headers = {'Content-Type': 'application/octet-stream'}
            try:
                response = requests.post(self.imageProcessingEndpoint, headers = headers, params = self.imageProcessingParams, data = frame)
            except Exception as e:
                print('__sendFrameForProcessing Excpetion -' + str(e))
                return "[]"

            if self.verbose:
                try:
                    print("Response from external processing service: (" + str(response.status_code) + ") " + json.dumps(response.json()))
                except Exception:
                    print("Response from external processing service (status code): " + str(response.status_code))
            print(response)
            return []
            #return json.dumps(response.json())

    def __displayTimeDifferenceInMs(self, endTime, startTime):
        return str(int((endTime-startTime) * 1000)) + " ms"

    def __enter__(self):
        if self.isWebcam:
            #The VideoStream class always gives us the latest frame from the webcam. It uses another thread to read the frames.
            if self.isRTSP==False:
                self.vs = VideoStream(int(self.videoPath))
                self.vs.setSize(4032,3040)
            else:
                self.vs = VideoStream(self.videoPath)
            self.vs.start()
            time.sleep(1.0)
            #needed to load at least one frame into the VideoStream class
            #self.capture = cv2.VideoCapture(int(self.videoPath))
        else:
            #In the case of a video file, we want to analyze all the frames of the video thus are not using VideoStream class
            self.capture = cv2.VideoCapture(self.videoPath)
        return self

    def get_display_frame(self):
        return self.displayFrame
    
    def __get_roi_cropped(self,img_raw, roi):
        #Crop selected roi from raw image
        roi_cropped = img_raw[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
        return roi_cropped
    
    def __process_frame(self, frame):
        #print("process_frame")
        roi1 = [1102, 90, 418, 1823]
        roi2 = [1588, 164, 418, 1823]
        roi3 = [2075, 172, 418, 1823]
        roi4 = [2591, 63, 418, 1823]
        return __get_roi_cropped(self,frame, roi1)
    
    
    
    def start(self):
        frameCounter = 0
        offsetCounter= 0
        perfForOneFrameInMs = None
        while True:
            if self.showVideo or self.verbose:
                startOverall = time.time()
            if self.verbose:
                startCapture = time.time()
            offsetCounter += 1
            frameCounter +=1
            if self.isWebcam:
                frame = self.vs.read()
            else:
                frame = self.capture.read()[1]
                if frameCounter == 1:
                    if self.capture.get(cv2.CAP_PROP_FRAME_WIDTH) < self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT):
                        self.autoRotate = True
                if self.autoRotate:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE) #The counterclockwise is random...It coudl well be clockwise. Is there a way to auto detect it?
            if self.verbose:
                if frameCounter == 1:
                    if not self.isWebcam:
                        print("Original frame size: " + str(int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))) + "x" + str(int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))))
                        print("Frame rate (FPS): " + str(int(self.capture.get(cv2.CAP_PROP_FPS))))
                print("Frame number: " + str(frameCounter))
                print("Time to capture (+ straighten up) a frame: " + self.__displayTimeDifferenceInMs(time.time(), startCapture))
                startPreProcessing = time.time()
            
            #Loop video
            if not self.isWebcam:             
                if frameCounter == self.capture.get(cv2.CAP_PROP_FRAME_COUNT):
                    if self.loopVideo: 
                        frameCounter = 0
                        self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    else:
                        break

            #Pre-process locally
            if self.nbOfPreprocessingSteps == 1 and self.convertToGray:
                preprocessedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.nbOfPreprocessingSteps == 1 and (self.resizeWidth != 0 or self.resizeHeight != 0):
                preprocessedFrame = cv2.resize(frame, (self.resizeWidth, self.resizeHeight))

            if self.nbOfPreprocessingSteps > 1:
                preprocessedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                preprocessedFrame = cv2.resize(preprocessedFrame, (self.resizeWidth,self.resizeHeight))
            
            if self.verbose:
                print("Time to pre-process a frame: " + self.__displayTimeDifferenceInMs(time.time(), startPreProcessing))
                startEncodingForProcessing = time.time()

            #Process externally
            if self.imageProcessingEndpoint != "":

                #Encode frame to send over HTTP
                if self.nbOfPreprocessingSteps == 0:
                    encodedFrame = cv2.imencode(".jpg", frame)[1].tostring()
                else:
                    encodedFrame = cv2.imencode(".jpg", preprocessedFrame)[1].tostring()

                if self.verbose:
                    print("Time to encode a frame for processing: " + self.__displayTimeDifferenceInMs(time.time(), startEncodingForProcessing))
                    startProcessingExternally = time.time()
                print(frameCounter) 
                #Send frame to Azure StorageBlob
                ##if self.AZURE_STORAGE_CONTAINER != "" and self.AZURE_STORAGE_BLOB != "":
                
                print("Frame uploaded to Azure Storage Blob")
                #Send over HTTP for processing
                if offsetCounter==100:
                    #response = self.__sendFrameForProcessing(encodedFrame)
                    self.__uploadToAzure(frameCounter,frame)
                    offsetCounter=0
                #response = self.__sendFrameForProcessing(encodedFrame)
                if self.verbose:
                    print("Time to process frame externally: " + self.__displayTimeDifferenceInMs(time.time(), startProcessingExternally))
                ##    startSendingToEdgeHub = time.time()

                #forwarding outcome of external processing to the EdgeHub
                ##if response != "[]" and self.sendToHubCallback is not None:
                ##    self.sendToHubCallback(response)
                ##    if self.verbose:
                ##        print("Time to message from processing service to edgeHub: " + self.__displayTimeDifferenceInMs(time.time(), startSendingToEdgeHub))
                ##        startDisplaying = time.time()

            #Display frames
            if self.showVideo:
                try:
                    if self.nbOfPreprocessingSteps == 0:
                        if self.verbose and (perfForOneFrameInMs is not None):
                            cv2.putText(frame, "FPS " + str(round(1000/perfForOneFrameInMs, 2)),(10, 35),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255), 2)
                        #if self.annotate:
                        #    #TODO: fix bug with annotate function
                        #    self.__annotate(frame, response)
                        
                        self.displayFrame = cv2.imencode('.jpg', process_frame(frame))[1].tobytes()
                    else:
                        if self.verbose and (perfForOneFrameInMs is not None):
                            cv2.putText(preprocessedFrame, "FPS " + str(round(1000/perfForOneFrameInMs, 2)),(10, 35),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255), 2)
                        #if self.annotate:
                        #    #TODO: fix bug with annotate function
                        #    self.__annotate(preprocessedFrame, response)
                      
                        #roi1 = [1102, 90, 418, 1823]
                        ##undistort the image
                        preprocessedFrame = self.UndistortParserInstance.undistortImage(preprocessedFrame)
                        print("Frame undistorted")
                        print(self.ROI1)
                        rs = self.ROI1[0].split(",")
                        roi1=[int(rs[0]),int(rs[1]),int(rs[2]),int(rs[3])]
                        preroi1= preprocessedFrame[int(roi1[1]):int(roi1[1]+roi1[3]), int(roi1[0]):int(roi1[0]+roi1[2])]
                        
                        #roi2 = [1588, 164, 418, 1823]
                        rs = self.ROI2[0].split(",")
                        roi2 = [int(rs[0]),int(rs[1]),int(rs[2]),int(rs[3])]
                        preroi2 = preprocessedFrame[int(roi2[1]):int(roi2[1]+roi2[3]), int(roi2[0]):int(roi2[0]+roi2[2])]
                        
                        #roi3 = [2075, 172, 418, 1823]
                        rs = self. ROI3[0].split(",")
                        roi3 = [int(rs[0]),int(rs[1]),int(rs[2]),int(rs[3])]
                        preroi3 = preprocessedFrame[int(roi3[1]):int(roi3[1]+roi3[3]), int(roi3[0]):int(roi3[0]+roi3[2])]
                        
                        #roi4 = [2591, 63, 418, 1823]
                        rs = self.ROI4[0].split(",")
                        roi4 = [int(rs[0]),int(rs[1]),int(rs[2]),int(rs[3])]
                        preroi4 = preprocessedFrame[int(roi4[1]):int(roi4[1]+roi4[3]), int(roi4[0]):int(roi4[0]+roi4[2])]
                        import numpy as np
                        numpy_horizontal_concat = np.concatenate((preroi1, preroi2, preroi3, preroi4), axis=1)
     
                        self.displayFrame = cv2.imencode('.jpg', numpy_horizontal_concat)[1].tobytes()
                except Exception as e:
                    print("Could not display the video to a web browser.") 
                    print('Excpetion -' + str(e))
                if self.verbose:
                    if 'startDisplaying' in locals():
                        print("Time to display frame: " + self.__displayTimeDifferenceInMs(time.time(), startDisplaying))
                    elif 'startSendingToEdgeHub' in locals():
                        print("Time to display frame: " + self.__displayTimeDifferenceInMs(time.time(), startSendingToEdgeHub))
                    else:
                        print("Time to display frame: " + self.__displayTimeDifferenceInMs(time.time(), startEncodingForProcessing))
                perfForOneFrameInMs = int((time.time()-startOverall) * 1000)
                if not self.isWebcam:
                    waitTimeBetweenFrames = max(int(1000 / self.capture.get(cv2.CAP_PROP_FPS))-perfForOneFrameInMs, 1)
                    print("Wait time between frames :" + str(waitTimeBetweenFrames))
                    if cv2.waitKey(waitTimeBetweenFrames) & 0xFF == ord('q'):
                        break

            if self.verbose:
                perfForOneFrameInMs = int((time.time()-startOverall) * 1000)
                print("Total time for one frame: " + self.__displayTimeDifferenceInMs(time.time(), startOverall))

    def __exit__(self, exception_type, exception_value, traceback):
        if not self.isWebcam:
            self.capture.release()
        if self.showVideo:
            self.imageServer.close()
            cv2.destroyAllWindows()