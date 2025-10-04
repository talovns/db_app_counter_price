import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QMainWindow

from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import QLocale

from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

from main_window import Ui_MainWindow
from add_window import Ui_Dialog
from connection import Data

class ExpenseTracker(QMainWindow):
    def __init__(self):
        super(ExpenseTracker, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.conn = Data()


        self.model = QStandardItemModel()
        self.ui.tableView.setModel(self.model)


        self.ui.new_order2.clicked.connect(self.open_new_transaction_window)
        self.ui.create_db.clicked.connect(self.create_db)


    def open_new_transaction_window(self):
        self.new_window = QtWidgets.QDialog()
        self.ui_window = Ui_Dialog()
        self.ui_window.setupUi(self.new_window)

        self.ui_window.name_buy.setMaxLength(20)
        self.ui_window.descritpion.setMaxLength(100)
        validator = QDoubleValidator(0.0, 1e12, 2)
        validator.setLocale(QLocale("ru_RU"))
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.ui_window.price.setValidator(validator)

        self.new_window.show()
        self.ui_window.saveButton.clicked.connect(self.add_new_transaction)




    def add_new_transaction(self):
        name = self.ui_window.name_buy.text()
        category = self.ui_window.category_box.currentText()
        date = self.ui_window.dateEdit.text()
        price = self.ui_window.price.text()
        description = self.ui_window.descritpion.text()


        if not name or not price:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните название и цену")
            return

        try:
            float(price)
            if float(price)<0:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Цена должна быть больше или равна нули")
                return
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Цена должна быть числом")
            return

        success = self.conn.add_new_transaction_query(name, category, date, price, description)
        if success:

            self.reload_data()
            self.new_window.close()
            QtWidgets.QMessageBox.information(self, "Успех", "Транзакция добавлена!")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось добавить транзакцию")

    def view_data(self):

        try:
            expenses = self.conn.get_all_expenses()

            self.model.clear()
            self.model.setHorizontalHeaderLabels(['Buy id', 'Название',"User id", 'Категория', 'Дата', 'Цена', 'Описание'])

            for row_data in expenses:
                row = []

                for item in row_data:
                    standard_item = QStandardItem(str(item))
                    standard_item.setTextAlignment(Qt.AlignCenter)
                    row.append(standard_item)
                self.model.appendRow(row)

            header = self.ui.tableView.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.ui.tableView.setColumnWidth(1, 160)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            self.ui.tableView.setColumnWidth(3, 180)
            self.ui.tableView.setColumnWidth(4, 150)
            self.ui.tableView.setColumnWidth(5, 200)
            header.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)


            print(f"Таблица обновлена: {len(expenses)} записей")

        except Exception as e:
            print(f"Error: {e}")



            print(f"Таблица обновлена: {len(expenses)} записей")

        except Exception as e:
            print(f"Error: {e}")


    def create_db(self):

        success = self.conn.connect_to_database()
        if success:
            QtWidgets.QMessageBox.information(self, "Успех", "Подключение к базе данных установлено!")

            self.view_data()
            self.reload_data()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось подключиться к базе данных")

    def reload_data(self):

        try:
            self.ui.food_price.setText(self.conn.total_study())
            self.ui.price_heal.setText(self.conn.total_health())
            self.ui.price_edu.setText(self.conn.total_education())
            self.ui.price_season.setText(self.conn.total_price())


            self.view_data()

            print(f"Data reloaded! учеба: {self.conn.total_study()}, здоровье: {self.conn.total_health()}, образование: {self.conn.total_education()}, всего потрачено: {self.conn.total_price()}")
        except Exception as e:
            print(f"Error reloading data: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseTracker()
    window.show()

    sys.exit(app.exec())