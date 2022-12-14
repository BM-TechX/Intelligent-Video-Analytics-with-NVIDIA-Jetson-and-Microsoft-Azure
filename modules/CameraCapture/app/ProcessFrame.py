# To make python 2 and python 3 compatible code
from __future__ import absolute_import
from threading import Thread
import cv2
from datetime import datetime
import numpy
import imutils
import threading
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955
# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread
# bufferless VideoCapture
class ProcessFrame(threading.Thread):
    def __init__(self,camera,threshold=0.5,infrencerbuttom = None, id="notdefined"):
        self.camera = camera
        self.frame = None
        self.frame_ready = False
        self.LaneState = None
        self.threshold = threshold
        self.infrencerbuttom = infrencerbuttom
        self.thread = None

    # grab frames as soon as they are available
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

    def processing(self):
        while True:
            try:
                frame = self.camera.read()
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frane_pred,self.LaneState = self.process_lane_bottom(frame_gray,self.threshold)
                self.frame = frane_pred
                self.frame_ready = True
            except Exception as e:
                print("something went wrong while reading frame from camera : " + id)
    def getframe(self):
        if(self.frame_ready):
            self.frame_ready = False
            return self.frame
        else:
            return None
               
    def start_processing(self):
        if self.infrencerbuttom is None:
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
