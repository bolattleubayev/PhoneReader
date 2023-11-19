import numpy as np
import cv2
import requests
import time
import datetime

vid = cv2.VideoCapture(0)

vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# Load the kNN model
samples = np.loadtxt('generalsamples.data',np.float32)
responses = np.loadtxt('generalresponses.data',np.float32)
responses = responses.reshape((responses.size,1))

model = cv2.ml.KNearest_create()
model.train(samples,cv2.ml.ROW_SAMPLE,responses)

# Constants
kernel = np.ones((5,5),np.uint8)
url = 'https://YOUR-API.herokuapp.com/api/v1/entries'
api_secret = "YOUR-SHA-1-ENCODED-SECRET"
minutes_between_regular_updates = 5

if not vid.isOpened():
    print("Cannot open camera")

# Capture frame-by-frame
ret, frame = vid.read()
# if frame is read correctly ret is True
if not ret:
    print("Can't receive frame (stream end?). Exiting ...")


# Clean image for recognition
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
binary_inverse = cv2.threshold(gray,80,255,cv2.THRESH_BINARY_INV)

thresh = binary_inverse[1]
thresh = cv2.erode(binary_inverse[1],kernel,iterations = 1)
thresh = cv2.dilate(thresh,kernel,iterations = 1)

# Extract contours
_,contours,_ = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

number_location_pairs = []

for cnt in contours:
    if cv2.contourArea(cnt) > 2000:
        [x,y,w,h] = cv2.boundingRect(cnt)
        if x > 120 and x < 560 \
                    and y > 100 and y < 340 \
                    and x+w < 560 and y+h < 340:
            roi = thresh[y:y+h,x:x+w]
            roismall = cv2.resize(roi,(15,15))
            roismall = roismall.reshape((1,225))
            roismall = np.float32(roismall)
            retval, results, neigh_resp, dists = model.findNearest(roismall, k = 1)
            string = str(int((results[0][0])))
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

if num == '.10':
    # print("LOW")
    pass
elif valNum < 2:
    pass
elif float(num) > 30:
    # print("Too high, invalid data")
    pass
elif float(num) < 2:
    # print("Too low, invalid data")
    pass
else:
    # print(num)
    number = int(float(num) * 18)
    dateStr = str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z"))
    timestamp = round(time.time() * 1000)
    
    data = [{
        "type": "sgv",
        "dateString": dateStr,
        "date": timestamp,
        "sgv": number,
        "direction": "Flat",
        "noise": 0,
        "filtered": 0,
        "unfiltered": float(num),
        "rssi": 0
    }]
    headers = {
        "Content-Type": "application/json",
        "api-secret": api_secret
    }
    try:
        x = requests.post(url, json = data, headers=headers)
    except Exception as e:
        print("API connection error: " + str(e))

# When everything done, release the capture
vid.release()
cv2.destroyAllWindows()