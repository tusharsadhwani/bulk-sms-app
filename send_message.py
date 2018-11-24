import requests
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QLineEdit, QProgressBar,
                             QTextEdit, QGridLayout, QMessageBox, QApplication)
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore
from contact_class import Contact
from pprint import pprint


class SendMessageWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        url_label = QLabel('URL:')
        msg_label = QLabel('Message:')
        self.url_edit = QLineEdit()
        self.msg_edit = QTextEdit()

        send_messages_btn = QPushButton('Send Messages', self)
        cancel_btn = QPushButton('Cancel', self)

        self.progress_bar = QProgressBar(self)

        grid = QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(url_label, 1, 0)
        grid.addWidget(self.url_edit, 1, 1, 1, 3)

        grid.addWidget(msg_label, 2, 0)
        grid.addWidget(self.msg_edit, 2, 1, 3, 3)

        grid.addWidget(send_messages_btn, 5, 0)
        send_messages_btn.clicked.connect(self.verify_msg)
        grid.addWidget(cancel_btn, 5, 1)
        cancel_btn.clicked.connect(self.close)

        grid.addWidget(self.progress_bar, 5, 1, 1, 3)

        self.setLayout(grid)
        self.setGeometry(300, 300, 400, 200)
        self.setWindowTitle('Send Bulk Messages')

    def verify_msg(self):
        url = self.url_edit.text().strip()
        msg = self.msg_edit.toPlainText().strip()
        if msg or url:
            message = msg + '\n' + url

            reply = QMessageBox.question(self, 'Confirm',
                                         f"Message:\n\n{message}\n\nSend this message?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.load_numbers(message)

        else:
            info = QMessageBox.information(self, 'Message',
                                           "You can't leave both URL and Message empty.",
                                           QMessageBox.Ok,
                                           QMessageBox.Ok)

    def load_numbers(self, message):
        numbers_array = []
        for contact in Contact.select():
            # print(f"{contact.name}: {contact.phone}")
            numbers_array.append('91' + contact.phone)

        if not numbers_array:
            info = QMessageBox.information(self, 'Message',
                                           "There are no numbers saved in the database.",
                                           QMessageBox.Ok,
                                           QMessageBox.Ok)
            return

        self.send_messages(numbers_array, message)

    def send_messages(self, numbers, message):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))

        # # WAY2SMS FREE
        # url = 'https://smsapi.engineeringtgr.com/send/'
        # key = 'KEY'

        # for index, number in enumerate(numbers):
        #     print(number)
        #     params = {
        #         'Mobile' : '9XXXXXXXXX',
        #         'Password' : 'PASSWORD',
        #         'Message' : message,
        #         'To' : number[2:],
        #         'Key' : key
        #     }

        #     response = requests.get(url, params=params)
        #     data = response.json()
        #     pprint(data)
        #     print()

        # TEXTLOCAL
        url = 'https://api.textlocal.in/send/'
        key = 'KEY'
        failed_msgs = []

        for index, number in enumerate(numbers):

            params = {
                'apikey': key,
                'numbers': [number],
                'message': message
            }

            response = requests.post(url, params=params)
            data = response.json()
            pprint(data)

            if not data.get('status', None) == 'success':
                if data.get('errors', None)[0]['code'] == 192:
                    info = QMessageBox.critical(self, 'Message',
                                                    "You cannot send messages between 9pm to 9am as per TRAI.",
                                                    QMessageBox.Ok,
                                                    QMessageBox.Ok)
                    return
                    
                else:
                    failed_msgs.append('+'+number)
                    if len(failed_msgs) > 10:
                        info = QMessageBox.critical(self, 'Error',
                                                    f"More than 10 messages were not sent, Process stopped. Error:\n{data['errors'][0]['message']}",
                                                    QMessageBox.Ok,
                                                    QMessageBox.Ok)
                        return

            self.progress_bar.setValue(((index+1)/len(numbers))*100)

        QApplication.restoreOverrideCursor()

        if failed_msgs:
            failed_msgs_list = ',\n'.join(failed_msgs)
            info = QMessageBox.information(self, 'Message',
                                           f"Some Messages were not sent:\n{failed_msgs_list}",
                                           QMessageBox.Ok,
                                           QMessageBox.Ok)
        else:
            info = QMessageBox.information(self, 'Message',
                                           "Sent succesfully.",
                                           QMessageBox.Ok,
                                           QMessageBox.Ok)

    def clear(self):
        self.url_edit.clear()
        self.msg_edit.clear()
