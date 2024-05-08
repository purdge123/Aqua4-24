from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDRaisedButton


class AddTankScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'add_tank_screen'
        self.orientation = "vertical"
        self.spacing = 15
        self.padding = [50, 0]  # Adjusting top padding to move the content to the center

        # Add a BoxLayout to hold text input fields dynamically
        self.text_input_layout = BoxLayout(orientation='vertical', spacing=10)
        self.add_widget(self.text_input_layout)

        # Add an initial text input for "Tank ID"
        self.add_text_input("Tank ID")

        # Add an empty widget for spacing
        self.add_widget(Label(size_hint_y=None, height=20))

        # Add a submit button
        submit_button = MDRaisedButton(
            text='Submit',
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'center_x': 0.5},
            on_press=self.submit_form
        )
        self.add_widget(submit_button)

    def add_text_input(self, label_text):
        # Helper method to add a new text input field
        label = Label(text=label_text, halign='center')
        text_input = TextInput(multiline=False, size_hint=(None, None), size=(200, 40), pos_hint={'center_x': 0.5})
        self.text_input_layout.add_widget(label)
        self.text_input_layout.add_widget(text_input)

    def submit_form(self, instance):
        # Add functionality to handle form submission (e.g., save data)
        # Access entered data from each text input field in the layout
        for i in range(0, len(self.text_input_layout.children), 2):
            label = self.text_input_layout.children[i]
            text_input = self.text_input_layout.children[i + 1]
            print(f"{label.text}: {text_input.text}")