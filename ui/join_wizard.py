from PySide6 import QtCore, QtWidgets
from db.inspector import fetch_tables, fetch_columns
from db.runner import execute_sql

class JoinWizard(QtWidgets.QDialog):
    sqlReady  = QtCore.Signal(str)
    dataReady = QtCore.Signal(list, list)   # headers, rows
    errorRaised = QtCore.Signal(str)

    def __init__(self, parent=None, conn=None):
        super().__init__(parent)
        self.setWindowTitle("Мастер JOIN")
        self.conn = conn

        # ---- UI ----
        lay = QtWidgets.QVBoxLayout(self)

        # выбор таблиц
        tRow = QtWidgets.QHBoxLayout()
        self.leftTable  = QtWidgets.QComboBox()
        self.rightTable = QtWidgets.QComboBox()
        tRow.addWidget(QtWidgets.QLabel("Левая таблица:"))
        tRow.addWidget(self.leftTable, 1)
        tRow.addSpacing(12)
        tRow.addWidget(QtWidgets.QLabel("Правая таблица:"))
        tRow.addWidget(self.rightTable, 1)
        lay.addLayout(tRow)

        # колонки
        colsRow = QtWidgets.QHBoxLayout()
        self.leftCols  = QtWidgets.QListWidget()
        self.rightCols = QtWidgets.QListWidget()
        self.leftCols.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.rightCols.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        colsRow.addWidget(self.leftCols, 1)
        colsRow.addWidget(self.rightCols, 1)
        lay.addLayout(colsRow)

        # ключи + тип join
        joinRow = QtWidgets.QHBoxLayout()
        self.joinType  = QtWidgets.QComboBox()
        self.joinType.addItems(["INNER", "LEFT", "RIGHT", "FULL"])
        self.leftKey   = QtWidgets.QComboBox()
        self.rightKey  = QtWidgets.QComboBox()
        joinRow.addWidget(QtWidgets.QLabel("Тип JOIN:"))
        joinRow.addWidget(self.joinType)
        joinRow.addSpacing(10)
        joinRow.addWidget(QtWidgets.QLabel("Ключи:"))
        joinRow.addWidget(self.leftKey, 1)
        joinRow.addWidget(QtWidgets.QLabel("="))
        joinRow.addWidget(self.rightKey, 1)
        lay.addLayout(joinRow)

        # кнопки
        btnRow = QtWidgets.QHBoxLayout()
        self.btnPreview = QtWidgets.QPushButton("Предпросмотр SQL")
        self.btnRun     = QtWidgets.QPushButton("Выполнить")
        self.btnClose   = QtWidgets.QPushButton("Закрыть")
        btnRow.addWidget(self.btnPreview)
        btnRow.addWidget(self.btnRun)
        btnRow.addStretch(1)
        btnRow.addWidget(self.btnClose)
        lay.addLayout(btnRow)

        self.btnClose.clicked.connect(self.reject)
        self.btnPreview.clicked.connect(self._preview)
        self.btnRun.clicked.connect(self._run)

        self.leftTable.currentTextChanged.connect(self._reload_left)
        self.rightTable.currentTextChanged.connect(self._reload_right)

        self._load_tables()

    # ---- data loading ----
    def _load_tables(self):
        if self.conn is None:
            return
        tables = fetch_tables(self.conn, 'public')
        self.leftTable.clear();  self.leftTable.addItems(tables)
        self.rightTable.clear(); self.rightTable.addItems([""] + tables)
        # загрузим сразу колонки для выбранных
        self._reload_left(); self._reload_right()

    def _reload_left(self):
        self.leftCols.clear(); self.leftKey.clear()
        t = self.leftTable.currentText()
        if not t or self.conn is None:
            return
        cols = [c for c, _ in fetch_columns(self.conn, t, 'public')]
        self.leftCols.addItems([f"{t}.{c}" for c in cols])
        self.leftKey.addItems([f"{t}.{c}" for c in cols])

    def _reload_right(self):
        self.rightCols.clear(); self.rightKey.clear()
        t = self.rightTable.currentText()
        if not t or self.conn is None:
            return
        cols = [c for c, _ in fetch_columns(self.conn, t, 'public')]
        self.rightCols.addItems([f"{t}.{c}" for c in cols])
        self.rightKey.addItems([f"{t}.{c}" for c in cols])

    # ---- SQL builder/run ----
    def _build_sql(self) -> str:
        lt = self.leftTable.currentText().strip()
        rt = self.rightTable.currentText().strip()
        if not lt:
            raise RuntimeError("Не выбрана левая таблица.")

        # выбранные колонки
        left_sel  = [i.text() for i in self.leftCols.selectedItems()]
        right_sel = [i.text() for i in self.rightCols.selectedItems()]
        select_cols = left_sel + right_sel
        if not select_cols:
            select_cols = [f"{lt}.*"]  # по умолчанию все

        parts = [f"SELECT {', '.join(select_cols)}", f"FROM {lt}"]

        if rt:
            jt = self.joinType.currentText().upper()
            lk = self.leftKey.currentText().strip()
            rk = self.rightKey.currentText().strip()
            if not lk or not rk:
                raise RuntimeError("Выберите ключи для соединения.")
            parts.append(f"{jt} JOIN {rt} ON {lk} = {rk}")

        return "\n".join(parts) + ";"

    def _preview(self):
        try:
            sql = self._build_sql()
            self.sqlReady.emit(sql)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", str(e))

    def _run(self):
        try:
            sql = self._build_sql()
            headers, rows = execute_sql(self.conn, sql)
            self.sqlReady.emit(sql)
            self.dataReady.emit(headers, rows)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка выполнения", str(e))
