from chatgui import ChatBotApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDRaisedButton
from kivy.animation import Animation


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        self.new_chatbotapp = ChatBotApp()
        super().__init__(**kwargs)
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
        hamburger_button =Button(
            size_hint=(None, None),
            size=(100, 35),
            background_normal="menuButton.png",
            pos_hint={'top': 0.80, 'right': 0.85}, # Adjusted top and right positions
            on_press=self.toggle_menu
        )

        top_layout2.add_widget(hamburger_button)
        hamburger_button.bind(on_press=self.toggle_menu)

        # Add a logout button to the top-right corner
        self.logout_button = MDRaisedButton(text="Logout", size_hint=(None, None), size=(70, 40))
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

        plus_button = MDRaisedButton(
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

    def create_menu_box(self):
        menu_box = BoxLayout(
            orientation='vertical',
            spacing=8
        )

        # Add menu items
        menu_items = ["Home", "Contact", "Help"]
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
            self.menu_layout.pos_hint = {'center_x': 0.20, 'center_y': 0.66}  # Adjusted pos_hint
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

        # Scroll to the top to show the latest message
        chat_layout.height = chat_layout.minimum_height
        chat_layout.parent.scroll_y = 0

    def add_tank_widget(self, tank_data):
        # Create a new BoxLayout for the tank widget
        tank_widget = BoxLayout(orientation='vertical', size_hint=(None, None), size=(90, 120))

        # Add a background image
        if tank_data['image_path'] and tank_data['image_path'] != 'No file chosen':
            tank_image = Image(source=tank_data['image_path'], allow_stretch=True, keep_ratio=False)
            tank_widget.add_widget(tank_image)

        # Add tank name and ID as labels
        tank_widget.add_widget(Label(text=f"Name: {tank_data['tank_name']}", size_hint_y=None, height=20, color=(1, 1, 1, 1)))
        tank_widget.add_widget(Label(text=f"ID: {tank_data['tank_id']}", size_hint_y=None, height=20, color=(1, 1, 1, 1)))

        # Add the tank widget to the tank container
        self.tank_container.add_widget(tank_widget)

        # Calculate the total width of all tank widgets in the tank container
        total_width = sum(child.width for child in self.tank_container.children)

        # Calculate the x-position to center the tank widgets horizontally
        center_x = (self.width - total_width) / 2

        # Adjust the position of the tank container to center all tank widgets horizontally
        self.tank_container.pos_hint = {'x': center_x / self.width, 'center_y': 0.5}




