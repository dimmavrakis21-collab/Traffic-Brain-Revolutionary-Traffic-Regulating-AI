# Code based on: https://medium.com/@amit25173/opencv-vehicle-detection-8fa8dfcd8458
# The  model is a machine learning model for object detection. It finds objects on a picture,
# and returns the probability of that object belonging to one of the classes that it knows (e.g. Human, Car, etc), and
# also returns a "bounding box", i.e. the (x, y, width, height) of the box around the object

import cv2
import numpy as np

# Load image from disk
image = cv2.imread('C:\\Users\markz\Downloads\cars-3819225_1280.jpg')
height, width = image.shape[:2]

# Load YOLO from disk
net = cv2.dnn.readNet("C:\\Users\markz\Downloads\yolov4-p5.weights", "C:\\Users\markz\Downloads\yolov4-p5.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Send the image to YOLO and get the outputs
blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
net.setInput(blob)
outs = net.forward(output_layers)

# YOLO produces three groups of outputs, so "outs" is a list with three different groups of detections. This is necessary
# for YOLO to detect objects of different scales (small, medium, large). But we don't care, we will go through all of them
# and select the cars
cars=[]
for out in outs:
    # Each "out" is a list of detections, one for each object it found
    for detection in out:
        #Each "detection" has 85 values: 4 coordinates for the bounding box, 1 confidence value for the detection, and
        # 80 probability scores, one for each class of object. We keep the 80 probabilities in the "scores" list
        # This is the list of classes for YOLO ("Car" is 2): https://gist.github.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8
        scores = detection[5:]
        # We keep the class with the highest probability in "class_id".
        class_id = int(scores.argmax())
        class_prob = scores[class_id]
        # If it has a high probability of being a car, keep the coordinates of the box in "cars"
        if class_prob > 0.5 and class_id==2:
            cars.append(detection[0:4])

# The problem with YOLO in OpenCV is that it returns multiple overlapping boxes for each object, with only a few pixels
# difference from each other. Let's show it:
# (This code draws the bounding boxes and waits for you to press Enter. You can delete it for your application.)
CarsWithBoxes=image.copy()
for car in cars:
    center_x = int(car[0] * width)
    center_y = int(car[1] * height)
    w = int(car[2] * width)
    h = int(car[3] * height)
    x = center_x - w // 2
    y = center_y - h // 2
    cv2.rectangle(CarsWithBoxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
cv2.imshow('YOLO Vehicle Detection', CarsWithBoxes)
cv2.waitKey(0)

#This value is the limit of overlap for throwing away extra boxes. The lower it is, the more boxes we throw away.
overlapThresh=0.96


#______________________________________________________________________________________________
# ------This code is a bit complicated. Don't worry if you don't understand it, it works--------
# (If you understand it congratulations, you are really good at Python!)
# We are going to detect overlapping boxes and remove them using this code: https://pyimagesearch.com/2014/11/17/non-maximum-suppression-object-detection-python/
def non_max_suppression_slow(boxes, overlapThresh):
    boxes = np.array(boxes)
    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return []
    # initialize the list of picked indexes
    pick = []
    # grab the coordinates of the bounding boxes
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]
    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # keep looping while some indexes still remain in the indexes list
    while len(idxs) > 0:
        # grab the last index in the indexes list, add the index
        # value to the list of picked indexes, then initialize
        # the suppression list (i.e. indexes that will be deleted)
        # using the last index
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        suppress = [last]
        # loop over all indexes in the indexes list
        for pos in range(0, last):
            # grab the current index
            j = idxs[pos]
            # find the largest (x, y) coordinates for the start of
            # the bounding box and the smallest (x, y) coordinates
            # for the end of the bounding box
            xx1 = max(x1[i], x1[j])
            yy1 = max(y1[i], y1[j])
            xx2 = min(x2[i], x2[j])
            yy2 = min(y2[i], y2[j])
            # compute the width and height of the bounding box
            w = max(0, xx2 - xx1 + 1)
            h = max(0, yy2 - yy1 + 1)
            # compute the ratio of overlap between the computed
            # bounding box and the bounding box in the area list
            overlap = float(w * h) / area[j]
            # if there is sufficient overlap, suppress the
            # current bounding box
            if overlap > overlapThresh:
                suppress.append(pos)
        # delete all indexes from the index list that are in the
        # suppression list
        idxs = np.delete(idxs, suppress)
    # return only the bounding boxes that were picked
    return boxes[pick]

cars2 = non_max_suppression_slow(cars,overlapThresh)
#------End of complicated code------
#______________________________________________________________________________________________



#Now we have thrown away the overlapping boxes. How many boxes did we keep?
numberOfCars = cars2.shape[0]
print("We have detected " + str(numberOfCars) + " cars.")


# This code draws the remaining boxes and waits for you to press Enter. You can delete it for your application.
CarsWithClearedBoxes=image.copy()
for car in cars2:
    center_x = int(car[0] * width)
    center_y = int(car[1] * height)
    w = int(car[2] * width)
    h = int(car[3] * height)
    x = center_x - w // 2
    y = center_y - h // 2
    cv2.rectangle(CarsWithClearedBoxes, (x, y), (x + w, y + h), (0, 255, 0), 2)
cv2.imshow('YOLO Vehicle Detection2', CarsWithClearedBoxes)
cv2.waitKey(0)
cv2.destroyAllWindows()

