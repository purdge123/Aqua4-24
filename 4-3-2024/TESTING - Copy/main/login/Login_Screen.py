from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.app import App
from pymongo import MongoClient
from kivy.uix.popup import Popup

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login_screen'
        self.orientation = "vertical"
        self.spacing = 15
        self.padding = [50, 0]  # Adjusting top padding to move the content to the center

        # Remove background image
        self.background = Image(source="Bg.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
        self.add_widget(self.background)

        # Set background color
        main_layout = GridLayout(cols=1, spacing=10, size_hint=(None, None), size=(300, 300),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5})
        main_layout.bind(minimum_size=main_layout.setter('size'))

        # Add logo image
        logo_image = Image(source="logo.png", size_hint=(None, None), size=(200, 200),pos_hint={'center_x': 0.5, 'center_y': 0.})
        main_layout.add_widget(logo_image)

        title = Label(text="Login or Signup", font_size=40, size_hint_y=None, height=40, font_name='times',
                      color='white', bold=True)
        main_layout.add_widget(title)

        input_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, height=80)

        self.username_input = TextInput(hint_text="Username", multiline=False, size_hint_y=None, height=40, hint_text_color=[0, 0, 0, 1])
        self.username_input.foreground_color = [0, 0, 0, 1]
        self.username_input.background_color = [1, 1, 1, 0.7]
        input_layout.add_widget(self.username_input)

        self.password_input = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height=40, hint_text_color=[0, 0, 0, 1])
        self.password_input.foreground_color = [0, 0, 0, 1]
        self.password_input.background_color = [1, 1, 1, 0.7]
        input_layout.add_widget(self.password_input)

        main_layout.add_widget(input_layout)

        button_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(180, 30), spacing=10)
        button_layout.pos_hint = {'center_x': 0.5}

        self.login_button = Button(background_normal="loginButton.png")
        self.login_button.bind(on_press=self.login)
        self.login_button.font_name = 'times'
        button_layout.add_widget(self.login_button)

        self.signup_button = Button(background_normal="signupButton.png")
        self.signup_button.bind(on_press=self.go_to_signup)
        self.signup_button.font_name = 'times'
        button_layout.add_widget(self.signup_button)

        main_layout.add_widget(button_layout)

        self.add_widget(main_layout)

    def login(self, instance):
        # Get username and password from input fields
        username = self.username_input.text
        password = self.password_input.text

        # Connect to your database
        client = MongoClient('mongodb://localhost:27017/')
        db = client['login_page']
        collection = db['login_signup']

        # Query the database to check if the username and password match
        user_data = collection.find_one({'username': username, 'password': password})

        if user_data:
            print("Login successful")
            # Perform actions after successful login, such as switching screens
            self.manager.current = 'home_screen'
        else:
            self.show_popup("Error", "Wrong username or password.")

        # Close the database connection
        client.close()

        # Clear input fields
        self.username_input.text = ""
        self.password_input.text = ""

    def go_to_signup(self, instance):
        self.manager.current = 'signup_screen'

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

        # Set background color
        main_layout = GridLayout(cols=1, spacing=10, size_hint=(None, None), size=(300, 300),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5})
        main_layout.bind(minimum_size=main_layout.setter('size'))

        title = Label(text="Signup Page", font_size=40, size_hint_y=None, height=40, font_name='times', bold=True)
        main_layout.add_widget(title)

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

        main_layout.add_widget(signup_input_layout)

        signup_button_layout = BoxLayout(orientation='horizontal', size_hint=(None, None), size=(200, 40), spacing=10)
        signup_button_layout.pos_hint = {'center_x': 0.5}  # Centering the buttons horizontally

        self.create_account_button = Button(text="Create Account")
        self.create_account_button.bind(on_press=self.create_account)
        self.create_account_button.font_name = 'times'  # Setting font for the create account button
        signup_button_layout.add_widget(self.create_account_button)

        main_layout.add_widget(signup_button_layout)

        self.add_widget(main_layout)

    def create_account(self, instance):
        # Get input values
        username = self.signup_username_input.text
        password = self.signup_password_input.text
        last_name = self.signup_lastname_input.text
        email = self.signup_email_input.text

        # Connect to MongoDB database
        client = MongoClient('mongodb://localhost:27017/')
        db = client['your_database_name']
        collection = db['your_collection_name']

        # Create a document to insert into the collection
        user_data = {
            'username': username,
            'password': password,
            'last_name': last_name,
            'email': email
        }

        # Insert the document into the collection
        collection.insert_one(user_data)

        # Close the database connection
        client.close()

        # Show a pop-up message indicating successful account creation
        self.show_popup("Success", "Account created successfully.")

        # Switch to the login screen
        self.manager.current = 'login_screen'

        # Clear input fields
        self.signup_username_input.text = ""
        self.signup_password_input.text = ""
        self.signup_lastname_input.text = ""
        self.signup_email_input.text = ""

    def show_popup(self, title, content):
        # Display a pop-up message with an OK button centered at the bottom
        popup_content = BoxLayout(orientation='vertical', spacing=10)
        popup_content.add_widget(Label(text=content, size_hint_y=None, height=40))

        ok_button = Button(text="OK", size_hint_y=None, height=40)
        ok_button.bind(on_press=lambda *args: self.popup.dismiss())

        # Center the "OK" button at the bottom
        bottom_layout = BoxLayout(size_hint_y=None, height=40)
        bottom_layout.add_widget(ok_button)
        popup_content.add_widget(bottom_layout)

        self.popup = Popup(title=title, content=popup_content, size_hint=(None, None), size=(300, 200), auto_dismiss=False)
        self.popup.open()
