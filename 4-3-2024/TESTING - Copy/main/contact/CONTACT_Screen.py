from pymongo import MongoClient
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.slider import Slider
from kivy.metrics import dp
from kivy.uix.popup import Popup

class ContactScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'contact_screen'

        # Set the background image
        with self.canvas.before:
            self.bg_image = Rectangle(source='media/mainBg.jpg', size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Initialize MongoDB connection
        self.client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection string
        self.db = self.client['login_page']  # Replace 'login_page' with your database name
        self.collection = self.db['user_feedback']  # Replace 'user_feedback' with your collection name

        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(10), dp(20)], size_hint=(1, 1))

        # Center logo at the top
        logo_box = BoxLayout(size_hint=(1, None), height=dp(150), padding=[dp(10), dp(10)], orientation='horizontal')
        logo = Image(source='media/logo.png', size_hint=(None, None), size=(dp(150), dp(150)))
        logo_box.add_widget(Widget())  # Spacer widget
        logo_box.add_widget(logo)
        logo_box.add_widget(Widget())  # Spacer widget
        main_layout.add_widget(logo_box)

        # Center feedback input field with heading
        feedback_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(1, None), padding=[dp(20), dp(10)], height=dp(200))
        
        # Feedback heading
        feedback_label = Label(text="Send Feedback", halign='center', color=(0, 0, 0, 1), font_size=dp(14), bold=True, size_hint_y=None, height=dp(40))
        
        # Feedback input field
        self.feedback_input = TextInput(multiline=True, size_hint=(None, None), width=dp(250), height=dp(100), foreground_color=(0, 0, 0, 1), font_size=dp(14))
        
        feedback_box.add_widget(feedback_label)
        feedback_box.add_widget(self.feedback_input)
        main_layout.add_widget(feedback_box)

        # Rating slider and label
        slider_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(1, None), height=dp(80), padding=[dp(20), dp(10)])
        self.rating_slider = Slider(min=1, max=5, value=3, step=1, size_hint_x=None, width=dp(250))
        self.rating_label = Label(text="Rating: 3 - Neutral", halign="center", size_hint=(None, None), size=(dp(250), dp(30)),
                                  color=(0, 0, 0, 1), font_size=dp(14))
        self.rating_slider.bind(value=self.update_rating_text)

        slider_layout.add_widget(self.rating_slider)
        slider_layout.add_widget(self.rating_label)
        main_layout.add_widget(slider_layout)

        # Submit button
        submit_button = Button(
            text='Submit',
            size_hint=(None, None),
            size=(dp(150), dp(40)),
            pos_hint={'center_x': 0.5},
            on_press=self.submit_form
        )
        submit_button_box = BoxLayout(size_hint=(1, None), height=dp(40), padding=[dp(20), dp(10)], orientation='horizontal')
        submit_button_box.add_widget(Widget())  # Spacer widget
        submit_button_box.add_widget(submit_button)
        submit_button_box.add_widget(Widget())  # Spacer widget
        main_layout.add_widget(submit_button_box)

        # Add the main layout to the screen
        self.add_widget(main_layout)

    def _update_rect(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def update_rating_text(self, instance, value):
        rating = int(value)
        comments = {
            1: "Unhappy",
            2: "Displeased",
            3: "Neutral",
            4: "Happy",
            5: "Very Happy"
        }
        self.rating_label.text = f"Rating: {rating} - {comments.get(rating, 'Unknown')}"

    def submit_form(self, instance):
        # Collect feedback data
        feedback_text = self.feedback_input.text
        rating = int(self.rating_slider.value)

        # Prepare data for MongoDB
        feedback_data = {
            'feedback_text': feedback_text,
            'rating': rating
        }

        # Insert data into MongoDB collection
        self.collection.insert_one(feedback_data)

        # Clear the form fields (optional)
        self.feedback_input.text = ''
        self.rating_slider.value = 3
        self.update_rating_text(self.rating_slider, self.rating_slider.value)

        # Show the feedback submitted popup
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(Label(text="Feedback submitted ", halign='center'))
        close_button = Button(text="Close", size_hint=(None, None), size=(dp(100), dp(50)), halign="center")
        content.add_widget(close_button)

        popup = Popup(title="Success", content=content, size_hint=(0.8, 0.4), auto_dismiss=True)
        close_button.bind(on_press=lambda x: self.on_popup_close(popup))
        popup.open()

    def on_popup_close(self, popup):
        popup.dismiss()
        # Navigate back to the home screen (adjust 'home_screen' to your actual home screen name)
        self.manager.current = 'home_screen'
