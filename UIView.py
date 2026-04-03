# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UIView.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSlider, QSpinBox, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)
import assets_rc

class Ui_UIView(object):
    def setupUi(self, UIView):
        if not UIView.objectName():
            UIView.setObjectName(u"UIView")
        UIView.resize(920, 720)
        icon = QIcon()
        icon.addFile(u":/pic/Mondrian.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        UIView.setWindowIcon(icon)
        self.centralwidget = QWidget(UIView)
        self.centralwidget.setObjectName(u"centralwidget")
        self.brandPanel = QWidget(self.centralwidget)
        self.brandPanel.setObjectName(u"brandPanel")
        self.brandPanel.setGeometry(QRect(12, 12, 896, 118))
        self.label_brand_title = QLabel(self.brandPanel)
        self.label_brand_title.setObjectName(u"label_brand_title")
        self.label_brand_title.setGeometry(QRect(20, 16, 420, 38))
        font = QFont()
        font.setFamilies([u"Segoe UI", u"Microsoft YaHei UI", u"Arial"])
        font.setPointSize(20)
        font.setBold(True)
        self.label_brand_title.setFont(font)
        self.label_brand_subtitle = QLabel(self.brandPanel)
        self.label_brand_subtitle.setObjectName(u"label_brand_subtitle")
        self.label_brand_subtitle.setGeometry(QRect(20, 56, 520, 24))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI", u"Microsoft YaHei UI", u"Arial"])
        font1.setPointSize(10)
        self.label_brand_subtitle.setFont(font1)
        self.label_brand_flow = QLabel(self.brandPanel)
        self.label_brand_flow.setObjectName(u"label_brand_flow")
        self.label_brand_flow.setGeometry(QRect(20, 84, 856, 22))
        self.label_brand_flow.setFont(font1)
        self.label_brand_title.setStyleSheet(u"color: #f8fafc; background: transparent;")
        self.label_brand_subtitle.setStyleSheet(u"color: #dbeafe; background: transparent;")
        self.label_brand_flow.setStyleSheet(u"color: #bfdbfe; background: transparent;")
        self.brandPanel.setStyleSheet(u"background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(34, 197, 94, 255), stop:0.52 rgba(16, 185, 129, 255), stop:1 rgba(14, 165, 233, 255)); border-radius: 18px;")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(530, 146, 378, 182))
        self.groupBox.setStyleSheet(u"QGroupBox { font-weight: 600; border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 14px; margin-top: 12px; padding-top: 12px; } QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; }")
        self.gridLayout_3 = QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(14, 18, 14, 14)
        self.label_language = QLabel(self.groupBox)
        self.label_language.setObjectName(u"label_language")

        self.gridLayout_3.addWidget(self.label_language, 3, 0, 1, 1)

        self.label_stop = QLabel(self.groupBox)
        self.label_stop.setObjectName(u"label_stop")

        self.gridLayout_3.addWidget(self.label_stop, 2, 0, 1, 1)

        self.choice_language = QComboBox(self.groupBox)
        self.choice_language.setObjectName(u"choice_language")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.choice_language.sizePolicy().hasHeightForWidth())
        self.choice_language.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.choice_language, 3, 1, 1, 1)

        self.label_start_key = QLabel(self.groupBox)
        self.label_start_key.setObjectName(u"label_start_key")

        self.gridLayout_3.addWidget(self.label_start_key, 0, 0, 1, 1)

        self.label_record = QLabel(self.groupBox)
        self.label_record.setObjectName(u"label_record")

        self.gridLayout_3.addWidget(self.label_record, 1, 0, 1, 1)

        self.hotkey_start = QPushButton(self.groupBox)
        self.hotkey_start.setObjectName(u"hotkey_start")

        self.gridLayout_3.addWidget(self.hotkey_start, 0, 1, 1, 1)

        self.hotkey_record = QPushButton(self.groupBox)
        self.hotkey_record.setObjectName(u"hotkey_record")

        self.gridLayout_3.addWidget(self.hotkey_record, 1, 1, 1, 1)

        self.hotkey_stop = QPushButton(self.groupBox)
        self.hotkey_stop.setObjectName(u"hotkey_stop")

        self.gridLayout_3.addWidget(self.hotkey_stop, 2, 1, 1, 1)

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(12, 340, 520, 52))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.btrecord = QPushButton(self.horizontalLayoutWidget)
        self.btrecord.setObjectName(u"btrecord")
        sizePolicy.setHeightForWidth(self.btrecord.sizePolicy().hasHeightForWidth())
        self.btrecord.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.btrecord)

        self.btrun = QPushButton(self.horizontalLayoutWidget)
        self.btrun.setObjectName(u"btrun")
        sizePolicy.setHeightForWidth(self.btrun.sizePolicy().hasHeightForWidth())
        self.btrun.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.btrun)

        self.btpauserecord = QPushButton(self.horizontalLayoutWidget)
        self.btpauserecord.setObjectName(u"btpauserecord")
        self.btpauserecord.setEnabled(False)
        sizePolicy.setHeightForWidth(self.btpauserecord.sizePolicy().hasHeightForWidth())
        self.btpauserecord.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.btpauserecord)

        self.verticalLayoutWidget = QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(12, 470, 896, 214))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tnumrd = QLabel(self.verticalLayoutWidget)
        self.tnumrd.setObjectName(u"tnumrd")

        self.horizontalLayout_2.addWidget(self.tnumrd)

        self.label_cursor_pos = QLabel(self.verticalLayoutWidget)
        self.label_cursor_pos.setObjectName(u"label_cursor_pos")
        self.label_cursor_pos.setLayoutDirection(Qt.RightToLeft)
        self.label_cursor_pos.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.label_cursor_pos)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.textlog = QTextEdit(self.verticalLayoutWidget)
        self.textlog.setObjectName(u"textlog")
        self.textlog.setEnabled(True)
        sizePolicy.setHeightForWidth(self.textlog.sizePolicy().hasHeightForWidth())
        self.textlog.setSizePolicy(sizePolicy)
        self.textlog.setReadOnly(True)

        self.verticalLayout.addWidget(self.textlog)

        self.formLayoutWidget_3 = QWidget(self.centralwidget)
        self.formLayoutWidget_3.setObjectName(u"formLayoutWidget_3")
        self.formLayoutWidget_3.setGeometry(QRect(12, 688, 300, 24))
        self.formLayout_3 = QFormLayout(self.formLayoutWidget_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_volume = QLabel(self.formLayoutWidget_3)
        self.label_volume.setObjectName(u"label_volume")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_volume)

        self.volumeSlider = QSlider(self.formLayoutWidget_3)
        self.volumeSlider.setObjectName(u"volumeSlider")
        self.volumeSlider.setOrientation(Qt.Horizontal)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.volumeSlider)

        self.groupBox_mcp = QGroupBox(self.centralwidget)
        self.groupBox_mcp.setObjectName(u"groupBox_mcp")
        self.groupBox_mcp.setGeometry(QRect(548, 338, 360, 116))
        self.groupBox_mcp.setStyleSheet(u"QGroupBox { font-weight: 600; border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 14px; margin-top: 12px; padding-top: 12px; } QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; }")
        self.gridLayout_mcp = QGridLayout(self.groupBox_mcp)
        self.gridLayout_mcp.setObjectName(u"gridLayout_mcp")
        self.gridLayout_mcp.setContentsMargins(14, 18, 14, 14)
        self.label_mcp_status_title = QLabel(self.groupBox_mcp)
        self.label_mcp_status_title.setObjectName(u"label_mcp_status_title")
        self.gridLayout_mcp.addWidget(self.label_mcp_status_title, 0, 0, 1, 1)
        self.label_mcp_status_value = QLabel(self.groupBox_mcp)
        self.label_mcp_status_value.setObjectName(u"label_mcp_status_value")
        self.gridLayout_mcp.addWidget(self.label_mcp_status_value, 0, 1, 1, 2)
        self.label_mcp_endpoint = QLabel(self.groupBox_mcp)
        self.label_mcp_endpoint.setObjectName(u"label_mcp_endpoint")
        self.gridLayout_mcp.addWidget(self.label_mcp_endpoint, 1, 0, 1, 3)
        self.bt_mcp_help = QPushButton(self.groupBox_mcp)
        self.bt_mcp_help.setObjectName(u"bt_mcp_help")
        self.gridLayout_mcp.addWidget(self.bt_mcp_help, 2, 1, 1, 1)
        self.bt_mcp_toggle = QPushButton(self.groupBox_mcp)
        self.bt_mcp_toggle.setObjectName(u"bt_mcp_toggle")
        self.gridLayout_mcp.addWidget(self.bt_mcp_toggle, 2, 2, 1, 1)

        self.groupBox_2 = QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(12, 146, 500, 182))
        self.groupBox_2.setStyleSheet(u"QGroupBox { font-weight: 600; border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 14px; margin-top: 12px; padding-top: 12px; } QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; }")
        self.gridLayout_4 = QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(14, 18, 14, 14)
        self.choice_theme = QComboBox(self.groupBox_2)
        self.choice_theme.setObjectName(u"choice_theme")
        sizePolicy.setHeightForWidth(self.choice_theme.sizePolicy().hasHeightForWidth())
        self.choice_theme.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.choice_theme, 3, 1, 1, 1)

        self.label_execute_interval = QLabel(self.groupBox_2)
        self.label_execute_interval.setObjectName(u"label_execute_interval")

        self.gridLayout_4.addWidget(self.label_execute_interval, 2, 0, 1, 1)

        self.label_theme = QLabel(self.groupBox_2)
        self.label_theme.setObjectName(u"label_theme")

        self.gridLayout_4.addWidget(self.label_theme, 3, 0, 1, 1)

        self.mouse_move_interval_ms = QSpinBox(self.groupBox_2)
        self.mouse_move_interval_ms.setObjectName(u"mouse_move_interval_ms")
        sizePolicy.setHeightForWidth(self.mouse_move_interval_ms.sizePolicy().hasHeightForWidth())
        self.mouse_move_interval_ms.setSizePolicy(sizePolicy)
        self.mouse_move_interval_ms.setMinimum(1)
        self.mouse_move_interval_ms.setMaximum(1000)
        self.mouse_move_interval_ms.setValue(100)

        self.gridLayout_4.addWidget(self.mouse_move_interval_ms, 2, 1, 1, 1)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.choice_script = QComboBox(self.groupBox_2)
        self.choice_script.setObjectName(u"choice_script")
        sizePolicy.setHeightForWidth(self.choice_script.sizePolicy().hasHeightForWidth())
        self.choice_script.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.choice_script, 0, 0, 1, 1)

        self.bt_open_script_files = QPushButton(self.groupBox_2)
        self.bt_open_script_files.setObjectName(u"bt_open_script_files")
        sizePolicy.setHeightForWidth(self.bt_open_script_files.sizePolicy().hasHeightForWidth())
        self.bt_open_script_files.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.bt_open_script_files, 0, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 3)
        self.gridLayout.setColumnStretch(1, 1)

        self.gridLayout_4.addLayout(self.gridLayout, 0, 1, 1, 1)

        self.label_script = QLabel(self.groupBox_2)
        self.label_script.setObjectName(u"label_script")

        self.gridLayout_4.addWidget(self.label_script, 0, 0, 1, 1)

        self.label_run_times = QLabel(self.groupBox_2)
        self.label_run_times.setObjectName(u"label_run_times")

        self.gridLayout_4.addWidget(self.label_run_times, 1, 0, 1, 1)

        self.stimes = QSpinBox(self.groupBox_2)
        self.stimes.setObjectName(u"stimes")
        sizePolicy.setHeightForWidth(self.stimes.sizePolicy().hasHeightForWidth())
        self.stimes.setSizePolicy(sizePolicy)
        self.stimes.setMaximum(99999)
        self.stimes.setValue(1)

        self.gridLayout_4.addWidget(self.stimes, 1, 1, 1, 1)

        UIView.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(UIView)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 920, 24))
        UIView.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(UIView)
        self.statusbar.setObjectName(u"statusbar")
        UIView.setStatusBar(self.statusbar)
        self.centralwidget.setStyleSheet(u"QPushButton { min-height: 36px; border-radius: 10px; padding: 6px 14px; font-weight: 600; } QPushButton#btrecord { background-color: #16a34a; color: white; } QPushButton#btrun { background-color: #0ea5e9; color: white; } QPushButton#btpauserecord { background-color: #f59e0b; color: white; } QPushButton#bt_mcp_toggle { background-color: #7c3aed; color: white; } QPushButton#bt_mcp_help { background-color: #334155; color: white; } QTextEdit { border: 1px solid rgba(148, 163, 184, 0.35); border-radius: 12px; padding: 8px; } QComboBox, QSpinBox { min-height: 32px; border-radius: 8px; padding-left: 8px; } QLabel#tnumrd { font-weight: 600; } QLabel#label_mcp_status_value { font-weight: 700; color: #16a34a; } QLabel#label_mcp_endpoint { color: #475569; }")

        self.retranslateUi(UIView)

        QMetaObject.connectSlotsByName(UIView)
    # setupUi

    def retranslateUi(self, UIView):
        UIView.setWindowTitle(QCoreApplication.translate("UIView", u"ClawMouse", None))
        self.label_brand_title.setText(QCoreApplication.translate("UIView", u"ClawMouse", None))
        self.label_brand_subtitle.setText(QCoreApplication.translate("UIView", u"Desktop automation, MCP control, window messaging and bridge workflows", None))
        self.label_brand_flow.setText(QCoreApplication.translate("UIView", u"WeChat -> Lobster -> ClawMouse MCP -> Trae -> Screenshot / result -> WeChat", None))
        self.groupBox.setTitle(QCoreApplication.translate("UIView", u"Hotkey Control", None))
        self.label_language.setText(QCoreApplication.translate("UIView", u"Language", None))
        self.label_stop.setText(QCoreApplication.translate("UIView", u"Stop", None))
        self.label_start_key.setText(QCoreApplication.translate("UIView", u"Run / Pause", None))
        self.label_record.setText(QCoreApplication.translate("UIView", u"Record / Pause", None))
        self.hotkey_start.setText("")
        self.hotkey_record.setText("")
        self.hotkey_stop.setText("")
        self.btrecord.setText(QCoreApplication.translate("UIView", u"Record", None))
        self.btrun.setText(QCoreApplication.translate("UIView", u"Run", None))
        self.btpauserecord.setText(QCoreApplication.translate("UIView", u"Pause Record", None))
        self.tnumrd.setText(QCoreApplication.translate("UIView", u"ClawMouse ready. Choose a script or start recording.", None))
        self.label_cursor_pos.setText(QCoreApplication.translate("UIView", u"Cursor:", None))
        self.label_volume.setText(QCoreApplication.translate("UIView", u"Volume", None))
        self.groupBox_mcp.setTitle(QCoreApplication.translate("UIView", u"MCP Service", None))
        self.label_mcp_status_title.setText(QCoreApplication.translate("UIView", u"Status", None))
        self.label_mcp_status_value.setText(QCoreApplication.translate("UIView", u"Starting...", None))
        self.label_mcp_endpoint.setText(QCoreApplication.translate("UIView", u"HTTP 127.0.0.1:8765", None))
        self.bt_mcp_help.setText(QCoreApplication.translate("UIView", u"Help", None))
        self.bt_mcp_toggle.setText(QCoreApplication.translate("UIView", u"Stop MCP", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("UIView", u"Run Profile", None))
        self.label_execute_interval.setText(QCoreApplication.translate("UIView", u"Move Precision", None))
        self.label_theme.setText(QCoreApplication.translate("UIView", u"Theme", None))
        self.bt_open_script_files.setText(QCoreApplication.translate("UIView", u"...", None))
        self.label_script.setText(QCoreApplication.translate("UIView", u"Script", None))
        self.label_run_times.setText(QCoreApplication.translate("UIView", u"Run Times", None))
    # retranslateUi

