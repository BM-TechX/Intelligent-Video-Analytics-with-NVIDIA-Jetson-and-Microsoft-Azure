import cv2

# ----------------------------
# Parse command line arguments
backSub = cv2.createBackgroundSubtractorMOG2()


inVideo = cv2.VideoCapture("C:/Users/leh/Downloads/test.mp4")

capture = inVideo
if not capture.isOpened():
    print('Unable to open: ')
    exit(0)
while True:
    ret, frame = capture.read()
    if frame is None:
        break
    
    fgMask = backSub.apply(frame)
    
    
    cv2.rectangle(frame, (10, 2), (100,20), (255,255,255), -1)
    cv2.putText(frame, str(capture.get(cv2.CAP_PROP_POS_FRAMES)), (15, 15),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (0,0,0))
    
    
    cv2.imshow('Frame', frame)
    cv2.imshow('FG Mask', fgMask)
    
    keyboard = cv2.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break