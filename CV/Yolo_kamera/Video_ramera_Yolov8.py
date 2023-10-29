# Importing libraries
from ultralytics import YOLO 
import cv2

# load model
model = YOLO("yolov8m.pt")

# video,  kamera 0
cap = cv2. VideoCapture(0)
# cap = cv2. VideoCapture('video.mp4')
cap.set(3, 640) # width
cap.set(4, 480) # height

# codec and create VideoWriter object
# fourcc = cv2.VideoWriter_fourcc(*'MJPG')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('video_Yolo.avi', fourcc, 20.0, (640, 480))


while True:
    # Capture frame-by-frame
    cuccess, img = cap.read()      
    results = model(img, save=True)
    result = results[0]     

    # parse result
    for box in result.boxes:
        
        # rectangle on image
        cords = box.xyxy[0].tolist()
        cords = [int(x) for x in cords]    
        x1, y1, x2, y2 =  cords
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

        # confidence 
        conf = round(box.conf[0].item(), 2)        
        print("Confidence --->", conf)

        # class name
        class_id = result.names[box.cls[0].item()]
        print("Class name -->", class_id)
       
        # text on image
        org = [x1, y1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (0, 255, 0)
        thickness = 2
        cv2.putText(img, class_id + ' ' + str(conf), org, font, fontScale, color, thickness)

        # write avi-video
        out.write(img) 

    # Display the resulting frame
    cv2.imshow('Camera', img)

    if cv2.waitKey(10) == ord('q'):
        break

# When everything done, release the capture
cap.release() 
out.release()
cv2.destroyAllWindows()