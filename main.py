
import os
import subprocess
import sqlite3
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRoundFlatButton
from kivy.metrics import dp
from fpdf import FPDF


# pip install pyinstaller


def pesel_checker(pesel):
    try:
        int(pesel)
        len_ = len(pesel)
        if len_ < 11:
            return False
        elif len_ > 11:
            return False

        """
        sprawdza czy miesiąc nie jest zawarty w liście poprawnych miesięcy
        sprawdza czy w miesiącach 31 dniowych dzień jest poza skalą od 1 do 31 dni
        sprawdza czy w miesiącach 30 dniowych dzień jest poza skalą od 1 do 30 dni
        sprawdza czy dzień w lutym w roku nie przestępczym jest większy od 28
        sprawdza czy dzień w lutym w roku przestępczym jest większy od 29
        """

        year = pesel[0:2]
        month = pesel[2:4]
        day = pesel[4:6]

        if month not in {'01', '02', '03', '04', '05', '06',
                         '07', '08', '09', '10', '11', '12',
                         '21', '22', '23', '24', '25', '26',
                         '27', '28', '29', '30', '31', '32',
                         '41', '42', '43', '44', '45', '46',
                         '47', '48', '49', '50', '51', '52',
                         '61', '62', '63', '64', '65', '66',
                         '67', '68', '69', '70', '71', '72',
                         '81', '82', '83', '84', '85', '86',
                         '87', '88', '89', '90', '91', '92'} \
                or not int(pesel[2]) % 2 and pesel[3] in {'1', '3', '5', '7', '8'} and not int(day) in range(1, 32) \
                or int(pesel[2]) % 2 and pesel[3] in {'0', '2'} and not int(day) in range(1, 32) \
                or not int(pesel[2]) % 2 and pesel[3] in {'2', '4', '6', '9'} and not int(day) in range(1, 31) \
                or int(pesel[2]) % 2 and pesel[3] == '1' and not int(day) in range(1, 31) \
                or not int(year) % 4 and month in {'02', '22', '42', '62', '82'} and int(day) > 29 \
                or int(year) % 4 and month in {'02', '22', '42', '62', '82'} and int(day) > 28:
            return False

        weight = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
        total = sum([int(pesel[f]) * weight[f] for f in range(10)])
        mod = total % 10
        if mod == 0:
            right_control = 0
        else:
            right_control = 10 - mod

        control_num = int(pesel[10])
        print(f'suma wynosi: {total}')
        print(f'wpisana lk: {control_num}')
        print(f'poprawna lk: {right_control}')
        if control_num != right_control:
            return False
        return pesel

    except ValueError:
        return False


class WindowManager(ScreenManager):
    pass


