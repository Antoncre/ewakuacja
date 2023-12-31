import platform
import subprocess
import sqlite3
import win32ui
import datetime
import pandas as pd
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
import os

os.environ['KIVY_NO_CONSOLELOG'] = '1'

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
        print(f'wpisana lk: {control_num}')
        print(f'poprawna lk: {right_control}')
        if control_num != right_control:
            return False
        return pesel

    except ValueError:
        return False


def base_el(l=False):
    conn = sqlite3.connect('my.db')
    c = conn.cursor()
    select_query = f"SELECT * FROM osoby"
    c.execute(select_query)
    records = c.fetchall()
    conn.close()
    if l:
        return len(records)
    else:
        return records


def gender(p):
    s = "Mężczyzna"
    if not int(p[9]) % 2:
        s = "Kobieta"
    return s


def chck_age(p):
    today = str(datetime.date.today()).replace('-', '')
    birth_date = f""
    y = p[0:2]
    m = p[2:4]
    d = p[4:6]
    match m[0]:
        case '0':
            birth_date = f'19{y}{m}{d}'
        case '1':
            birth_date = f'19{y}{m}{d}'
        case '2':
            birth_date = f'20{y}{str(int(m)-20).zfill(2)}{d}'
        case '3':
            birth_date = f'20{y}{str(int(m)-20).zfill(2)}{d}'
        case '4':
            birth_date = f'21{y}{str(int(m)-40).zfill(2)}{d}'
        case '5':
            birth_date = f'21{y}{str(int(m)-40).zfill(2)}{d}'
        case '6':
            birth_date = f'22{y}{str(int(m)-60).zfill(2)}{d}'
        case '7':
            birth_date = f'22{y}{str(int(m)-60).zfill(2)}{d}'
        case '8':
            birth_date = f'18{y}{str(int(m)-80).zfill(2)}{d}'
        case '9':
            birth_date = f'18{y}{str(int(m)-80).zfill(2)}{d}'

    diff = int(today) - int(birth_date)
    if diff < 0:
        return "Przed narodzeniem"
    if diff < 10000:
        return "Niemowlę"
    else:
        return int(str(diff)[:-4])


def export_xlsx(return_frame=False):
    dlg = win32ui.CreateFileDialog(0, 'xlsx', 'Ewakuacja - Stgargard - obszar 1', 0, '.xlsx||')
    lp = [l[0] for l in base_el()]
    s = [gender(l[4]) for l in base_el()]
    nm = [l[2] for l in base_el()]
    srnm = [l[1] for l in base_el()]
    p = [l[4] for l in base_el()]
    age = [chck_age(l[4]) for l in base_el()]
    address = [l[5] for l in base_el()]
    phone = [l[6] for l in base_el()]
    df1 = pd.DataFrame({'Nr karty ewakuacji': lp, 'Płeć': s, 'Imię': nm, 'Nazwisko': srnm, 'PESEL': p,
                        'Wiek': age, 'Adres': address,
                        'Rejon - miejsce skąd': ['' for _ in range(len(lp))],
                        'Rejon - miejsce dokąd': ['' for _ in range(len(lp))], 'Telefon': phone,
                        'Obrażenia': ['' for _ in range(len(lp))], 'Uwagi': ['' for f in range(len(lp))]})

    if return_frame:
        return df1
    dlg.DoModal()
    if '.xlsx' in dlg.GetPathName():
        df1.to_excel(dlg.GetPathName(), index=False, header=True)



class PDF(FPDF):
    def center(self):
        self.cell(93.5, 30, 'Yeah',  align='C')


class WindowManager(ScreenManager):
    pass


