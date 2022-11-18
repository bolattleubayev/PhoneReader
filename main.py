# import the opencv library
import cv2
import numpy as np

# define a video capture object
vid = cv2.VideoCapture(1)

samples = np.loadtxt('generalsamples.data',np.float32)
responses = np.loadtxt('generalresponses.data',np.float32)
responses = responses.reshape((responses.size,1))

model = cv2.ml.KNearest_create()
model.train(samples,cv2.ml.ROW_SAMPLE,responses)

while(True):
    
    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # thresh = cv2.adaptiveThreshold(gray,255,1,1,11,2)
    thresh2 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
    thresh = cv2.morphologyEx(thresh2[1], cv2.MORPH_OPEN, (5,5))

    _,contours,_ = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    
    number_location_pairs = []

    for cnt in contours:
        [x,y,w,h] = cv2.boundingRect(cnt)
        if  h > 70 and w > 70:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            roi = thresh[y:y+h,x:x+w]
            roismall = cv2.resize(roi,(10,10))
            roismall = roismall.reshape((1,100))
            roismall = np.float32(roismall)
            retval, results, neigh_resp, dists = model.findNearest(roismall, k = 1)
            string = str(int((results[0][0])))
            cv2.putText(frame,string,(x,y+h),0,1,(0,255,0))
            number_location_pairs.append([string, x])

    # Form a reading
    valNum = len(number_location_pairs)
    # Arrange by x axis
    number_location_pairs = sorted(number_location_pairs,key=lambda l:l[1])
    num = ''
    for i in range(valNum):
        if i == valNum - 1:
            num += '.'
        num += number_location_pairs[i][0]
    print(num)
    # Display the resulting frame
    
    cv2.imshow('frame', thresh)
    # the 'q' button is as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
