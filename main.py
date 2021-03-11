from PyQt5.QtWidgets import QApplication
import sheet
import clock
import sys

try:
    app = QApplication(sys.argv)
    watch = clock.Clock()
    watch.show()

    gsheet = sheet.GoogleSheet()

    watch.sec_last = watch.make_sec_from_list(gsheet.read_data('A5', 'F5'))

    app.exec()

# print(watch.delta)

    gsheet.send_data('A3', 'F3', [list(watch.get_values(watch.delta).values())])
    gsheet.send_data('A8', 'F8', [list(watch.get_values(watch.max_delta).values())])

except BaseException as error:
    print(error)









