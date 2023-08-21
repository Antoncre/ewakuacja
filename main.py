
import os
import subprocess
import sqlite3
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.core.window import Window

# pip install pyinstaller

Builder.load_file('my.kv')

Window.clearcolor = (0, 0, 0, 1)
Window.fullscreen = False
Window.size = (Window.height, Window.width)


class TheLayout(Widget):
    conn = sqlite3.connect('my.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE if not Exists osoby
            (
                surname text, 
                name text,
                father text,
                pesel text, 
                address text, 
                phone text
            )""")
    conn.commit()
    conn.close()

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
            conn = sqlite3.connect('my.db')
            c = conn.cursor()
            INSERT_QUERY = f"INSERT INTO osoby VALUES ('{self.surname.text}','{self.name.text}'," \
                           f"'{self.fathers_name.text}', '{self.pesel.text}', '{self.address.text}', " \
                           f"'{self.number.text}')"
            c.execute(INSERT_QUERY)
            conn.commit()
            conn.close()

    def _on_keyboard_down(self, keycode):
        if self.surname.focus and keycode == 40:  # 40 - Enter key pressed
            self.name.focus = True

    def show_people(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        SELECT_QUERY = f"SELECT * FROM osoby"
        c.execute(SELECT_QUERY)
        records = c.fetchall()
        word = ''
        for record in records:
            word = f'{word}/n{record}'
            self.nothing.text = word
            print(word)
        conn.commit()
        conn.close()


class EwakuacjaApp(App):
    def build(self):
        return TheLayout()


if __name__ == '__main__':
    EwakuacjaApp().run()
