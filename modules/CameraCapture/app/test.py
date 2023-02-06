import cv2

# Open the video capture using the pipeline string
cap = cv2.VideoCapture("nvargussrc sensor-id:1  ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

# Check if the video capture was successfully opened
if not cap.isOpened():
    print("Failed to open the video capture")
    exit()

# Start capturing frames
while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    # Check if the frame was successfully read
    if not ret:
        print("Failed to read a frame from the video capture")
        break
    print("Frame read successfully")
    # Display the frame

    # Check if the user pressed the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture
cap.release()

# Destroy all OpenCV windows
