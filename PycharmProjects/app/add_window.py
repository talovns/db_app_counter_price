# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'addwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDateEdit,
    QDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)
import res_new_window_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(694, 652)
        Dialog.setStyleSheet(u"background-color: rgb(82, 73, 109);\n"
"font: 14pt \"Segoe UI\";")
        self.horizontalLayout = QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_new = QFrame(Dialog)
        self.frame_new.setObjectName(u"frame_new")
        self.frame_new.setStyleSheet(u"background-color: rgb(65, 65, 65);\n"
"border: 1px solid #000000;\n"
"border-radius: 20px; ")
        self.frame_new.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_new.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_new)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.newbuylabel = QLabel(self.frame_new)
        self.newbuylabel.setObjectName(u"newbuylabel")
        self.newbuylabel.setMaximumSize(QSize(16777215, 50))
        self.newbuylabel.setStyleSheet(u"border: None;\n"
"font: 18pt \"Segoe UI\";\n"
"color: rgb(255, 243, 110)")

        self.verticalLayout.addWidget(self.newbuylabel, 0, Qt.AlignmentFlag.AlignHCenter)

        self.name_buy = QLineEdit(self.frame_new)
        self.name_buy.setObjectName(u"name_buy")
        self.name_buy.setMinimumSize(QSize(0, 50))
        self.name_buy.setStyleSheet(u"padding-left: 20px;")

        self.verticalLayout.addWidget(self.name_buy)

        self.category_box = QComboBox(self.frame_new)
        self.category_box.addItem("")
        self.category_box.addItem("")
        self.category_box.addItem("")
        self.category_box.setObjectName(u"category_box")
        self.category_box.setMinimumSize(QSize(0, 50))
        self.category_box.setStyleSheet(u"padding-left: 20px;\n"
"")

        self.verticalLayout.addWidget(self.category_box)

        self.dateEdit = QDateEdit(self.frame_new)
        self.dateEdit.setObjectName(u"dateEdit")
        self.dateEdit.setMinimumSize(QSize(0, 50))
        self.dateEdit.setStyleSheet(u"padding-left: 20px;")
        self.dateEdit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.dateEdit.setDateTime(QDateTime(QDate(2025, 1, 1), QTime(0, 0, 0)))

        self.verticalLayout.addWidget(self.dateEdit)

        self.price = QLineEdit(self.frame_new)
        self.price.setObjectName(u"price")
        self.price.setMinimumSize(QSize(0, 50))
        self.price.setStyleSheet(u"padding-left: 20px;")

        self.verticalLayout.addWidget(self.price)

        self.descritpion = QLineEdit(self.frame_new)
        self.descritpion.setObjectName(u"descritpion")
        self.descritpion.setMinimumSize(QSize(0, 50))
        self.descritpion.setStyleSheet(u"padding-left: 20px;")

        self.verticalLayout.addWidget(self.descritpion)

        self.saveButton = QPushButton(self.frame_new)
        self.saveButton.setObjectName(u"saveButton")
        self.saveButton.setMinimumSize(QSize(0, 0))
        self.saveButton.setStyleSheet(u"QPushButton{\n"
"border-radius: 5px;\n"
"background-color: rgb(42, 42, 42);\n"
"border: 1px solid #000000;\n"
"border-radius: 5px;\n"
"wieght: 250px;\n"
"hight: 50px;\n"
"padding: 12px 16px;\n"
"margin: 0px 0px 6px 0px; \n"
"}\n"
"\n"
"QPushButton:hover{\n"
"	transform: translateY(-3px);\n"
"	margin: 3px 0px 6px 0px; \n"
"    padding: 11px 19px 5px 19px; \n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"	background-color: rgb(102, 102, 102);\n"
"}")
        icon = QIcon()
        icon.addFile(u":/icon/icons/done.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.saveButton.setIcon(icon)

        self.verticalLayout.addWidget(self.saveButton)


        self.horizontalLayout.addWidget(self.frame_new)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.newbuylabel.setText(QCoreApplication.translate("Dialog", u"\u041d\u043e\u0432\u0430\u044f \u043f\u043e\u043a\u0443\u043f\u043a\u0430", None))
        self.name_buy.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043f\u043e\u043a\u0443\u043f\u043a\u0438", None))
        self.category_box.setItemText(0, QCoreApplication.translate("Dialog", u"\u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435", None))
        self.category_box.setItemText(1, QCoreApplication.translate("Dialog", u"\u0417\u0434\u043e\u0440\u043e\u0432\u044c\u0435", None))
        self.category_box.setItemText(2, QCoreApplication.translate("Dialog", u"\u0423\u0447\u0435\u0431\u0430", None))

        self.price.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u043f\u043e\u043a\u0443\u043f\u043a\u0438", None))
        self.descritpion.setPlaceholderText(QCoreApplication.translate("Dialog", u"\u041f\u0440\u0438\u043c\u0435\u0447\u0430\u043d\u0438\u0435", None))
        self.saveButton.setText(QCoreApplication.translate("Dialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c", None))
    # retranslateUi

