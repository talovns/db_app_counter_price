from PySide6 import QtCore, QtWidgets
from db.inspector import fetch_tables, fetch_columns
from db.runner import execute_ddl

# аккуратные кавычки для идентификаторов и списков
def _qid(name: str) -> str:
    return '"' + (name or "").replace('"', '""') + '"'

def _qid_list(items) -> str:
    return ", ".join(_qid(x) for x in items if x)

class AlterSchemaDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, conn=None):
        super().__init__(parent)
        self.setWindowTitle("Схема БД (ALTER)")
        self.conn = conn
        self.schema = "public"

        lay = QtWidgets.QVBoxLayout(self)

        # выбор таблицы
        row = QtWidgets.QHBoxLayout()
        self.tableCombo = QtWidgets.QComboBox()
        row.addWidget(QtWidgets.QLabel("Таблица:"))
        row.addWidget(self.tableCombo, 1)
        lay.addLayout(row)

        # вкладки
        self.tabs = QtWidgets.QTabWidget()
        lay.addWidget(self.tabs, 1)

        # --- ADD COLUMN
        w_add = QtWidgets.QWidget(); f = QtWidgets.QFormLayout(w_add)
        self.addName = QtWidgets.QLineEdit()
        self.addType = QtWidgets.QLineEdit()
        self.addNullable = QtWidgets.QCheckBox("NULLABLE (разрешить NULL)")
        self.addDefault  = QtWidgets.QLineEdit()
        self.addDefault.setPlaceholderText("пример: 0 или 'text' или NOW()")
        f.addRow("Имя колонки:", self.addName)
        f.addRow("Тип (напр. VARCHAR(50)):", self.addType)
        f.addRow(self.addNullable)
        f.addRow("DEFAULT (опц.):", self.addDefault)
        self.tabs.addTab(w_add, "ADD COLUMN")

        # --- DROP COLUMN
        w_drop = QtWidgets.QWidget(); fd = QtWidgets.QFormLayout(w_drop)
        self.dropCol = QtWidgets.QComboBox()
        fd.addRow("Колонка:", self.dropCol)
        self.tabs.addTab(w_drop, "DROP COLUMN")

        # --- RENAME COLUMN
        w_ren = QtWidgets.QWidget(); fr = QtWidgets.QFormLayout(w_ren)
        self.renOld = QtWidgets.QComboBox()
        self.renNew = QtWidgets.QLineEdit()
        fr.addRow("Было:", self.renOld)
        fr.addRow("Стало:", self.renNew)
        self.tabs.addTab(w_ren, "RENAME COLUMN")

        # --- ALTER TYPE
        w_type = QtWidgets.QWidget(); ft = QtWidgets.QFormLayout(w_type)
        self.typeCol = QtWidgets.QComboBox()
        self.typeNew = QtWidgets.QLineEdit()
        self.typeUsing = QtWidgets.QLineEdit()
        self.typeUsing.setPlaceholderText("USING-выражение (опц.), напр. price::numeric")
        ft.addRow("Колонка:", self.typeCol)
        ft.addRow("Новый тип:", self.typeNew)
        ft.addRow("USING (опц.):", self.typeUsing)
        self.tabs.addTab(w_type, "ALTER TYPE")

        # --- NOT NULL
        w_nn = QtWidgets.QWidget(); fnn = QtWidgets.QFormLayout(w_nn)
        self.nnCol = QtWidgets.QComboBox()
        self.nnAction = QtWidgets.QComboBox()
        self.nnAction.addItems(["SET NOT NULL", "DROP NOT NULL"])
        fnn.addRow("Колонка:", self.nnCol)
        fnn.addRow("Действие:", self.nnAction)
        self.tabs.addTab(w_nn, "NOT NULL")

        # --- UNIQUE
        w_u = QtWidgets.QWidget(); v = QtWidgets.QVBoxLayout(w_u)
        boxAdd = QtWidgets.QGroupBox("Добавить UNIQUE")
        fa = QtWidgets.QFormLayout(boxAdd)
        self.uName = QtWidgets.QLineEdit()
        self.uCols = QtWidgets.QListWidget(); self.uCols.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        fa.addRow("Имя ограничения:", self.uName)
        fa.addRow("Колонки:", self.uCols)
        v.addWidget(boxAdd)

        boxDrop = QtWidgets.QGroupBox("Удалить UNIQUE")
        fd2 = QtWidgets.QFormLayout(boxDrop)
        self.uDropName = QtWidgets.QComboBox()
        fd2.addRow("Ограничение:", self.uDropName)
        v.addWidget(boxDrop)
        self.tabs.addTab(w_u, "UNIQUE")

        # --- CHECK
        w_c = QtWidgets.QWidget(); vc = QtWidgets.QVBoxLayout(w_c)
        boxAddC = QtWidgets.QGroupBox("Добавить CHECK")
        fc = QtWidgets.QFormLayout(boxAddC)
        self.cName = QtWidgets.QLineEdit()
        self.cExpr = QtWidgets.QLineEdit()
        self.cExpr.setPlaceholderText("пример: price >= 0 AND price <= 100000")
        fc.addRow("Имя ограничения:", self.cName)
        fc.addRow("Выражение CHECK:", self.cExpr)
        vc.addWidget(boxAddC)

        boxDropC = QtWidgets.QGroupBox("Удалить CHECK")
        fcd = QtWidgets.QFormLayout(boxDropC)
        self.cDropName = QtWidgets.QComboBox()
        fcd.addRow("Ограничение:", self.cDropName)
        vc.addWidget(boxDropC)
        self.tabs.addTab(w_c, "CHECK")

        # --- FOREIGN KEY
        w_fk = QtWidgets.QWidget(); vfk = QtWidgets.QVBoxLayout(w_fk)

        addFk = QtWidgets.QGroupBox("Добавить FOREIGN KEY")
        ffk = QtWidgets.QFormLayout(addFk)
        self.fkName = QtWidgets.QLineEdit()
        self.fkLocalCols = QtWidgets.QListWidget(); self.fkLocalCols.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        # референс
        self.fkRefTable = QtWidgets.QComboBox()
        self.fkRefCols  = QtWidgets.QListWidget(); self.fkRefCols.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        # действия
        self.fkOnDelete = QtWidgets.QComboBox(); self.fkOnUpdate = QtWidgets.QComboBox()
        actions = ["NO ACTION", "CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT"]
        self.fkOnDelete.addItems(actions); self.fkOnUpdate.addItems(actions)

        ffk.addRow("Имя ограничения:", self.fkName)
        ffk.addRow("Локальные колонки:", self.fkLocalCols)
        ffk.addRow("Внешняя таблица:", self.fkRefTable)
        ffk.addRow("Внешние колонки:", self.fkRefCols)
        ffk.addRow("ON DELETE:", self.fkOnDelete)
        ffk.addRow("ON UPDATE:", self.fkOnUpdate)
        vfk.addWidget(addFk)

        dropFk = QtWidgets.QGroupBox("Удалить FOREIGN KEY")
        fkd = QtWidgets.QFormLayout(dropFk)
        self.fkDropName = QtWidgets.QComboBox()
        fkd.addRow("Ограничение:", self.fkDropName)
        vfk.addWidget(dropFk)
        self.tabs.addTab(w_fk, "FOREIGN KEY")

        # кнопки
        btnRow = QtWidgets.QHBoxLayout()
        self.btnPreview = QtWidgets.QPushButton("Предпросмотр SQL")
        self.btnApply   = QtWidgets.QPushButton("Применить")
        self.btnClose   = QtWidgets.QPushButton("Закрыть")
        btnRow.addWidget(self.btnPreview)
        btnRow.addWidget(self.btnApply)
        btnRow.addStretch(1)
        btnRow.addWidget(self.btnClose)
        lay.addLayout(btnRow)

        self.btnClose.clicked.connect(self.reject)
        self.btnPreview.clicked.connect(self._preview)
        self.btnApply.clicked.connect(self._apply)
        self.tableCombo.currentTextChanged.connect(self._on_table_changed)
        self.fkRefTable.currentTextChanged.connect(self._reload_fk_ref_cols)

        self._load_tables()

    # ---------- загрузка списков ----------
    def _load_tables(self):
        if self.conn is None:
            return
        self.tableCombo.clear()
        self.tableCombo.addItems(fetch_tables(self.conn, self.schema))
        # fk: список референсных таблиц тоже
        self.fkRefTable.clear()
        self.fkRefTable.addItems(fetch_tables(self.conn, self.schema))
        self._on_table_changed()

    def _on_table_changed(self):
        t = self.tableCombo.currentText()
        for cb in (self.dropCol, self.renOld, self.typeCol, self.nnCol):
            cb.clear()
        self.uCols.clear(); self.uDropName.clear()
        self.cDropName.clear()
        self.fkLocalCols.clear(); self.fkDropName.clear()

        if not t or self.conn is None:
            return

        # колонки таблицы
        cols = [c for c, _ in fetch_columns(self.conn, t, self.schema)]
        for cb in (self.dropCol, self.renOld, self.typeCol, self.nnCol):
            cb.addItems(cols)
        self.uCols.addItems(cols)
        self.fkLocalCols.addItems(cols)

        # существующие ограничения
        self._reload_constraints()

        # fk: отрефрешим список внешних колонок для выбранной реф.таблицы
        self._reload_fk_ref_cols()

    def _reload_fk_ref_cols(self):
        rt = self.fkRefTable.currentText()
        self.fkRefCols.clear()
        if not rt or self.conn is None:
            return
        rcols = [c for c, _ in fetch_columns(self.conn, rt, self.schema)]
        self.fkRefCols.addItems(rcols)

    def _reload_constraints(self):
        """Подтянуть имена ограничений по типам для текущей таблицы."""
        t = self.tableCombo.currentText()
        if not t or self.conn is None:
            return
        sql = """
            SELECT conname, contype
            FROM pg_constraint c
            JOIN pg_class     t ON t.oid = c.conrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE n.nspname = %s AND t.relname = %s
            ORDER BY conname;
        """
        names_u, names_c, names_f = [], [], []
        with self.conn.cursor() as cur:
            cur.execute(sql, (self.schema, t))
            for name, typ in cur.fetchall():
                if   typ == 'u': names_u.append(name)
                elif typ == 'c': names_c.append(name)
                elif typ == 'f': names_f.append(name)
        self.uDropName.clear(); self.uDropName.addItems(names_u)
        self.cDropName.clear(); self.cDropName.addItems(names_c)
        self.fkDropName.clear(); self.fkDropName.addItems(names_f)

    # ---------- сборка SQL ----------
    def _build_sql(self) -> str:
        t = self.tableCombo.currentText().strip()
        if not t:
            raise RuntimeError("Не выбрана таблица.")
        tab = f"{_qid(t)}"  # схема опущена (public по умолчанию)

        idx = self.tabs.currentIndex()

        # 0 — ADD COLUMN
        if idx == 0:
            name = self.addName.text().strip()
            typ  = self.addType.text().strip()
            if not name or not typ:
                raise RuntimeError("ADD COLUMN: заполните имя и тип.")
            nullable = "" if self.addNullable.isChecked() else " NOT NULL"
            dflt = self.addDefault.text().strip()
            dpart = f" DEFAULT {dflt}" if dflt else ""
            return f"ALTER TABLE {tab} ADD COLUMN {_qid(name)} {typ}{nullable}{dpart};"

        # 1 — DROP COLUMN
        if idx == 1:
            c = self.dropCol.currentText().strip()
            if not c:
                raise RuntimeError("DROP COLUMN: выберите колонку.")
            return f"ALTER TABLE {tab} DROP COLUMN {_qid(c)};"

        # 2 — RENAME COLUMN
        if idx == 2:
            old = self.renOld.currentText().strip()
            new = self.renNew.text().strip()
            if not old or not new:
                raise RuntimeError("RENAME COLUMN: заполните поля.")
            return f"ALTER TABLE {tab} RENAME COLUMN {_qid(old)} TO {_qid(new)};"

        # 3 — ALTER TYPE
        if idx == 3:
            c = self.typeCol.currentText().strip()
            typ = self.typeNew.text().strip()
            using = self.typeUsing.text().strip()
            if not c or not typ:
                raise RuntimeError("ALTER TYPE: выберите колонку и укажите тип.")
            upart = f" USING {using}" if using else ""
            return f"ALTER TABLE {tab} ALTER COLUMN {_qid(c)} TYPE {typ}{upart};"

        # 4 — NOT NULL
        if idx == 4:
            c = self.nnCol.currentText().strip()
            act = self.nnAction.currentText()
            if not c:
                raise RuntimeError("NOT NULL: выберите колонку.")
            if act.startswith("SET"):
                return f"ALTER TABLE {tab} ALTER COLUMN {_qid(c)} SET NOT NULL;"
            else:
                return f"ALTER TABLE {tab} ALTER COLUMN {_qid(c)} DROP NOT NULL;"

        # 5 — UNIQUE
        if idx == 5:
            # определим, в какой половине пользователь работает:
            # если выделены колонки — это добавление; иначе удаление по имени
            sel_cols = [i.text() for i in self.uCols.selectedItems()]
            if sel_cols:
                name = self.uName.text().strip()
                if not name:
                    raise RuntimeError("UNIQUE: укажите имя ограничения.")
                return f"ALTER TABLE {tab} ADD CONSTRAINT {_qid(name)} UNIQUE ({_qid_list(sel_cols)});"
            else:
                d = self.uDropName.currentText().strip()
                if not d:
                    raise RuntimeError("UNIQUE: выберите имя для удаления.")
                return f"ALTER TABLE {tab} DROP CONSTRAINT {_qid(d)};"

        # 6 — CHECK
        if idx == 6:
            expr = self.cExpr.text().strip()
            if expr:
                name = self.cName.text().strip()
                if not name:
                    raise RuntimeError("CHECK: укажите имя ограничения.")
                return f"ALTER TABLE {tab} ADD CONSTRAINT {_qid(name)} CHECK ({expr});"
            else:
                d = self.cDropName.currentText().strip()
                if not d:
                    raise RuntimeError("CHECK: выберите имя для удаления.")
                return f"ALTER TABLE {tab} DROP CONSTRAINT {_qid(d)};"

        # 7 — FOREIGN KEY
        if idx == 7:
            # добавление, если выбраны колонки; иначе удаление по имени
            local_cols = [i.text() for i in self.fkLocalCols.selectedItems()]
            if local_cols:
                name = self.fkName.text().strip()
                if not name:
                    raise RuntimeError("FOREIGN KEY: укажите имя.")
                rt = self.fkRefTable.currentText().strip()
                ref_cols = [i.text() for i in self.fkRefCols.selectedItems()]
                if not rt or not ref_cols:
                    raise RuntimeError("FOREIGN KEY: выберите внешнюю таблицу и колонки.")
                od = self.fkOnDelete.currentText(); ou = self.fkOnUpdate.currentText()
                od_part = f" ON DELETE {od}" if od else ""
                ou_part = f" ON UPDATE {ou}" if ou else ""
                return (
                    f"ALTER TABLE {tab} "
                    f"ADD CONSTRAINT {_qid(name)} "
                    f"FOREIGN KEY ({_qid_list(local_cols)}) "
                    f"REFERENCES {_qid(rt)} ({_qid_list(ref_cols)})"
                    f"{od_part}{ou_part};"
                )
            else:
                d = self.fkDropName.currentText().strip()
                if not d:
                    raise RuntimeError("FOREIGN KEY: выберите имя для удаления.")
                return f"ALTER TABLE {tab} DROP CONSTRAINT {_qid(d)};"

        raise RuntimeError("Неизвестная операция.")

    # ---------- действия ----------
    def _preview(self):
        try:
            sql = self._build_sql()
            QtWidgets.QMessageBox.information(self, "SQL", sql)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", str(e))

    def _apply(self):
        try:
            sql = self._build_sql()
            execute_ddl(self.conn, sql)
            QtWidgets.QMessageBox.information(self, "Готово", "Изменения применены.")
            # после изменения схемы обновим колонки/ограничения
            self._on_table_changed()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Ошибка", str(e))
