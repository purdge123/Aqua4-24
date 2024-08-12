from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
from threading import Thread, Event, Lock
from queue import Queue
from ultralytics import YOLO
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
import logging
from kivy.metrics import dp
import time
from kivy.uix.widget import Widget

# Set up logging
logging.basicConfig(level=logging.INFO)

class ScanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'scan_screen'
        self.camera_ip = 'rtsp://192.168.100.6:8080/h264_ulaw.sdp'  # Default IP address

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
        back_button = Button(background_normal="media/report.png", size_hint=(None, None), size=(100, 40), pos_hint={'x': 0, 'y': 0})
        back_button.bind(on_press=self.go_back)
        self.add_widget(back_button)

        # Queue for storing frames
        self.frame_queue = Queue(maxsize=10)
        self.processed_frame_queue = Queue(maxsize=10)

        # Lock for thread synchronization
        self.lock = Lock()

        # List to store detected diseases and screenshots
        self.detected_diseases = []

        # Flag to signal threads to stop
        self.stop_event = Event()

    def on_enter(self):
        logging.info("Starting video stream...")
        self.start_video_stream()

        # Start threads for capturing and processing frames
        self.capture_thread = Thread(target=self.capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()

        self.process_thread = Thread(target=self.process_frames)
        self.process_thread.daemon = True
        self.process_thread.start()

        # Schedule frame updates
        Clock.schedule_interval(self.update_frame, 1.0 / 30.0)  # Update frame every 1/30th of a second

    def start_video_stream(self):
        # Release existing capture if it exists
        if hasattr(self, 'cap') and self.cap.isOpened():
            logging.info("Releasing existing video capture...")
            self.cap.release()
            self.cap = None

        cv2.destroyAllWindows()

        # Clear queues
        with self.lock:
            self.frame_queue.queue.clear()
            self.processed_frame_queue.queue.clear()

        # Attempt to start the video stream with retries
        retry_count = 5
        for _ in range(retry_count):
            self.cap = cv2.VideoCapture(self.camera_ip)
            if self.cap.isOpened():
                logging.info("Video stream started successfully.")
                return
            logging.warning("Failed to open video stream. Retrying...")
            time.sleep(1)  # Wait before retrying

        logging.error("Error: Cannot open video stream after retries.")

    def capture_frames(self):
        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret or frame is None:
                continue
            frame = cv2.resize(frame, (640, 480))
            with self.lock:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
                else:
                    self.frame_queue.get()
                    self.frame_queue.put(frame)

    def process_frames(self):
        while not self.stop_event.is_set():
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

                for disease_detection in results_disease[0].boxes:
                    disease_label = int(disease_detection.cls)
                    disease_conf = float(disease_detection.conf)
                    disease_box = disease_detection.xyxy.cpu().numpy().astype(int)[0]
                    dx1, dy1, dx2, dy2 = disease_box
                    cv2.rectangle(frame, (x1 + dx1, y1 + dy1), (x1 + dx2, y1 + dy2), (0, 255, 0), 2)
                    disease_class_name = self.class_names_disease.get(disease_label, "Unknown")
                    cv2.putText(frame, f'{disease_class_name} {disease_conf:.2f}', (x1 + dx1, y1 + dy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Save the screenshot
                    screenshot_path = f'screenshot_{label}_{disease_label}.png'
                    cv2.imwrite(screenshot_path, fish_roi)

                    # Store the disease information along with the fish name
                    fish_class_name = self.class_names_default.get(label, "Unknown")
                    self.detected_diseases.append({
                        "image": screenshot_path,
                        "fish_name": fish_class_name,
                        "name": disease_class_name,
                        "cure": "Cure information here"  # Replace with actual cure data
                    })

                # Draw the fish bounding box on the original frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                class_name = self.class_names_default.get(label, "Unknown")
                cv2.putText(frame, f'{class_name} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            with self.lock:
                if not self.processed_frame_queue.full():
                    self.processed_frame_queue.put(frame)
                else:
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

    def go_back(self, instance):
        logging.info("Stopping threads and releasing resources...")
        self.stop_event.set()
        self.capture_thread.join()
        self.process_thread.join()
        if hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()
        self.manager.current = 'home_screen'
        self.generate_report()

    def generate_report(self):
        # Create a layout for the popup
        box_layout = BoxLayout(orientation='vertical', spacing=dp(50), padding=dp(10), size_hint_y=None)
        box_layout.bind(minimum_height=box_layout.setter('height'))

        if not self.detected_diseases:
            no_data_label = Label(text="No diseases detected.", size_hint_y=None, height=dp(30))
            box_layout.add_widget(no_data_label)
        else:
            for disease in self.detected_diseases:
                # Create a vertical BoxLayout to organize the elements
                disease_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180))

                # Add image of the disease
                img = Image(source=disease["image"], size_hint=(None, None), size=(dp(40), dp(100)),
                            pos_hint={'center_x': 0.5})
                disease_layout.add_widget(img)

                # Add fish name
                label_fish_name = Label(text=f"Fish Name: {disease['fish_name']}", size_hint_y=None, height=dp(30),
                                        halign='center')
                label_fish_name.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
                disease_layout.add_widget(label_fish_name)

                # Add disease name
                label_name = Label(text=f"Disease Name: {disease['name']}", size_hint_y=None, height=dp(30),
                                halign='center')
                label_name.bind(size=lambda s, w: s.setter('text_size')(s, (s.width, None)))
                disease_layout.add_widget(label_name)

                # Add cure information with text wrapping
                cure_text = self.get_cure_text(disease['name'])
                label_cure = Label(text=f"Cure: {cure_text}", size_hint_y=None,
                                text_size=(dp(200), None),  # Adjust the width to match the popup width
                                halign='center', valign='middle')
                label_cure.bind(size=lambda s, w: s.setter('height')(s, s.texture_size[1]))
                disease_layout.add_widget(label_cure)

                # Add the disease layout to the box layout
                box_layout.add_widget(disease_layout)

        # Add ScrollView to the layout
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(box_layout)

        # Create a button to close the popup
        close_button = Button(text="Close", size_hint=(None, None), size=(dp(70), dp(30)))
        close_button.bind(on_press=lambda instance: self.popup.dismiss())

        # Add button to the layout
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=dp(10))
        button_layout.add_widget(close_button)
        box_layout.add_widget(button_layout)

        # Show the report in a popup
        self.popup = Popup(title="Disease Report", content=scroll_view, size_hint=(0.9, 0.9))
        self.popup.open()


            
    def get_cure_text(self, disease_name):
        # Placeholder for the actual cure information
        # Replace this function with your logic to retrieve the actual cure information
        cures = {
            "EUS": "Treat with potassium permanganate bath (2-4 ppm) and antibiotics like oxytetracycline.",
            "Rotten gills": "Improve water quality, perform water changes, and treat with formalin or potassium permanganate.",
            "Fin rot": "Treat with antibiotics like tetracycline or chloramphenicol, and improve water conditions.",
            "Eye disease": "Isolate the affected fish, maintain good water quality, and treat with antibiotic eye drops.",
            "Fin lesions": "Clean the wound and treat with antiseptic or antibiotic ointment. Ensure proper water conditions."
        }

        return cures.get(disease_name, "Cure information not available")