class MainWindow(Screen):
    @staticmethod
    def excel_export():
        export_xlsx()
        # TODO: dodać zmianę obszaru w ustawieniach i zmieniać jako element w bazie danych a tu jako zmienną

    @staticmethod
    def csv_export():
        df = export_xlsx(True)
        dlg = win32ui.CreateFileDialog(0, 'csv', 'Ewakuacja - Stgargard - obszar 1', 0, '.csv||')
        dlg.DoModal()
        if '.csv' in dlg.GetPathName():
            df.to_csv(dlg.GetPathName(), index=False, header=True, encoding='utf-8')

            # df = pd.read_csv(dlg.GetPathName(), encoding='utf-8')
            # print('CSV read', df)

    @staticmethod
    def json_export():
        df = export_xlsx(True)
        dlg = win32ui.CreateFileDialog(0, 'json', 'Ewakuacja - Stgargard - obszar 1', 0, '.json||')
        dlg.DoModal()
        if '.json' in dlg.GetPathName():
            df.to_json(dlg.GetPathName(), index=False)

            # df = pd.read_json(dlg.GetPathName())
            # print('Json read', df)

    def opens_printing(self, both=True, empty=False):

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
                        if len(" ".join(w_btw_spaces[:wn])) <= 40:
                            number_of_word_to_include_last = wn

                    before_space = " ".join(w_btw_spaces[:number_of_word_to_include_last])
                    after_space = " ".join(w_btw_spaces[number_of_word_to_include_last:])
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

        if '2' in self.il_os.text:
            both = False

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

        lp = str(base_el(True) + 1)
        lp_1 = str(base_el(True) + 2)

        if empty:
            surname = pesel = number = surname_1 = pesel_1 = number_1 = "__________"
            firstname = fathers_name = address = name_1 = fathers_name_1 = address_1 = ''
            lp = "_____"
            lp_1 = "_____"

        def a_1(text, text1='', al="", al1='', br=False, br1=False, sz=12.0, sz1=16.0, h=5.0, w1=20.0, w2=70.0):
            if text1:
                return (pdf.set_font('Sans_pro', '', sz),
                        pdf.cell(w1, h, text, border=br, align=al),
                        pdf.set_font('Sans_pro', '', sz1),
                        pdf.cell(w2, h, text1, border=br1, align=al1),
                        )
            else:
                return (pdf.set_font('Sans_pro', '', sz),
                        pdf.cell(95, h, text, align=al, border=br),
                    )

        def b_c(text, text1='', al="", al1="", br=False, br1=False, sz=12, sz1=16, h=5, w1=20.0, w2=70.0):
            if text1:
                return (pdf.set_font('Sans_pro', '', 12),
                        pdf.cell(0.2, h+5, f"", border=True),
                        pdf.cell(10, h, f""),
                        pdf.set_font('Sans_pro', '', sz),
                        pdf.cell(w1, h, text, border=br, align=al),
                        pdf.set_font('Sans_pro', '', sz1),
                        pdf.cell(w2, h, text1, border=br1, align=al1, ln=True),
                    )
            else:
                return (pdf.set_font('Sans_pro', '', 12),
                        pdf.cell(0.2, h+3, f"", border=True),
                        pdf.cell(10, h, f""),
                        pdf.set_font('Sans_pro', '', sz),
                        pdf.cell(93, h, text, align=al, border=br, ln=True)
                    )

        def pesel_text(num, p):
            if num == 1:
                pdf.set_font('Sans_pro', '', 12)
                pdf.cell(20, 5, f"PESEL:")
                pdf.set_font('Sans_pro', '', 16)
                if not empty:
                    [pdf.cell(5, 5, f"{p[n]}", border=True) for n in range(11)]
                else:
                    [pdf.cell(5, 5, "", border=True) for _ in range(11)]
                pdf.cell(20, 5, f"")
            elif num == 2:
                pdf.set_font('Sans_pro', '', 25)
                pdf.cell(0.2, 14, f"", border=True)
                pdf.cell(10, 14, f"")
                pdf.set_font('Sans_pro', '', 12)
                pdf.cell(20, 5, f"PESEL:")
                pdf.set_font('Sans_pro', '', 16)
                if not empty:
                    [pdf.cell(5, 5, f"{p[n]}", border=True) for n in range(11)]
                else:
                    [pdf.cell(5, 5, "", border=True) for _ in range(11)]
                pdf.cell(0, 5, "", ln=True)

        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.add_font('Sans_pro', '', 'Sans_pro.otf', uni=True)

        # page 1
        a_1("", h=5)
        b_c("", h=5)
        # Title
        a_1(f"Karta Ewakuacji Nr {lp.zfill(5)}", sz=18)
        b_c(f"Karta Ewakuacji Nr {lp.zfill(5)}   B", sz=18)
        # surname
        a_1('Nazwisko: ', text1=f"{surname.title()}", sz=12, sz1=16, w1=20, w2=75)
        b_c('Nazwisko: ', text1=f"{surname.title()}", sz=12, sz1=16, w1=20, w2=75)
        # Names
        if empty:
            a_1("Imię, imię ojca: ", text1=f"", sz=12, sz1=16, w1=20, w2=75)
            b_c("Imię, imię ojca: ", text1=f"", sz=12, sz1=16, w1=20, w2=75)
        else:
            a_1("Imię, imię ojca: ", text1=f"{firstname.title()}, {fathers_name.title()}", sz=12, sz1=16, w1=30, w2=65)
            b_c("Imię, imię ojca: ", text1=f"{firstname.title()}, {fathers_name.title()}", sz=12, sz1=16, w1=30, w2=65)
        # Pesel
        pesel_text(1, pesel)
        pesel_text(2, pesel)
        # Address
        a_1('Adres stałego zamieszkania:', sz=12)
        b_c('Adres stałego zamieszkania:', sz=12)
        adres(address)
        # Phone
        a_1(f"Telefon Kontaktowy: ", text1=f"{number}", sz=12, sz1=16, w1=39.5, w2=55.5)
        b_c(f"Telefon Kontaktowy: ", text1=f"{number}", sz=12, sz1=16, w1=39.5, w2=55.5)
        # Issued by
        a_1(f"Organ wydający kartę: podpis, data:", text1=' ', sz=10,  w1=80.5, w2=14.5, al='C')
        b_c(f"Organ wydający kartę: podpis, data:", text1=' ', sz=10,  w1=80.5, w2=14.5, al='C')
        a_1(f"", text1=' ', br=True, h=10, w1=80.5, w2=14.5)
        b_c(f"", text1=' ', br=True, h=10, w1=80.5, w2=14.5)
        # Info
        pdf.cell(100, 2, "", ln=True)
        a_1('Pouczenie', text1=' ', w1=85, w2=10, sz=16, al="C")
        pdf.cell(0.2, 12, f"", border=True)
        pdf.cell(80.5, 5, f"-------------------------"*3, ln=True)
        pdf.cell(80.5, 3, "", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        a_1("1. Kartę należy utrzymywać w ciągłej aktualnośći", w1=95)
        # C part and info
        b_c(f"Karta Ewakuacji Nr {lp.zfill(5)}    C", sz=18, h=8)
        a_1("Zmian i wpisów mogą dokonywać tylko", w1=95)
        b_c('Nazwisko: ', text1=f"{surname.title()}", sz=12, sz1=16, w1=20, w2=75)
        # Names
        if empty:
            a_1("uprawnione organy", w1=95)
            b_c("Imię, imię ojca: ", text1=f"", sz=12, sz1=16, w1=20, w2=75)
        else:
            a_1("uprawnione organy", w1=95)
            b_c("Imię, imię ojca: ", text1=f"{firstname.title()}, {fathers_name.title()}", sz=12, sz1=16, w1=30, w2=65)
        # Pesel
        a_1("2. Karta jest ważna tylko z dokumentem", w1=95)
        pesel_text(2, pesel)
        # Address
        a_1('tożsamości.', sz=12)
        b_c('Adres stałego zamieszkania:', sz=12)
        a_1("3. Karta stanowi podstawę otrzymania", w1=95)
        pdf.cell(0.2, 14, border=True)
        pdf.cell(10, 14, f"")
        adres(address, 1)
        pdf.cell(18.5, 5, f"", ln=True)
        pdf.set_font('Sans_pro', '', 12)
        pdf.cell(95, 5, f"przysługujących świadczeń.")
        pdf.set_font('Sans_pro', '', 14)
        pdf.cell(0.2, 14, f"", border=True)
        pdf.cell(10, 14, f"")
        adres(address, 2)
        # Phone
        a_1("przysługujących świadczeń", w1=95)
        b_c(f"Telefon Kontaktowy: ", text1=f"{number}", sz=12, sz1=16, w1=39.5, w2=55.5)
        # Issued by
        a_1(f"A", h=20, sz=30, al='C')
        b_c(f"Organ wydający kartę: podpis, data:", text1=' ', sz=10, w1=80.5, w2=14.5, al='C')
        a_1(f"")
        b_c(f"", text1=' ', br=True, h=10, w1=80.5, w2=14.5)
        pdf.cell(80.5, 5, f"_________" * 12,ln=True)
        a_1(f"", h=15)
        b_c(f"", h=15)
        if both:
            # Doubling the part I but another info
            # Title
            a_1(f"Karta Ewakuacji Nr {lp_1.zfill(5)}", sz=18)
            b_c(f"Karta Ewakuacji Nr {lp_1.zfill(5)}   B", sz=18)
            # surname
            a_1('Nazwisko: ', text1=f"{surname_1.title()}", sz=12, sz1=16, w1=20, w2=75)
            b_c('Nazwisko: ', text1=f"{surname_1.title()}", sz=12, sz1=16, w1=20, w2=75)
            # Names
            if empty:
                a_1("Imię, imię ojca: ", text1=f"", sz=12, sz1=16, w1=20, w2=75)
                b_c("Imię, imię ojca: ", text1=f"", sz=12, sz1=16, w1=20, w2=75)
            else:
                a_1("Imię, imię ojca: ", text1=f"{name_1.title()}, {fathers_name_1.title()}", sz=12, sz1=16, w1=30,
                    w2=65)
                b_c("Imię, imię ojca: ", text1=f"{name_1.title()}, {fathers_name_1.title()}", sz=12, sz1=16, w1=30,
                    w2=65)
            # Pesel
            pesel_text(1, pesel_1)
            pesel_text(2, pesel_1)
            # Address
            a_1('Adres stałego zamieszkania:', sz=12)
            b_c('Adres stałego zamieszkania:', sz=12)
            adres(address_1)
            # Phone
            a_1(f"Telefon Kontaktowy: ", text1=f"{number_1}", sz=12, sz1=16, w1=39.5, w2=55.5)
            b_c(f"Telefon Kontaktowy: ", text1=f"{number_1}", sz=12, sz1=16, w1=39.5, w2=55.5)
            # Issued by
            a_1(f"Organ wydający kartę: podpis, data:", text1=' ', sz=10, w1=80.5, w2=14.5, al='C')
            b_c(f"Organ wydający kartę: podpis, data:", text1=' ', sz=10, w1=80.5, w2=14.5, al='C')
            a_1(f"", text1=' ', br=True, h=10, w1=80.5, w2=14.5)
            b_c(f"", text1=' ', br=True, h=10, w1=80.5, w2=14.5)
            # Info
            pdf.cell(100, 2, "", ln=True)
            a_1('Pouczenie', text1=' ', w1=85, w2=10, sz=16, al="C")
            pdf.cell(0.2, 12, f"", border=True)
            pdf.cell(80.5, 5, f"-------------------------" * 3, ln=True)
            pdf.cell(80.5, 3, "", ln=True)
            pdf.set_font('Sans_pro', '', 12)
            a_1("1. Kartę należy utrzymywać w ciągłej aktualnośći", w1=95)
            # C part and info
            b_c(f"Karta Ewakuacji Nr {lp_1.zfill(5)}    C", sz=18, h=8)
            a_1("Zmian i wpisów mogą dokonywać tylko", w1=95)
            b_c('Nazwisko: ', text1=f"{surname_1.title()}", sz=12, sz1=16, w1=20, w2=75)
            # Names
            if empty:
                a_1("uprawnione organy", w1=95)
                b_c("Imię, imię ojca: ", text1=f"", sz=12, sz1=16, w1=20, w2=75)
            else:
                a_1("uprawnione organy", w1=95)
                b_c("Imię, imię ojca: ", text1=f"{name_1.title()}, {name_1.title()}", sz=12, sz1=16, w1=30,
                    w2=65)
            # Pesel
            a_1("2. Karta jest ważna tylko z dokumentem", w1=95)
            pesel_text(2, pesel_1)
            # Address
            a_1('tożsamości.', sz=12)
            b_c('Adres stałego zamieszkania:', sz=12)
            a_1("3. Karta stanowi podstawę otrzymania", w1=95)
            pdf.cell(0.2, 14, border=True)
            pdf.cell(10, 14, f"")
            adres(address, 1)
            pdf.cell(18.5, 5, f"", ln=True)
            pdf.set_font('Sans_pro', '', 12)
            pdf.cell(95, 5, f"przysługujących świadczeń.")
            pdf.set_font('Sans_pro', '', 14)
            pdf.cell(0.2, 14, f"", border=True)
            pdf.cell(10, 14, f"")
            adres(address, 2)
            # Phone
            a_1("przysługujących świadczeń", w1=95)
            b_c(f"Telefon Kontaktowy: ", text1=f"{number_1}", sz=12, sz1=16, w1=39.5, w2=55.5)
            # Issued by
            a_1(f"A", h=20, sz=30, al='C')
            b_c(f"Organ wydający kartę: podpis, data:", text1=' ', sz=10, w1=80.5, w2=14.5, al='C')
            a_1(f"")
            b_c(f"", text1=' ', br=True, h=10, w1=80.5, w2=14.5)
            pdf.cell(80.5, 5, f"_________" * 12, ln=True)
        # Second page
        # Living place
        pdf.add_page()
        pdf.set_font('Sans_pro', '', 12)

        def a_2(text, al="", br="LR", sz=12, h=7):
            return (pdf.set_font('Sans_pro', '', sz),
                    pdf.cell(0.2, h+3, f"", border=True),
                    pdf.cell(5.5, h, f""),
                    pdf.cell(93, h, text, align=al, border=br, ln=True)
                    )

        def b_2(text, sz=12, al="", br="", h=7):
            return (pdf.set_font('Sans_pro', '', sz),
                    pdf.cell(90, h, text, border=br, align=al),
                    pdf.cell(5, h, "")
                    )

        def c_2(text, sz=12, al="", br="", h=7):
            return (pdf.set_font('Sans_pro', '', sz),
                    pdf.cell(95, h, text, align=al, border=br)
                    )

        def signed(p):
            s = "podpisany"
            if empty:
                s = "podpisany(a)"
            else:
                if not int(p[9]) % 2:
                    s = "podpisana"
            return s

        c_2(f"Adres miejsca zakwaterowania..........................")
        a_2(f"Adres miejsca zakwaterowania..........................", br='')
        c_2(f"..............."*5)
        a_2(f"..............."*5, br='')
        b_2('B', sz=20, al="C", br='LTR', h=20)
        a_2(f"A", al="C", br='LTR', h=20, sz=20)
        b_2('', sz=20, al="C", br='LBR', h=26)
        a_2(f"", al="C", br='LR', sz=20, h=26)

        c_2(f"___________"*4, sz=12)

        a_2(f"Ja niżej {signed(pesel)} {surname.title()} {firstname.title()}")
        c_2("Adres miejsca zakwaterowania..........................")
        a_2(f"w dniu ____20__ r. odmawiam poddania się")
        c_2(f"..............."*5)
        a_2(f"procesowi ewakuacji")
        b_2("Adnotacje", h=10, br="LTR")
        a_2(f"Podpis:____________", al="R", br="LR")
        b_2("C", h=10, br="LR", sz=20, al="C")
        a_2(f"")
        b_2(f"Ja niżej {signed(pesel)} {surname.title()} {firstname.title()}", br="LR")
        a_2(f"Nie dotyczy w przypadku obowiązków nałożonych")
        b_2(f"w dniu ____20__ r. odmawiam poddania się", br="LR")
        a_2(f"na obywateli zapisami w ustawie o klęsce")
        b_2(f"procesowi ewakuacji", br="LR")
        a_2(f"żywiołowej, stanie wyjątkowym oraz wojennym")
        b_2(f"Podpis:____________", al="R", br="LBR", h=10)
        a_2(f"", br="LBR", h=10)
        pdf.cell(95, 4, "-----"*14, align='C')
        pdf.cell(0.2, 4, "", align='C', border=True)
        pdf.cell(100, 4, "-----"*14, align='C', ln=True)

        if both:
            # 2nd part of 2nd page
            c_2("", h=5, br='')
            a_2("", h=5, br='')
            c_2(f"Adres miejsca zakwaterowania..........................")
            a_2(f"Adres miejsca zakwaterowania..........................", br='')
            c_2(f"..............." * 5)
            a_2(f"..............." * 5, br='')
            b_2('B', sz=20, al="C", br='LTR', h=20)
            a_2(f"A", al="C", br='LTR', h=20, sz=20)
            b_2('', sz=20, al="C", br='LBR', h=26)
            a_2(f"", al="C", br='LR', sz=20, h=26)

            c_2(f"___________" * 4, sz=12)

            a_2(f"Ja niżej {signed(pesel_1)} {surname_1.title()} {name_1.title()}")
            c_2("Adres miejsca zakwaterowania..........................")
            a_2(f"w dniu ____20__ r. odmawiam poddania się")
            c_2(f"..............." * 5)
            a_2(f"procesowi ewakuacji")
            b_2("Adnotacje", h=10, br="LTR")
            a_2(f"Podpis:_____________", al="R", br="LR")
            b_2("C", h=10, br="LR", sz=20, al="C")
            a_2(f"")
            b_2(f"Ja niżej {signed(pesel_1)} {surname_1.title()} {name_1.title()}", br="LR")
            a_2(f"Nie dotyczy w przypadku obowiązków nałożonych")
            b_2(f"w dniu ____20__ r. odmawiam poddania się", br="LR")
            a_2(f"na obywateli zapisami w ustawie o klęsce")
            b_2(f"procesowi ewakuacji", br="LR")
            a_2(f"żywiołowej, stanie wyjątkowym oraz wojennym")
            b_2(f"Podpis:_____________", al="R", br="LBR")
            a_2(f"", br="LBR")
            pdf.cell(95, 4, "-----" * 14, align='C')
            pdf.cell(0.2, 4, "", align='C', border=True)
            pdf.cell(100, 4, "-----" * 14, align='C', ln=True)

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
        # self.surname.text = "Kowalski"
        # self.firstname.text = "Jan"
        # self.fathers_name.text = "Jakub"
        # self.pesel.text = "22292911118"
        # self.address.text = "Hetmana Stefana Czarnieckiego 240B/90F, 73-110, Stargard"
        # self.number.text = "111222333"
        # self.surname_1.text = "Wzorowa"
        # self.name_1.text = "Jadwiga"
        # self.fathers_name_1.text = "Władysław"
        # self.pesel_1.text = "31242211123"
        # self.address_1.text = "Kazimierza Wielkiego 183C/40A, 73-110, Stargard"
        # self.number_1.text = "333222111"
        # do usubięcia

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
                self.pesel_1.fine and self.address_1.fine and self.number_1.fine\
                or self.surname.fine and self.firstname.fine and self.fathers_name.fine and \
                self.pesel.fine and self.address.fine and self.number.fine and "2" in self.il_os.text:
            self.print_btn.disabled = False
        else:
            self.print_btn.disabled = True
            self.save_btn.disabled = True

    def il_os_f(self):
        if "1" in self.il_os.text:
            self.il_os.text = "-> 2 os"
            self.second_form.pos_hint = {'x': 0, 'y': -2}
            self.second_form.size_hint = (0.05, 0)
        else:
            self.il_os.text = "-> 1 os"
            self.second_form.pos_hint = {'x': 0, 'y': 0}
            self.second_form.size_hint = (1, 1)

    def enable_printing(self):
        self.save_btn.disabled = False
        self.il_os.disabled = True

    def _on_keyboard_down(self, keycode):
        if self.surname.focus and keycode == 40:  # 40 - Enter key pressed
            self.firstname.focus = True

    def save_and_clear(self):
        conn = sqlite3.connect('my.db')
        c = conn.cursor()
        insert_query = f"INSERT INTO osoby VALUES ('{base_el(True)+1}', '{self.surname.text.title()}', '{self.firstname.text.title()}'," \
                       f"'{self.fathers_name.text.title()}', '{self.pesel.text}', '{self.address.text.title()}', " \
                       f"'{self.number.text}')"
        insert_query_2 = f"INSERT INTO osoby VALUES ('{base_el(True)+2}', '{self.surname_1.text.title()}','{self.name_1.text.title()}'," \
                         f"'{self.fathers_name_1.text.title()}', '{self.pesel_1.text}', '{self.address_1.text.title()}', " \
                         f"'{self.number_1.text}')"
        c.execute(insert_query)
        if "1" in self.il_os.text:
            c.execute(insert_query_2)
        conn.commit()
        conn.close()
        self.print_btn.disabled = self.save_btn.disabled = True
        self.il_os.disabled = False
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
        rws = [record for record in records]
        conn.commit()
        conn.close()
        table = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            check=True,
            background_color_selected_cell="e4514f",
            background_color="000000",
            column_data=[
                ("Nr Karty", dp(40)),
                ("Nazwisko", dp(55)),
                ("Imię", dp(55)),
                ("Imię ojca", dp(55)),
                ("PESEL", dp(55)),
                ("Adres zamieszkania", dp(120)),
                ("Nr telefonu", dp(40)),
            ],
            row_data=rws
        )
        self.mainbox.add_widget(table)

    class Table(MDApp):
        def build(self):
            Window.clearcolor = (0, 0, 0, 1)
            Window.maximize()
            self.theme_cls.theme_style = 'Dark'
            kv = Builder.load_file('my.kv')
            table_window = TableWindow()
            table_window.show_table()
            return kv


class EwakuacjaApp(MDApp):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        Window.maximize()
        self.theme_cls.theme_style = 'Dark'
        kv = Builder.load_file('my.kv')
        table_window = TableWindow()
        table_window.show_table()
        return kv

    def on_start(self):
        # Initialize the app here if needed
        pass


if __name__ == '__main__':
    EwakuacjaApp().run()
