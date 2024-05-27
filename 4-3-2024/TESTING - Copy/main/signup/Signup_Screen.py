from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from pymongo import MongoClient
import re

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'signup_screen'
        self.orientation = "vertical"
        self.spacing = 15
        self.padding = [50, 0]  # Adjusting top padding to move the content to the center

        # Adding background image for signup screen
        self.background = Image(source="images (11).jpeg", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
        self.add_widget(self.background)

        # BoxLayout to hold the back button and existing content
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        self.add_widget(top_layout)

        # Back button
        back_button = Button(text="Back", size_hint=(None, None), size=(80, 40))
        back_button.bind(on_press=self.go_to_login_screen)
        top_layout.add_widget(back_button)

        signup_layout = GridLayout(cols=1, spacing=10, size_hint=(None, None), size=(300, 300),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.5})
        signup_layout.bind(minimum_size=signup_layout.setter('size'))

        title = Label(text="Signup Page", font_size=40, size_hint_y=None, height=40, font_name='times', bold=True)
        signup_layout.add_widget(title)

        # Add signup input fields and buttons similar to login screen
        signup_input_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, height=200)

        # Customize input fields' background color
        input_background_color = (1, 1, 1, 0.7)  # Transparent color (black with alpha 0)

        self.signup_username_input = TextInput(
            hint_text="First name", multiline=False, size_hint_y=None, height=40,
            background_color=input_background_color,  # Set background color
            hint_text_color=[0, 0, 0, 1]  # Set hint text color to white
        )
        signup_input_layout.add_widget(self.signup_username_input)

        self.signup_lastname_input = TextInput(
            hint_text="Last name", multiline=False, size_hint_y=None, height=40,
            background_color=input_background_color, # Set background color
            hint_text_color=[0, 0, 0, 1]  # Set hint text color to white
        )
        signup_input_layout.add_widget(self.signup_lastname_input)

        self.signup_email_input = TextInput(
            hint_text="Email", multiline=False, size_hint_y=None, height=40,
            background_color=input_background_color,  # Set background color
            hint_text_color=[0, 0, 0, 1]  # Set hint text color to white
        )
        signup_input_layout.add_widget(self.signup_email_input)

        self.signup_password_input = TextInput(
            hint_text="Password", password=True, multiline=False, size_hint_y=None, height=40,
            background_color=input_background_color,  # Set background color
            hint_text_color=[0, 0, 0, 1]  # Set hint text color to white
        )
        signup_input_layout.add_widget(self.signup_password_input)

        signup_layout.add_widget(signup_input_layout)

        signup_button_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(200, 40), spacing=10)
        signup_button_layout.pos_hint = {'center_x': 0.5}  # Centering the buttons horizontally

        self.create_account_button = Button(text="Create Account")
        self.create_account_button.bind(on_press=self.create_account)
        self.create_account_button.font_name = 'times'  # Setting font for the create account button
        signup_button_layout.add_widget(self.create_account_button)

        signup_layout.add_widget(signup_button_layout)

        self.add_widget(signup_layout)

    def create_account(self, instance):
        # Get input values
        username = self.signup_username_input.text
        password = self.signup_password_input.text
        last_name = self.signup_lastname_input.text
        email = self.signup_email_input.text

        # Validate input fields
        if not username or not password or not last_name or not email:
            # Display a pop-up message if any field is empty
            self.show_popup("Error", "All fields are required.", color=(1, 0, 0, 1))  # Red color for error message
        else:
            # Connect to MongoDB
            client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection string
            db = client['login_page']  # Replace 'your_database_name' with your actual database name
            collection = db['login_signup']  # Collection name where user data will be stored

            # Check if username already exists in the database
            existing_username = collection.find_one({'username': username})
            if existing_username:
                # Username already exists, show error message
                self.show_popup("Error", "Username already exists.", color=(1, 0, 0, 1))  # Red color for error message
            else:
                # Check if email already exists in the database
                existing_email = collection.find_one({'email': email})
                if existing_email:
                    # Email already exists, show error message
                    self.show_popup("Error", "Email already exists.", color=(1, 0, 0, 1))  # Red color for error message
                else:
                    # Validate email format using regular expression
                    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                    if not re.match(email_pattern, email):
                        # Invalid email format, show error message
                        self.show_popup("Error", "Invalid email format.", color=(1, 0, 0, 1))  # Red color for error message
                    else:
                        # Create a document to insert into the collection
                        user_data = {
                            'username': username,
                            'password': password,
                            'last_name': last_name,
                            'email': email
                        }

                        # Insert the document into the collection
                        collection.insert_one(user_data)

                        # Close the MongoDB connection
                        client.close()

                        # Show a pop-up message indicating successful account creation
                        self.show_popup("Success", "Account created successfully.", color=(0, 1, 0, 1))  # Green color for success message

                        # Switch to the login screen
                        self.manager.current = 'login_screen'

                        # Clear input fields
                        self.signup_username_input.text = ""
                        self.signup_password_input.text = ""
                        self.signup_lastname_input.text = ""
                        self.signup_email_input.text = ""

    def show_popup(self, title, content, color=(0, 0, 0, 1)):
        # Display a pop-up message with an OK button centered at the bottom
        popup_content = BoxLayout(orientation='vertical', spacing=10)
        popup_content.add_widget(Label(text=content, size_hint_y=None, height=40, color=color))

        ok_button = Button(text="OK", size_hint_y=None, height=40)
        ok_button.bind(on_press=lambda *args: self.popup.dismiss())

        # Center the "OK" button at the bottom
        bottom_layout = BoxLayout(size_hint_y=None, height=40)
        bottom_layout.add_widget(ok_button)
        popup_content.add_widget(bottom_layout)

        self.popup = Popup(title=title, content=popup_content, size_hint=(None, None), size=(300, 200), auto_dismiss=False)
        self.popup.open()

    def go_to_login_screen(self, instance):
        # Switch to the login screen
        self.manager.current = 'login_screen'



    
