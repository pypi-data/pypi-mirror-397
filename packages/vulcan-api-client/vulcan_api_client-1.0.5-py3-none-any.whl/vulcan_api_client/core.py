from ast import literal_eval
import time
import re
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By

class Vulcan:
    def __init__(self, username, password, city, school, cookie=None):
        self.driver = webdriver.Chrome()
        self.session = requests.session()

        self.username = username
        self.password = password
        self.city = city
        self.school = school
        self.cookie = cookie

        if self.cookie is not True:
            self.driver.get(f'https://logowanie.edu.{self.city}.pl/LoginPage.aspx')
            time.sleep(1)
            self.driver.set_window_size(1920, 1080)

            # Defining fields and buttons at the start
            username_input = self.driver.find_element(By.ID, 'Username')
            username_input.send_keys(self.username)

            password_input = self.driver.find_element(By.ID, 'Password')
            password_input.send_keys(self.password)

            login_btn = self.driver.find_element(By.CSS_SELECTOR, 'button.submit-button.box-line')
            login_btn.click()

            # Simulating a regular user, so appropriate cookies will create
            self.driver.get(f'https://uonetplus.edu.{self.city}.pl/{self.city}/Start.mvc')
            self.driver.get(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/App')

            # Defining all the buttons first, so it'll get them already
            grades_btn = self.driver.find_element(By.ID, 'ext-element-209')
            presence_btn = self.driver.find_element(By.ID, 'ext-element-452')
            exams_btn = self.driver.find_element(By.ID, 'ext-element-579')
            behavior_btn = self.driver.find_element(By.ID, 'ext-element-628')
            pupil_bg_btn = self.driver.find_element(By.ID, 'ext-element-746')
            announcements_btn = self.driver.find_element(By.ID, 'ext-element-761')
            meetings_btn = self.driver.find_element(By.ID, 'ext-element-777')
            schedule_btn = self.driver.find_element(By.ID, 'ext-element-945')
            exams_and_hw_btn = self.driver.find_element(By.ID, 'ext-element-1159')
            school_and_teachers_btn = self.driver.find_element(By.ID, 'ext-element-1203')

            # Clicking said buttons
            presence_btn.click()
            grades_btn.click()
            behavior_btn.click()
            exams_btn.click()
            pupil_bg_btn.click()
            announcements_btn.click()
            meetings_btn.click()
            schedule_btn.click()
            exams_and_hw_btn.click()
            school_and_teachers_btn.click()

            # Getting and setting the cookies
            self.cookies = self.driver.get_cookies()
            self.driver.quit()
        elif self.cookie is True:
            self.cookies = literal_eval(open('.vulcan.cookie', 'r',encoding='utf-8').read())
        else:
            raise AttributeError(
                'Use True in the cookie variable while defining Vulcan() if you\'d like to read from a file (When export_cookies() is ran)',
                'Otherwise leave it empty. Please don\'t crash out - Maintainer :D'
                )

        for cookie in self.cookies:
            self.session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie.get('domain', '').lstrip('.'),
                path=cookie.get('path', '/')
            )

    def export_cookies(self):
        with open('./.vulcan.cookie','w', encoding='utf-8') as file:
            file.write(str(self.cookies))
        return 'DONE'

    def refresh_cookies(self):
        self.driver.get(f'https://logowanie.edu.{self.city}.pl/LoginPage.aspx')
        time.sleep(1)
        self.driver.set_window_size(1920, 1080)

        # Defining fields and buttons at the start
        username_input = self.driver.find_element(By.ID, 'Username')
        username_input.send_keys(self.username)

        password_input = self.driver.find_element(By.ID, 'Password')
        password_input.send_keys(self.password)

        login_btn = self.driver.find_element(By.CSS_SELECTOR, 'button.submit-button.box-line')
        login_btn.click()

        # Simulating a regular user, so appropriate cookies will create
        self.driver.get(f'https://uonetplus.edu.{self.city}.pl/{self.city}/Start.mvc')
        self.driver.get(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/App')

        # Defining all the buttons first, so it'll get them already
        grades_btn = self.driver.find_element(By.ID, 'ext-element-209')
        presence_btn = self.driver.find_element(By.ID, 'ext-element-452')
        exams_btn = self.driver.find_element(By.ID, 'ext-element-579')
        behavior_btn = self.driver.find_element(By.ID, 'ext-element-628')
        pupil_bg_btn = self.driver.find_element(By.ID, 'ext-element-746')
        announcements_btn = self.driver.find_element(By.ID, 'ext-element-761')
        meetings_btn = self.driver.find_element(By.ID, 'ext-element-777')
        schedule_btn = self.driver.find_element(By.ID, 'ext-element-945')
        exams_and_hw_btn = self.driver.find_element(By.ID, 'ext-element-1159') # Okay I digress, why the hell is this merger together on the website instead of making it with two categories? Less work for me I guess, but still kinda unintuitive.
        school_and_teachers_btn = self.driver.find_element(By.ID, 'ext-element-1203')

        # Clicking said buttons
        grades_btn.click()
        presence_btn.click()
        behavior_btn.click()
        exams_btn.click()
        pupil_bg_btn.click()
        announcements_btn.click()
        meetings_btn.click()
        schedule_btn.click()
        exams_and_hw_btn.click()
        school_and_teachers_btn.click()

        # Getting and setting the cookies
        self.cookies = self.driver.get_cookies()
        self.driver.quit()

        for cookie in self.cookies:
            self.session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie.get('domain', '').lstrip('.'),
                path=cookie.get('path', '/')
            )
    def get_classes(self, date):
        classes = []
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/PlanZajec.mvc/Get', data={"data": f"{date}T00:00"}, timeout=5).json()

        for rows in response['data']['Rows']:
            for cols in rows:
                description = cols['Description'].strip()
                formatted = description.replace('<div>','').replace('</div>','').replace('<span class=\'\'>','').replace('</span>','').replace('<span class=\'x-treelabel-ppl\'>','').replace('<br />',' ')
                hours = re.findall('\\d+ \\d+:\\d+ \\d+:\\d+', formatted)
                cleaned_text = formatted
                for h in hours:
                    cleaned_text = cleaned_text.replace(h, '')
                for items in formatted.split('\n'):
                    classes.append(items)

        monday = [classes[1], classes[7], classes[13], classes[19], classes[25], classes[31], classes[37], classes[43], classes[49], classes[55], classes[61], classes[67]]
        tuesday = [classes[2], classes[8], classes[14], classes[20], classes[26], classes[32], classes[38], classes[44], classes[50], classes[56], classes[62], classes[68]]
        wednesday = [classes[3], classes[9], classes[15], classes[21], classes[27], classes[33], classes[39], classes[45], classes[51], classes[57], classes[63], classes[69]]
        thursday = [classes[4], classes[10], classes[16], classes[21], classes[28], classes[34], classes[40], classes[46], classes[52], classes[58], classes[64], classes[70]]
        friday = [classes[5], classes[11], classes[17], classes[22], classes[29], classes[35], classes[41], classes[47], classes[53], classes[59], classes[65], classes[71]]
        hours = ['7.05 - 7.50','8.00 - 8.45', '8.55 - 9.40','9.50 - 10.35', '10.45 - 11.30', '11.50 - 12.35', '12.55 - 13.40', '13.50 - 14.35', '14.45 - 15.30', '15.40 - 16.25', '16.35 - 17.20', '17.30 - 18.15']

        return {
            "Monday": monday,
            "Tuesday": tuesday,
            "Wednesday": wednesday,
            "Thursday": thursday,
            "Friday": friday,
        }
    def get_grades(self, okres):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/Oceny.mvc/Get', data={"okres":okres}).json()
        return response['data']['Oceny'] # For the love of god don't parse this.

    def get_attendance(self, date):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/Frekwencja.mvc/Get',data={"idTypWpisuFrekwencji":-1,"data":f"{date}T00:00"}).json()
        return response['data']

    def get_behavior(self):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/UwagiIOsiagniecia.mvc/Get', data={}).json()
        return response['data']
    def get_pupil_bg(self, okres):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/StatystykiOcenyCzastkowe.mvc/Get', data={"idOkres":okres}).json()
        return response['data']
    def get_announcements(self):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/Ogloszenia.mvc/Get').json()
        return response['data']
    def get_meetings(self):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/Zebrania.mvc/Get').json()
        return response['data']
    def get_exams(self, date):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/Sprwadziany.mvc/Get', data={'data': f'{date}T00:00:00', 'rokSzkolny': time.localtime().tm_year}).json()
        return response['data']['SprawdzianyGroupedByDayList']
    def get_homework(self, date):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/Homework.mvc/Get', data={'data': f'{date}T00:00:00', 'rokSzkolny': time.localtime().tm_year, 'statusFilter': -1})
        return response['data']
    def get_school_and_teachers(self):
        response = self.session.post(f'https://uonetplus-uczen.edu.{self.city}.pl/{self.city}/{self.school}/SzkolaINauczyciele.mvc/Get', data={}).json()
        return response['data']
