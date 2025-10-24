
from PySide6 import QtCore, QtWidgets
from db.inspector import fetch_tables, fetch_columns
from db.runner import execute_sql

FUNCS = [
    ("UPPER", "UPPER({col})"),
    ("LOWER", "LOWER({col})"),
    ("SUBSTRING", "SUBSTRING({col} FROM 1 FOR 5)"),
    ("TRIM", "TRIM({col})"),
    ("LPAD", "LPAD({col}, 10, '0')"),
    ("RPAD", "RPAD({col}, 10, ' ')"),
    ("CONCAT", "CONCAT({col}, ' — ', {col})"),
]

class StringFuncsDialog(QtWidgets.QDialog):
    sqlReady = QtCore.Signal(str)
    dataReady = QtCore.Signal(list, list)
    errorRaised = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Строковые функции")
        self.resize(700, 500)
        lay = QtWidgets.QVBoxLayout(self)

        top = QtWidgets.QHBoxLayout()
        self.table = QtWidgets.QComboBox()
        self.column = QtWidgets.QComboBox()
        self.func = QtWidgets.QComboBox(); self.func.addItems([f[0] for f in FUNCS])
        top.addWidget(QtWidgets.QLabel("Таблица:")); top.addWidget(self.table,1)
        top.addWidget(QtWidgets.QLabel("Колонка:")); top.addWidget(self.column,1)
        top.addWidget(QtWidgets.QLabel("Функция:")); top.addWidget(self.func,1)

        self.preview = QtWidgets.QPlainTextEdit(); self.preview.setReadOnly(True)
        btns = QtWidgets.QHBoxLayout()
        self.previewBtn = QtWidgets.QPushButton("Предпросмотр SQL")
        self.runBtn = QtWidgets.QPushButton("Выполнить")
        btns.addWidget(self.previewBtn); btns.addWidget(self.runBtn)

        lay.addLayout(top)
        lay.addWidget(QtWidgets.QLabel("SQL:"))
        lay.addWidget(self.preview,1)
        lay.addLayout(btns)

        self._load_tables()
        self.table.currentTextChanged.connect(self._load_cols)
        self.previewBtn.clicked.connect(self._do_preview)
        self.runBtn.clicked.connect(self._do_run)

    def _load_tables(self):
        self.table.clear()
        tables = fetch_tables('public')
        self.table.addItems(tables)
        if tables:
            self._load_cols(tables[0])

    def _load_cols(self, t: str):
        self.column.clear()
        for c, _ in fetch_columns(t, 'public'):
            self.column.addItem(c)

    def build_sql(self) -> str:
        t = self.table.currentText()
        c = self.column.currentText()
        func_tpl = FUNCS[self.func.currentIndex()][1]
        expr = func_tpl.format(col=f"{t}.{c}")
        return f"SELECT {expr} AS value FROM {t} LIMIT 200;"

    def _do_preview(self):
        try:
            sql = self.build_sql()
            self.preview.setPlainText(sql)
            self.sqlReady.emit(sql)
        except Exception as e:
            self.errorRaised.emit(str(e))

    def _do_run(self):
        try:
            sql = self.build_sql()
            headers, rows = execute_sql(sql)
            self.preview.setPlainText(sql)
            self.sqlReady.emit(sql)
            self.dataReady.emit(headers, rows)
            self.accept()
        except Exception as e:
            self.errorRaised.emit(str(e))
