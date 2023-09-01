import platform
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
# from kivymd.uix.boxlayout import MDBoxLayout
# from kivymd.uix.button import MDRoundFlatButton
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
                         '87', '88', '89', '93.5', '91', '93.5'} \
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


class PDF(FPDF):
    def center(self):
        self.cell(93.5, 30, 'Yeah',  align='C')


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

        def adres(my_add, num=0):
            if num:
                if len(my_add) >= 38:
                    w_btw_spaces = my_add.split(' ')
                    # first second third fourth fifth sixth
                    number_of_word_to_include_last = 0
                    for wn in range(len(w_btw_spaces)):
                        if len(" ".join(w_btw_spaces[:wn])) <= 40:
                            number_of_word_to_include_last = wn

                    before_space = " ".join(w_btw_spaces[:number_of_word_to_include_last])
                    after_space = " ".join(w_btw_spaces[number_of_word_to_include_last:])
                    if num == 1:
                        pdf.cell(95, 5, f"{before_space.title()}")
                    elif num == 2:
                        pdf.cell(95, 5, f"{after_space.title()}")
                else:
                    if num == 1:
                        pdf.cell(95, 5, f"{my_add.title()}")
                    elif num == 2:
                        pdf.cell(95, 5, f"")
            else:
                if len(my_add) >= 38:
                    w_btw_spaces = my_add.split(' ')
                    # first second third fourth fifth sixth
                    number_of_word_to_include_last = 0
                    for wn in range(len(w_btw_spaces)):
                        print("lent", len(" ".join(w_btw_spaces[:wn])))
                        if len(" ".join(w_btw_spaces[:wn])) <= 40:
                            number_of_word_to_include_last = wn

                    before_space = " ".join(w_btw_spaces[:number_of_word_to_include_last])
                    after_space = " ".join(w_btw_spaces[number_of_word_to_include_last:])
                    print("before space", before_space)
                    print("after space", after_space)
                    pdf.cell(95, 5, f"{before_space.title()}")
                    pdf.set_font('Sans_pro', '', 25)
                    pdf.cell(0.2, 14, f"", border=True)
                    pdf.cell(10, 14, f"")
                    pdf.set_font('Sans_pro', '', 14)
                    pdf.cell(95, 5, f"{before_space.title()}", ln=True)
                    pdf.cell(95, 5, f"{after_space.title()}")
                    pdf.cell(0.2, 14, f"", border=True)
                    pdf.cell(10, 14, f"")
                    pdf.set_font('Sans_pro', '', 14)
                    pdf.cell(95, 5, f"{after_space.title()}", ln=True)
                else:
                    pdf.cell(95, 5, f"{my_add.title()}")
                    pdf.set_font('Sans_pro', '', 25)
                    pdf.cell(0.2, 14, f"", border=True)
                    pdf.cell(10, 14, f"")
                    pdf.set_font('Sans_pro', '', 14)
                    pdf.cell(95, 5, f"{my_add.title()}", ln=True)
                    pdf.cell(95, 5, f"")
                    pdf.set_font('Sans_pro', '', 25)
                    pdf.cell(0.2, 14, f"", border=True)
                    pdf.cell(10, 14, f"")
                    pdf.set_font('Sans_pro', '', 14)
                    pdf.cell(95, 5, f"", ln=True)

        firstname = self.firstname.text
        surname = self.surname.text
        fathers_name = self.fathers_name.text
        pesel = self.pesel.text
        address = self.address.text
        number = self.number.text

        name_1 = self.name_1.text
        surname_1 = self.surname_1.text
        fathers_name_1 = self.fathers_name_1.text
        pesel_1 = self.pesel_1.text
        address_1 = self.address_1.text
        number_1 = self.number_1.text

        lp = '1'
        lp_1 = '2'
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()

        # page 1

        # Title
        pdf.add_font('Sans_pro', '', 'Sans_pro.otf', uni=True)
        pdf.set_font('Sans_pro', '', 18)
        pdf.cell(95, 5, f"Karta Ewakuacji Nr {lp.zfill(5)}")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 18)
        pdf.cell(95, 5, f"Karta Ewakuacji Nr {lp.zfill(5)}   B", ln=True)
        # surname
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"Nazwisko: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(75, 5, f"{surname.title()}")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"Nazwisko: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(75, 5, f"{surname.title()}", ln=True)
        # Names
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(30, 5, f"Imię, imię ojca: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(65, 5, f"{firstname.title()}, {fathers_name.title()}")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(30, 5, f"Imię, imię ojca: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(65, 5, f"{firstname.title()}, {fathers_name.title()}", ln=True)
        # Pesel
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"PESEL:")
        pdf.set_font('Sans_pro', '', 16)
        [pdf.cell(5, 5, f"{pesel[n]}", border=True) for n in range(11)]
        pdf.cell(20, 5, f"")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"PESEL:")
        pdf.set_font('Sans_pro', '', 16)
        [pdf.cell(5, 5, f"{pesel[n]}", border=True) for n in range(11)]
        pdf.cell(0, 5, "", ln=True)
        # Address
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"Adres stałego zamieszkania:")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"Adres stałego zamieszkania:", ln=True)
        pdf.set_font('Sans_pro', '', 14)
        adres(address)
        # Phone
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(39.5, 5, f"Telefon Kontaktowy: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(55.5, 5, f"{number}")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 10, f"", border=True)
        pdf.cell(11.5, 10, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(39.5, 5, f"Telefon Kontaktowy: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(54, 5, f"{number}", ln=True)
        # Issued by
        pdf.set_font('Sans_pro', '', 10)
        pdf.cell(80, 5, f"Organ wydający kartę: podpis, data:", align="C")
        pdf.cell(25, 5, f"")
        pdf.cell(80, 5, f"Organ wydający kartę: podpis, data:", align="C", ln=True)
        pdf.cell(80.5, 12,"", border=True)
        pdf.cell(14.5, 20, f"")
        pdf.cell(0.2, 25, f"", border=True)
        pdf.cell(11.5, 20, f"")
        pdf.cell(80.5, 12,f"", border=True, ln=True)
        pdf.cell(100, 2, "", ln=True)
        pdf.cell(25, 5, "")
        # Info
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(30, 5, f"Pouczenie", align="C")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(40, 12, f"")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 12, f"", border=True)
        pdf.cell(80.5, 5, f"-------------------------"*3, ln=True)
        pdf.cell(80.5, 3, "", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(90, 5, f"1. Kartę należy utrzymywać w ciągłej aktualnośći")
        pdf.cell(5, 5, f"")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 10, f"", border=True)
        pdf.cell(10, 5, f"",)
        # C part and info
        pdf.set_font('Sans_pro', '', 18)
        pdf.cell(95, 8, f"Karta Ewakuacji Nr {lp.zfill(5)}    C", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"Zmian i wpisów mogą dokonywać tylko")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 10, f"", border=True)
        pdf.cell(10, 5, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 6, f"Nazwisko: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(73.5, 6, f"{surname.title()}", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"uprawnione organy.")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(28.5, 5, f"Imię, imię ojca: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(65, 5, f"{firstname.title()}, {fathers_name.title()}", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"2. Karta jest ważna tylko z dokumentem")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"PESEL:")
        pdf.set_font('Sans_pro', '', 16)
        [pdf.cell(5, 5, f"{pesel[n]}", border=True) for n in range(11)]
        pdf.cell(20, 5, f"", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"tożsamości.")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"Adres stałego zamieszkania:", ln=True)
        pdf.cell(95, 5, f"3. Karta stanowi podstawę otrzymania")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        adres(address, 1)
        pdf.cell(18.5, 5, f"", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"przysługujących świadczeń.")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        adres(address, 2)
        pdf.cell(18.5, 5, f"", ln=True)
        pdf.cell(95, 5, f"")
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(39.5, 5, f"Telefon Kontaktowy: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(54, 5, f"{number}", ln=True)
        pdf.set_font('Sans_pro', '', 30)
        pdf.cell(95, 20, f"A", align="C")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 10)
        pdf.cell(80, 5, f"Organ wydający kartę: podpis, data:", align="C", ln=True)
        pdf.cell(95, 5, f"")
        pdf.set_font('Sans_pro', '', 10)
        pdf.cell(0.2, 18.7, f"", border=True)
        pdf.cell(11.5, 20, f"")
        pdf.cell(80.5, 12,f"", align="C", border=True, ln=True)
        pdf.cell(80.5, 5, f"_________" * 12,ln=True)
        # Doubling the part I but another info
        # Title
        pdf.set_font('Sans_pro', '', 18)
        pdf.cell(95, 10, f"Karta Ewakuacji Nr {lp_1.zfill(5)}")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 18)
        pdf.cell(95, 10, f"Karta Ewakuacji Nr {lp_1.zfill(5)}   B", ln=True)
        # surname
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"Nazwisko: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(75, 5, f"{surname_1.title()}")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"Nazwisko: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(75, 5, f"{surname_1.title()}", ln=True)
        # Names
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(30, 5, f"Imię, imię ojca: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(65, 5, f"{name_1.title()}, {fathers_name_1.title()}")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(30, 5, f"Imię, imię ojca: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(65, 5, f"{name_1.title()}, {fathers_name_1.title()}", ln=True)
        # Pesel
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"PESEL:")
        pdf.set_font('Sans_pro', '', 16)
        [pdf.cell(5, 5, f"{pesel_1[n]}", border=True) for n in range(11)]
        pdf.cell(20, 5, f"")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"PESEL:")
        pdf.set_font('Sans_pro', '', 16)
        [pdf.cell(5, 5, f"{pesel_1[n]}", border=True) for n in range(11)]
        pdf.cell(0, 5, "", ln=True)
        # Address
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"Adres stałego zamieszkania:")
        pdf.set_font('Sans_pro', '', 25)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"Adres stałego zamieszkania:", ln=True)
        pdf.set_font('Sans_pro', '', 14)
        adres(address_1)
        # Phone
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(39.5, 5, f"Telefon Kontaktowy: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(55.5, 5, f"{number_1}")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 10, f"", border=True)
        pdf.cell(11.5, 10, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(39.5, 5, f"Telefon Kontaktowy: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(54, 5, f"{number_1}", ln=True)
        # Issued by
        pdf.set_font('Sans_pro', '', 10)
        pdf.cell(80, 5, f"Organ wydający kartę: podpis, data:", align="C")
        pdf.cell(25, 5, f"")
        pdf.cell(80, 5, f"Organ wydający kartę: podpis, data:", align="C", ln=True)
        pdf.cell(80.5, 12,"", border=True)
        pdf.cell(14.5, 20, f"")
        pdf.cell(0.2, 25, f"", border=True)
        pdf.cell(11.5, 20, f"")
        pdf.cell(80.5, 12,f"", border=True, ln=True)
        pdf.cell(100, 2, "", ln=True)
        pdf.cell(25, 5, "")
        # Info
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(30, 5, f"Pouczenie", align="C")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(40, 12, f"")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 12, f"", border=True)
        pdf.cell(80.5, 5, f"-------------------------" * 3, ln=True)
        pdf.cell(80.5, 3, "", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(90, 5, f"1. Kartę należy utrzymywać w ciągłej aktualnośći")
        pdf.cell(5, 5, f"")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 10, f"", border=True)
        pdf.cell(10, 5, f"", )
        # C part and info
        pdf.set_font('Sans_pro', '', 18)
        pdf.cell(95, 8, f"Karta Ewakuacji Nr {lp_1.zfill(5)}    C", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"Zmian i wpisów mogą dokonywać tylko")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 10, f"", border=True)
        pdf.cell(10, 5, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 6, f"Nazwisko: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(73.5, 6, f"{surname_1.title()}", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"uprawnione organy.")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(28.5, 5, f"Imię, imię ojca: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(65, 5, f"{name_1.title()}, {fathers_name_1.title()}", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"2. Karta jest ważna tylko z dokumentem")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(20, 5, f"PESEL:")
        pdf.set_font('Sans_pro', '', 16)
        [pdf.cell(5, 5, f"{pesel_1[n]}", border=True) for n in range(11)]
        pdf.cell(20, 5, f"", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"tożsamości.")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"Adres stałego zamieszkania:", ln=True)
        pdf.cell(95, 5, f"3. Karta stanowi podstawę otrzymania")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        adres(address_1, 1)
        pdf.cell(18.5, 5, f"", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"przysługujących świadczeń.")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        adres(address_1, 2)
        pdf.cell(18.5, 5, f"", ln=True)
        pdf.cell(95, 5, f"")
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(39.5, 5, f"Telefon Kontaktowy: ")
        pdf.set_font('Sans_pro', '', 16)
        pdf.cell(54, 5, f"{number_1}", ln=True)
        pdf.set_font('Sans_pro', '', 30)
        pdf.cell(95, 10, f"A", align="C")
        pdf.set_font('Sans_pro', '', 14)
        # pdf.cell(0.2, 14, f"", border=True)
        pdf.set_font('Sans_pro', '', 10)
        pdf.cell(80, 5, f"Organ wydający kartę: podpis, data:", align="C", ln=True)
        pdf.cell(95, 5, f"")
        pdf.set_font('Sans_pro', '', 10)
        pdf.cell(0.2, 12, f"", border=True)
        pdf.cell(11.5, 10, f"")
        pdf.cell(80.5, 12, f"", align="C", border=True, ln=True)
        pdf.page()

        pdf.output('the_pdf.pdf')
        file_path = 'the_pdf.pdf'
        if os.path.exists(file_path):
            try:
                if platform.system() == 'Linux':  # Linux
                    print(os.path.abspath(file_path))
                    subprocess.call(('xdg-open', f"{os.path.abspath(file_path)}"))
                elif platform.system() == 'Windows':  # Windows
                    subprocess.run(f'start {os.path.abspath(file_path)}', shell=True)
                    # alternate ver without absolute path: subprocess.run(['start /wait /min, '', file_path],
                    # shell=True)
                elif platform.system() == 'Darwin':
                    subprocess.call(('open', file_path))
            except FileNotFoundError:
                print('File not found 404')
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
        self.surname.text = "Kowalski"
        self.firstname.text = "Josh"
        self.fathers_name.text = "Jakub"
        self.pesel.text = "11111111116"
        self.address.text = "Hetmana Stefana Czarnieckiego 24B/90C, 73-110, Stargard, woj. Zachodniopomorskie"
        self.number.text = "111222333"
        self.surname_1.text = "Dziadowska"
        self.name_1.text = "Jadwiga"
        self.fathers_name_1.text = "Władysław"
        self.pesel_1.text = "11122211113"
        self.address_1.text = "Kazimierza Wielkiego 83C/14, Stargard"
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
