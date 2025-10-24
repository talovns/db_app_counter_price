from PySide6 import QtCore, QtWidgets

class RightPanel(QtWidgets.QWidget):
    requestRunQuery = QtCore.Signal()
    requestPreviewSQL = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RightPanel")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.columnsGroup = self._group("Колонки")
        self.filtersGroup = self._group("Фильтры (WHERE)")
        self.sortGroup    = self._group("Сортировка (ORDER BY)")
        self.groupGroup   = self._group("Группировка/Агрегаты (GROUP BY)")
        self.havingGroup  = self._group("HAVING")

        self.columnsList = QtWidgets.QListWidget()
        self.columnsList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.columnsFilter = QtWidgets.QLineEdit()
        self.columnsFilter.setPlaceholderText("Поиск колонки...")

        self.filtersList = QtWidgets.QListWidget()
        self.addFilterBtn = QtWidgets.QPushButton("＋ Добавить условие")

        self.sortList = QtWidgets.QListWidget()
        self.addSortBtn = QtWidgets.QPushButton("＋ Добавить сортировку")

        self.groupList = QtWidgets.QListWidget()
        self.addGroupBtn = QtWidgets.QPushButton("＋ Добавить группировку")

        self.havingEdit = QtWidgets.QLineEdit()
        self.havingEdit.setPlaceholderText("Напр.: SUM(amount) > 5000")

        btnRow = QtWidgets.QHBoxLayout()
        self.previewBtn = QtWidgets.QPushButton("Предпросмотр SQL")
        self.runBtn     = QtWidgets.QPushButton("Выполнить")
        btnRow.addWidget(self.previewBtn)
        btnRow.addWidget(self.runBtn)

        colLay = QtWidgets.QVBoxLayout()
        colLay.addWidget(self.columnsFilter)
        colLay.addWidget(self.columnsList)
        self.columnsGroup.layout().addLayout(colLay)

        self.filtersGroup.layout().addWidget(self.filtersList)
        self.filtersGroup.layout().addWidget(self.addFilterBtn)
        self.sortGroup.layout().addWidget(self.sortList)
        self.sortGroup.layout().addWidget(self.addSortBtn)
        self.groupGroup.layout().addWidget(self.groupList)
        self.groupGroup.layout().addWidget(self.addGroupBtn)
        self.havingGroup.layout().addWidget(self.havingEdit)

        layout.addWidget(self.columnsGroup, 1)
        layout.addWidget(self.filtersGroup, 1)
        layout.addWidget(self.sortGroup, 1)
        layout.addWidget(self.groupGroup, 1)
        layout.addWidget(self.havingGroup, 0)
        layout.addLayout(btnRow, 0)

        self.previewBtn.clicked.connect(self.requestPreviewSQL)
        self.runBtn.clicked.connect(self.requestRunQuery)

    def _group(self, title: str) -> QtWidgets.QGroupBox:
        gb = QtWidgets.QGroupBox(title, self)
        gb.setObjectName(title.replace(" ", "_"))
        lay = QtWidgets.QVBoxLayout(gb)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)
        return gb
