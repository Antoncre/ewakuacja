
import os
import subprocess
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window

Builder.load_file('my.kv')


class TheLayout(Widget):
    surname = ObjectProperty(None)
    name = ObjectProperty(None)
    fathers_name = ObjectProperty(None)
    pesel = ObjectProperty(None)
    number = ObjectProperty(None)
    address = ObjectProperty(None)
    button = ObjectProperty(None)

    def opens_printing(self):
        name = self.name.text
        surname = self.surname.text
        print(name, surname)
        file_path = '115.pdf'

        if os.path.exists(file_path):
            try:
                subprocess.run(f'start /wait /min {os.path.abspath(file_path)}', shell=True)
                # alternate ver without absolute path: subprocess.run(['start /wait /min, '', file_path], shell=True)
                print("File sent to printer.")
            except Exception as e:
                print("Error printing file:", e)
        else:
            print("File not found.")

    def typer(self):
        self.button.disabled = True
        self.surname.fine = False
        self.name.fine = False
        self.fathers_name.fine = False
        self.pesel.fine = False
        self.address.fine = False
        self.number.fine = False

        # print(locals())
        if self.number.text:
            try:
                number = int(self.number.text)
                self.number.background_color = 'white'
                if len(str(number)) < 9 or len(str(number)) > 11:
                    self.number.background_color = 'yellow'
                else:
                    self.number.fine = True
            except ValueError:
                self.number.background_color = 'red'

        if self.number.fine:
            self.button.disabled = False

    def _on_keyboard_down(self, keycode):
        if self.surname.focus and keycode == 40:  # 40 - Enter key pressed
            self.name.focus = True


class EwakuacjaApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        Window.fullscreen = False
        Window.size = (1100, 800)
        return TheLayout()


if __name__ == '__main__':
    EwakuacjaApp().run()
