from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLCDNumber, QPushButton
from PyQt5.QtCore import QTimer, QTime, QDateTime

import design
import sheet
import webbrowser


class Clock(QtWidgets.QMainWindow, design.Ui_MainWindow, QLCDNumber):

    text = ''
    max_delta = 0
    def __init__(self):

        super().__init__()

        self.setupUi(self)
        self.gsheet = sheet.GoogleSheet()
        title = "Days without coronavirus..."
        self.setWindowTitle(title)
        self.lcdNumber.setSegmentStyle(QLCDNumber.Filled)
        self.btnReset.clicked.connect(self.to_null)
        self.btnOpenData.clicked.connect(self.open_data)

        timer = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(1000)

        timer_send = QTimer(self)
        timer_send.timeout.connect(self.send_delta_max)
        timer_send.start(10000)

        self.last_date = self.get_date()

        self.sec_start = QDateTime.currentSecsSinceEpoch()
        self.sec_last = self.sec_start
        self.delta = 0
        self.set_delta(self.sec_start, self.sec_last)
        self.max_delta = self.delta
        self.was_null = False
        self.new_max = False

    def to_null(self):
        """
        Обнуляет счетчик и отправляет данные в таблиц
        """

        self.was_null = True
        self.last_date = self.get_date()
        self.sec_last = self.sec_start
        self.gsheet.send_data('A5', 'F5', [list(self.last_date.values())])
        self.gsheet.send_data('A3', 'F3', [list(self.get_values(self.delta).values())])

    def open_data(self):
        """
        Вызывается при нажатии кнопки и открывает таблицу с данными в браузере

        """
        url = 'https://docs.google.com/spreadsheets/d/' + self.gsheet.spreadsheetId
        webbrowser.open(url)

    def format_date(self, yrs, mns, days, hrs, mints, secs):
        """
        Форматирует дату, убирая оттуда нулевые значения для нормального отображения в приложении

        :param yrs: количество лет
        :param mns: количество месяцев
        :param days: количество дней
        :param hrs: количество часов
        :param mints: количество минут
        :param secs: количество секунд
        :return: Отформатированная строка с данными
        """

        if int(yrs) != 0:
            res = yrs + ' ' + mns + ' ' + days + ' ' + hrs \
                  + ':' + mints + ':' + secs

            if int(yrs) < 10:
                digit_count = 16

            else:
                if int(yrs) < 100:
                    digit_count = 17
                else:
                    digit_count = 19

        else:
            if int(mns) != 0:
                res = mns + ' ' + days + ' ' + hrs \
                      + ':' + mints + ':' + secs
                digit_count = 14

            else:
                if int(days) != 0:
                    res = days + ' ' + hrs \
                          + ':' + mints + ':' + secs
                    digit_count = 11

                else:
                    if int(hrs) != 0:
                        res = hrs + ':' + mints + ':' + secs
                        digit_count = 8

                    else:
                        res = mints + ':' + secs
                        digit_count = 5
        self.lcdNumber.setDigitCount(digit_count)
        return res

    def send_delta_max(self):
        """
        Записывает в таблицу максимум счетчика за все время

        """
        self.gsheet.send_data('A3', 'F3', [list(self.get_values(self.delta).values())])

        if self.new_max:
            self.gsheet.send_data('A8', 'F8', [list(self.get_values(self.max_delta).values())])
            self.new_max = False

    def check_max(self):
        """
        Обновляет значение максимума
        """
        if self.delta > self.max_delta:
            self.max_delta = self.delta
            self.new_max = True

    def set_delta(self,  now_time, last_time):
        """
        Высчитвает разницу между now_time и  last_time и записывает ее в self.delta

        :param now_time: настоящее время
        :param last_time: время последнего обнуления счетчика

        """
        self.delta = now_time - last_time
        self.check_max()

    def show_time(self):
        """
        Отображает self.delta в приложении

        """
        self.sec_start = QDateTime.currentSecsSinceEpoch()
        self.set_delta(self.sec_start, self.sec_last)
        res = self.format_date(
            self.get_values(self.delta).get('Year'),
            self.get_values(self.delta).get('Month'),
            self.get_values(self.delta).get('Day'),
            self.get_values(self.delta).get('Hours'),
            self.get_values(self.delta).get('Minutes'),
            self.get_values(self.delta).get('Seconds')

            )

        self.lcdNumber.display(res)

    def get_values(self, value):
        """
        переводит время из секунд с начала эпохи в обычный формат

        :param value: время для перевода в секундах
        """
        v_secs = str(value % 60)
        v_mints = str(value % 3600 // 60)
        v_hrs = str(value % (3600 * 24) // 3600)
        v_days = str((value % (3600 * 24 * 30) // (3600 * 24)))
        v_mons = str((value % (3600 * 24 * 365) // (3600 * 24 * 30)))  # TODO сделать только дни!
        v_yrs = str(value // (3600 * 24 * 365))

        return {
            'Year': v_yrs,
            'Month': v_mons,
            'Day': v_days,
            'Hours': v_hrs,
            'Minutes': v_mints,
            'Seconds': v_secs,
        }

    def make_sec_from_list(self, gs_data):
        """
        Переводит время из строки в секунды с начала эпохи

        :param gs_data: массив данных из таблицы
        """
        row = gs_data[0]
        date_time = QDateTime.fromString(' '.join(row), "yyyy MM dd hh mm ss")
        return QDateTime.toSecsSinceEpoch(date_time)

    @staticmethod
    def get_date():
        """
        Получает текущуие дату и время
        :return:
        """
        return {
            'Year': QDateTime.currentDateTime().toString("yyyy"),
            'Month': QDateTime.currentDateTime().toString("MM"),
            'Day': QDateTime.currentDateTime().toString("dd"),
            'Hours': QDateTime.currentDateTime().toString("hh"),
            'Minutes': QDateTime.currentDateTime().toString("mm"),
            'Seconds': QDateTime.currentDateTime().toString("ss"),
        }
