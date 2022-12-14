# To make python 2 and python 3 compatible code
from __future__ import absolute_import
from threading import Thread
import cv2
from datetime import datetime
import numpy
import imutils
import threading
import UndistortParser
from UndistortParser import UndistortParser
import BufferLess
from BufferLess import BufferLess
import numpy as np
import time
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955
# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread
# bufferless VideoCapture
class ProcessFrame(threading.Thread):
    def __init__(self,videoPath,threshold=0.5,infrencerTop = None, id="notdefined",
                ROI1="0,0,0,0",
                ROI2="0,0,0,0",
                ROI3="0,0,0,0",
                ROI4="0,0,0,0",
                 ):
        self.camera = BufferLess(videoPath,id="rtsp")
        self.frame = None
        self.frame_ready = False
        self.LaneState = None
        self.threshold = threshold
        self.infrencerTop = infrencerTop
        self.thread = None
        self.genral_rotation = 358.5
        self.roi1_rotation=360.1
        self.roi2_rotation=359.8
        self.roi3_rotation=359.25
        self.roi4_rotation=358.7
        self.roi1a = [9,100,303,1750]
        self.roi2a = [15,100,316,1750]
        self.roi3a = [30,100,320,1750]
        self.roi4a = [30,100,325,1750]
        self.UndistortParserInstance = UndistortParser()
        self.resizeWidth = 0
        self.resizeHeight = 0
        self.ROI1 = ROI1
        self.ROI2 = ROI2
        self.ROI3 = ROI3
        self.ROI4 = ROI4
        self.Lane1State=None
        self.Lane2State=None
        self.Lane3State=None
        self.Lane4State=None
            
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

    def getframe(self):
        if(self.frame_ready):
            self.frame_ready = False
            return self.frame
        else:
            return None
    def processing(self):
        while True:
            try:
                _,frame = self.camera.read()
                
                try:
                    print("frame starting preprocessing")
                    preprocessedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    if (self.resizeWidth != 0 or self.resizeHeight != 0):
                        preprocessedFrame = cv2.resize(frame, (self.resizeWidth, self.resizeHeight))
                    print("Undistorting frame")
                    preprocessedFrame = self.UndistortParserInstance.undistortImage(preprocessedFrame)
                    print("rotating frame")
                    preprocessedFrame=imutils.rotate(preprocessedFrame,self.genral_rotation)

                    print ("frame processed")
                    preroi1 = self.get_process_lane(self.ROI1,self.roi1a,self.roi1_rotation,preprocessedFrame)
                    preroi2 = self.get_process_lane(self.ROI2,self.roi2a,self.roi2_rotation,preprocessedFrame)
                    preroi3 = self.get_process_lane(self.ROI3,self.roi3a,self.roi3_rotation,preprocessedFrame)
                    preroi4 = self.get_process_lane(self.ROI4,self.roi4a,self.roi4_rotation,preprocessedFrame)
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
                    #####################COMBINE
                    print("combining")
                    print (self.Lane1State + " " + self.Lane2State + " " + self.Lane3State + " " + self.Lane4State)
                    numpy_horizontal_concat = np.concatenate((preroi1_img_ot, preroi2_img_ot, preroi3_img_ot, preroi4_img_ot), axis=1)
                    self.frame= numpy_horizontal_concat
                    self.frame_ready = True
                except:
                    print("frame size is 0")
                    time.sleep(1.0)
            except Exception as e:
                print("Error grab 0 " + str(e))
          
    def start_processing(self):
        if self.infrencerTop is None:
            print("Infrencer is not initialized")
            return False
        else:
            thread1 = threading.Thread(target=self.processing)
            thread1.start()
            self.thread = thread1
            return True
     
    def stop_processing(self):
        self.thread.terminate()
        return True
