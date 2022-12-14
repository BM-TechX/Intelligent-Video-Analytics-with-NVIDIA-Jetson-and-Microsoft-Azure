# To make python 2 and python 3 compatible code
from __future__ import absolute_import
from threading import Thread
import cv2
from datetime import datetime
import numpy
import imutils
import threading
import time
import BufferLess
from BufferLess import BufferLess
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955
# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread
# bufferless VideoCapture
class ProcessFrameUSB(threading.Thread):
    def __init__(self,threshold=0.5,infrencerbuttom = None,height=3040,witdh=4032):
        self.camera1 = None
        self.camera2 = None
        self.camera3 = None
        self.camera3 = None
        self.frame1 = None
        self.frame1_ready = False
        self.frame2 = None
        self.frame2_ready = False
        self.frame3 = None
        self.frame3_ready = False
        self.frame4 = None
        self.frame4_ready = False
        self.LaneState = None
        self.threshold = threshold
        self.infrencerbuttom = infrencerbuttom
        self.height = height
        self.witdh = witdh
        try:
            self.camera1 = cv2.VideoCapture('/dev/video0')
            self.camera1.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
            self.camera1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            #self.camera1 = BufferLess(0)
            time.sleep(5.0)      
        except Exception as e:
            print("Error initCamera 0 " + e)
        try:
            self.camera2 = cv2.VideoCapture('/dev/video1')
            self.camera2.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
            self.camera2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            time.sleep(5.0)
        except:
            print("Error initCamera 1 " +e)
        try:
            self.camera3 = cv2.VideoCapture('/dev/video2')
            self.camera3.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
            self.camera3.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            time.sleep(5.0)
        except:
            print("Error initCamera 2 " +e)
        try:
            self.camera4 = cv2.VideoCapture('/dev/video3')
            self.camera4.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
            self.camera4.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            time.sleep(5.0)
        except:
            print("Error initCamera 3 " +e)
        
        
    # grab frames as soon as they are available
    def get_process_lane(self,rs,regioninner,rotation,frame):
        region1= rs[0].split(",")
        roi1=[int(region1[0]),int(region1[1]),int(region1[2]),int(region1[3])]
        frame_cropped= frame[int(roi1[1]):int(roi1[1]+roi1[3]), int(roi1[0]):int(roi1[0]+roi1[2])]
        frame_cropped_rotated=imutils.rotate(frame_cropped,rotation)
        frame_cropped_rotated_inner = frame_cropped_rotated[int(regioninner[1]):int(regioninner[1]+regioninner[3]), int(regioninner[0]):int(regioninner[0]+regioninner[2])]
        return frame_cropped_rotated_inner
    
    def process_lane_bottom(self,frame,threshold):
        preroi_img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        preroi_img_ot,predictions =self.infrencerbuttom.getInfrence(preroi_img)
        LaneState = predictions.pred_label + " " + str(round(predictions.pred_score,2))
        if(predictions.pred_score>threshold):
            try:
                self.__uploadToAzure(str(datetime.date)+".jpg",frame=preroi_img)
                state="ALARM"
            except Exception as e:
                    print("something went wrong while uploading to azure : ")
        cv2.putText(preroi_img_ot, LaneState, (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
        return preroi_img_ot,LaneState
    
    def processing(self):
        while True:
            try:
                _,frame1 = self.camera1.read()
                frame_gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                frame_pred1,self.LaneState = self.process_lane_bottom(frame_gray1,self.threshold)
                self.frame1= frame_pred1
                self.frame1_ready = True
            except Exception as e:
                print("Error grab 0 " + e)
            try:
                _,frame2 = self.camera2.read()
                frame_gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                frame_pred2,self.LaneState = self.process_lane_bottom(frame_gray2,self.threshold)
                self.frame2 = frame_pred2
                self.frame2_ready = True
            except:
                print("Error grab 1")
            try:
                _,frame3 = self.camera3.read()
                frame_gray3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)
                frame_pred3,self.LaneState = self.process_lane_bottom(frame_gray3,self.threshold)
                self.frame3 = frame_pred3
                self.frame3_ready = True
            except:
                print("Error grab 2")
            try:
                _,frame4 = self.camera4.read()
                frame_gray4 = cv2.cvtColor(frame4, cv2.COLOR_BGR2GRAY)
                frame_pred4,self.LaneState = self.process_lane_bottom(frame_gray4,self.threshold)
                self.frame4 = frame_pred4
                self.frame4_ready = True
            except:
                print("Error grab 3")

    def getframe(self,cameraid):
        if(self.frame1_ready and cameraid == "0"):
            self.frame1_ready = False
            return self.frame1
        elif (self.frame2_ready and cameraid == "1"):
            self.frame2_ready = False
            return self.frame2
        elif(self.frame3_ready and cameraid == "2"):
            self.frame3_ready = False
            return self.frame3
        elif(self.frame4_ready and cameraid == "3"):
            self.frame4_ready = False
            return self.frame4
        else:
            return None
               
    def start_processing(self):
        if self.infrencerbuttom is None:
            print("Infrencer is not initialized")
            return False
        else:
            thread1 = threading.Thread(target=self.processing)
            thread1.start()
            return True
     
   
