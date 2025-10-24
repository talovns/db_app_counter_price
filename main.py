import sys
from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QLocale

from main_window import Ui_MainWindow
from add_window import Ui_Dialog
from connection import Data

from ui.right_panel import RightPanel
from ui.query_builder import QueryBuilderController
from ui.join_wizard import JoinWizard
from ui.alter_schema import AlterSchemaDialog
from ui.string_funcs import StringFuncsDialog

from utils.csv_export import export_rows_to_csv
from utils.no_quote_delegate import NoQuoteDelegate
from utils.no_quote import install_no_quote_filter


class ExpenseTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ---- защита от кавычек в полях ввода + делегаты для таблиц ----
        install_no_quote_filter(self)
        for tv in self.findChildren(QtWidgets.QTableView):
            tv.setItemDelegate(NoQuoteDelegate(tv))

        # ---- объект работы с БД (подключение выполним по кнопке) ----
        self.conn = Data()                  # self.conn.connection is None until connect_to_database()

        # ---- правая панель + контроллер конструктора SELECT ----
        self._rightPanel = RightPanel(self)
        self._queryCtl   = QueryBuilderController(self._rightPanel, None, self)

        dock = QtWidgets.QDockWidget("Параметры", self)
        dock.setObjectName("RightDock")
        dock.setWidget(self._rightPanel)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setVisible(True)
        self.rightDock = dock

        # предпросмотр/результаты/ошибки из конструктора SELECT
        self._queryCtl.sqlReady.connect(lambda s: QtWidgets.QMessageBox.information(self, "SQL", s))
        self._queryCtl.dataReady.connect(self._render_results)
        self._queryCtl.errorRaised.connect(lambda m: QtWidgets.QMessageBox.warning(self, "Ошибка", str(m)))

        # ---- меню "Инструменты" ----
        mb = self.menuBar()
        tools = mb.addMenu("Инструменты")

        actBuilder = tools.addAction("Конструктор SELECT (правая панель)")
        actJoin    = tools.addAction("Мастер JOIN...")
        actAlter   = tools.addAction("Схема БД (ALTER)...")
        actStrF    = tools.addAction("Строковые функции...")
        actExport  = tools.addAction("Экспорт CSV...")

        actBuilder.triggered.connect(self._toggle_builder)
        actJoin.triggered.connect(self._open_join)
        actAlter.triggered.connect(self._open_alter)
        actStrF.triggered.connect(self._open_strf)
        actExport.triggered.connect(self._export_csv)

        # ---- модель для главной таблицы ----
        self.model = QStandardItemModel()
        self.ui.tableView.setModel(self.model)

        # ---- кнопки ----
        self.ui.new_order2.clicked.connect(self.open_new_transaction_window)
        self.ui.create_db.clicked.connect(self.create_db)

    # ===== вспомогательное =====
    def _render_results(self, headers, rows):
        model = QtGui.QStandardItemModel(self)
        model.setColumnCount(len(headers))
        model.setHorizontalHeaderLabels(headers)
        for row in rows:
            items = [QtGui.QStandardItem("" if v is None else str(v)) for v in row]
            model.appendRow(items)

        tv = self.ui.tableView
        tv.setModel(model)

    def _require_conn(self) -> bool:
        if not getattr(self.conn, "is_connected", False) or self.conn.connection is None:
            QtWidgets.QMessageBox.warning(self, "Нет подключения",
                                          "Сначала нажмите «Создать базу данных» и дождитесь сообщения об успехе.")
            return False
        return True

    # ===== обработчики меню =====
    def _toggle_builder(self):
        if not self._require_conn():
            return
        if hasattr(self, "rightDock") and self.rightDock is not None:
            self.rightDock.setVisible(True)
            self.rightDock.raise_()

    def _open_join(self):
        if not self._require_conn():
            return
        dlg = JoinWizard(self)
        dlg.sqlReady.connect(lambda s: QtWidgets.QMessageBox.information(self, "SQL", s))
        dlg.dataReady.connect(self._render_results)
        dlg.exec()

    def _open_alter(self):
        if not self._require_conn():
            return
        AlterSchemaDialog(self).exec()

    def _open_strf(self):
        if not self._require_conn():
            return
        dlg = StringFuncsDialog(self)
        dlg.sqlReady.connect(lambda s: QtWidgets.QMessageBox.information(self, "SQL", s))
        dlg.dataReady.connect(self._render_results)
        dlg.exec()

    def _export_csv(self):
        tv = self.ui.tableView
        if tv.model() is None or tv.model().rowCount() == 0:
            QtWidgets.QMessageBox.information(self, "Экспорт", "Нет данных в таблице")
            return

        m = tv.model()
        headers = [m.headerData(i, Qt.Horizontal) or f"col{i+1}" for i in range(m.columnCount())]
        rows = []
        for r in range(m.rowCount()):
            row = [m.index(r, c).data() for c in range(m.columnCount())]
            rows.append(row)

        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохранить CSV", "result.csv", "CSV (*.csv)")
        if path:
            export_rows_to_csv(path, headers, rows)
            QtWidgets.QMessageBox.information(self, "Экспорт", f"Сохранено: {path}")

    # ===== логика приложения =====
    def create_db(self):
        success = self.conn.connect_to_database()
        if not success:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        QtWidgets.QMessageBox.information(self, "Успех", "Подключение к базе данных установлено!")
        self.view_data()
        self.reload_data()

        # подключаем правую панель к живому соединению и подгружаем схему
        self._queryCtl.conn = self.conn.connection
        self._queryCtl.refresh_schema()

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
            p = float(price)
            if p < 0:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Цена должна быть больше или равна нулю")
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
            self.model.setHorizontalHeaderLabels(
                ['Buy id', 'Название', "User id", 'Категория', 'Дата', 'Цена', 'Описание']
            )

            for row_data in expenses:
                row = []
                for item in row_data:
                    it = QStandardItem(str(item))
                    it.setTextAlignment(Qt.AlignCenter)
                    row.append(it)
                self.model.appendRow(row)

            header = self.ui.tableView.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.ui.tableView.setColumnWidth(1, 160)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            self.ui.tableView.setColumnWidth(3, 180)
            self.ui.tableView.setColumnWidth(4, 150)
            self.ui.tableView.setColumnWidth(5, 200)
            header.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        except Exception as e:
            print(f"view_data error: {e}")

    def reload_data(self):
        try:
            self.ui.food_price.setText(self.conn.total_study())
            self.ui.price_heal.setText(self.conn.total_health())
            self.ui.price_edu.setText(self.conn.total_education())
            self.ui.price_season.setText(self.conn.total_price())
            self.view_data()
        except Exception as e:
            print(f"reload_data error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseTracker()
    window.show()
    sys.exit(app.exec())
