import cv2 
vid = cv2.VideoCapture('rtsp://admin:S0lskin1234!@10.10.50.102:554')
while True:
    print("reading")
    ret, frame = vid.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break