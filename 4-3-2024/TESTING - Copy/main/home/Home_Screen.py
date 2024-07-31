from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.animation import Animation
from scan.Scan_Screen import ScanScreen
from pymongo import MongoClient
from chatgui import ChatBotApp


class HomeScreen(Screen):
    new_chatbot = ChatBotApp()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tank_popup = None  # Store reference to tank details popup
        self.name = 'home_screen'
        self.orientation = "vertical"
        self.spacing = 15
        self.padding = [50, 0]  # Adjusting top padding to move the content to the center
        
        # Adding background image for the home screen
        self.menu_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(200, 120),
            pos_hint={'center_x': 0.55, 'top': 0.80}  # Adjusted pos_hint for horizontal shift
        )
        self.menu_layout.opacity = 0  # Initially hidden
        self.add_widget(Image(source="mainBg.jpg", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))

        # Create an instance of MenuBox
        menu_box = self.create_menu_box()
        self.menu_layout.add_widget(menu_box)
        self.add_widget(self.menu_layout)

        # Logo and Logout button layout
        top_layout2 = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            height=20,
            pos_hint={'top': 0.80, 'left': 0.85} # Adjusted left position to 0.85
        )

        top_layout1 = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            height=40,
            pos_hint={'top': 0.95, 'right': 1}
        )

        # Add a chat button at the bottom right corner
        chat_button = Button(
            size_hint=(None,None ),
            size=(80, 80),
            pos_hint={'right': 0.98, 'bottom': 0.02},
            background_normal="chatButton.png",
            on_press=self.open_chat_popup
        )
        anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(chat_button)
        self.add_widget(chat_button)

        # Add a hamburger menu toggle button with an image
        hamburger_button = Button(
            size_hint=(None, None),
            size=(100, 35),
            background_normal="menuButton.png",
            pos_hint={'top': 0.80, 'right': 0.85}, # Adjusted top and right positions
            on_press=self.toggle_menu
        )

        top_layout2.add_widget(hamburger_button)
        hamburger_button.bind(on_press=self.toggle_menu)

        # Add a logout button to the top-right corner
        self.logout_button = Button(background_normal="logoutButton.png", size_hint=(None, None), size=(70, 30))
        top_layout1.add_widget(self.logout_button)
        self.logout_button.bind(on_press=self.go_to_login)

        self.add_widget(top_layout1)
        self.add_widget(top_layout2)

        # Central transparent square box with a plus button
        center_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(200, 200),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        plus_button = Button(
            text="+",
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_press=self.on_plus_button_press
        )
        center_layout.add_widget(plus_button)
        self.add_widget(center_layout)

        # Create a BoxLayout to hold the tank widgets
        self.tank_container = BoxLayout(
            orientation='horizontal',
            spacing=10,  # Add space between each tank widget
            size_hint=(None, None),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.tank_container)

        # Dictionary to store the toggle state for each tank widget
        self.tank_toggle_states = {}

        # MongoDB setup
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client['tank_database']
        self.collection = self.db['tanks']

        # User-specific data (you need to set this when the user logs in)
        self.username = 'ali'

        # Fetch user-specific tanks from MongoDB
        self.fetch_user_tanks()

    def fetch_user_tanks(self):
        user_tanks = self.collection.find({"username": self.username})
        for tank_data in user_tanks:
            self.add_tank_widget(tank_data)

    def create_menu_box(self):
        menu_box = BoxLayout(
            orientation='vertical',
            spacing=8
        )

        # Add menu items
        menu_items = ["Home", "Contact", "Help", "Scan"]
        for item in menu_items:
            menu_button = Button(text=item, size_hint_y=None, size=(70, 40), height=40)
            menu_button.bind(on_press=self.on_menu_button_press)
            menu_box.add_widget(menu_button)

        return menu_box

    def toggle_menu(self, instance):
        # Toggle the visibility of the menu
        if self.menu_layout.opacity == 0:
            self.menu_layout.opacity = 1
            self.menu_layout.size_hint_x = 0.2  # Adjust the width as needed
            self.menu_layout.pos_hint = {'center_x': 0.17, 'center_y': 0.54}  # Adjusted pos_hint
        else:
            self.menu_layout.opacity = 0
            self.menu_layout.size_hint_x = None
            self.menu_layout.width = 0

    def on_menu_button_press(self, instance):
        # Handle menu item press (add functionality here)
        if instance.text == "Home":
            self.manager.current = 'home_screen'
        elif instance.text == "Contact":
            # Handle Contact button press (add functionality here)
            self.manager.current = 'chat_screen'
        elif instance.text == "Help":
            self.show_help_popup()
        elif instance.text == "Scan":
            self.manager.current = 'scan_screen'
            
    def go_to_home(self, instance):
        self.manager.current = 'home_screen'

    def show_help_popup(self):
        # Create a popup for help
        help_popup = Popup(title='Help', content=Label(text='We are here to help you'), size_hint=(None, None), size=(300, 200))
        help_popup.open()

    def go_to_login(self, instance):
        self.manager.current = 'login_screen'

    def on_plus_button_press(self, instance):
        self.manager.current = 'add_tank_screen'

    def open_chat_popup(self, instance):
    # Create a popup for chat
        chat_popup = Popup(title='Chat Bot', size_hint=(None, None), size=(320, 450))

        # Create a simple chat layout with a ScrollView, a GridLayout, a TextInput, and a Send button
        chat_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        chat_layout.bind(minimum_height=chat_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 0.9))
        scroll_view.add_widget(chat_layout)

        chat_input = TextInput(multiline=False, size_hint_y=None, height=40)
        send_button = Button(text='Send', size_hint_y=None, height=40, on_press=lambda x: self.send_chat_message(chat_input, chat_layout))

        popup_layout = GridLayout(cols=1)
        popup_layout.add_widget(scroll_view)
        popup_layout.add_widget(chat_input)
        popup_layout.add_widget(send_button)

        chat_popup.content = popup_layout
        chat_popup.open()


    def send_chat_message(self, chat_input, chat_layout):
        user_message = chat_input.text.strip()
    
        # Check if the user message is empty
        if not user_message:
            # Bot response for empty user message
            response = "It seems like you haven't typed anything. Could you please provide some input?"
        else:
            # Get response from chatbot
            response = self.new_chatbot.send_message(chat_input)
        # Define styles for user and bot messages
        user_color = (0.678, 0.847, 0.902, 1)  # Light blue
        bot_color = (1, 0.647, 0, 1)  # Orange

        # Create Labels for user and bot messages with appropriate text_size for wrapping
        user_label = Label(
            text=f'[b]You:[/b] {user_message}',
            size_hint_y=None,
            height=self.get_text_height(user_message),
            color=user_color,
            markup = True,
            text_size=(self.width * 0.9, None),
            halign='left',
            padding=[dp(220), 0]
        )
        user_label.bind(texture_size=user_label.setter('size'))
        chat_layout.add_widget(user_label)

        bot_label = Label(
            text=f'[b]Bot:[/b] {response}',
            size_hint_y=None,
            height=self.get_text_height(response),
            color=bot_color,
            markup = True,
            text_size=(self.width * 0.9, None),
            halign='left',
            padding=[dp(220), 0]
        )
        bot_label.bind(texture_size=bot_label.setter('size'))
        chat_layout.add_widget(bot_label)

        # Scroll to the bottom of the chat
        chat_layout.height = chat_layout.minimum_height
        chat_layout.parent.scroll_y = 0  # Ensure the ScrollView scrolls to the bottom
        chat_input.text = ''

    def get_text_height(self, text):
        # Estimate the height required for the text
        return dp(40) * (text.count('\n') + 1)

    def add_tank_widget(self, tank_data):
        # Create a BoxLayout to hold tank details
        tank_widget = BoxLayout(orientation='vertical', size_hint=(None, None), size=(200, 250), padding=10)

        # Add tank image
        tank_image = Image(source="tank2.jpg", size_hint=(None, None), size=(200, 200))
        tank_widget.add_widget(tank_image)

        # Add tank name
        tank_name = Label(text=f"Name: {tank_data['tank_name']}", size_hint=(None, None), size=(200, 50))
        tank_widget.add_widget(tank_name)

        # Add toggle button to show tank details
        toggle_button = Button(text="Show Details", size_hint=(None, None), size=(200, 50))
        toggle_button.bind(on_release=lambda btn: self.toggle_tank_details(btn, tank_data))
        tank_widget.add_widget(toggle_button)

        self.tank_container.add_widget(tank_widget)

        # Initially hide tank details
        self.tank_toggle_states[toggle_button] = False

    def toggle_tank_details(self, button, tank_data):
        if button in self.tank_toggle_states:
            current_state = self.tank_toggle_states[button]
            self.tank_toggle_states[button] = not current_state

            if self.tank_toggle_states[button]:
                # Show tank details in a popup
                self.show_tank_details_popup(tank_data)
                button.text = "Hide Details"
            else:
                # Close the tank details popup if it exists
                if self.tank_popup:
                    self.tank_popup.dismiss()
                button.text = "Show Details"

    def show_tank_details_popup(self, tank_data):
        # Create a popup to display tank details
        details_layout = BoxLayout(orientation='vertical', padding=10)

        # Add tank details to the layout
        tank_id_label = Label(text=f"Tank ID: {tank_data['tank_id']}")
        tank_size_label = Label(text=f"Tank Size: {tank_data['tank_size']}")
        num_fishes_label = Label(text=f"Number of Fishes: {tank_data['num_fishes']}")

        details_layout.add_widget(tank_id_label)
        details_layout.add_widget(tank_size_label)
        details_layout.add_widget(num_fishes_label)

        self.tank_popup = Popup(title="Tank Details", content=details_layout, size_hint=(None, None), size=(300, 200))
        self.tank_popup.open()