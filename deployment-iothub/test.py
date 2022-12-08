import cv2
import time

vcap0 = cv2.VideoCapture("0") 
vcap1 = cv2.VideoCapture("/dev/video1")
vcap2 = cv2.VideoCapture("/dev/video2")
vcap3 = cv2.VideoCapture("/dev/video3")
vcap4 = cv2.VideoCapture("/dev/video4")
vcap5 = cv2.VideoCapture("/dev/video5")
vcap6 = cv2.VideoCapture("/dev/video6")
vcap7 = cv2.VideoCapture("/dev/video7")
vcap8 = cv2.VideoCapture("/dev/video8")
for i in range(0, 10):
    print("trying to open camera : " + str(i) + "")
    vcap = cv2.VideoCapture(i)
    if vcap.isOpened():
        print("camera opened :" + str(i) )
        vcap.release()
        break
    else:
        print("camera not opened :" + str(i))
        vcap.release()
        continue
   
    