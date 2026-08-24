import cv2
import numpy as np
import os

try:
    from ultralytics import YOLO
except ImportError:
    print("WARNING: ultralytics not found. Please install it.")
    YOLO = None

# Load the local YOLOv8 model
yolo_checkpoint = r"D:\projects\New_ML_Project\yolov8n.pt"

model = None
if YOLO and os.path.exists(yolo_checkpoint):
    try:
        model = YOLO(yolo_checkpoint)
        print("YOLOv8 Model Loaded Successfully!")
    except Exception as e:
        print(f"Error loading YOLOv8: {e}")
        model = None

# YOLOv8 class IDs for vehicles: 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
VEHICLE_CLASSES = {2, 3, 5, 7}

class TrafficCamera:
    def __init__(self, name):
        self.name = name
        self.current_count = 0
        self.latest_frame = None
        self.reset()
        
    def reset(self):
        self.current_count = 0
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "Waiting for upload...", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        self.latest_frame = frame
        
    def process_image(self, image_bytes):
        """Processes an uploaded image byte array using YOLOv8."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return 0, self.latest_frame

        # Resize for consistent rapid processing
        frame = cv2.resize(frame, (640, 480))
        
        count = 0
        if model is not None:
            try:
                # Run YOLOv8 prediction
                results = model.predict(frame, conf=0.25, verbose=False)
                
                # Filter for vehicles and draw bounding boxes
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        if cls_id in VEHICLE_CLASSES:
                            count += 1
                            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            
            except Exception as e:
                print(f"ERROR inside YOLO prediction: {e}")
                count = 0
        else:
            print("WARNING: YOLO model unavailable.")
            count = 0
            
        self.current_count = int(count)
        
        # Add road name & count overlay on image
        cv2.putText(frame, f"{self.name} - Detected: {count}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
        self.latest_frame = frame
        return self.current_count, self.latest_frame

    def get_count(self):
        return self.current_count
        
    def get_frame(self):
        return self.latest_frame

# Initialize 4 cameras to hold states
cameras = {
    "South": TrafficCamera("South"),
    "North": TrafficCamera("North"),
    "West": TrafficCamera("West"),
    "East": TrafficCamera("East")
}