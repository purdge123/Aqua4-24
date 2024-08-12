from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '640')
from kivy.uix.screenmanager import ScreenManager
from home.Home_Screen import HomeScreen
from addtank.AddTank_Screen import  AddTankScreen
from signup.Signup_Screen import SignupScreen
from login.Login_Screen import LoginScreen
from scan.Scan_Screen import ScanScreen
from contact.CONTACT_Screen import  ContactScreen
from help.HELP_Screen import  HelpScreen
from kivymd.app import MDApp


class LoginSignupApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(SignupScreen(name='signup_screen'))
        sm.add_widget(HomeScreen(name='home_screen'))
        sm.add_widget(AddTankScreen(name='add_tank_screen'))
        sm.add_widget(ContactScreen(name='contact_screen'))
        sm.add_widget(HelpScreen(name='help_screen'))
        sm.add_widget(ScanScreen(name='scan_screen'))

        
        return sm


if __name__ == "__main__":
    LoginSignupApp().run()