class MainWindow(Screen):
    conn = sqlite3.connect('my.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE if not Exists osoby
            (
                lp integer,
                surname text, 
                name text,
                father text,
                pesel text, 
                address text, 
                phone text
            )""")
    conn.commit()
    conn.close()

    def excel_export(self):
        pass
        # choose the location where to save the exported file

    def csv_export(self):
        pass

    def db_export(self):
        pass

    def opens_printing(self):
        firstname = self.firstname.text
        surname = self.surname.text
        fathers_name = self.fathers_name.text
        pesel = self.pesel.text
        address = self.address.text
        number = self.number.text

        name_1 = self.firstname.text
        surname_1 = self.surname.text
        fathers_name_1 = self.fathers_name.text
        pesel_1 = self.pesel.text
        address_1 = self.address.text
        number_1 = self.number.text

        nr = '1'
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.add_font('Sans_pro', '', 'Sans_pro.otf', uni=True)
        pdf.set_font('Sans_pro', 'B', 16)
        pdf.cell(70, 10, f"Karta Ewakuacji Nr {nr.zfill(5)}", ln=True)
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(70, 10, f"Nazwisko: {surname.title()}", ln=True)
        pdf.cell(70, 10, f"Imię, imię ojca: {firstname.title()}, {fathers_name.title()}", ln=True)
        pdf.cell(20, 10, f"PESEL:")
        [pdf.cell(5, 9, f"{pesel[n]}", border=True) for n in range(11)]
        pdf.output('the_pdf.pdf')
        file_path = 'the_pdf.pdf'
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
        self.surname.fine = False
        self.firstname.fine = False
        self.fathers_name.fine = False
        self.pesel.fine = False
        self.address.fine = False
        self.number.fine = False
        self.surname_1.fine = False
        self.name_1.fine = False
        self.fathers_name_1.fine = False
        self.pesel_1.fine = False
        self.address_1.fine = False
        self.number_1.fine = False

        # do usubięcia
        self.surname.text = "janek"
        self.firstname.text = "franek"
        self.fathers_name.text = "franek"
        self.pesel.text = "11111111116"
        self.address.text = "franek"
        self.number.text = "111222333"
        self.surname_1.text = "franek"
        self.name_1.text = "franek"
        self.fathers_name_1.text = "franek"
        self.pesel_1.text = "11122211113"
        self.address_1.text = "11122211113"
        self.number_1.text = "333222111"
        # do usubięcia

        self.surname.text.title()
        # self.firstname.text = self.firstname.text.title()
        # self.fathers_name.text = self.fathers_name.text.title()
        # self.address.text = self.address.text.title()
        # self.surname_1.text = self.surname_1.text.title()
        # self.name_1.text = self.name_1.text.title()
        # self.fathers_name_1.text = self.fathers_name_1.text.title()
        # self.address_1.text = self.address_1.text.title()


        # print(locals())
        with self.surname.canvas.after:
            self.surname.canvas.after.clear()
            if self.surname.text:
                self.surname.fine = True
            else:
                self.surname.fine = False
                Color(1, 182/255, 20/255, 1)
                Line(rectangle=(self.surname.x, self.surname.y,
                                self.surname.width, self.surname.height),
                     width=2)

        with self.firstname.canvas.after:
            self.firstname.canvas.after.clear()
            if self.firstname.text:
                self.firstname.fine = True
            else:
                self.firstname.fine = False
                self.firstname.fine = False
                Color(1, 182/255, 20/255, 1)
                Line(rectangle=(self.firstname.x, self.firstname.y,
                                self.firstname.width, self.firstname.height),
                     width=2)
                
        with self.fathers_name.canvas.after:
            self.fathers_name.canvas.after.clear()
            if self.fathers_name.text:
                self.fathers_name.fine = True
            else:
                self.fathers_name.fine = False
                Color(1, 182/255, 20/255, 1)
                Line(rectangle=(self.fathers_name.x, self.fathers_name.y,
                                self.fathers_name.width, self.fathers_name.height),
                     width=2)

        with self.address.canvas.after:
            self.address.canvas.after.clear()
            if self.address.text:
                self.address.fine = True
            else:
                self.address.fine = False
                self.address.fine = False
                Color(1, 182/255, 20/255, 1)
                Line(rectangle=(self.address.x, self.address.y,
                                self.address.width, self.address.height),
                     width=2)
                
        with self.number.canvas.after:
            self.number.canvas.after.clear()
            if self.number.text:
                try:
                    self.number.foreground_color = (0, 0, 0, 1)
                    number = int(self.number.text)
                    self.number.background_color = 'white'
                    if len(str(number)) < 9 or len(str(number)) > 12:
                        self.number.fine = False
                        Color(1, 182/255, 20/255, 1)
                        Line(rectangle=(self.number.x, self.number.y,
                                        self.number.width, self.number.height),
                             width=2)
                    else:
                        self.number.fine = True
                except ValueError:
                    self.number.fine = False
                    Color(1, 182/255, 20/255, 1)
                    Line(rectangle=(self.number.x, self.number.y,
                                    self.number.width, self.number.height),
                         width=2)
            else:
                self.number.fine = False
                Color(1, 182/255, 20/255, 1)
                Line(rectangle=(self.number.x, self.number.y,
                                self.number.width, self.number.height),
                     width=2)
                
        with self.pesel.canvas.after:
            self.pesel.canvas.after.clear()
            if self.pesel.text:
                try:
                    int(self.pesel.text)
                    if pesel_checker(self.pesel.text):
                        self.pesel.fine = True
                    else:
                        self.pesel.fine = False
                        Color(1, 182/255, 20/255, 1)
                        Line(rectangle=(self.pesel.x, self.pesel.y,
                                        self.pesel.width, self.pesel.height),
                             width=2)
                except ValueError:
                    self.pesel.fine = False
                    Color(1, 182/255, 20/255, 1)
                    Line(rectangle=(self.pesel.x, self.pesel.y,
                                    self.pesel.width, self.pesel.height),
                         width=2)
            else:
                Color(1, 182/255, 20/255, 1)
                Line(rectangle=(self.pesel.x, self.pesel.y,
                                self.pesel.width, self.pesel.height),
                     width=2)

        with self.surname_1.canvas.after:
            self.surname_1.canvas.after.clear()
            if self.surname_1.text:
                self.surname_1.fine = True
            else:
                self.surname_1.fine = False
                Color(1, 182 / 255, 20 / 255, 1)
                Line(rectangle=(self.surname_1.x, self.surname_1.y,
                                self.surname_1.width, self.surname_1.height),
                     width=2)

        with self.name_1.canvas.after:
            self.name_1.canvas.after.clear()
            if self.name_1.text:
                self.name_1.fine = True
            else:
                self.name_1.fine = False
                self.name_1.fine = False
                Color(1, 182 / 255, 20 / 255, 1)
                Line(rectangle=(self.name_1.x, self.name_1.y,
                                self.name_1.width, self.firstname.height),
                     width=2)

        with self.fathers_name_1.canvas.after:
            self.fathers_name_1.canvas.after.clear()
            if self.fathers_name_1.text:
                self.fathers_name_1.fine = True
            else:
                self.fathers_name_1.fine = False
                Color(1, 182 / 255, 20 / 255, 1)
                Line(rectangle=(self.fathers_name_1.x, self.fathers_name_1.y,
                                self.fathers_name_1.width, self.fathers_name_1.height),
                     width=2)

        with self.address_1.canvas.after:
            self.address_1.canvas.after.clear()
            if self.address_1.text:
                self.address_1.fine = True
            else:
                self.address_1.fine = False
                self.address_1.fine = False
                Color(1, 182 / 255, 20 / 255, 1)
                Line(rectangle=(self.address_1.x, self.address_1.y,
                                self.address_1.width, self.address_1.height),
                     width=2)

        with self.number_1.canvas.after:
            self.number_1.canvas.after.clear()
            if self.number_1.text:
                try:
                    self.number_1.foreground_color = (0, 0, 0, 1)
                    number_1 = int(self.number_1.text)
                    self.number_1.background_color = 'white'
                    if len(str(number_1)) < 9 or len(str(number_1)) > 12:
                        self.number_1.fine = False
                        Color(1, 182 / 255, 20 / 255, 1)
                        Line(rectangle=(self.number_1.x, self.number_1.y,
                                        self.number_1.width, self.number_1.height),
                             width=2)
                    else:
                        self.number_1.fine = True
                except ValueError:
                    self.number_1.fine = False
                    Color(1, 182 / 255, 20 / 255, 1)
                    Line(rectangle=(self.number_1.x, self.number_1.y,
                                    self.number_1.width, self.number_1.height),
                         width=2)
            else:
                self.number_1.fine = False
                Color(1, 182 / 255, 20 / 255, 1)
                Line(rectangle=(self.number_1.x, self.number_1.y,
                                self.number_1.width, self.number_1.height),
                     width=2)

        with self.pesel_1.canvas.after:
            self.pesel_1.canvas.after.clear()
            if self.pesel_1.text:
                try:
                    int(self.pesel_1.text)
                    if pesel_checker(self.pesel_1.text):
                        self.pesel_1.fine = True
                    else:
                        self.pesel_1.fine = False
                        Color(1, 182 / 255, 20 / 255, 1)
                        Line(rectangle=(self.pesel_1.x, self.pesel_1.y,
                                        self.pesel_1.width, self.pesel_1.height),
                             width=2)
                except ValueError:
                    self.pesel_1.fine = False
                    Color(1, 182 / 255, 20 / 255, 1)
                    Line(rectangle=(self.pesel_1.x, self.pesel_1.y,
                                    self.pesel_1.width, self.pesel_1.height),
                         width=2)
            else:
                Color(1, 182 / 255, 20 / 255, 1)
                Line(rectangle=(self.pesel_1.x, self.pesel_1.y,
                                self.pesel_1.width, self.pesel_1.height),
                     width=2)

        if self.surname.fine and self.firstname.fine and self.fathers_name.fine and \
                self.pesel.fine and self.address.fine and self.number.fine and \
                self.surname_1.fine and self.name_1.fine and self.fathers_name_1.fine and \
                self.pesel_1.fine and self.address_1.fine and self.number_1.fine:
            self.print_btn.disabled = False
            self.save_btn.disabled = False
        else:
            self.print_btn.disabled = True
            self.save_btn.disabled = True

    def _on_keyboard_down(self, keycode):
        if self.surname.focus and keycode == 40:  # 40 - Enter key pressed
            self.firstname.focus = True

    def save_and_clear(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        insert_query = f"INSERT INTO osoby VALUES ('{self.surname.text.title()}','{self.firstname.text.title()}'," \
                       f"'{self.fathers_name.text.title()}', '{self.pesel.text}', '{self.address.text.title()}', " \
                       f"'{self.number.text}')"
        insert_query_2 = f"INSERT INTO osoby VALUES ('{self.surname_1.text.title()}','{self.name_1.text.title()}'," \
                         f"'{self.fathers_name_1.text.title()}', '{self.pesel_1.text}', '{self.address_1.text.title()}', " \
                         f"'{self.number_1.text}')"
        c.execute(insert_query)
        c.execute(insert_query_2)
        conn.commit()
        conn.close()
        self.print_btn.disabled = self.save_btn.disabled = True
        self.surname.text = self.firstname.text = self.fathers_name.text = self.pesel.text = self.address.text = \
            self.number.text = self.surname_1.text = self.name_1.text = self.fathers_name_1.text = self.number.text = \
            self.pesel_1.text = self.address_1.text = self.number_1.text = ''

    def show_people(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        select_query = f"SELECT * FROM osoby"
        c.execute(select_query)
        records = c.fetchall()
        word = ''
        for record in records:
            word = f'{word}/n{record}'
            self.nothing.text = word
        conn.commit()
        conn.close()


class TableWindow(Screen):
    # def __init__(self, **kwargs):
    #     super(TableWindow, self).__init__(**kwargs)
    #     table = MDDataTable(
    #         pos_hint={'center_x': 1, 'center_y': 0.5},
    #         size_hint=(1, 1),
    #         background_color_selected_cell="e4514f",
    #         column_data=[
    #             ("Nr Karty", dp(140)),
    #             ("Nazwisko", dp(140)),
    #             ("Imię", dp(140)),
    #             ("Imię ojca", dp(140)),
    #             ("PESEL", dp(140)),
    #             ("Nr telefonu", dp(140)),
    #         ],
    #         row_data=[
    #             ("1", "Hue", "Jaune", "Josh", "00000000000", "555555555")
    #         ]
    #     )
    #     self.mainbox.add_widget(table)
    #     print('widget added')

    def show_table(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        select_query = f"SELECT * FROM osoby"
        c.execute(select_query)
        records = c.fetchall()
        for record in records:
            print(record)
        conn.commit()
        conn.close()
        table = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(1, 1),
            background_color_selected_cell="e4514f",
            column_data=[
                ("Nr Karty", dp(25)),
                ("Nazwisko", dp(40)),
                ("Imię", dp(40)),
                ("Imię ojca", dp(40)),
                ("PESEL", dp(44)),
                ("Adres zamieszkania", dp(70)),
                ("Nr telefonu", dp(40)),
            ],
            row_data=[
                ("1", "Hue", "Jaune", "Josh", "00000000000", "555555555", "hmm")
            ]
        )
        self.mainbox.add_widget(table)


class EwakuacjaApp(MDApp):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        Window.maximize()
        self.theme_cls.theme_style = 'Dark'
        table_window = TableWindow()
        kv = Builder.load_file('my.kv')
        return kv

    def on_start(self):
        # Initialize the app here if needed
        pass


if __name__ == '__main__':
    EwakuacjaApp().run()
