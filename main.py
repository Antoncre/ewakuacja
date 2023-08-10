
import os
import subprocess
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty


class TheLayout(Widget):
    surname = ObjectProperty(None)
    name = ObjectProperty(None)
    fathers_name = ObjectProperty(None)
    pesel = ObjectProperty(None)
    number = ObjectProperty(None)
    adres = ObjectProperty(None)
    burron = ObjectProperty(None)
    def opens_printing(self):
        name = self.name.text
        surname = self.surname.text
        print(name, surname)
        file_path = '115.pdf'  # Replace with the actual file path

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
        self.number.fine = False
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


class MyApp(App):
    def build(self):
        return TheLayout()


if __name__ == '__main__':
    MyApp().run()