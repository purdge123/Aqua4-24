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
        self.add_widget(Image(source="mainBg.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))

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
            self.manager.current = 'home_screen'
            
    def go_to_home(self, instance):
        self.manager.current = 'home_screen'

    def show_help_popup(self):
        # Create a popup for help
        help_popup = Popup(title='Help', content=Label(text='We are here to help you'), size_hint=(None, None), size=(300, 200))
        help_popup.open()

    def go_to_login(self, instance):
        self.manager.current = 'login_screen'

    def on_plus_button_press(self, instance):
        # Handle the plus button press by switching to the NewEntryScreen
        self.manager.current = 'add_tank_screen'

    def open_chat_popup(self, instance):
        # Create a popup for chat
        chat_popup = Popup(title='Chat Bot', size_hint=(None, None), size=(320, 450))

        # Create a simple chat layout with a ScrollView, a GridLayout, a TextInput, and a Send button
        chat_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        chat_layout.bind(minimum_height=chat_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, None), size=(200, 300))
        scroll_view.add_widget(chat_layout)

        chat_input = TextInput(multiline=False, size_hint_y=None, height=40)
        send_button = Button(text='Send', size_hint_y=None, height=40, on_press=lambda x: self.send_chat_message(chat_input, chat_layout))

        chat_popup.content = GridLayout(cols=1)
        chat_popup.content.add_widget(scroll_view)
        chat_popup.content.add_widget(chat_input)
        chat_popup.content.add_widget(send_button)

        chat_popup.open()

    def send_chat_message(self, message, chat_layout):
        # Handle sending chat messages (add your chatbot logic here)
        self.new_chatbot = ChatBotApp()

        # Create multiline labels for user and bot responses
        user_response_label = Label(
            text=f'[color=#00FF00][b]You:[/b][/color] ' + message.text,
            markup=True,
            halign='left',
            size_hint=(1, None),
            height=20,
            text_size=(280, None)
        )

        bot_response_label = Label(
            text=f'[color=#FF0000][b]Bot:[/b][/color] ' + self.new_chatbot.send_message(message),
            markup=True,
            halign='left',
            size_hint=(1, None),
            height=15,
            text_size=(280, None)
        )

        # Add labels to the chat layout
        chat_layout.add_widget(user_response_label)
        chat_layout.add_widget(bot_response_label)

        # Clear the chat input
        message.text = ''

    def add_tank_widget(self, tank_data):
        # Create a new BoxLayout for the tank widget
        tank_widget = BoxLayout(orientation='vertical', size_hint=(None, None), size=(120, 160))
        tank_widget.tank_data = tank_data  # Store tank_data in the tank_widget

        # Add a background image
        if tank_data['image_path'] and tank_data['image_path'] != 'No file chosen':
            tank_image = Image(source=tank_data['image_path'], allow_stretch=True, keep_ratio=False)
            tank_widget.add_widget(tank_image)

            # Add tank name as a Label under the image
            tank_name_label = Label(text=tank_data['tank_name'], size_hint_y=None, height=dp(20))
            tank_widget.add_widget(tank_name_label)

            tank_image.bind(on_touch_down=lambda instance, touch: self.toggle_tank_details(touch, tank_widget, tank_data))

        # Add the tank widget to the tank container
        self.tank_container.add_widget(tank_widget)

        # Initialize the toggle state for this tank widget
        self.tank_toggle_states[tank_widget] = False

        # Calculate the total width of all tank widgets in the tank container
        total_width = sum(child.width for child in self.tank_container.children)

        # Calculate the x-position to center the tank widgets horizontally
        center_x = (self.width - total_width) / 2

        # Adjust the position of the tank container to center all tank widgets horizontally
        self.tank_container.pos_hint = {'x': center_x / self.width, 'center_y': 0.5}

    def toggle_tank_details(self, touch, tank_widget, tank_data):
        if tank_widget.collide_point(*touch.pos):
            # Always show tank details when the image is touched
            self.show_tank_details_popup(tank_data)

    def show_tank_details_popup(self, tank_data):
        # Create a popup for tank details
        self.tank_popup = Popup(title='Tank Details', size_hint=(None, None), size=(400, 400))

        # Create TextInput widgets for editable fields
        tank_name_input = TextInput(text=tank_data['tank_name'], multiline=False, size_hint_y=None, height=dp(40))
        tank_id_input = TextInput(text=tank_data['tank_id'], multiline=False, size_hint_y=None, height=dp(40))
        tank_size_input = TextInput(text=tank_data['tank_size'], multiline=False, size_hint_y=None, height=dp(40))

        # Add tank image to the popup content
        tank_image = Image(source=tank_data['image_path'], size_hint=(None, None), size=(300, 300), allow_stretch=True, keep_ratio=True)
        tank_details_label = Label(
            text=f"Name: {tank_data['tank_name']}\nID: {tank_data['tank_id']}\nSize: {tank_data['tank_size']}",
            size_hint_y=None, height=dp(100), color=(1, 1, 1, 1))

        save_button = Button(text='Save', size_hint_y=None, height=dp(40))
        save_button.bind(on_press=lambda x: self.save_tank_details(tank_data, tank_name_input.text, tank_id_input.text, tank_size_input.text))
        delete_button = Button(text='Delete', size_hint_y=None, height=dp(40))
        delete_button.bind(on_press=lambda x: self.delete_tank_details(tank_data))

        # Add widgets to the tank details popup
        content = BoxLayout(orientation='vertical')
        content.add_widget(tank_image)
        content.add_widget(tank_name_input)
        content.add_widget(tank_id_input)
        content.add_widget(tank_size_input)
        content.add_widget(save_button)
        content.add_widget(delete_button)

        self.tank_popup.content = content
        self.tank_popup.open()

    def save_tank_details(self, tank_data, new_name, new_id, new_size):
        # Update tank_data dictionary with new values
        tank_data['tank_name'] = new_name
        tank_data['tank_id'] = new_id
        tank_data['tank_size'] = new_size

        # Update the displayed tank details in the popup
        tank_details_text = f"Name: {new_name}\nID: {new_id}\nSize: {new_size}"
        self.tank_popup.content.children[0].children[3].text = tank_details_text  # Update the Label in the popup

        # Update MongoDB with the new tank details (if needed)
        # Example:
        # self.collection.update_one({'_id': tank_data['_id']}, {"$set": tank_data})

        self.tank_popup.dismiss()

    def delete_tank_details(self, tank_data):
        # Delete tank details from MongoDB
        # Example:
        # self.collection.delete_one({'_id': tank_data['_id']})

        # Remove tank widget from tank_container
        for child in self.tank_container.children[:]:
            if child.tank_data == tank_data:
                self.tank_container.remove_widget(child)
                break

        self.tank_popup.dismiss()
