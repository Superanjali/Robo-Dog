import cv2
import numpy as np
# from msvcrt import getch
import serial
from time import sleep
import math
from timeit import default_timer as timer
import sys

# own files
# from ai_lib.line_partition import detect_3_partition

# Params ####################################################################3
morph_kernel = np.ones((7,7),np.uint8)
GREEN_COLOR = (0, 255, 128)
BLUE_COLOR = (255, 0, 0)

#print settings
boxsize, baseline = cv2.getTextSize('Test text', cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
text_height = boxsize[1]

#image draw:
ANNOTATE_MIN_SURFACE = 1000  # mnimal surface to draw detection contour on

# Functions #############################################################

class RedHue():
    def __init__(self):
        # red color hsv boundarie. Red color is across 180 hue 
        self.hue_across_180 = True
        self.ll = np.array([0, 80, 0], dtype = "uint8")
        self.lh = np.array([5, 255, 255], dtype = "uint8")
        self.ul = np.array([165, 80, 0], dtype = "uint8")
        self.uh = np.array([179, 255, 255], dtype = "uint8")

red_hue_params = RedHue()

#Encapsulate the robot webcam IO:
class CameraIO ():
    def __init__(self, port = 0):
        self.cam = cv2.VideoCapture(port)

    #Returns ret_val,image
    def read(self):
        return self.cam.read()
    
    def __del__(self):
        self.cam.release()

def cv2_simple_putText(img, text, xpos, ypos):
    cv2.putText(img, text, (xpos, ypos), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN_COLOR, 2) 

# Detect max contour corresponding to a given color:
# Returns contour_Detected, img  (with contour details drawn)
def detect_hue_max_contour(hsv_img_,hue_params,transform_argument):
    print('detect_hue_max_contour')
    # perform red color detection        
    lower_hue_range = cv2.inRange(hsv_img_, hue_params.ll, hue_params.lh)
    if hue_params.hue_across_180:
        upper_hue_range = cv2.inRange(hsv_img_, hue_params.ul, hue_params.uh)
        detected_hue = np.maximum(lower_hue_range, upper_hue_range)
    else:
        detected_hue = lower_hue_range

    # Apply morphological transformation to diferentiate better the detected object            
    hue_transform = cv2.morphologyEx(detected_hue, transform_argument, morph_kernel)        
    # get contours
    img_c, contours, hierarchy = cv2.findContours(hue_transform, 
                                                  cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours):
        contour = max(contours, key=cv2.contourArea)
        return True, contour, detected_hue
    else:
        return False, 0, detected_hue

# returns the detected contour's center and coordinates: Draws info on the passed image
def get_contour_info(img_, contour, annotate_img, annotate_min_surface):
    print('get_contour_info')
    # mark the object center and the coordinates
    Mclose = cv2.moments(contour)
    surface = int(Mclose["m00"])
    x_center = int (Mclose["m10"] / Mclose["m00"])
    y_center = int (Mclose["m01"] / Mclose["m00"])

    if annotate_img and (surface >= annotate_min_surface):
        cv2.circle(img_,(x_center,y_center), 50, GREEN_COLOR, 3)
        coordinates = '%d, %d' % (x_center,y_center)
        str_surface = '%s' % surface
        cv2_simple_putText(img_, coordinates, 10, 10 + text_height)
        cv2_simple_putText(img_, str_surface, 10, 10 + 3*text_height)        
        cv2.drawContours(img_, [contour], 0, BLUE_COLOR, 3)

    return x_center, y_center, surface

# Return surface and cam coordinates of the detected hue:
def get_hue_center(img_,hue_params_, annotate_img, annotate_min_surface, transform_argument_='open'):
    print('get_hue_center')
    if transform_argument_ == 'open':
        transform_argument_ = cv2.MORPH_OPEN
    else:
        transform_argument_ = cv2.MORPH_CLOSE

    hsv_img = cv2.cvtColor(img_, cv2.COLOR_BGR2HSV)
    # Detect max contour for a given hue
    detected_contour, contour, detected_hue = \
        detect_hue_max_contour(hsv_img,hue_params_,transform_argument_)
     
    if detected_contour:
        x_cam, y_cam, surface = \
            get_contour_info(img_, contour, annotate_img, ANNOTATE_MIN_SURFACE)            
        return surface, x_cam, y_cam
    else:
        return 0,0,0  # 0 surface means no object detected

# Main ####################################################################

mirror = False
cameraIO_ = CameraIO()

while True:
    ret_val, img_ = cameraIO_.read()
    if not ret_val:
        continue
    if mirror: 
        img_ = cv2.flip(img_, 1)
    surface, x_cam, y_cam = \
        get_hue_center(img_, red_hue_params, True, ANNOTATE_MIN_SURFACE, 'open')

    
    # cv2.imshow('Hue match',detected_hue)
    cv2.imshow('Detection',img_)
    if cv2.waitKey(1) == 27: 
        cv2.destroyAllWindows()
        # cv2.destroyWindow('my webcam')
        cameraIO_.__del__()
        break  # esc to quit

    