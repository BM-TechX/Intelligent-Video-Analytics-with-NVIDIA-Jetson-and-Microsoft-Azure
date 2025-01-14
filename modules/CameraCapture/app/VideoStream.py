# To make python 2 and python 3 compatible code
from __future__ import absolute_import

from threading import Thread
import sys
if sys.version_info[0] < 3:  # e.g python version <3
    import cv2
else:
    import cv2
# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955


# import the Queue class from Python 3
if sys.version_info >= (3, 0):
    from queue import Queue
# otherwise, import the Queue class for Python 2.7
else:
    from Queue import Queue

# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread


class VideoStream(object):
    
    def __init__(self, path, queueSize=1):
        self.stream = cv2.VideoCapture(path)
        #self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.path = path
        self.retrycount=4
        #self.stream.set(cv2.CAP.PROP_FRAME_WIDTH, 1920)
        #self.stream.set(cv2.CAP.PROP_FRAME_HEIGHT, 1080)
        self.stopped = False
        self.Q = Queue(maxsize=queueSize)
    def setSize(self, width, height):
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    def setFPS(self, fps):
        try:
            self.stream.set(cv2.CAP_PROP_FPS, fps)
        except:
            print("Error setting FPS")
    def start(self):
        # start a thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    def retryUpdate(self):
        if (self.retrycount > 0):
            self.stream.release()
            self.stream = cv2.VideoCapture(self.path)
            #self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.retrycount=self.retrycount-1
            self.stop=False
            self.update()
        print("retrying to open video stream")
            
    def update(self):
        try:
            while True:
                if self.stopped:
                    return

                if not self.Q.full():
                    (grabbed, frame) = self.stream.read()
                    # if the `grabbed` boolean is `False`, then we have
                    # reached the end of the video file
                    if not grabbed:
                        #self.stop()
                        self.retryUpdate()
                        
                        #return
                    self.retrycount=4
                    self.Q.put(frame)

                    # Clean the queue to keep only the latest frame
                    while self.Q.qsize() > 1:
                        self.Q.get()
        except Exception as e:
            print("got error: "+str(e))

    def read(self):
        return self.Q.get()

    def more(self):
        return self.Q.qsize() > 0

    def stop(self):
        self.stopped = True

    def __exit__(self, exception_type, exception_value, traceback):
        self.stream.release()
        
