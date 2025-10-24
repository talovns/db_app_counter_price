from PySide6 import QtWidgets
from .no_quote import NoQuoteEventFilter

class NoQuoteDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filters = []

    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        filt = NoQuoteEventFilter(editor)
        editor.installEventFilter(filt)
        self._filters.append(filt)
        return editor
