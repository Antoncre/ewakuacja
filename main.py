import kivy

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class Layout(GridLayout):
    def __init__(self, **kwargs):
        super(Layout, self).__init__(**kwargs)
        self.cols = 1
        self.add_widget(Label(text="Imię", font_size=54, color='green'))
        self.name = TextInput(multiline=False, font_size=33)
        self.add_widget(self.name)
        self.add_widget(Label(text="Nazwisko", font_size=54, color='green'))
        self.surname = TextInput(multiline=False)
        self.add_widget(self.surname)
        self.submit = Button(text='Drukuj')
        self.add_widget(self.submit)


class MyApp(App):
    def build(self):
        return Layout()


if __name__ == '__main__':
    MyApp().run()