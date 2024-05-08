from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from home.Home_Screen import HomeScreen
from addtank.AddTank_Screen import  AddTankScreen
from signup.Signup_Screen import SignupScreen
from login.Login_Screen import LoginScreen
from chat.CHAT_Screen import  ChatScreen


class LoginSignupApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(SignupScreen())
        sm.add_widget(HomeScreen())
        sm.add_widget(AddTankScreen())
        sm.add_widget(ChatScreen())

        
        return sm


if __name__ == "__main__":
    LoginSignupApp().run()