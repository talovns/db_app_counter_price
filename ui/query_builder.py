from PySide6 import QtCore, QtWidgets, QtGui
from typing import List
from db.inspector import fetch_all_columns
from db.runner import execute_sql
import re


class QueryBuilderController(QtCore.QObject):
    # regex’ы
    _DOLLAR   = re.compile(r"\$\$(.*?)\$\$")
    _AGG_RX   = re.compile(r'\b(AVG|SUM|COUNT|MIN|MAX)\s*\(', re.I)
    _ALIAS_RX = re.compile(r'^(?P<expr>.+?)\s+AS\s+(?P<alias>"?[\w.]+"?)$', re.I)

    # сигналы
    sqlReady   = QtCore.Signal(str)
    dataReady  = QtCore.Signal(list, list)   # headers, rows
    errorRaised = QtCore.Signal(str)

    def __init__(self, right_panel_widget, db_connection=None, parent=None):
        super().__init__(parent)
        self.ui = right_panel_widget
        self.conn = db_connection           # psycopg2 connection или None
        self.schema: dict = {}
        self._all_columns: List[str] = []

        self._apply_columns([])
        self._connect_signals()

        # auto-чистка пустых/битых пунктов
        self.ui.filtersList.itemChanged.connect(
            lambda it: self._on_item_changed(self.ui.filtersList, it)
        )
        self.ui.sortList.itemChanged.connect(
            lambda it: self._on_item_changed(self.ui.sortList, it)
        )
        self.ui.groupList.itemChanged.connect(
            lambda it: self._on_item_changed(self.ui.groupList, it)
        )

    # ---------- wiring ----------
    def _connect_signals(self):
        self.ui.columnsFilter.textChanged.connect(self._filter_columns)
        self.ui.addFilterBtn.clicked.connect(self._add_filter_item)
        self.ui.addSortBtn.clicked.connect(self._add_sort_item)
        self.ui.addGroupBtn.clicked.connect(self._add_group_item)
        self.ui.requestPreviewSQL.connect(self.preview_sql)
        self.ui.requestRunQuery.connect(self.run_query)

    # ---------- schema ----------
    def refresh_schema(self):
        try:
            if self.conn is None:
                raise RuntimeError("Нет подключения к БД. Сначала нажмите «Создать базу данных».")
            self.schema = fetch_all_columns(self.conn, 'public')
            items: List[str] = []
            for t, cols in self.schema.items():
                for c, _ in cols:
                    items.append(f"{t}.{c}")
            self._all_columns = items
            self._apply_columns(items)
        except Exception as e:
            self._all_columns = []
            self._apply_columns([])
            self.errorRaised.emit(str(e))

    def _apply_columns(self, items: List[str]):
        self.ui.columnsList.clear()
        for s in items:
            self.ui.columnsList.addItem(QtWidgets.QListWidgetItem(s))

    def _filter_columns(self, text: str):
        if not self._all_columns:
            return
        text = (text or "").lower()
        items = [s for s in self._all_columns if text in s.lower()]
        self._apply_columns(items)

    # ---------- editors ----------
    def _add_filter_item(self):
        it = QtWidgets.QListWidgetItem('"category" = $$Образование$$')
        it.setFlags(it.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.ui.filtersList.addItem(it)
        self.ui.filtersList.editItem(it)

    def _add_sort_item(self):
        it = QtWidgets.QListWidgetItem('"date" DESC')
        it.setFlags(it.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.ui.sortList.addItem(it)
        self.ui.sortList.editItem(it)

    def _add_group_item(self):
        it = QtWidgets.QListWidgetItem('"category"')
        it.setFlags(it.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.ui.groupList.addItem(it)
        self.ui.groupList.editItem(it)

    # ---------- helpers ----------
    def _selected_columns(self) -> List[str]:
        return [i.text() for i in self.ui.columnsList.selectedItems()] or ["*"]

    def _normalize_condition(self, text: str) -> str | None:
        s = (text or "").strip()
        if not s:
            return None

        # "col" = $$NULL$$  ->  "col" IS NULL  (и <>/!= -> IS NOT NULL)
        m = re.match(r'^\s*("?[\w.]+"?)\s*(=|<>|!=)\s*\$\$NULL\$\$\s*$', s, flags=re.I)
        if m:
            col, op = m.group(1), m.group(2)
            return f"{col} IS NULL" if op == '=' else f"{col} IS NOT NULL"

        def repl(rx: re.Match) -> str:
            val = rx.group(1)
            if val.strip() == "":
                raise ValueError("empty-dollar")
            return "'" + val.replace("'", "''") + "'"

        try:
            s = self._DOLLAR.sub(repl, s)
        except ValueError:
            return None
        return s

    def _collect_items(self, listw: QtWidgets.QListWidget, normalize=False) -> List[str]:
        out = []
        for i in range(listw.count()):
            t = listw.item(i).text()
            t = self._normalize_condition(t) if normalize else (t or "").strip()
            if t and "$$" not in t:  # страховка: не пропускаем суррогатные $$ в SQL
                out.append(t)
        return out

    def _filters(self) -> List[str]:
        return self._collect_items(self.ui.filtersList, normalize=True)

    def _sort(self) -> List[str]:
        return self._collect_items(self.ui.sortList, normalize=False)

    def _group(self) -> List[str]:
        return self._collect_items(self.ui.groupList, normalize=False)

    def _is_agg(self, s: str) -> bool:
        return bool(self._AGG_RX.search(s or ""))

    def _unique(self, seq):
        out, seen = [], set()
        for x in seq:
            if x not in seen:
                out.append(x); seen.add(x)
        return out

    def _parse_agg_aliases(self, aggregates: list[str]) -> dict[str, str]:
        """
        'AVG(price) AS avgprc' -> {'avgprc': 'AVG(price)'}
        """
        out = {}
        for a in aggregates:
            m = self._ALIAS_RX.match((a or "").strip())
            if m:
                expr  = m.group('expr').strip()
                alias = m.group('alias').strip().strip('"')
                out[alias] = expr
        return out

    # ---------- SQL builder ----------
    def build_sql(self) -> str:
        # выбрано в «Колонки»
        selected_cols = self._selected_columns()
        selected_no_star = [] if selected_cols == ['*'] else selected_cols

        # «Группировка/Агрегаты»
        grp_items    = self._group()
        aggregates   = [g for g in grp_items if self._is_agg(g)]
        group_manual = [g for g in grp_items if not self._is_agg(g)]

        # неагрегированные из SELECT
        nonagg_selected = [c for c in selected_no_star if not self._is_agg(c)]

        # финальные колонки для GROUP BY: явные + все неагрегированные из SELECT
        group_cols = self._unique(group_manual + nonagg_selected)

        # SELECT-список
        if aggregates:
            select_list = self._unique(group_cols + aggregates)
        else:
            select_list = selected_cols

        cols = ", ".join(select_list)

        # FROM — пробуем вывести из выбранных колонок/групп
        from_table = None
        for s in (selected_no_star or group_cols):
            if "." in s:
                from_table = s.split(".", 1)[0]
                break
        if not from_table and self.schema:
            from_table = next(iter(self.schema.keys()))
        if not from_table:
            raise RuntimeError("Не удалось определить таблицу для SELECT (выбери колонки).")

        parts = [f"SELECT {cols}", f"FROM {from_table}"]

        filters = self._filters()
        if filters:
            parts.append("WHERE " + " AND ".join(filters))

        if group_cols:
            parts.append("GROUP BY " + ", ".join(group_cols))

        # HAVING: алиасы из SELECT в HAVING не работают -> заменим на выражения
        having = (self.ui.havingEdit.text() or "").strip()
        if having:
            alias_map = self._parse_agg_aliases(aggregates)
            for alias, expr in alias_map.items():
                having = re.sub(rf'\b{re.escape(alias)}\b', expr, having)
            parts.append("HAVING " + having)

        sort = self._sort()
        if sort:
            parts.append("ORDER BY " + ", ".join(sort))

        return "\n".join(parts) + ";"

    # ---------- misc ----------
    def _on_item_changed(self, listw: QtWidgets.QListWidget, item: QtWidgets.QListWidgetItem):
        txt = (item.text() or "").strip()
        if not txt:
            listw.takeItem(listw.row(item))
            return
        if listw is self.ui.filtersList:
            if txt.count("$$") % 2 == 1 or re.search(r'\$\$\s*\$\$', txt):
                listw.takeItem(listw.row(item))
                return
            item.setBackground(QtGui.QBrush()); item.setToolTip("")

    @QtCore.Slot()
    def preview_sql(self):
        try:
            self.sqlReady.emit(self.build_sql())
        except Exception as e:
            self.errorRaised.emit(str(e))

    @QtCore.Slot()
    def run_query(self):
        try:
            if self.conn is None:
                raise RuntimeError("Нет подключения к БД. Сначала нажмите «Создать базу данных».")
            sql = self.build_sql()
            headers, rows = execute_sql(self.conn, sql)
            self.sqlReady.emit(sql)
            self.dataReady.emit(headers, rows)
        except Exception as e:
            self.errorRaised.emit(str(e))
