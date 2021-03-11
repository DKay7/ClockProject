import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheet:
    def __init__(self):
        self.CREDENTIALS_FILE = 'files/clock-project-271214-6f2207203513.json'
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.CREDENTIALS_FILE,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']
        )

        self.http_auth = self.credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=self.http_auth)

        self.spreadsheetId = ''
        self.sheetId = 0

    def read_data(self, start_cell, end_cell):
        """
        Читает данные из таблицы

        :param start_cell: Индекс верхней левой клетки
        :param end_cell: Индекс нижней правой клетки
        """
        ranges = ["Лист номер один!{0}:{1}".format(start_cell, end_cell)]
        results = self.service.spreadsheets().values().\
            batchGet(
                    spreadsheetId=self.spreadsheetId,
                    ranges=ranges,
                    valueRenderOption='UNFORMATTED_VALUE',
                    dateTimeRenderOption='FORMATTED_STRING'
        ).execute()

        sheet_values = results['valueRanges'][0]['values']
        c = -1
        for i in range(len(sheet_values[0])):
            if len(sheet_values[0][i]) < 2:
                while len(sheet_values[0][i]) < 2:
                    sheet_values[0][i] = '0' + str(sheet_values[0][i])
                c += 1
        if c != -1:
            self.send_data(start_cell, end_cell, sheet_values)

        return sheet_values

    def send_data(self, cell_start, cell_end, data):
        """
        Записывает данные в таблицу

        :param cell_start: Индекс верхней левой клетки
        :param cell_end: Индекс нижней правой клетки
        :param data: Массив данных
        """
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheetId, body={
            "valueInputOption": "USER_ENTERED",

            "data": [
                {"range": "Лист номер один!{0}:{1}".format(cell_start, cell_end),
                 "majorDimension": "ROWS",
                 "values": data}
            ]
        }).execute()
