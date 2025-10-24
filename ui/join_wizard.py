
from PySide6 import QtCore, QtWidgets
from db.inspector import fetch_tables, fetch_columns
from db.runner import execute_sql

JOIN_TYPES = ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"]

class JoinWizard(QtWidgets.QDialog):
    sqlReady = QtCore.Signal(str)
    dataReady = QtCore.Signal(list, list)  # headers, rows
    errorRaised = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Мастер JOIN")
        self.setObjectName("JoinWizard")
        self.resize(900, 600)

        main = QtWidgets.QVBoxLayout(self)

        selects = QtWidgets.QHBoxLayout()
        self.leftTable = QtWidgets.QComboBox()
        self.rightTable = QtWidgets.QComboBox()
        self.joinType = QtWidgets.QComboBox(); self.joinType.addItems(JOIN_TYPES)
        selects.addWidget(QtWidgets.QLabel("Левая таблица:")); selects.addWidget(self.leftTable, 1)
        selects.addWidget(QtWidgets.QLabel("Правая таблица:")); selects.addWidget(self.rightTable, 1)
        selects.addWidget(QtWidgets.QLabel("Тип:")); selects.addWidget(self.joinType)

        self.conds = QtWidgets.QListWidget()
        self.addCondBtn = QtWidgets.QPushButton("＋ Условие users.id = expenses.user_id")

        colsLay = QtWidgets.QHBoxLayout()
        self.leftCols = QtWidgets.QListWidget(); self.leftCols.setSelectionMode(self.leftCols.MultiSelection)
        self.rightCols = QtWidgets.QListWidget(); self.rightCols.setSelectionMode(self.rightCols.MultiSelection)
        colsLay.addWidget(self.leftCols,1); colsLay.addWidget(self.rightCols,1)

        self.preview = QtWidgets.QPlainTextEdit(); self.preview.setReadOnly(True)
        btns = QtWidgets.QHBoxLayout()
        self.previewBtn = QtWidgets.QPushButton("Предпросмотр SQL")
        self.runBtn = QtWidgets.QPushButton("Выполнить")
        btns.addWidget(self.previewBtn); btns.addWidget(self.runBtn)

        main.addLayout(selects)
        main.addWidget(QtWidgets.QLabel("Условия ON:"))
        main.addWidget(self.conds,1)
        main.addWidget(self.addCondBtn,0)
        main.addWidget(QtWidgets.QLabel("Выбор колонок результата:"))
        main.addLayout(colsLay,1)
        main.addWidget(QtWidgets.QLabel("SQL:"))
        main.addWidget(self.preview,1)
        main.addLayout(btns)

        self._load_tables()
        self.leftTable.currentTextChanged.connect(self._load_left_cols)
        self.rightTable.currentTextChanged.connect(self._load_right_cols)
        self.addCondBtn.clicked.connect(self._add_default_cond)
        self.previewBtn.clicked.connect(self._do_preview)
        self.runBtn.clicked.connect(self._do_run)

    def _load_tables(self):
        tables = fetch_tables('public')
        self.leftTable.addItems(tables)
        self.rightTable.addItems(tables)
        if tables:
            self._load_left_cols(tables[0])
            self._load_right_cols(tables[0])

    def _load_left_cols(self, t):
        self.leftCols.clear()
        for c, _ in fetch_columns(t, 'public'):
            self.leftCols.addItem(f"{t}.{c}")

    def _load_right_cols(self, t):
        self.rightCols.clear()
        for c, _ in fetch_columns(t, 'public'):
            self.rightCols.addItem(f"{t}.{c}")

    def _add_default_cond(self):
        lt = self.leftTable.currentText() or "users"
        rt = self.rightTable.currentText() or "expenses"
        it = QtWidgets.QListWidgetItem(f"{lt}.id = {rt}.{lt}_id")
        it.setFlags(it.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.conds.addItem(it); self.conds.editItem(it)

    def build_sql(self) -> str:
        lt = self.leftTable.currentText()
        rt = self.rightTable.currentText()
        join = self.joinType.currentText()
        if not lt or not rt:
            raise RuntimeError("Выберите обе таблицы.")
        on_conds = " AND ".join([self.conds.item(i).text() for i in range(self.conds.count())]) or "TRUE"
        cols = [i.text() for i in self.leftCols.selectedItems()] + [i.text() for i in self.rightCols.selectedItems()]
        select = ", ".join(cols) if cols else "*"
        sql = f"SELECT {select}\nFROM {lt}\n{join} {rt} ON {on_conds};"
        return sql

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
