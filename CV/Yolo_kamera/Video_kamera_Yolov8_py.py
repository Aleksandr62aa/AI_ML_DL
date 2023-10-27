# Setup YOLO using Python
from ultralytics import YOLO

# load model
model = YOLO("yolov8m.pt")

# predict model, video camera "0"
results = model.predict(source='0', show=True)