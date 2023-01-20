# To make python 2 and python 3 compatible code
from __future__ import absolute_import

import cv2, queue, threading, time
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955

# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread

import threading


# bufferless VideoCapture
class BufferLess:
    def __init__(self, name,setFPS=0,setWidth=0,setHeight=0,id=""):
        self.cap = cv2.VideoCapture('rtsp://admin:S0lskin1234!@10.10.50.102:554')
        if (setFPS > 0):
            self.cap.set(cv2.CAP_PROP_FPS, setFPS)
        if (setWidth > 0):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, setWidth)
        if (setHeight > 0):
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, setHeight)
        self.lock = threading.Lock()
        self.t = threading.Thread(target=self._reader)
        self.t.daemon = True
        self.id = id
        self.t.start()
        self.frame1 = None
        self.frame1_ready = False
    
    # grab frames as soon as they are available
    def _reader(self):
        print("Starting reader thread")
        print ("doing some initial grabs")
        try:
            self.cap.read()
            self.cap.read()
            self.cap.read()
        except:
            print("Error grabbing initial frames")
        while True:
            with self.lock:
                #print("frameCAP" +self.id)
                try:
                    ret = self.cap.grab()
                except:
                    print("Error grabbing frame")
                    ret = self.cap.grab()
            if not ret:
                break
    
    
 
 
    # retrieve latest frame
    def read(self):
        with self.lock:
            _, frame = self.cap.retrieve()
        return frame
    
    
    def read_gray(self):
        with self.lock:
            cap, frame = self.cap.retrieve()
            if cap:
                try:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                except:
                    print("Error converting to gray")
        return frame
    def stop(self):
        self.cap.release()
        
        return True