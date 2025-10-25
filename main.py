import sys
from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QDoubleValidator, QStandardItemModel, QStandardItem

from main_window import Ui_MainWindow
from add_window import Ui_Dialog
from connection import Data

# расширения
from ui.string_funcs import StringFuncsDialog
from ui.alter_schema import AlterSchemaDialog
from ui.join_wizard import JoinWizard
from utils.csv_export import export_rows_to_csv
from ui.query_builder import QueryBuilderController
from ui.right_panel import RightPanel
from utils.no_quote_delegate import NoQuoteDelegate
from utils.no_quote import install_no_quote_filter


class ExpenseTracker(QMainWindow):
    def __init__(self):
        super(ExpenseTracker, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- запрет одиночной кавычки
        try:
            self._no_quote_filter = install_no_quote_filter(self)
        except Exception as _e:
            print("no-quote filter warning:", _e)

        try:
            for tv in self.findChildren(QtWidgets.QTableView):
                tv.setItemDelegate(NoQuoteDelegate(tv))
        except Exception as _e:
            print("delegate warning:", _e)

        # соединение с БД (создаётся объект, подключение — по кнопке)
        self.conn = Data()

        # модель общей таблицы
        self.model = QStandardItemModel()
        self.ui.tableView.setModel(self.model)

        # --- правая панель (Конструктор SELECT)
        try:
            self._rightPanel = RightPanel(self)
            self._queryCtl = QueryBuilderController(self._rightPanel, None, self)

            def _sql_preview(sql: str):
                QtWidgets.QMessageBox.information(self, "SQL", sql)

            def _render(headers, rows):
                model = QtGui.QStandardItemModel(self)
                model.setColumnCount(len(headers))
                model.setHorizontalHeaderLabels(headers)
                for row in rows:
                    items = [QtGui.QStandardItem("" if v is None else str(v)) for v in row]
                    model.appendRow(items)
                tv = getattr(self.ui, "tableView", None)
                if tv is None:
                    tviews = self.findChildren(QtWidgets.QTableView)
                    tv = tviews[0] if tviews else None
                if tv is not None:
                    tv.setModel(model)

            def _error(msg):
                QtWidgets.QMessageBox.warning(self, "Ошибка", str(msg))

            self._queryCtl.sqlReady.connect(_sql_preview)
            self._queryCtl.dataReady.connect(_render)
            self._queryCtl.errorRaised.connect(_error)

            dock = QtWidgets.QDockWidget("Параметры", self)
            dock.setObjectName("RightDock")
            dock.setWidget(self._rightPanel)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            dock.show()
            self.rightDock = dock
        except Exception as _e:
            print("right panel wiring warning:", _e)

        # --- ДОК-ПАНЕЛЬ «ПОИСК ПО ТЕКСТУ» (пункт ТЗ №3)
        self._build_search_dock()

        # --- меню инструментов
        try:
            mb = self.menuBar()
            tools = mb.addMenu("Инструменты")

            actBuilder = tools.addAction("Конструктор SELECT (правая панель)")
            actJoin    = tools.addAction("Мастер JOIN...")
            actAlter   = tools.addAction("Схема БД (ALTER)...")
            actStrF    = tools.addAction("Строковые функции...")
            actExport  = tools.addAction("Экспорт CSV...")

            actBuilder.triggered.connect(self._show_builder)
            actJoin.triggered.connect(self._open_join)
            actAlter.triggered.connect(self._open_alter)
            actStrF.triggered.connect(self._open_strf)
            actExport.triggered.connect(self._export_csv)
        except Exception as _e:
            print("menu wiring warn:", _e)

        # кнопки
        self.ui.new_order2.clicked.connect(self.open_new_transaction_window)
        self.ui.create_db.clicked.connect(self.create_db)

    # ------------------------- ПОИСК ДОК -------------------------

    def _build_search_dock(self):
        """Верхняя док-панель: колонка + оператор (LIKE/ILIKE/~/~*/!~/!~*) + шаблон."""
        panel = QtWidgets.QWidget()
        hl = QtWidgets.QHBoxLayout(panel)
        hl.setContentsMargins(8, 8, 8, 8)
        hl.setSpacing(10)

        self.searchCol = QtWidgets.QComboBox()
        # ищем по типичным текстовым полям
        self.searchCol.addItems(["name", "category", "date", "description"])

        self.searchOp = QtWidgets.QComboBox()
        self.searchOp.addItems(["LIKE", "ILIKE", "~", "~*", "!~", "!~*"])

        self.searchEdit = QtWidgets.QLineEdit()
        self.searchEdit.setPlaceholderText("Шаблон: %уч%  или  ^\\d{2}\\.\\d{2}\\.\\d{4}$")

        self.searchBtn  = QtWidgets.QPushButton("Найти")
        self.clearBtn   = QtWidgets.QPushButton("Сброс")

        hl.addWidget(QtWidgets.QLabel("Поиск:"))
        hl.addWidget(self.searchCol)
        hl.addWidget(self.searchOp)
        hl.addWidget(self.searchEdit, 1)
        hl.addWidget(self.searchBtn)
        hl.addWidget(self.clearBtn)

        dock = QtWidgets.QDockWidget("Поиск по тексту", self)
        dock.setObjectName("SearchDock")
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        dock.setWidget(panel)
        self.addDockWidget(Qt.TopDockWidgetArea, dock)
        self.searchDock = dock

        self.searchBtn.clicked.connect(self.apply_search)
        self.clearBtn.clicked.connect(self.clear_search)

    def apply_search(self):
        """Выполнить поиск и показать результат в общей таблице."""
        if not self.conn.is_connected:
            QtWidgets.QMessageBox.warning(self, "Поиск", "Сначала подключитесь к БД (кнопка «Создать базу данных»).")
            return

        col = self.searchCol.currentText()
        op  = self.searchOp.currentText()
        pat = (self.searchEdit.text() or "").strip()

        if not pat:
            self.view_data()
            return

        # Для LIKE/ILIKE, если пользователь не указал %/_ — сделаем «содержит»
        if op in ("LIKE", "ILIKE") and ('%' not in pat and '_' not in pat):
            pat = f"%{pat}%"

        try:
            rows = self.conn.search_expenses(col, op, pat)
            self._populate_table(rows)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка поиска", str(e))

    def clear_search(self):
        self.searchEdit.clear()
        self.view_data()

    # ------------------------- МЕНЮ/ДИАЛОГИ -------------------------

    def _show_builder(self):
        if hasattr(self, "rightDock"):
            self.rightDock.setVisible(True)
            self.rightDock.raise_()

    def _open_join(self):
        dlg = JoinWizard(self)
        dlg.sqlReady.connect(lambda s: QtWidgets.QMessageBox.information(self, "SQL", s))
        dlg.dataReady.connect(self._render_results_from_tuple)
        dlg.exec()

    def _open_alter(self):
        AlterSchemaDialog(self, self.conn.connection).exec()

    def _open_strf(self):
        dlg = StringFuncsDialog(self, self.conn.connection)
        dlg.sqlReady.connect(lambda s: QtWidgets.QMessageBox.information(self, "SQL", s))
        dlg.dataReady.connect(self._render_results_from_tuple)
        dlg.exec()

    def _export_csv(self):
        tv = getattr(self.ui, "tableView", None)
        if tv is None or tv.model() is None:
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

    def _render_results_from_tuple(self, payload, maybe_rows=None):
        """
        Принимает результаты в гибких форматах:
        1) два отдельных аргумента: headers, rows
        2) один аргумент-кортеж:   (headers, rows)
        3) dict с ключами:         {"headers": [...], "rows": [...]}
        4) просто список rows:     [[...], ...] — заголовки придумаем col1..N
        """
        # Вариант 1: сигнал прислал два параметра
        if maybe_rows is not None:
            headers, rows = payload, maybe_rows

        else:
            data = payload
            # Вариант 2: кортеж (headers, rows)
            if isinstance(data, tuple) and len(data) == 2:
                headers, rows = data

            # Вариант 3: словарь
            elif isinstance(data, dict) and "headers" in data and "rows" in data:
                headers, rows = data["headers"], data["rows"]

            # Вариант 4: только строки
            elif isinstance(data, list):
                rows = data
                headers = [f"col{i + 1}" for i in range(len(rows[0]))] if rows else []

            else:
                QtWidgets.QMessageBox.warning(
                    self, "Ошибка", f"Неподдержимый формат данных: {type(data)}"
                )
                return

        # Отрисуем результат в tableView
        model = QtGui.QStandardItemModel(self)
        model.setColumnCount(len(headers))
        model.setHorizontalHeaderLabels(headers)
        for row in rows:
            items = [QtGui.QStandardItem("" if v is None else str(v)) for v in row]
            model.appendRow(items)

        tv = getattr(self.ui, "tableView", None)
        if tv is None:
            tviews = self.findChildren(QtWidgets.QTableView)
            tv = tviews[0] if tviews else None
        if tv is not None:
            tv.setModel(model)

    # ------------------------- CRUD UI -------------------------

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
            if float(price) < 0:
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

    # ------------------------- VIEW / DB -------------------------

    def create_db(self):
        success = self.conn.connect_to_database()
        if success:
            QtWidgets.QMessageBox.information(self, "Успех", "Подключение к базе данных установлено!")
            self.view_data()
            self.reload_data()
            if hasattr(self, "_queryCtl") and self._queryCtl is not None:
                self._queryCtl.conn = self.conn.connection
                self._queryCtl.refresh_schema()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Не удалось подключиться к базе данных")

    def _populate_table(self, expenses):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Buy id', 'Название', "User id", 'Категория', 'Дата', 'Цена', 'Описание'])
        for row_data in expenses:
            row = []
            for item in row_data:
                it = QStandardItem("" if item is None else str(item))
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

    def view_data(self):
        try:
            expenses = self.conn.get_all_expenses()
            self._populate_table(expenses)
        except Exception as e:
            print(f"Error: {e}")

    def reload_data(self):
        try:
            self.ui.food_price.setText(self.conn.total_study())
            self.ui.price_heal.setText(self.conn.total_health())
            self.ui.price_edu.setText(self.conn.total_education())
            self.ui.price_season.setText(self.conn.total_price())
            self.view_data()
        except Exception as e:
            print(f"Error reloading data: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseTracker()
    window.show()
    sys.exit(app.exec())
