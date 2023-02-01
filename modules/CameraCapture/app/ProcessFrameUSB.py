# To make python 2 and python 3 compatible code
from __future__ import absolute_import
from threading import Thread
import cv2
import numpy
import imutils
import threading
import time
import BufferLess
from BufferLess import BufferLess
import UploadToAzure
from UploadToAzure import UploadToAzure
from azure.storage.blob import BlobServiceClient, PublicAccess
import usb.core

from datetime import datetime

# pylint: disable=E1101
# pylint: disable=E0401
# Disabling linting that is not supported by Pylint for C extensions such as OpenCV. See issue https://github.com/PyCQA/pylint/issues/1955
# This class reads all the video frames in a separate thread and always has the keeps only the latest frame in its queue to be grabbed by another thread
# bufferless VideoCapture
class ProcessFrameUSB(threading.Thread):
    	# 4032×3040@10fps; 
        # 3840×2160@20fps; 
        # 2592×1944@30fps; 
        # 2560×1440@30fps; 
        # 1920×1080@60fps; 
        # 1600×1200@50fps; 
        # 1280×960@100fps; 
        # 1280×760@100fps; 
        # 640×480@80fps
    def __init__(self,threshold=0.7,infrencerbuttom = None,height=1080,witdh=1920,table="notSet",AZURE_STORAGE_BLOB=None):
        self.camera1 = None
        self.camera2 = None
        self.camera3 = None
        self.camera4 = None
        self.frame1 = None
        self.frame1_ready = False
        self.frame2 = None
        self.frame2_ready = False
        self.frame3 = None
        self.frame3_ready = False
        self.frame4 = None
        self.frame4_ready = False
        self.LaneState = None
        self.LaneState1 = None
        self.LaneState2 = None
        self.LaneState3 = None
        self.LaneState4 = None
        self.table = table
        self.threshold = threshold
        self.infrencerbuttom = infrencerbuttom
        self.thread1 = None
        self.height = height
        self.witdh = witdh
        self.connectionstring = "DefaultEndpointsProtocol=https;AccountName=camtagstoreaiem;AccountKey=TwURR9XUNY+jsvTvMzGdjUxb+x8q+MCSLiVxNwGBdg5vjwkBEP6q1DWUI+SId91AxHxJKIzOLjBq+ASt2YALow==;EndpointSuffix=core.windows.net"
        self.AZURE_STORAGE_BLOB = AZURE_STORAGE_BLOB
        self.upload = UploadToAzure(self.connectionstring,self.table)
        self.ALARM=0
        self.threadcam1 = None
        self.threadcam2 = None
        self.threadcam3 = None
        self.threadcam4 = None
        self.cam1= None
        self.cam2= None
        self.cam3= None
        self.cam4= None
        self.errorgrap1 = 0
        self.errorgrap2 = 0
        self.errorgrap3 = 0
        self.errorgrap4 = 0
        self.uploadToAzure = 0
        try :
            self.upload.connectToAzure()
            self.upload.createTable(self.table)
            if(self.upload.test_con()):
                print("Connected to Azure")
            else:
                self.upload.intiateTable(self.table)
        except Exception as e:
            print("Error initCamera " + str(e))
        #######figure out which usb camera is associated with which lane
        for i in range(0, 11):
            vcap = cv2.VideoCapture("/dev/video"+str(i))
            print("trying to open camera :" + str(i) )
            if vcap.isOpened():
                print("camera opened :" + str(i))
                if(self.cam1 == None):
                    self.cam1= "/dev/video"+str(i)
                elif(self.cam2 == None):
                    self.cam2= "/dev/video"+str(i)
                elif(self.cam3 == None):
                    self.cam3= "/dev/video"+str(i)
                elif(self.cam4 == None):
                    self.cam4= "/dev/video"+str(i)
                vcap.release()
            else:
                vcap.release()

 
        try:
            self.camera1 = cv2.VideoCapture(self.cam1)
            self.camera1.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
            self.camera1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            #self.camera1 = BufferLess(0)
            time.sleep(2.0)      
        except Exception as e:
            print("Error initCamera 0 " + str(e))
        try:
            self.camera2 = cv2.VideoCapture(self.cam2)
            self.camera2.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
            self.camera2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera2.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            time.sleep(2.0)
        except:
            print("Error initCamera 1 " +str(e))
        try:
            self.camera3 = cv2.VideoCapture(self.cam3)
            self.camera3.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
            self.camera3.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera3.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            time.sleep(2.0)
        except:
            print("Error initCamera 2 " +str(e))
        try:
            self.camera4 = cv2.VideoCapture(self.cam4)
            self.camera4.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
            self.camera4.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camera4.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            time.sleep(2.0)
        except:
            print("Error initCamera 3 " +str(e))
            
    def containsCheck(self,str1):
        if (self.cam1 == 'dev/video'+str1):
            return True
        elif(self.cam2 == 'dev/video'+str1):
            return True
        elif(self.cam3 == 'dev/video'+str1):
            return True
        elif(self.cam4 == 'dev/video'+str1):
            return True
        else:
            return False
    def setcam(self,camid,str1):
        try:
            print("setcam " + camid + " " + str1)
            if(camid == "CAM1"):
                self.cam1 = str1
                self.camera1 = cv2.VideoCapture(self.cam1)
                self.camera1.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
                self.camera1.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.camera1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.camera1.set(cv2.CAP_PROP_FPS, 4)
                return True
            elif(camid == "CAM2"):
                self.cam2 = str1
                self.camera2 = cv2.VideoCapture(self.cam2)
                self.camera2.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
                self.camera2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.camera2.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.camera1.set(cv2.CAP_PROP_FPS, 4)
                return True
            elif(camid == "CAM3"):
                self.cam3 = str1
                self.camera3 = cv2.VideoCapture(self.cam3)
                self.camera3.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
                self.camera3.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.camera3.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.camera1.set(cv2.CAP_PROP_FPS, 4)
                return True
            elif(camid == "CAM4"):
                self.cam4 = str1
                self.camera4 = cv2.VideoCapture(self.cam4)
                self.camera4.set(cv2.CAP_PROP_FRAME_WIDTH,  self.witdh)
                self.camera4.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self.camera4.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.camera1.set(cv2.CAP_PROP_FPS, 4)
                return True
        except Exception as e:
            print("Error initCamera  " + str(camid) +str(e))
            return False
                                            
    def retryCamEstab(self,camid):
        try:
            print("retrying to open camera :" + str(camid) )
            
            for i in range(0, 11):
                if(self.containsCheck(str(i)) == False):
                    vcap = cv2.VideoCapture("/dev/video"+str(i))
                    print("trying to open camera :" + str(i) )
                    if vcap.isOpened():
                        vcap.release()
                        self.setcam(camid,"/dev/video"+str(i))
                        break   
                    else:
                        vcap.release()


            
        except Exception as e:
            print("Error initCamera  " + str(camid) +str(e))
            return None
        
    def __gstreamer_pipeline(
        camera_id,
        capture_width=1920,
        capture_height=1080,
        display_width=1920,
        display_height=1080,
        framerate=10,
        flip_method=0,
    ):
        return (
                "nvarguscamerasrc sensor-id=%d ! "
                "video/x-raw(memory:NVMM), "
                "width=(int)%d, height=(int)%d, "
                "format=(string)NV12, framerate=(fraction)%d/1 ! "
                "nvvidconv flip-method=%d ! "
                "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                "videoconvert ! "
                "video/x-raw, format=(string)BGR ! appsink max-buffers=1 drop=True"
                % (
                        camera_id,
                        capture_width,
                        capture_height,
                        framerate,
                        flip_method,
                        display_width,
                        display_height,
                )
        )
    # grab frames as soon as they are available
    def get_process_lane(self,rs,regioninner,rotation,frame):
        region1= rs[0].split(",")
        roi1=[int(region1[0]),int(region1[1]),int(region1[2]),int(region1[3])]
        frame_cropped= frame[int(roi1[1]):int(roi1[1]+roi1[3]), int(roi1[0]):int(roi1[0]+roi1[2])]
        frame_cropped_rotated=imutils.rotate(frame_cropped,rotation)
        frame_cropped_rotated_inner = frame_cropped_rotated[int(regioninner[1]):int(regioninner[1]+regioninner[3]), int(regioninner[0]):int(regioninner[0]+regioninner[2])]
        return frame_cropped_rotated_inner
    
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
    
        try:
            now = datetime.now()
            #now.month, now.day, now.year, now.hour, now.minute, now.secon
            entity={
                'PartitionKey': id,
                'RowKey': str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second),
                'Prediction': predictions.pred_label,
                'Score': str(predictions.pred_score),
                'anomaly_map': str(predictions.anomaly_map),
                'pred_mask': str(predictions.pred_mask),
                #'Timestamp': str(datetime.datetime.now())
            }
            if(self.upload.test_con()):
                self.upload.uploadtoTable(entity)
            else:
                self.upload.intiateTable(self.table)
                self.upload.uploadtoTable(entity)
        except Exception as e:
            print("Error connecting to Azure " + str(e))
    def __uploadToAzure(self, filename, frame):
        try:
            print("uploading to azure:" + filename)
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

    def process_lane_bottom(self,frame,threshold,id):
        preroi_img = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        preroi_img_ot,predictions =self.infrencerbuttom.getInfrence(preroi_img)
        LaneState = predictions.pred_label + " " + str(round(predictions.pred_score,2))
        now = datetime.now()
        rowkey = str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second) + str(now.microsecond)
        url = ""
        if(predictions.pred_score>threshold):
            try:
                height, width, channels = preroi_img_ot.shape
                start_point = (0,0)
                end_point = (width, height)
                color = (0,0,255)
                thickness = 8
                preroi_img_ot = cv2.rectangle(preroi_img_ot, start_point, end_point, color, thickness)
                if(self.uploadToAzure ==1):
                    self.__uploadToAzure(filename=rowkey+id,frame=preroi_img)
                    url = "https://camtagstoreaiem.blob.core.windows.net/fiberdefectstest/"+rowkey+id+ ".jpg"
                self.ALARM = self.ALARM + 1
            except Exception as e:
                    print("something went wrong while uploading to azure")
            cv2.putText(preroi_img_ot, LaneState, (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 1)
        else:
            cv2.putText(preroi_img_ot, LaneState, (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 1)
        if(self.uploadToAzure==1):
            self.azUp(predictions,id,rowkey,url)
        return preroi_img_ot,LaneState
    
    
    def processCAM1(self):
        while True:
            try:
                _,frame1 = self.camera1.read()
                frame_gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                frame_pred1,self.LaneState1 = self.process_lane_bottom(frame_gray1,self.threshold,"usb1")
                self.frame1= frame_pred1
                self.frame1_ready = True
            except Exception as e:
                print("Error grab 1")
                #if(self.errorgrap1  > 10):
                self.camera1.release()
                self.cam1=None
                self.retryCamEstab("CAM1")
                self.errorgrap1 = 0
                #else:
                #    self.errorgrap1 = self.errorgrap1 + 1
                
    def processCAM2(self):
        while True:
            try:
                _,frame2 = self.camera2.read()
                frame_gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                frame_pred2,self.LaneState2 = self.process_lane_bottom(frame_gray2,self.threshold,"usb2")
                self.frame2 = frame_pred2
                self.frame2_ready = True
            except:
                print("Error grab 2")
                #if(self.errorgrap2  > 10):
                self.camera2.release()
                self.cam2=None
                self.retryCamEstab("CAM2")
                self.errorgrap2 = 0
                #else:
                #    self.errorgrap2 = self.errorgrap2 + 1
                
                
                
                
    def processCAM3(self):
        while True:
            try:
                _,frame3 = self.camera3.read()
                frame_gray3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)
                frame_pred3,self.LaneState3 = self.process_lane_bottom(frame_gray3,self.threshold,"usb3")
                self.frame3 = frame_pred3
                self.frame3_ready = True
            except:
                print("Error grab 3")
                #if(self.errorgrap3  > 10):
                self.camera3.release()
                self.cam3=None
                self.retryCamEstab("CAM3")
                self.errorgrap3 = 0
                #else:
                    #self.errorgrap3 = self.errorgrap3 + 1



    def processCAM4(self):
        while True:
            try:
                _,frame4 = self.camera4.read()
                frame_gray4 = cv2.cvtColor(frame4, cv2.COLOR_BGR2GRAY)
                frame_pred4,self.LaneState4 = self.process_lane_bottom(frame_gray4,self.threshold,"usb4")
                self.frame4 = frame_pred4
                self.frame4_ready = True
            except:
                print("Error grab 4")
                #if(self.errorgrap4  > 10):
                self.camera4.release()
                self.cam4=None
                self.retryCamEstab("CAM4")
                self.errorgrap4 = 0
                #else:
                 #   self.errorgrap1 = self.errorgrap1 + 1
            
    def processing(self):
        while True:
            try:
                _,frame1 = self.camera1.read()
                frame_gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                frame_pred1,self.LaneState1 = self.process_lane_bottom(frame_gray1,self.threshold,"usb1")
                self.frame1= frame_pred1
                self.frame1_ready = True
            except Exception as e:
                print("Error grab 0 " + str(e))
                if(self.errorgrap1  > 10):
                    self.camera1.release()
                    self.cam1=None
                    self.retryCamEstab("CAM1")
                    self.errorgrap1 = 0
                else:
                    self.errorgrap1 = self.errorgrap1 + 1
            try:
                _,frame2 = self.camera2.read()
                frame_gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                frame_pred2,self.LaneState2 = self.process_lane_bottom(frame_gray2,self.threshold,"usb2")
                self.frame2 = frame_pred2
                self.frame2_ready = True
            except:
                print("Error grab 1")
                if(self.errorgrap2  > 10):
                    self.camera2.release()
                    self.cam2=None
                    self.retryCamEstab("CAM2")
                    self.errorgrap2 = 0
                else:
                    self.errorgrap2 = self.errorgrap2 + 1
            try:
                _,frame3 = self.camera3.read()
                frame_gray3 = cv2.cvtColor(frame3, cv2.COLOR_BGR2GRAY)
                frame_pred3,self.LaneState3 = self.process_lane_bottom(frame_gray3,self.threshold,"usb3")
                self.frame3 = frame_pred3
                self.frame3_ready = True
            except:
                print("Error grab 2")
                if(self.errorgrap3  > 10):
                    self.camera3.release()
                    self.cam3=None
                    self.retryCamEstab("CAM3")
                    self.errorgrap3 = 0
                else:
                    self.errorgrap2 = self.errorgrap2 + 1
            try:
                _,frame4 = self.camera4.read()
                frame_gray4 = cv2.cvtColor(frame4, cv2.COLOR_BGR2GRAY)
                frame_pred4,self.LaneState4 = self.process_lane_bottom(frame_gray4,self.threshold,"usb4")
                self.frame4 = frame_pred4
                self.frame4_ready = True
            except:
                print("Error grab 3")
                if(self.errorgrap4 > 10):
                    self.camera4.release()
                    self.cam4=None
                    self.retryCamEstab("CAM4")
                    self.errorgrap4 = 0
                else:
                    self.errorgrap4 = self.errorgrap4 + 1

    def getframe(self,cameraid):
        if(self.frame1_ready and cameraid == "0"):
            self.frame1_ready = False
            return self.LaneState1,self.frame1
        elif (self.frame2_ready and cameraid == "1"):
            self.frame2_ready = False
            return self.LaneState2,self.frame2
        elif(self.frame3_ready and cameraid == "2"):
            self.frame3_ready = False
            return self.LaneState3,self.frame3
        elif(self.frame4_ready and cameraid == "3"):
            self.frame4_ready = False
            return self.LaneState4,self.frame4
        else:
            return None
               
    def start_processing(self):
        if self.infrencerbuttom is None:
            print("Infrencer is not initialized")
            return False
        else:
            thread1 = threading.Thread(target=self.processing)
            thread1.start()
            self.thread1 = thread1
            # self.threadcam1 = threading.Thread(target=self.processCAM1)
            # self.threadcam1.start()
            # self.threadcam2 = threading.Thread(target=self.processCAM2)
            # self.threadcam2.start()
            # self.threadcam3 = threading.Thread(target=self.processCAM3)
            # self.threadcam3.start()
            # self.threadcam4 = threading.Thread(target=self.processCAM4)
            # self.threadcam4.start()
            
            return True
    def stop_processing(self):
        try:
            self.thread1.terminate()
            # self.threadcam1.terminate()
            # self.threadcam2.terminate()
            # self.threadcam3.terminate()
            # self.threadcam4.terminate()
            # self.camera1.release()
            # self.camera2.release()
            # self.camera3.release()
            # self.camera4.release()
        except:
            print("Error stopping processing")
            return False
        return True
   
