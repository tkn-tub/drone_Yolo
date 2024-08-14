import cv2
from ultralytics import YOLO
import numpy as np

# Load the video capture
cap = cv2.VideoCapture("orange.mp4")

# Initialize the YOLO model
model = YOLO("yolov8m.pt")

def trackFrame(frame):

    # Run YOLOv8 tracking on the frame, persisting tracks between frames
    results = model.track(frame, persist=True ,classes = [49], device = "mps",iou_threshold=0.95)

    result = results[0]

    classes = result.boxes.cls.cpu().numpy()
        
    print("checking if classes really exist",result,classes)

    # Visualize the results on the frame
    annotated_frame = result.plot()
    
    # Return the annotated frame
    return annotated_frame
        


def processFrame(frame):

    # Perform inference using the YOLO model on the frame
    results = model(frame, device="mps")

    
    
    # Counter to determine number of oranges in a single frame 
    count = 0

    # Access the first result (YOLO model may return multiple results for different scales)
    result = results[0]

    # Extract bounding boxes, classes, and confidence scores
    bounding_boxes = result.boxes.xyxy.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy()
    confidences = result.boxes.conf.cpu().numpy()
    
    # Iterate over detected objects
    for box, class_type, confidence in zip(bounding_boxes, classes, confidences):
        (x1, y1, x2, y2) = box.astype(int)
        if confidence > 0.6  :
            # Draw bounding box and label on the frame
            label = model.names[int(class_type)]
            label_text = f"{label}: {confidence:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # Increment the count of recognised oranges in the frame 
            count +=1


    # Display the annotated frame
    return frame



