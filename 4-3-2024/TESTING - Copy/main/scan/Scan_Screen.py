from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
from threading import Thread, Lock
from queue import Queue
from ultralytics import YOLO
import numpy as np

class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'scan_screen'
        self.camera_ip = 'rtsp://192.168.1.101:8080/h264_ulaw.sdp'  # Default IP address

        # Load YOLOv8 models
        model_path_disease = "C:/Users/Dell/OneDrive/Desktop/Main FYP/Aqua4-24/4-3-2024/disease_trained_yolov8.pt"
        model_path_default = "C:/Users/Dell/OneDrive/Desktop/Main FYP/Aqua4-24/4-3-2024/yolov8_best.pt"
        self.model_disease = YOLO(model_path_disease)
        self.model_default = YOLO(model_path_default)

        # Get class names from the models
        self.class_names_disease = self.model_disease.names
        self.class_names_default = self.model_default.names

        # Adding Image widget with full size
        self.image_widget = Image()
        self.add_widget(self.image_widget)

        # Adding back button
        back_button = Button(background_normal="backButton.png", size_hint=(None, None), size=(100, 40), pos_hint={'x': 0, 'y': 0})
        back_button.bind(on_press=self.go_back)
        self.add_widget(back_button)

        # Queue for storing frames
        self.frame_queue = Queue(maxsize=10)
        self.processed_frame_queue = Queue(maxsize=10)

        # Lock for thread synchronization
        self.lock = Lock()

    def on_enter(self):
        # Start capturing frames from the video stream when the screen is entered
        print("Starting video stream...")
        self.cap = cv2.VideoCapture(self.camera_ip)
        if not self.cap.isOpened():
            print("Error: Cannot open video stream")

        # Start threads for capturing and processing frames
        self.capture_thread = Thread(target=self.capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()

        self.process_thread = Thread(target=self.process_frames)
        self.process_thread.daemon = True
        self.process_thread.start()

        # Schedule frame updates
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)  # Update frame every 1/30th of a second

    def capture_frames(self):
        while True:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                continue
            frame = cv2.resize(frame, (640, 480))
            with self.lock:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
                else:
                    # Skip frames if the queue is full to reduce lag
                    self.frame_queue.get()
                    self.frame_queue.put(frame)

    def process_frames(self):
        while True:
            with self.lock:
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                else:
                    continue

            results_default = self.model_default(frame)

            for detection in results_default[0].boxes:
                label = int(detection.cls)
                conf = float(detection.conf)
                box = detection.xyxy.cpu().numpy().astype(int)[0]
                x1, y1, x2, y2 = box
                fish_roi = frame[y1:y2, x1:x2]  # Crop the fish region

                results_disease = self.model_disease(fish_roi)

                # Process detection results for disease model within the fish ROI
                for disease_detection in results_disease[0].boxes:
                    disease_label = int(disease_detection.cls)
                    disease_conf = float(disease_detection.conf)
                    disease_box = disease_detection.xyxy.cpu().numpy().astype(int)[0]
                    dx1, dy1, dx2, dy2 = disease_box
                    # Adjust coordinates to the original frame
                    cv2.rectangle(frame, (x1 + dx1, y1 + dy1), (x1 + dx2, y1 + dy2), (0, 255, 0), 2)
                    disease_class_name = self.class_names_disease.get(disease_label, "Unknown")
                    cv2.putText(frame, f'{disease_class_name} {disease_conf:.2f}', (x1 + dx1, y1 + dy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Draw the fish bounding box on the original frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                class_name = self.class_names_default.get(label, "Unknown")
                cv2.putText(frame, f'{class_name} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            with self.lock:
                if not self.processed_frame_queue.full():
                    self.processed_frame_queue.put(frame)
                else:
                    # Skip frames if the queue is full to reduce lag
                    self.processed_frame_queue.get()
                    self.processed_frame_queue.put(frame)

    def update_frame(self, dt):
        with self.lock:
            if not self.processed_frame_queue.empty():
                frame = self.processed_frame_queue.get()
            else:
                return

        window_size = self.image_widget.size
        resized = cv2.resize(frame, (int(window_size[0]), int(window_size[1])))

        buf = cv2.flip(resized, 0).tobytes()
        texture = Texture.create(size=(resized.shape[1], resized.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

        self.image_widget.texture = texture

    def on_leave(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def go_back(self, instance):
        self.running = False  # Set the flag to False to stop the threads
        self.cap.release()
        cv2.destroyAllWindows()
        self.manager.current = 'home_screen'