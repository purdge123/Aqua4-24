from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDRaisedButton
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class AddTankScreen(Screen):
    def __init__(self, username=None, **kwargs):
        super().__init__(**kwargs)
        self.name = 'add_tank_screen'
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client['login_page']
        self.collection = self.db['Addition_page']
        self.username = username  # Set username dynamically during login
        self.default_image_path = "default_image.png"  # Define the default image path

        self.setup_ui()

    def setup_ui(self):
        self.add_widget(Image(source="home_image.jpg", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))

        float_layout = FloatLayout()
        self.add_widget(float_layout)

        # Center Layout
        self.center_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(400, 500), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        float_layout.add_widget(self.center_layout)

        # Back Button
        back_button = Button(background_normal="backButton.png", size_hint=(None, None), size=(100, 40), pos_hint={'x': 0.04, 'y': 0.03}, on_press=self.go_back)
        float_layout.add_widget(back_button)

        # Input Fields
        self.text_input_layout = BoxLayout(orientation='vertical', spacing=15)
        self.center_layout.add_widget(self.text_input_layout)

        self.tank_id_label = self.create_text_input("Tank ID", self.generate_tank_id(), readonly=True)
        self.tank_name_input = self.create_text_input("Tank Name")
        self.tank_size_input = self.create_text_input("Tank Size")
        self.num_fishes_input = self.create_text_input("Number of Fishes")
        self.camera_ip_input = self.create_text_input("Camera IP Address")  # New field

        # File Chooser
        self.file_path_label = Label(text='No file chosen', color=(0, 0, 0, 1), size_hint=(None, None), size=(200, 40), pos_hint={'center_x': 0.5})
        file_chooser_button = MDRaisedButton(text='Choose File', size_hint=(None, None), size=(200, 40), pos_hint={'center_x': 0.5}, on_press=self.open_file_chooser)
        self.text_input_layout.add_widget(file_chooser_button)
        self.text_input_layout.add_widget(self.file_path_label)

        # Submit Button
        submit_button = MDRaisedButton(text='Submit', size_hint=(None, None), size=(200, 40), pos_hint={'center_x': 0.5}, on_press=self.submit_form)
        self.center_layout.add_widget(submit_button)

    def create_text_input(self, label_text, default_text='', readonly=False):
        # Create a text input field with a label
        box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(None, None), size=(400, 40))
        label = Label(text=label_text, color=(0, 0, 0, 1), size_hint=(None, None), size=(150, 40))
        text_input = TextInput(text=default_text, multiline=False, size_hint=(None, None), size=(150, 30), readonly=readonly)
        box.add_widget(label)
        box.add_widget(text_input)
        self.text_input_layout.add_widget(box)
        return text_input

    def open_file_chooser(self, instance):
        # Open a file chooser dialog
        file_chooser = FileChooserIconView(filters=['*.png', '*.jpg'], size_hint=(1, 1))
        popup = Popup(title='Choose an image file', content=file_chooser, size_hint=(0.9, 0.9))
        file_chooser.bind(on_submit=self.file_selected)
        self.popup = popup
        popup.open()

    def file_selected(self, file_chooser, selection, *args):
        # Handle file selection
        if selection:
            self.file_path_label.text = selection[0]
        self.popup.dismiss()

    def generate_tank_id(self):
        # Generate a unique Tank ID
        try:
            last_tank = self.collection.find_one(sort=[("tank_id", -1)])
            last_id = int(last_tank["tank_id"]) if last_tank else 0
            return f"{last_id + 1:03}"
        except PyMongoError as e:
            print(f"MongoDB Error: {e}")
            return "001"

    def submit_form(self, instance):
        # Collect and save form data
        image_path = self.file_path_label.text if self.file_path_label.text != 'No file chosen' else self.default_image_path
        
        tank_data = {
            "username": self.username,
            "tank_id": self.tank_id_label.text,
            "tank_name": self.tank_name_input.text,
            "tank_size": self.tank_size_input.text,
            "num_fishes": self.num_fishes_input.text,
            "camera_ip": self.camera_ip_input.text,  # Include the camera IP address
            "image_path": image_path
        }
        try:
            self.collection.insert_one(tank_data)
            home_screen = self.manager.get_screen('home_screen')
            home_screen.add_tank_widget(tank_data)
            self.manager.current = 'home_screen'
            self.tank_id_label.text = self.generate_tank_id()
        except PyMongoError as e:
            print(f"MongoDB Error: {e}")

    def go_back(self, instance):
        self.manager.current = 'home_screen'
