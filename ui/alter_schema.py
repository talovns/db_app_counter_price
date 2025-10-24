
from PySide6 import QtCore, QtWidgets
from db.inspector import fetch_tables, fetch_columns
from db.runner import execute_ddl

class AlterSchemaDialog(QtWidgets.QDialog):
    errorRaised = QtCore.Signal(str)
    success = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Схема БД (ALTER)")
        self.setObjectName("AlterSchema")
        self.resize(800, 520)

        lay = QtWidgets.QVBoxLayout(self)

        pick = QtWidgets.QHBoxLayout()
        self.tableCombo = QtWidgets.QComboBox()
        pick.addWidget(QtWidgets.QLabel("Таблица:"))
        pick.addWidget(self.tableCombo,1)

        self.columns = QtWidgets.QTreeWidget()
        self.columns.setHeaderLabels(["Колонка", "Тип"])

        btns = QtWidgets.QHBoxLayout()
        self.addColBtn = QtWidgets.QPushButton("＋ Добавить столбец")
        self.renameColBtn = QtWidgets.QPushButton("✎ Переименовать")
        self.dropColBtn = QtWidgets.QPushButton("🗑 Удалить")
        self.changeTypeBtn = QtWidgets.QPushButton("⇄ Сменить тип")
        btns.addWidget(self.addColBtn); btns.addWidget(self.renameColBtn)
        btns.addWidget(self.changeTypeBtn); btns.addWidget(self.dropColBtn)

        self.log = QtWidgets.QPlainTextEdit(); self.log.setReadOnly(True)

        lay.addLayout(pick)
        lay.addWidget(self.columns,1)
        lay.addLayout(btns)
        lay.addWidget(QtWidgets.QLabel("Лог:"))
        lay.addWidget(self.log,1)

        self._load_tables()
        self.tableCombo.currentTextChanged.connect(self._load_columns)
        self.addColBtn.clicked.connect(self._add_column)
        self.renameColBtn.clicked.connect(self._rename_column)
        self.dropColBtn.clicked.connect(self._drop_column)
        self.changeTypeBtn.clicked.connect(self._change_type)

    def _append(self, s: str):
        self.log.appendPlainText(s)

    def _load_tables(self):
        self.tableCombo.clear()
        self.tableCombo.addItems(fetch_tables('public'))
        if self.tableCombo.count():
            self._load_columns(self.tableCombo.currentText())

    def _load_columns(self, table: str):
        self.columns.clear()
        for c, t in fetch_columns(table, 'public'):
            self.columns.addTopLevelItem(QtWidgets.QTreeWidgetItem([c, t]))

    def _add_column(self):
        table = self.tableCombo.currentText()
        name, ok = QtWidgets.QInputDialog.getText(self, "Добавить столбец", "Имя столбца:")
        if not ok or not name: return
        dtype, ok = QtWidgets.QInputDialog.getText(self, "Тип", "Напр.: integer / text / numeric(12,2) / date")
        if not ok or not dtype: return
        sql = f'ALTER TABLE public.{table} ADD COLUMN "{name}" {dtype};'
        try:
            execute_ddl(sql); self._append(sql); self._load_columns(table); self.success.emit("Столбец добавлен.")
        except Exception as e:
            self.errorRaised.emit(str(e)); self._append(f"Ошибка: {e}")

    def _rename_column(self):
        table = self.tableCombo.currentText()
        item = self.columns.currentItem()
        if not item: return
        old = item.text(0)
        new, ok = QtWidgets.QInputDialog.getText(self, "Переименовать", f'{old} →')
        if not ok or not new: return
        sql = f'ALTER TABLE public.{table} RENAME COLUMN "{old}" TO "{new}";'
        try:
            execute_ddl(sql); self._append(sql); self._load_columns(table); self.success.emit("Столбец переименован.")
        except Exception as e:
            self.errorRaised.emit(str(e)); self._append(f"Ошибка: {e}")

    def _drop_column(self):
        table = self.tableCombo.currentText()
        item = self.columns.currentItem()
        if not item: return
        col = item.text(0)
        yn = QtWidgets.QMessageBox.question(self, "Удалить столбец", f'Удалить "{col}"? Это необратимо.')
        if yn != QtWidgets.QMessageBox.Yes: return
        sql = f'ALTER TABLE public.{table} DROP COLUMN "{col}";'
        try:
            execute_ddl(sql); self._append(sql); self._load_columns(table); self.success.emit("Столбец удалён.")
        except Exception as e:
            self.errorRaised.emit(str(e)); self._append(f"Ошибка: {e}")

    def _change_type(self):
        table = self.tableCombo.currentText()
        item = self.columns.currentItem()
        if not item: return
        col = item.text(0)
        dtype, ok = QtWidgets.QInputDialog.getText(self, "Сменить тип", "Новый тип (напр.: date / text / integer):")
        if not ok or not dtype: return
        using, ok = QtWidgets.QInputDialog.getText(self, "USING (опционально)", 'Напр.: to_date("date", \'DD.MM.YYYY\')')
        using_sql = f' USING {using}' if ok and using.strip() else ''
        sql = f'ALTER TABLE public.{table} ALTER COLUMN "{col}" TYPE {dtype}{using_sql};'
        try:
            execute_ddl(sql); self._append(sql); self._load_columns(table); self.success.emit("Тип изменён.")
        except Exception as e:
            self.errorRaised.emit(str(e)); self._append(f"Ошибка: {e}")
