from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
from threading import Thread
from queue import Queue
from ultralytics import YOLO

class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'scan_screen'

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
        back_button = Button(text='Back', size_hint=(None, None), size=(120, 40), pos_hint={'x': 0, 'y': 0})
        back_button.bind(on_press=self.go_back)
        self.add_widget(back_button)

        # Queue for storing frames
        self.frame_queue = Queue(maxsize=10)

    def on_enter(self):
        # Start capturing frames from the video stream when the screen is entered
        print("Starting video stream...")
        self.cap = cv2.VideoCapture('http://192.168.100.89:8080/video')
        if not self.cap.isOpened():
            print("Error: Cannot open video stream")
        # Start a separate thread for capturing frames
        self.capture_thread = Thread(target=self.capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        # Schedule frame updates
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)  # Update frame every 1/30th of a second

    def capture_frames(self):
        while True:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                continue
            # Resize frame to reduce processing load
            frame = cv2.resize(frame, (640, 480))
            if not self.frame_queue.full():
                self.frame_queue.put(frame)

    def update_frame(self, dt):
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()
            # Perform inference with both models
            results_disease = self.model_disease(frame)
            results_default = self.model_default(frame)

            # Process detection results for disease model
            for detection in results_disease[0].boxes:
                label = int(detection.cls)
                conf = float(detection.conf)
                box = detection.xyxy.cpu().numpy().astype(int)[0]
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                class_name = self.class_names_disease.get(label, "Unknown")
                cv2.putText(frame, f'{class_name} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Process detection results for default model
            for detection in results_default[0].boxes:
                label = int(detection.cls)
                conf = float(detection.conf)
                box = detection.xyxy.cpu().numpy().astype(int)[0]
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                class_name = self.class_names_default.get(label, "Unknown")
                cv2.putText(frame, f'{class_name} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Resize frame to fit the screen size
            window_size = self.image_widget.size
            resized = cv2.resize(frame, (int(window_size[0]), int(window_size[1])))

            # Convert frame to texture
            buf = cv2.flip(resized, 0).tobytes()
            texture = Texture.create(size=(resized.shape[1], resized.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

            # Update image texture
            self.image_widget.texture = texture

    def on_leave(self):
        # Stop the video stream when leaving the screen
        self.cap.release()
        cv2.destroyAllWindows()

    def go_back(self, instance):
        # Stop the video stream
        self.cap.release()
        cv2.destroyAllWindows()
        # Go back to the home screen
        self.manager.current = 'home_screen'
