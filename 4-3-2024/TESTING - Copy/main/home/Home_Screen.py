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
from kivy.animation import Animation
from pymongo import MongoClient
from chatgui import ChatBotApp
from pymongo.errors import PyMongoError
from bson import ObjectId

class MongoDBClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            cls._instance.client = MongoClient("mongodb://localhost:27017/")
            cls._instance.db = cls._instance.client['login_page']
            cls._instance.collection = cls._instance.db['Addition_page']
        return cls._instance

class HomeScreen(Screen):
    new_chatbot = ChatBotApp()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = None  # Initialize username attribute

        # Initialize UI components
        self.setup_ui()

        # Fetch user-specific tanks from MongoDB
        self.fetch_user_tanks()

    def on_enter(self, *args):
        self.update_username_from_login()  # Ensure username is updated
        self.fetch_user_tanks()  # Fetch tanks for the current user

    def update_username_from_login(self):
        if self.manager:
            login_screen = self.manager.get_screen('login_screen')
            if login_screen and hasattr(login_screen, 'username'):
                self.username = login_screen.username
                print(f"Username set in HomeScreen: {self.username}")

    def setup_ui(self):
        self.add_background_image()
        self.add_menu()
        self.add_top_buttons()
        self.add_center_button()
        self.add_tank_container()

    def add_background_image(self):
        self.add_widget(Image(source="mainBg.jpg", allow_stretch=True, keep_ratio=False, size_hint=(dp(1), dp(1))))

    def add_menu(self):
        self.menu_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(200), dp(120)),  # Initial size; adjust as necessary
            pos_hint={'center_x': 0.17, 'center_y': 0.54}  # Initial position
        )

        self.menu_layout.opacity = 0
        self.add_widget(self.menu_layout)
        self.menu_layout.add_widget(self.create_menu_box())

    def add_top_buttons(self):
        top_layout1 = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            height=dp(40),
            pos_hint={'top': 0.95, 'right': 1}
        )
        top_layout2 = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            height=dp(20),
            pos_hint={'top': 0.80, 'left': 0.85}
        )
        chat_button = Button(
            size_hint=(None, None),
            size=(dp(80), dp(80)),
            pos_hint={'right': 0.98, 'bottom': 0.02},
            background_normal="chatButton.png",
            on_press=self.open_chat_popup
        )
        self.animate_button(chat_button)
        self.add_widget(chat_button)

        hamburger_button = Button(
            size_hint=(None, None),
            size=(dp(100), dp(35)),
            background_normal="menuButton.png",
            pos_hint={'top': 0.80, 'right': 0.85},
            on_press=self.toggle_menu
        )
        
        # Add logo to the top left
        logo = Image(source="logo.png", size_hint=(None, None), size=(dp(80), dp(80)))
        top_layout2.add_widget(logo)
        
        top_layout2.add_widget(hamburger_button)
        self.add_widget(top_layout2)

        logout_button = Button(
            background_normal="logoutButton.png",
            size_hint=(None, None),
            size=(dp(70), dp(30))
        )
        top_layout1.add_widget(logout_button)
        logout_button.bind(on_press=self.go_to_login)
        self.add_widget(top_layout1)

    def add_center_button(self):
        center_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(50), dp(50)),  # Adjusted size to match the button size
            pos_hint={'center_y': 0.5, 'right': 1}  # Center vertically and align to the right
        )
        plus_button = Button(
            text="+",
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            on_press=self.on_plus_button_press
        )
        center_layout.add_widget(plus_button)
        self.add_widget(center_layout)

    

    def create_menu_box(self):
        menu_box = BoxLayout(orientation='vertical', spacing=dp(8))
        menu_items = ["Home", "Contact", "Help", "Scan"]
        for item in menu_items:
            menu_button = Button(text=item, size_hint_y=None, size=(dp(70), dp(40)), height=dp(40))
            menu_button.bind(on_press=self.on_menu_button_press)
            menu_box.add_widget(menu_button)
        return menu_box

    def animate_button(self, button):
        anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(button)

    def toggle_menu(self, instance):
        if self.menu_layout.opacity == 0:
            # Make the menu visible
            self.menu_layout.opacity = 1
            self.menu_layout.size_hint_x = dp(0.2)
            self.menu_layout.pos_hint = {'center_x': 0.17, 'center_y': 0.54}
            self.menu_layout.width = dp(200)  # Ensure the width is set so the buttons are interactable
            
            # Bring the menu to the front
            self.bring_menu_to_front()
        else:
            # Hide the menu
            self.menu_layout.opacity = 0
            self.menu_layout.size_hint_x = None
            self.menu_layout.width = dp(0)
            self.menu_layout.pos_hint = {'center_x': 0.17, 'center_y': 0.54}
            
    def bring_menu_to_front(self):
        # Remove the menu layout and re-add it to ensure it is on top
        self.remove_widget(self.menu_layout)
        self.add_widget(self.menu_layout)


    def on_menu_button_press(self, instance):
        if instance.text == "Home":
            self.manager.current = 'home_screen'
        elif instance.text == "Contact":
            self.manager.current = 'chat_screen'
        elif instance.text == "Help":
            self.show_help_popup()
        elif instance.text == "Scan":
            self.manager.current = 'scan_screen'

    def go_to_home(self, instance):
        self.manager.current = 'home_screen'

    def show_help_popup(self):
        help_popup = Popup(
            title='Help',
            content=Label(text='We are here to help you'),
            size_hint=(None, None),
            size=(dp(300), dp(200))
        )
        help_popup.open()

    def go_to_login(self, instance):
        self.manager.current = 'login_screen'

    def on_plus_button_press(self, instance):
        add_tank_screen = self.manager.get_screen('add_tank_screen')
        add_tank_screen.username = self.username
        self.manager.current = 'add_tank_screen'

    def open_chat_popup(self, instance):
        chat_popup = Popup(title='Chat Bot', size_hint=(None, None), size=(dp(320), dp(450)))
        chat_layout = GridLayout(cols=1, spacing=(10), size_hint_y=None)
        chat_layout.bind(minimum_height=chat_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1,0.9))
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
        user_message = chat_input.text
        response = self.new_chatbot.send_message(chat_input)

        # Define styles for user and bot messages
        user_color = (0.678, 0.847, 0.902, 1)  # Light blue
        bot_color = (1, 0.647, 0, 1)  # Orange

        # Create Labels for user and bot messages with bold text and appropriate text_size for wrapping
        user_label = Label(
            text=f'[b]You:[/b] {user_message}',
            size_hint_y=None,
            height=self.get_text_height(user_message),
            color=user_color,
            markup=True,  # Enable markup to use [b] for bold text
            text_size=(self.width * 0.9, None),
            halign='left',
            padding=[dp(220), 0]  # Add padding to the left
        )
        chat_layout.add_widget(user_label)

        bot_label = Label(
            text=f'[b]Bot:[/b] {response}',
            size_hint_y=None,
            height=self.get_text_height(response),
            color=bot_color,
            markup=True,  # Enable markup to use [b] for bold text
            text_size=(self.width * 0.9, None),
            halign='left',
            padding=[dp(220), 0]  # Add padding to the left
        )
        chat_layout.add_widget(bot_label)

        # Scroll to the bottom of the chat
        chat_layout.height = chat_layout.minimum_height
        chat_layout.parent.scroll_y = 0  # Ensure the ScrollView scrolls to the bottom
        chat_input.text = ''

    def get_text_height(self, text):
        # Estimate the height required for the text
        return dp(40) * (text.count('\n') + 1)



    def fetch_user_tanks(self):
        db = MongoDBClient().collection
        if self.username:
            user_tanks = db.find({"username": self.username})
            self.tank_container.clear_widgets()  # Clear existing widgets
            for tank_data in user_tanks:
                self.add_tank_widget(tank_data)
        else:
            print("Username is not set. Cannot fetch tanks.")

    

    def start_scan(self, tank_data):
        camera_ip = tank_data.get("camera_ip", "default_ip")  # Use the IP saved in the tank data
        scan_screen = self.manager.get_screen('scan_screen')
        scan_screen.camera_ip = camera_ip
        self.manager.current = 'scan_screen'


    def toggle_tank_details(self, button, tank_data):
        if self.tank_toggle_states.get(button):
            if self.tank_popup:
                self.tank_popup.dismiss()
            button.text = "Show Details"
        else:
            self.show_tank_details_popup(tank_data)
            button.text = "Hide Details"
        self.tank_toggle_states[button] = not self.tank_toggle_states.get(button)

    
    def open_tank_details_popup(self, tank_data):
        details_layout = BoxLayout(orientation='vertical', padding=dp(10))
        
        # Add tank details to the popup
        tank_id_label = Label(text=f"Tank ID: {tank_data['tank_id']}")
        tank_name_label = Label(text=f"Tank Name: {tank_data['tank_name']}")
        tank_size_label = Label(text=f"Tank Size: {tank_data['tank_size']}")
        num_fishes_label = Label(text=f"Number of Fishes: {tank_data['num_fishes']}")
        camera_ip_label = Label(text=f"Camera IP Address: {tank_data.get('camera_ip', '')}")  # Show camera IP if available
        
        details_layout.add_widget(tank_id_label)
        details_layout.add_widget(tank_name_label)
        details_layout.add_widget(tank_size_label)
        details_layout.add_widget(num_fishes_label)
        details_layout.add_widget(camera_ip_label)

        # Create a layout for the buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        scan_button = Button(text="Scan", size_hint_x=None, width=dp(100))
        scan_button.bind(on_release=lambda btn: self.handle_scan_button_press(tank_data))
        edit_button = Button(text="Edit", size_hint_x=None, width=dp(100))
        edit_button.bind(on_release=lambda btn: self.open_edit_popup(tank_data))
        close_button = Button(text="Close", size_hint_x=None, width=dp(100))
        close_button.bind(on_release=lambda btn: self.tank_popup.dismiss())

        button_layout.add_widget(scan_button)
        button_layout.add_widget(edit_button)
        button_layout.add_widget(close_button)
        
        details_layout.add_widget(button_layout)

        # Create and open the popup
        self.tank_popup = Popup(title="Tank Details", content=details_layout, size_hint=(None, None), size=(dp(300), dp(300)))
        self.tank_popup.open()

    def open_edit_popup(self, tank_data):
        edit_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Create text inputs for editing
        tank_name_input = TextInput(text=tank_data['tank_name'], multiline=False, size_hint_y=None, height=dp(30))
        tank_size_input = TextInput(text=tank_data['tank_size'], multiline=False, size_hint_y=None, height=dp(30))
        num_fishes_input = TextInput(text=tank_data['num_fishes'], multiline=False, size_hint_y=None, height=dp(30))
        camera_ip_input = TextInput(text=tank_data.get('camera_ip', ''), multiline=False, size_hint_y=None, height=dp(30))
        
        edit_layout.add_widget(Label(text="Tank Name"))
        edit_layout.add_widget(tank_name_input)
        edit_layout.add_widget(Label(text="Tank Size"))
        edit_layout.add_widget(tank_size_input)
        edit_layout.add_widget(Label(text="Number of Fishes"))
        edit_layout.add_widget(num_fishes_input)
        edit_layout.add_widget(Label(text="Camera IP Address"))
        edit_layout.add_widget(camera_ip_input)

        # Create a layout for the buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        save_button = Button(text="Save", size_hint_x=None, width=dp(100))
        save_button.bind(on_release=lambda btn: self.save_edit(tank_data['tank_id'], tank_name_input.text, tank_size_input.text, num_fishes_input.text, camera_ip_input.text))
        cancel_button = Button(text="Cancel", size_hint_x=None, width=dp(100))
        cancel_button.bind(on_release=lambda btn: self.edit_popup.dismiss())

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)
        
        edit_layout.add_widget(button_layout)

        # Create and open the popup
        self.edit_popup = Popup(title="Edit Tank Details", content=edit_layout, size_hint=(None, None), size=(dp(300), dp(350)))
        self.edit_popup.open()
    
    def save_edit(self, tank_id, tank_name, tank_size, num_fishes, camera_ip):
        db = MongoDBClient().collection
        try:
            query = {"tank_id": tank_id, "username": self.username}
            new_values = {
                "$set": {
                    "tank_name": tank_name,
                    "tank_size": tank_size,
                    "num_fishes": num_fishes,
                    "camera_ip": camera_ip
                }
            }

            # Debugging: Check if document exists
            existing_document = db.find_one(query)
            if existing_document:
                print(f"Existing document: {existing_document}")
            else:
                print("No matching document found for the update.")
                return

            result = db.update_one(query, new_values)
            
            if result.modified_count > 0:
                print("Document updated successfully")
            else:
                print("No documents were updated. This might be because the values you tried to set are the same as the current values.")

            # Refresh the UI or perform any additional operations
            self.edit_popup.dismiss()
            self.tank_popup.dismiss()
            self.refresh_tanks()

        except PyMongoError as e:
            print(f"MongoDB Error: {e}")


            
    def refresh_tanks(self):
        self.tank_container.clear_widgets()  # Clear existing widgets
        self.fetch_user_tanks()  # Fetch and display updated tank data


    def handle_scan_button_press(self, tank_data):
        self.start_scan(tank_data)
        self.tank_popup.dismiss()
        
    def add_tank_container(self):
        # Create a GridLayout to center tank widgets
        self.tank_container = GridLayout(
            cols=1,  # Adjust the number of columns
            spacing=dp(4),
            size_hint=(None, None),
            width=dp(200),  # Width of the GridLayout
            row_default_height=dp(220),
            pos_hint={'center_x': 0.5, 'top': 1},  # Center vertically
            height=self.height  # Make sure to use the full height
        )
        self.tank_container.bind(minimum_height=self.tank_container.setter('height'))

        # Use ScrollView to enable vertical scrolling
        scroll_view = ScrollView(
            size_hint=(None, None),
            size=(dp(250), dp(350)),
            pos_hint={'y': 0, 'x': 0.1},
            do_scroll_x=False  # Disable horizontal scrolling# Center vertically, and some gap from the left
        )
        scroll_view.add_widget(self.tank_container)

        self.add_widget(scroll_view)
    
    def add_tank_widget(self, tank_data):
        # Create a vertical BoxLayout for the tank widget
        tank_widget = BoxLayout(orientation='vertical', size_hint=(None, None), size=(dp(200), dp(220)), padding=dp(1))

        # Tank name label above the image
        tank_name = Label(text=f"[color=000000]Name: {tank_data['tank_name']}[/color]",markup=True,size_hint=(None, None),size=(dp(200), dp(20)),padding=(dp(2), dp(1))  )
        # Image widget
        image_source = tank_data.get("image_path", "default_image.jpg")
        tank_image = Image(source=image_source, size_hint=(None, None), size=(dp(200), dp(150)))  # Set size to 2 cm square
        # Show Details Button
        show_details_button = Button(text="Show Details", size_hint=(None, None), size=(dp(200), dp(40)))
        show_details_button.bind(on_press=lambda btn: self.open_tank_details_popup(tank_data))
        
        
        
        tank_widget.add_widget(tank_image)
        tank_widget.add_widget(tank_name)
        tank_widget.add_widget(show_details_button)

        # Add the tank widget to the GridLayout container
        self.tank_container.add_widget(tank_widget)
        
    def on_size(self, *args):
        self.tank_container.size = (self.width, self.height)