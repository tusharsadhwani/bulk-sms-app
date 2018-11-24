import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QGridLayout, QWidget, QAction, QHeaderView,
                             QStyle, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtGui import QIcon
from functools import partial
from contact_class import Contact

class ManageDbWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Manage Database')
        self.setGeometry(420, 420, 600, 300)

        modify_all_btn = QPushButton('Save Changes', self)
        reset_all_btn = QPushButton('Undo Changes', self)
        delete_all_btn = QPushButton('Delete Shown Rows', self)
        modify_all_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
        reset_all_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_BrowserReload')))
        delete_all_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCancelButton')))
        modify_all_btn.clicked.connect(self.modify_all)
        reset_all_btn.clicked.connect(self.reset_all)
        delete_all_btn.clicked.connect(self.delete_all)

        self.search_edit = QLineEdit()
        f = self.search_edit.font()
        f.setPointSize(12)
        self.search_edit.setFont(f)
        self.search_edit.returnPressed.connect(self.get_results)

        self.table_widget = QTableWidget()
        grid = QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)

        grid.addWidget(self.search_edit, 0, 0, 1, 5)
        grid.addWidget(modify_all_btn, 1, 0)
        grid.addWidget(reset_all_btn, 1, 1)
        grid.addWidget(delete_all_btn, 1, 2)
        grid.addWidget(self.table_widget, 2, 0, 5, 5)

        self.contacts_list = []

    def get_results(self):
        text = self.search_edit.text()

        query = (Contact
                 .select()
                 .where((Contact.name.contains(text)) |
                        (Contact.phone.contains(text)) |
                        (Contact.address.contains(text)))
                 .order_by(Contact.phone)
                )

        self.contacts_list = []
        for contact in query:
            self.contacts_list.append((contact.name, contact.phone, contact.address))

        self.create_table(self.contacts_list)

    def create_table(self, contacts_list):
        if not self.contacts_list:
            self.table_widget.setRowCount(1)
            self.table_widget.setColumnCount(1)
            table_header = self.table_widget.horizontalHeader()
            table_header.setSectionResizeMode(0, QHeaderView.Stretch)
            self.table_widget.setItem(0, 0, QTableWidgetItem("No Entries found."))
            return

        self.table_widget.setRowCount(len(self.contacts_list))
        self.table_widget.setColumnCount(len(self.contacts_list[0])+3)
        table_header = self.table_widget.horizontalHeader()
        table_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table_header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_widget.setColumnWidth(3, 20)
        self.table_widget.setColumnWidth(4, 20)
        self.table_widget.setColumnWidth(5, 20)

        for row, rval in enumerate(self.contacts_list):
            for col, cval in enumerate(rval):
                self.table_widget.setItem(row, col, QTableWidgetItem(cval))

        modify_btn_list = []
        delete_btn_list = []
        reset_btn_list = []

        for row in range(len(self.contacts_list)):
            modify_btn = QPushButton('', self)
            reset_btn = QPushButton('', self)
            delete_btn = QPushButton('', self)

            modify_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogApplyButton')))
            reset_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_BrowserReload')))
            delete_btn.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogCancelButton')))

            modify_btn.setToolTip('Save Changes')
            reset_btn.setToolTip('Reset Row')
            delete_btn.setToolTip('Delete Entry')

            modify_btn.clicked.connect(self.modify_row)
            reset_btn.clicked.connect(self.reset_row)
            delete_btn.clicked.connect(self.delete_row)

            modify_btn_list.append(modify_btn)
            reset_btn_list.append(reset_btn)
            delete_btn_list.append(delete_btn)
            self.table_widget.setCellWidget(row, 3, modify_btn)
            self.table_widget.setCellWidget(row, 4, reset_btn)
            self.table_widget.setCellWidget(row, 5, delete_btn)

    def print_cell(self):
        button = self.sender()
        position = button.pos()
        index = self.table_widget.indexAt(position)
        print(index.row(), index.column())

    def modify_row(self, row_number=None):
        singular = 0
        if row_number is False:
            singular += 1
            button = self.sender()
            position = button.pos()
            index = self.table_widget.indexAt(position)
            row_number = index.row()

            reply = QMessageBox.question(self, 'Message',
                                         "Save changes?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if not reply == QMessageBox.Yes:
                return

        name = self.table_widget.item(row_number, 0).text()
        phone = self.table_widget.item(row_number, 1).text()
        address = self.table_widget.item(row_number, 2).text()

        old_phone = self.contacts_list[row_number][1]
        if phone != old_phone:
            Contact.delete().where(Contact.phone == old_phone).execute()

        Contact.replace(name=name, phone=phone, address=address).execute()

        if singular:
            self.get_results()

    def reset_row(self, row_number=None):
        if row_number is False:
            button = self.sender()
            position = button.pos()
            index = self.table_widget.indexAt(position)
            row_number = index.row()

        for col_number, cval in enumerate(self.contacts_list[row_number]):
                self.table_widget.setItem(row_number, col_number, QTableWidgetItem(cval))

    def delete_row(self, row_number=None):
        singular = 0
        if row_number is False:
            singular += 1
            button = self.sender()
            position = button.pos()
            index = self.table_widget.indexAt(position)
            row_number = index.row()

            reply = QMessageBox.critical(self, 'Message',
                                         "Are you sure you want to delete this entry?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

            if not reply == QMessageBox.Yes:
                return

        phone = self.table_widget.item(row_number, 1).text()
        Contact.delete().where(Contact.phone == phone).execute()
        
        if singular:
            self.get_results()
    
    def modify_all(self):
        reply = QMessageBox.question(self, 'Message',
                                         "Save all changes?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)

        if not reply == QMessageBox.Yes:
            return

        for i in range(len(self.contacts_list)):
            # print(i)
            self.modify_row(i)
        self.get_results()

    def reset_all(self):
        for i in range(len(self.contacts_list)):
            self.reset_row(i)

    def delete_all(self):
        reply = QMessageBox.critical(self, 'Message',
                                         "Are you sure you want to delete all these entries?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
        if not reply == QMessageBox.Yes:
            return

        for i in range(len(self.contacts_list)):
            self.delete_row(i)
        self.get_results()

    def reload(self):
        self.search_edit.clear()
        self.get_results()