from PySide6 import QtCore, QtWidgets
from db.inspector import fetch_tables, fetch_columns
from db.runner import execute_sql


def _q(s: str) -> str:
    """Безопасная строка для SQL: 'a' -> ''a'' (пробелы сохраняем как есть)."""
    return "'" + (s or "").replace("'", "''") + "'"


def _ident(name: str) -> str:
    """Кавычим идентификатор, если он не процитирован."""
    if not name:
        return name
    if name.startswith('"') and name.endswith('"'):
        return name
    return f'"{name}"'


class StringFuncsDialog(QtWidgets.QDialog):
    sqlReady  = QtCore.Signal(str)
    dataReady = QtCore.Signal(list, list)   # headers, rows

    def __init__(self, parent=None, conn=None):
        super().__init__(parent)
        self.setWindowTitle("Строковые функции")
        self.conn = conn

        lay = QtWidgets.QVBoxLayout(self)

        # Таблица/колонка
        row = QtWidgets.QHBoxLayout()
        self.tableCombo  = QtWidgets.QComboBox()
        self.columnCombo = QtWidgets.QComboBox()
        row.addWidget(QtWidgets.QLabel("Таблица:"))
        row.addWidget(self.tableCombo, 1)
        row.addSpacing(8)
        row.addWidget(QtWidgets.QLabel("Колонка:"))
        row.addWidget(self.columnCombo, 1)
        lay.addLayout(row)

        # Функция + аргументы
        grid = QtWidgets.QGridLayout()
        self.funcCombo = QtWidgets.QComboBox()
        self.funcCombo.addItems([
            "UPPER", "LOWER", "SUBSTRING", "TRIM", "LPAD", "RPAD", "CONCAT", "LENGTH"
        ])
        grid.addWidget(QtWidgets.QLabel("Функция:"), 0, 0)
        grid.addWidget(self.funcCombo, 0, 1)

        self.arg1 = QtWidgets.QLineEdit()
        self.arg2 = QtWidgets.QLineEdit()
        self.arg1.setPlaceholderText("Напр.: 1 (для SUBSTRING/LPAD/RPAD) или суффикс для CONCAT")
        self.arg2.setPlaceholderText("Напр.: 5 или символ заполнения / префикс для CONCAT")
        grid.addWidget(QtWidgets.QLabel("Арг.1:"), 1, 0); grid.addWidget(self.arg1, 1, 1)
        grid.addWidget(QtWidgets.QLabel("Арг.2:"), 2, 0); grid.addWidget(self.arg2, 2, 1)
        lay.addLayout(grid)

        # Кнопки
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
        self.tableCombo.currentTextChanged.connect(self._reload_columns)

        self._load_tables()

    # ---------------- Data load ----------------
    def _load_tables(self):
        if self.conn is None:
            return
        self.tableCombo.clear()
        self.tableCombo.addItems(fetch_tables(self.conn, 'public'))
        self._reload_columns()

    def _reload_columns(self):
        t = self.tableCombo.currentText()
        self.columnCombo.clear()
        if not t or self.conn is None:
            return
        cols = [c for c, _ in fetch_columns(self.conn, t, 'public')]
        self.columnCombo.addItems(cols)

    # ---------------- Build expression ----------------
    def _build_expr(self) -> str:
        t  = (self.tableCombo.currentText() or "").strip()
        c  = (self.columnCombo.currentText() or "").strip()
        fn = self.funcCombo.currentText()

        # ВАЖНО: не .strip() — сохраняем ведущие/хвостовые пробелы пользователя
        a1 = self.arg1.text()  # суффикс для CONCAT / длина / паттерн и т.д.
        a2 = self.arg2.text()  # префикс для CONCAT / ширина / заполнитель и т.д.

        if not t or not c:
            raise RuntimeError("Выберите таблицу и колонку.")

        t_ident = _ident(t)
        col = f'{t_ident}."{c}"' if '"' not in c else f'{t_ident}.{c}'
        col_txt = f'({col})::text'  # безопасно для всех типов

        def _to_int(name: str, val: str) -> int:
            try:
                return int((val or "").strip())
            except Exception:
                raise RuntimeError(f"{name}: укажите целое число.")

        match fn:
            case "UPPER":
                return f"UPPER({col_txt})"

            case "LOWER":
                return f"LOWER({col_txt})"

            case "SUBSTRING":
                # SUBSTRING(str FROM start [FOR length])
                if not (a1 or "").strip():
                    raise RuntimeError("SUBSTRING: укажите start (Арг.1) и при необходимости length (Арг.2).")
                start = _to_int("SUBSTRING start", a1)
                if (a2 or "").strip():
                    length_n = _to_int("SUBSTRING length", a2)
                    return f"SUBSTRING({col_txt} FROM {start} FOR {length_n})"
                else:
                    return f"SUBSTRING({col_txt} FROM {start})"

            case "TRIM":
                # TRIM(BOTH 'x' FROM str) или просто TRIM(str)
                return f"TRIM(BOTH {_q(a1)} FROM {col_txt})" if a1 != "" else f"TRIM({col_txt})"

            case "LPAD":
                if not (a1 or "").strip():
                    raise RuntimeError("LPAD: укажите ширину (Арг.1).")
                width = _to_int("LPAD width", a1)
                pad = f", {_q(a2)}" if a2 != "" else ""
                return f"LPAD({col_txt}, {width}{pad})"

            case "RPAD":
                if not (a1 or "").strip():
                    raise RuntimeError("RPAD: укажите ширину (Арг.1).")
                width = _to_int("RPAD width", a1)
                pad = f", {_q(a2)}" if a2 != "" else ""
                return f"RPAD({col_txt}, {width}{pad})"

            case "CONCAT":
                # Арг.2 — префикс (слева), Арг.1 — суффикс (справа)
                pieces = []
                if a2 != "":
                    pieces.append(_q(a2))   # префикс, сохраняем пробелы
                pieces.append(col_txt)      # значение колонки
                if a1 != "":
                    pieces.append(_q(a1))   # суффикс, сохраняем пробелы
                return " || ".join(pieces) if pieces else col_txt

            case "LENGTH":
                return f"LENGTH({col_txt})"

        raise RuntimeError("Неизвестная функция.")

    def _build_sql(self) -> str:
        t = (self.tableCombo.currentText() or "").strip()
        if not t:
            raise RuntimeError("Не выбрана таблица.")
        expr = self._build_expr()
        return f"SELECT {expr} AS result FROM {_ident(t)};"

    # ---------------- Run/Preview ----------------
    def _preview(self):
        try:
            sql = self._build_sql()
            self.sqlReady.emit(sql)
            QtWidgets.QMessageBox.information(self, "SQL", sql)
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
