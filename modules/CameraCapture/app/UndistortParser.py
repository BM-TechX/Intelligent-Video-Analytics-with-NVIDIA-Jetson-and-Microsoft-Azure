# To make python 2 and python 3 compatible code
from __future__ import absolute_import
import cv2 # Import the OpenCV library to enable computer vision
import numpy as np # Import the NumPy scientific computing library
import glob # Used to get retrieve files that have a specified pattern
# Returns an undistorted image given by a processing service
# Returns rectangle boundaries in the CV2 format (topLeftX, topLeftY, bottomRightX, bottomRightY) given by a processing service

class UndistortParser:
    def __init__(self):
        # Get the camera calibration matrix and distortion coefficients
        ret, camera_matrix, distortion_coefficients, rvecs, tvecs = self.getUndistortedImageFromProcessingService()
        self.ret=ret
        self.camera_matrix=camera_matrix
        self.distortion_coefficients=distortion_coefficients
        self.rvecs=rvecs
        self.tvecs=tvecs
        
    def getUndistortedImageFromProcessingService(self):
        # Chessboard dimensions
        number_of_squares_X = 7 # Number of chessboard squares along the x-axis
        number_of_squares_Y = 10  # Number of chessboard squares along the y-axis
        nX = number_of_squares_X - 1 # Number of interior corners along x-axis
        nY = number_of_squares_Y - 1 # Number of interior corners along y-axis
        square_size = 0.015# Length of the side of a square in meters
        # Store vectors of 3D points for all chessboard images (world coordinate frame)
        object_points = []
        # Store vectors of 2D points for all chessboard images (camera coordinate frame)
        image_points = []
        # Set termination criteria. We stop either when an accuracy is reached or when
        # we have finished a certain number of iterations.
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # Define real world coordinates for points in the 3D coordinate frame
        # Object points are (0,0,0), (1,0,0), (2,0,0) ...., (5,8,0)
        object_points_3D = np.zeros((nX * nY, 3), np.float32)       
        # These are the x and y coordinates                                              
        object_points_3D[:,:2] = np.mgrid[0:nY, 0:nX].T.reshape(-1, 2) 
        object_points_3D = object_points_3D * square_size
        images= glob.glob('*.jpg')
        gray=cv2.imread(images[0],0)
        # Go through each chessboard image, one by one
        for image_file in images:
            # Load the image
            image = cv2.imread(image_file)  
            # Convert the image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  
            # Find the corners on the chessboard
            success, corners = cv2.findChessboardCorners(gray, (nY, nX), None)
            # If the corners are found by the algorithm, draw them
            if success == True:
                # Append object points
                object_points.append(object_points_3D)
                # Find more exact corner pixels       
                corners_2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)       
                # Append image points
                image_points.append(corners_2)
                # Draw the corners
                cv2.drawChessboardCorners(image, (nY, nX), corners_2, success)
                # Display the image. Used for testing.
                # Display the window for a short period. Used for testing
                #cv2.waitKey(200) 
            # Get the camera calibration matrix and distortion coefficients
        #ret, camera_matrix, distortion_coefficients, rvecs, tvecs = cv2.calibrateCamera(object_points, image_points, gray.shape[::-1], None, None)
        return cv2.calibrateCamera(object_points, image_points, gray.shape[::-1], None, None)
    def undistortImage(self, image):
        # Undistort the image
        height, width = image.shape[:2]
        # Returns optimal camera matrix and a rectangular region of interest
        optimal_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(self.camera_matrix, self.distortion_coefficients, 
                                                                    (width,height), 
                                                                    1, 
                                                                    (width,height))
        return cv2.undistort(image, self.camera_matrix, self.distortion_coefficients, None, optimal_camera_matrix)