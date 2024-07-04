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

class AddTankScreen(Screen):
    last_assigned_tank_id = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'add_tank_screen'
        self.add_widget(Image(source="home_image.jpg", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))

        # MongoDB setup
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client['login_page']
        self.collection = self.db['Addition_page']

        # User-specific data (you need to set this when the user logs in)
        self.username = 'ali'

        # Use FloatLayout to position elements precisely
        float_layout = FloatLayout()
        self.add_widget(float_layout)

        # Outer BoxLayout to center everything
        self.center_layout = BoxLayout(orientation='vertical', size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        float_layout.add_widget(self.center_layout)

        # Add a back button at the top left corner
        back_button = Button(
            background_normal="backButton.png",
            size_hint=(None, None),
            size=(100, 40),
            pos_hint={'x': 0.04, 'y': 0.03},
            on_press=self.go_back
        )
        float_layout.add_widget(back_button)

        # Add a BoxLayout to hold text input fields dynamically
        self.text_input_layout = BoxLayout(orientation='vertical', spacing=15)
        self.center_layout.add_widget(self.text_input_layout)

        # Generate initial Tank ID
        initial_tank_id = self.generate_tank_id()

        # Add text input for Tank Name
        self.tank_name_input = self.add_text_input("Tank Name")  # Read-only Tank ID

        # Add text label for Tank ID
        self.tank_id_label = TextInput(text=initial_tank_id, multiline=False, readonly=True, size_hint=(None, None), size=(150, 30))
        self.add_text_input_field("Tank ID", self.tank_id_label)

        # Add text inputs for Tank Size and Number of Fishes
        self.tank_size_input = self.add_text_input("Tank Size")
        self.num_fishes_input = self.add_text_input("Number of Fishes")

        # Add a button to choose a file
        self.add_file_chooser()

        # Add an empty widget for spacing
        self.center_layout.add_widget(Label(size_hint_y=None, height=20))

        # Add a submit button
        submit_button = MDRaisedButton(
            text='Submit',
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'center_x': 0.5},
            on_press=self.submit_form
        )
        self.center_layout.add_widget(submit_button)

    def add_text_input(self, label_text, default_text='', readonly=False):
        # Helper method to add a new text input field
        box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(None, None), size=(400, 40))
        label = Label(text=label_text, color=(0, 0, 0, 1), size_hint=(None, None), size=(150, 40), halign='right', valign='middle')
        label.bind(size=label.setter('text_size'))  # Bind the label size to text_size to make text wrap properly
        text_input = TextInput(
            text=default_text,
            multiline=False,
            size_hint=(None, None),
            size=(150, 30),
            readonly=readonly
        )
        box.add_widget(label)
        box.add_widget(text_input)
        self.text_input_layout.add_widget(box)
        return text_input

    def add_text_input_field(self, label_text, text_input):
        # Helper method to add a new text input field with an existing TextInput
        box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(None, None), size=(400, 40))
        label = Label(text=label_text, color=(0, 0, 0, 1), size_hint=(None, None), size=(150, 40), halign='right', valign='middle')
        label.bind(size=label.setter('text_size'))  # Bind the label size to text_size to make text wrap properly
        box.add_widget(label)
        box.add_widget(text_input)
        self.text_input_layout.add_widget(box)

    def add_file_chooser(self):
        # Add a button to open file chooser
        file_chooser_button = MDRaisedButton(
            text='Choose File',
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'center_x': 0.5},
            on_press=self.open_file_chooser
        )
        self.file_path_label = Label(text='No file chosen', color=(0, 0, 0, 1), size_hint=(None, None), size=(200, 40), pos_hint={'center_x': 0.5})
        
        self.text_input_layout.add_widget(file_chooser_button)
        self.text_input_layout.add_widget(self.file_path_label)

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
        # Generate a unique Tank ID by incrementing the last assigned Tank ID
        AddTankScreen.last_assigned_tank_id += 1
        tank_id = f"{AddTankScreen.last_assigned_tank_id:03}"
        return tank_id

    def submit_form(self, instance):
        # Access entered data from each text input field in the layout
        tank_data = {
            "username": self.username,
            "tank_id": self.tank_id_label.text,
            "tank_name": self.tank_name_input.text,
            "tank_size": self.tank_size_input.text,
            "num_fishes": self.num_fishes_input.text,
            "image_path": self.file_path_label.text
        }

        # Save to MongoDB
        self.collection.insert_one(tank_data)

        # Pass the data to the HomeScreen and switch to it
        self.manager.get_screen('home_screen').add_tank_widget(tank_data)
        self.manager.current = 'home_screen'

        # Generate a new Tank ID for the next entry
        self.tank_id_label.text = self.generate_tank_id()

    def go_back(self, instance):
        self.manager.current = 'home_screen'
