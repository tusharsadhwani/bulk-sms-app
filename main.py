import sys
from peewee import SqliteDatabase
from contact_class import Contact
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QGridLayout, QMessageBox, QApplication)

from send_message import SendMessageWindow
from manage_db import ManageDbWindow

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        name_label = QLabel('Name:')
        phone_label = QLabel('Phone Number:')
        address_label = QLabel('Address:')
        whitespace = QLabel()

        self.info = QLabel()

        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.address_edit = QTextEdit()

        add_btn = QPushButton('Add to Database', self)
        manage_db_btn = QPushButton('Manage Database', self)
        send_message_btn = QPushButton('Send Bulk Message', self)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(name_label, 1, 0)
        grid.addWidget(self.name_edit, 1, 1, 1, 2)

        grid.addWidget(phone_label, 2, 0)
        grid.addWidget(self.phone_edit, 2, 1, 1, 2)

        grid.addWidget(address_label, 3, 0)
        grid.addWidget(self.address_edit, 3, 1, 2, 3)

        grid.addWidget(whitespace, 5, 0)

        grid.addWidget(add_btn, 6, 1)
        add_btn.clicked.connect(self.verify_entry)
        grid.addWidget(manage_db_btn, 6, 2)
        manage_db_btn.clicked.connect(self.manage_db)
        grid.addWidget(send_message_btn, 6, 4)
        send_message_btn.clicked.connect(self.send_message)

        grid.addWidget(self.info, 7, 0, 1, 5)

        self.setLayout(grid)
        self.setGeometry(400, 400, 500, 120)
        self.setWindowTitle('PTS')
        self.show()
    
    def verify_entry(self):
        name = self.name_edit.text() or 'Unknown'
        phone = self.phone_edit.text()
        address = self.address_edit.toPlainText().strip().replace('\n', ', ')

        if phone.startswith('+91'):
            if phone.lstrip('+').isdigit() and len(phone) == 13:
                phone = phone.replace('+91', '')
                self.add_to_db(name, phone, address)
            else:
                self.alert_verify()
        else:
            if phone.isdigit() and len(phone) == 10:
                self.add_to_db(name, phone, address)
            else:
                self.alert_verify()

    def add_to_db(self, name, phone, address):
        try:
            tushar = Contact.create(name=name, phone=phone, address=address)
            self.info.setText(f"{name}: +91{phone} added Successfully!")
        except:
            self.info.setText(f"There already exists a contact with number +91{phone}...")

    def alert_verify(self):
        info = QMessageBox.information(self, 'Message',
                                       "The entered number is not valid.",
                                       QMessageBox.Ok,
                                       QMessageBox.Ok)

    def send_message(self):
        send_message_window.clear()
        send_message_window.show()

    def manage_db(self):
        manage_db_window.reload()
        manage_db_window.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    contacts_db = SqliteDatabase('contacts.db')
    contacts_db.connect()
    contacts_db.create_tables([Contact])

    app = QApplication(sys.argv)
    main_window = MainWindow()
    send_message_window = SendMessageWindow()
    manage_db_window = ManageDbWindow()
    sys.exit(app.exec_())