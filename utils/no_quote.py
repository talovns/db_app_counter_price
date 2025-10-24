from PySide6 import QtCore, QtGui, QtWidgets

# Запрещённые символы
BLOCKED_CHARS = {"'"}


def _is_paste_key_event(ev: QtGui.QKeyEvent) -> bool:
    """
    Проверяем, является ли это событие вставкой (Ctrl+V / Shift+Insert).
    Нам это нужно, потому что не во всех версиях PySide6 есть QEvent.Paste
    и не во всех оно срабатывает стабильно.
    """
    if not isinstance(ev, QtGui.QKeyEvent):
        return False

    # Стандартная проверка Qt: Ctrl+V на любой раскладке
    if ev.matches(QtGui.QKeySequence.Paste):
        return True

    # Ручные проверки на всякий случай
    # Ctrl+V
    if (ev.modifiers() & QtCore.Qt.ControlModifier) and ev.key() == QtCore.Qt.Key_V:
        return True

    # Shift+Insert
    if (ev.modifiers() & QtCore.Qt.ShiftModifier) and ev.key() == QtCore.Qt.Key_Insert:
        return True

    return False


class NoQuoteEventFilter(QtCore.QObject):
    """
    Вешается на все поля ввода (QLineEdit, QTextEdit, QPlainTextEdit,
    а также на редактируемые ComboBox). Делает 2 вещи:
    1) Запрещает ввод символа "'".
    2) Чистит буфер при вставке (Ctrl+V / Shift+Insert), выкидывая "'".
    """

    toast_ms = 1200  # сколько висит тултип

    def _blocked(self, s: str) -> bool:
        return any(ch in s for ch in BLOCKED_CHARS)

    def _sanitize(self, s: str) -> str:
        # Убираем запрещённые символы из текста
        for ch in BLOCKED_CHARS:
            s = s.replace(ch, "")
        return s

    def _show_toast(self, widget: QtWidgets.QWidget | None):
        """
        Показывает небольшой тултип возле курсора типа "символ запрещён".
        Не модальное окно, не мешает работать.
        """
        QtWidgets.QToolTip.showText(
            QtGui.QCursor.pos(),
            "Символ ' запрещён",
            widget if isinstance(widget, QtWidgets.QWidget) else None,
            QtCore.QRect(),
            self.toast_ms
        )

    def _handle_paste_into_widget(self, obj: QtCore.QObject) -> bool:
        """
        Берём текст из буфера обмена, чистим от запрещённых символов
        и вставляем вручную в объект редактирования.
        Возвращаем True, если ВСТАВКУ мы обработали сами и исходное событие
        надо глушить.
        """
        cbtxt = QtWidgets.QApplication.clipboard().text() or ""
        clean = self._sanitize(cbtxt)

        # LineEdit
        if isinstance(obj, QtWidgets.QLineEdit):
            obj.insert(clean)
            self._show_toast(obj)
            return True

        # QTextEdit / QPlainTextEdit
        if isinstance(obj, (QtWidgets.QTextEdit, QtWidgets.QPlainTextEdit)):
            cursor = obj.textCursor()
            cursor.insertText(clean)
            self._show_toast(obj)
            return True

        # editable ComboBox -> работаем через lineEdit()
        if isinstance(obj, QtWidgets.QComboBox) and obj.isEditable():
            le = obj.lineEdit()
            if le is not None:
                le.insert(clean)
                self._show_toast(obj)
                return True

        # иначе не трогаем
        return False

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """
        Этот метод Qt вызывает на КАЖДОЕ событие клавы/вставки/и т.п.,
        пока фильтр повешен на виджет.
        Если возвращаем True -> Qt считает, что мы полностью обработали событие и дальше его не пускает.
        Если False -> Qt обрабатывает событие как обычно.
        """

        # 1. Обрабатываем нажатия клавиш
        if event.type() == QtCore.QEvent.KeyPress:
            if isinstance(event, QtGui.QKeyEvent):
                # Детектируем "вставку" через клавиатуру (Ctrl+V, Shift+Insert)
                if _is_paste_key_event(event):
                    # перехватываем вставку, чистим текст вручную
                    handled = self._handle_paste_into_widget(obj)
                    if handled:
                        return True  # глушим стандартную вставку
                    # если не смогли обработать — пропустим дальше

                # Обычный ввод символа
                txt = event.text() or ""
                if self._blocked(txt):
                    # пользователь нажал ' — запрещаем
                    self._show_toast(obj if isinstance(obj, QtWidgets.QWidget) else None)
                    return True  # блокируем эту клавишу

            return False  # другие клавиши отдаём приложению

        # 2. Обрабатываем событие вставки "мышкой"/"контекстным меню"
        #    Не во всех билдах PySide6 QEvent.Paste вообще существует,
        #    поэтому здесь делаем проверку безопасно.
        evt_type = event.type()
        paste_type = getattr(QtCore.QEvent, "Paste", None)
        if paste_type is not None and evt_type == paste_type:
            # кто-то пытается вставить текст
            handled = self._handle_paste_into_widget(obj)
            if handled:
                return True
            return False

        # 3. Всё остальное нас не интересует
        return False


def install_no_quote_filter(root: QtWidgets.QWidget) -> NoQuoteEventFilter:
    """
    Вызывается один раз из main после setupUi(self).
    Проходит по всем виджетам внутри окна и навешивает фильтр
    на вводимые поля.
    """
    filt = NoQuoteEventFilter(root)

    editable_classes = (
        QtWidgets.QLineEdit,
        QtWidgets.QTextEdit,
        QtWidgets.QPlainTextEdit,
        QtWidgets.QComboBox,
    )

    for w in root.findChildren(QtWidgets.QWidget):
        # ComboBox фильтруем только если он редактируемый (isEditable())
        if isinstance(w, QtWidgets.QComboBox):
            if w.isEditable():
                w.installEventFilter(filt)
        elif isinstance(w, editable_classes):
            w.installEventFilter(filt)

    return filt
