from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.metrics import dp

class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'help_screen'

        # Set the background image
        with self.canvas.before:
            self.bg_image = Rectangle(source='media/mainBg.jpg', size=Window.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Create the main layout with padding to position widgets
        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(30), dp(20), dp(10)], spacing=dp(10), size_hint=(1, 1))

        # Create the heading label
        heading = Label(
            text='Help',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24),
            bold=True,
            color=(0, 0, 1, 1),  # Blue color
            halign='center',
            valign='middle'
        )
        heading.bind(size=heading.setter('text_size'))
        main_layout.add_widget(heading)

        # Create the instructions text
        instructions = (
            "Welcome to the application help screen!\n\n"
            "To get started with the application, please follow the instructions below:\n\n"
            "1. **Download IP Webcam:**\n"
            "   - Go to the Play Store on your Android device and search for 'IP Webcam'.\n"
            "   - Download and install the IP Webcam app.\n\n"
            "2. **Set Up IP Webcam:**\n"
            "   - Open the IP Webcam app on your device.\n"
            "   - Configure the settings according to your needs, such as resolution and port number.\n"
            "   - Start the server to obtain the IP address and port number.\n\n"
            "3. **Integrate with the Application:**\n"
            "   - Enter the IP address and port number from the IP Webcam app into the application's settings.\n"
            "   - The application will use this information to connect to the camera feed.\n\n"
            "4. **Usage:**\n"
            "   - Use the application to monitor your tank and analyze the footage captured by the IP Webcam.\n"
            "   - Ensure the camera is correctly positioned to cover the tank area.\n\n"
            "For any issues or support, feel free to contact us:\n\n"
            "- se20f-051@ssuet.edu.pk\n"
            "- se20f-057@ssuet.edu.pk\n"
            "- se20f-059@ssuet.edu.pk\n"
            "- se20f-084@ssuet.edu.pk"
        )

        # Create a ScrollView to make the text scrollable
        scroll_view = ScrollView(size_hint=(1, 0.5), do_scroll_x=False)
        instructions_label = Label(
            text=instructions,
            color=(0, 0, 0, 1),  # Black color
            text_size=(Window.width - dp(40), None),  # Adjust text size to fit the width
            size_hint_y=None,
            height=dp(600)  # Adjust height as necessary
        )
        scroll_view.add_widget(instructions_label)

        # Add ScrollView to the main layout
        main_layout.add_widget(scroll_view)

        # Create the Back button
        back_button = Button(
            text='Back',
            size_hint=(None, None),
            size=(dp(50), dp(20)),
            pos_hint={'right': 0.1, 'top': 0.1},
            background_color=(1, 0, 0, 1),  # Red color for visibility
            on_press=self.go_back
        )
        main_layout.add_widget(back_button)

        # Add the main layout to the screen
        self.add_widget(main_layout)

    def _update_rect(self, *args):
        self.bg_image.size = self.size
        self.bg_image.pos = self.pos

    def go_back(self, instance):
        self.manager.current = 'home_screen'  # Replace 'home_screen' with the actual name of your home screen
