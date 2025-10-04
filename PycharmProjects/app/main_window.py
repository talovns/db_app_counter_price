# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QMainWindow, QPushButton,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)
import res_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1110, 703)
        MainWindow.setStyleSheet(u"background-color: rgb(82, 73, 109);\n"
"font: 14pt \"Segoe UI\";")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.bothqframe = QFrame(self.centralwidget)
        self.bothqframe.setObjectName(u"bothqframe")
        self.bothqframe.setMinimumSize(QSize(0, 0))
        self.bothqframe.setMaximumSize(QSize(1000, 600))
        self.horizontalLayout_8 = QHBoxLayout(self.bothqframe)
        self.horizontalLayout_8.setSpacing(30)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.highsize = QFrame(self.bothqframe)
        self.highsize.setObjectName(u"highsize")
        self.highsize.setMaximumSize(QSize(500, 23423))
        self.highsize.setStyleSheet(u"background-color: rgb(65, 65, 65);\n"
"border: 1px solid #000000;\n"
"border-radius: 20px; \n"
"")
        self.verticalLayout = QVBoxLayout(self.highsize)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.priceless_season = QLabel(self.highsize)
        self.priceless_season.setObjectName(u"priceless_season")
        self.priceless_season.setMaximumSize(QSize(220, 50))
        self.priceless_season.setStyleSheet(u"padding-left: 10px;\n"
"background-color: rgb(54, 54, 54);\n"
"border: None;\n"
"font: 18pt \"Segoe UI\";")

        self.horizontalLayout_2.addWidget(self.priceless_season)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.price_season = QLabel(self.highsize)
        self.price_season.setObjectName(u"price_season")
        self.price_season.setStyleSheet(u"font: 24pt \"Segoe UI\";\n"
"padding-left: 10px;\n"
"background-color: rgb(117, 117, 117);")

        self.horizontalLayout_3.addWidget(self.price_season)

        self.icon_rub_season = QLabel(self.highsize)
        self.icon_rub_season.setObjectName(u"icon_rub_season")
        self.icon_rub_season.setMaximumSize(QSize(40, 16777215))
        self.icon_rub_season.setStyleSheet(u"background-color: rgb(24, 24, 24);\n"
"padding-left: 8px")
        self.icon_rub_season.setPixmap(QPixmap(u":/icons/icons/rubly.svg"))

        self.horizontalLayout_3.addWidget(self.icon_rub_season)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_8.addWidget(self.highsize)

        self.categories = QFrame(self.bothqframe)
        self.categories.setObjectName(u"categories")
        self.categories.setMaximumSize(QSize(700, 23423))
        self.categories.setStyleSheet(u"background-color: rgb(65, 65, 65);\n"
"border: 1px solid #000000;\n"
"border-radius: 20px; \n"
"")
        self.verticalLayout_2 = QVBoxLayout(self.categories)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.category_label = QLabel(self.categories)
        self.category_label.setObjectName(u"category_label")
        self.category_label.setStyleSheet(u"background-color: rgb(54, 54, 54);\n"
"padding-left: 70px;\n"
"padding-right: 50px;\n"
"border: None;\n"
"")

        self.horizontalLayout_4.addWidget(self.category_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.priceless = QLabel(self.categories)
        self.priceless.setObjectName(u"priceless")
        self.priceless.setStyleSheet(u"background-color: rgb(54, 54, 54);\n"
"padding-left: 60px;\n"
"padding-right: 50px;\n"
"border: None;\n"
"")

        self.horizontalLayout_4.addWidget(self.priceless)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.icon_edu = QLabel(self.categories)
        self.icon_edu.setObjectName(u"icon_edu")
        self.icon_edu.setMaximumSize(QSize(35, 16777215))
        self.icon_edu.setStyleSheet(u"background-color: rgb(24, 24, 24);\n"
"padding-left: 5px;")
        self.icon_edu.setPixmap(QPixmap(u":/icons/icons/education.svg"))

        self.horizontalLayout_5.addWidget(self.icon_edu)

        self.edu_label = QLabel(self.categories)
        self.edu_label.setObjectName(u"edu_label")
        self.edu_label.setMaximumSize(QSize(275, 16777215))
        self.edu_label.setStyleSheet(u"background-color: rgb(117, 117, 117);\n"
"\n"
"padding-left: 3px")

        self.horizontalLayout_5.addWidget(self.edu_label)

        self.price_edu = QLabel(self.categories)
        self.price_edu.setObjectName(u"price_edu")
        self.price_edu.setStyleSheet(u"background-color: rgb(117, 117, 117);\n"
"padding-left: 4px;")

        self.horizontalLayout_5.addWidget(self.price_edu)

        self.icon_rub_edu = QLabel(self.categories)
        self.icon_rub_edu.setObjectName(u"icon_rub_edu")
        self.icon_rub_edu.setMaximumSize(QSize(30, 16777215))
        self.icon_rub_edu.setStyleSheet(u"background-color: rgb(24, 24, 24);\n"
"padding-left: 3px")
        self.icon_rub_edu.setPixmap(QPixmap(u":/icons/icons/rubly.svg"))

        self.horizontalLayout_5.addWidget(self.icon_rub_edu)


        self.verticalLayout_2.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.icon_healhy = QLabel(self.categories)
        self.icon_healhy.setObjectName(u"icon_healhy")
        self.icon_healhy.setMaximumSize(QSize(35, 16777215))
        self.icon_healhy.setStyleSheet(u"background-color: rgb(24, 24, 24);\n"
"padding-left: 5px")
        self.icon_healhy.setPixmap(QPixmap(u":/icons/icons/healthy.svg"))

        self.horizontalLayout_6.addWidget(self.icon_healhy)

        self.name_heal = QLabel(self.categories)
        self.name_heal.setObjectName(u"name_heal")
        self.name_heal.setMaximumSize(QSize(275, 16777215))
        self.name_heal.setStyleSheet(u"background-color: rgb(117, 117, 117);\n"
"padding-left: 3px;")

        self.horizontalLayout_6.addWidget(self.name_heal)

        self.price_heal = QLabel(self.categories)
        self.price_heal.setObjectName(u"price_heal")
        self.price_heal.setStyleSheet(u"background-color: rgb(117, 117, 117);\n"
"padding-left: 4px;")

        self.horizontalLayout_6.addWidget(self.price_heal)

        self.rub_healhy = QLabel(self.categories)
        self.rub_healhy.setObjectName(u"rub_healhy")
        self.rub_healhy.setMaximumSize(QSize(30, 16777215))
        self.rub_healhy.setStyleSheet(u"background-color: rgb(24, 24, 24);\n"
"\n"
"padding-left: 3px")
        self.rub_healhy.setPixmap(QPixmap(u":/icons/icons/rubly.svg"))

        self.horizontalLayout_6.addWidget(self.rub_healhy)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.icon_food = QLabel(self.categories)
        self.icon_food.setObjectName(u"icon_food")
        self.icon_food.setMaximumSize(QSize(35, 16777215))
        self.icon_food.setStyleSheet(u"background-color: rgb(24, 24, 24);\n"
"padding-left: 5px")
        self.icon_food.setPixmap(QPixmap(u":/icons/icons/food.svg"))

        self.horizontalLayout_7.addWidget(self.icon_food)

        self.name_food = QLabel(self.categories)
        self.name_food.setObjectName(u"name_food")
        self.name_food.setMaximumSize(QSize(275, 16777215))
        self.name_food.setStyleSheet(u"background-color: rgb(117, 117, 117);\n"
"padding-left: 3px;")

        self.horizontalLayout_7.addWidget(self.name_food)

        self.food_price = QLabel(self.categories)
        self.food_price.setObjectName(u"food_price")
        self.food_price.setStyleSheet(u"background-color: rgb(117, 117, 117);\n"
"padding-left: 4px;")

        self.horizontalLayout_7.addWidget(self.food_price)

        self.rub__icon_price = QLabel(self.categories)
        self.rub__icon_price.setObjectName(u"rub__icon_price")
        self.rub__icon_price.setMaximumSize(QSize(30, 16777215))
        self.rub__icon_price.setStyleSheet(u"background-color: rgb(24, 24, 24);\n"
"\n"
"padding-left: 3px")
        self.rub__icon_price.setPixmap(QPixmap(u":/icons/icons/rubly.svg"))

        self.horizontalLayout_7.addWidget(self.rub__icon_price)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)


        self.horizontalLayout_8.addWidget(self.categories)


        self.gridLayout.addWidget(self.bothqframe, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.buttons = QFrame(self.centralwidget)
        self.buttons.setObjectName(u"buttons")
        self.buttons.setMinimumSize(QSize(900, 0))
        self.buttons.setMaximumSize(QSize(1000, 100))
        self.buttons.setToolTipDuration(-1)
        self.buttons.setStyleSheet(u"")
        self._2 = QHBoxLayout(self.buttons)
        self._2.setSpacing(30)
        self._2.setObjectName(u"_2")
        self._2.setContentsMargins(9, -1, 9, -1)
        self.create_db = QPushButton(self.buttons)
        self.create_db.setObjectName(u"create_db")
        self.create_db.setStyleSheet(u"QPushButton{\n"
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
        icon.addFile(u":/icons/icons/db.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.create_db.setIcon(icon)

        self._2.addWidget(self.create_db)

        self.new_order2 = QPushButton(self.buttons)
        self.new_order2.setObjectName(u"new_order2")
        self.new_order2.setStyleSheet(u"QPushButton{\n"
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
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/add.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.new_order2.setIcon(icon1)

        self._2.addWidget(self.new_order2)


        self.gridLayout.addWidget(self.buttons, 1, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setMaximumSize(QSize(16777215, 16777215))
        self.tableView.setStyleSheet(u"QTableView{\n"
"background-color: rgb(65, 65, 65);\n"
"border: None;\n"
"border-radius: 15px; \n"
"}\n"
"QTableView:section{\n"
"border:Node;\n"
"background-color: rgb(34, 34, 34);\n"
"height: 50px;\n"
"font-size: 14px;\n"
"}\n"
"QTableView:item{\n"
"border-style: None;\n"
"border-bottom: rgba(255, 255, 255, 40)\n"
"}\n"
"QTableView:item:selected{\n"
"border: None;\n"
"background-color: rgb(126, 126, 126);\n"
"border-bottom: rgba(255, 255, 255, 40);\n"
"}\n"
"")
        self.tableView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tableView.setShowGrid(False)
        self.tableView.horizontalHeader().setDefaultSectionSize(135)

        self.gridLayout.addWidget(self.tableView, 2, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.priceless_season.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0442\u0440\u0430\u0447\u0435\u043d\u043e \u0432\u0441\u0435\u0433\u043e ", None))
        self.price_season.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.icon_rub_season.setText("")
        self.category_label.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f", None))
        self.priceless.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u0442\u0440\u0430\u0447\u0435\u043d\u043e", None))
        self.icon_edu.setText("")
        self.edu_label.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435 ", None))
        self.price_edu.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.icon_rub_edu.setText("")
        self.icon_healhy.setText("")
        self.name_heal.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0434\u043e\u0440\u043e\u0432\u044c\u0435", None))
        self.price_heal.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.rub_healhy.setText("")
        self.icon_food.setText("")
        self.name_food.setText(QCoreApplication.translate("MainWindow", u"\u0415\u0434\u0430", None))
        self.food_price.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.rub__icon_price.setText("")
        self.create_db.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0431\u0430\u0437\u0443 \u0434\u0430\u043d\u043d\u044b\u0445", None))
        self.new_order2.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043f\u043e\u043a\u0443\u043f\u043a\u0443 ", None))
    # retranslateUi

