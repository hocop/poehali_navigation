import numpy as np
import cv2
from math import *
import requests
import time

# parameters
#################################################################
# for Ruslan's computer
camName = 'right'
camTgFiMax = 0.661
camTgThMax = 0.372

# for Colya's computer
#camName = 'left'
#camTgFiMax = 0.641
#camTgThMax = 0.360

serAddr = 'http://127.0.0.1:5000/cord'

minArea = 25 # minimum pixels seen to send info

view = True
scaling = 1.0
erosion = 3
threshold = 4
#################################################################

count = 0

def compAngles(x, y):
	return (x/camTgFiMax*0.5, -(y-1.0)/camTgThMax*0.5)

def sendAngles(tgFi, tgTh):
	try:
		requests.post(serAddr, data={'tgFi':tgFi, 'tgTh':tgTh, 'cam':camName}, timeout = 0.03)
	except requests.exceptions.ConnectTimeout:
		global count
		print 'no response', count
		count += 1

def getFrame():
	ret, frame = cap.read()
	frame = cv2.resize(frame, None, fx=scaling, fy=scaling)
	return frame

# start
cap = cv2.VideoCapture(0)
old_frame = getFrame()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
hsv = np.zeros_like(old_frame)
hsv[...,1] = 255

# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)

while(True):
	# Time measure
	start = time.time()
	
	# Capture frame-by-frame
	frame = getFrame()
	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
	# calculate optical changes
	mag = cv2.absdiff(frame_gray, old_gray)
	
	# mask
	ret,mask = cv2.threshold(mag,threshold,255,cv2.THRESH_BINARY)
	mask = cv2.erode(mask, None, iterations=erosion)
	mask = cv2.dilate(mask, None, iterations=erosion)
	
	# Moments
	M = cv2.moments(mask)
	area = M['m00']/255.0 #num of pixels seen
	#mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
	if area > minArea:
		cx = int(M['m10'] / (M['m00']+1))
		cy = int(M['m01'] / (M['m00']+1))
		cr = int(sqrt(area/pi))
		cv2.circle(frame, (cx,cy), cr, (0,255,0), 5)
		
		# Send info
		height, width = mask.shape
		x = (2*cx - width) / float(width)
		y = (2*cy - height) / float(height)
		tgFi, tgTh = compAngles(x, y)
		sendAngles(tgFi, tgTh) #============TO=COPTER==========>>>>>>>>>
	
	# Display the resulting frame
	if view:
		cv2.imshow('frame', frame)
		cv2.imshow('mask', mask)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
	
	# Update previous frame
	old_gray = frame_gray.copy()
	
	# Time
	end = time.time()
	#print end - start


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
