# -*- encoding:utf-8 -*-
import datetime
import json
from typing import List

import json5
import os
import sys
import threading
import platform
import locale
import Recorder

from PySide6.QtGui import QTextCursor, QPixmap
from qt_material import list_themes, QtStyleTools
from PySide6.QtCore import *
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PySide6.QtMultimedia import QSoundEffect
from loguru import logger

from Event import ScriptEvent, flag_multiplemonitor
from Plugin.Manager import PluginManager
from UIView import Ui_UIView

from KeymouseGo import to_abs_path
from Util.RunScriptClass import RunScriptClass
from Util.Global import State
from Util.ClickedLabel import Label


os.environ['QT_ENABLE_HIGHDPI_SCALING'] = "1"
# if platform.system() == 'Windows':
#     HOT_KEYS = ['F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
#                 'XButton1', 'XButton2', 'Middle']
# else:
#     HOT_KEYS = ['F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
#                 'Middle']

logger.remove()
if sys.stdout is not None:
    logger.add(sys.stdout, backtrace=True, diagnose=True,
               level='DEBUG')
logger.add(to_abs_path('logs', '{time}.log'), rotation='20MB', backtrace=True, diagnose=True,
           level='INFO')


def get_assets_path(*paths):
    # pyinstaller -F --add-data ./assets;assets KeymouseGo.py
    try:
        root = sys._MEIPASS
    except:
        root = os.getcwd()
    return os.path.join(root, 'assets', *paths)


scripts = []
scripts_map = {'current_index': 0, 'choice_language': '简体中文'}


def get_script_list_from_dir():
    global scripts

    if not os.path.exists(to_abs_path('scripts')):
        os.mkdir(to_abs_path('scripts'))
    scripts = os.listdir(to_abs_path('scripts'))[::-1]
    scripts = list(filter(lambda s: s.endswith('.txt') or s.endswith('.json5'), scripts))


def update_script_map():
    global scripts_map
    
    for (i, item) in enumerate(scripts):
        scripts_map[item] = i

class UIFunc(QMainWindow, Ui_UIView, QtStyleTools):
    updateStateSignal: Signal = Signal(State)

    def __init__(self, app):
        global scripts

        super(UIFunc, self).__init__()

        logger.info('assets root:{0}'.format(get_assets_path()))

        self.setupUi(self)
        self._apply_brand_icon()
        self._apply_responsive_layout()

        self.app = app

        self.state = State(State.IDLE)

        self.config = self.loadconfig()

        self.setFocusPolicy(Qt.NoFocus)
        self.mcp_host = '127.0.0.1'
        self.mcp_port = int(self.config.value("Config/MCPPort", 8765))
        self.mcp_process = QProcess(self)
        self.mcp_process.setProcessChannelMode(QProcess.MergedChannels)
        self.mcp_process.started.connect(self.handle_mcp_process_started)
        self.mcp_process.readyReadStandardOutput.connect(self.handle_mcp_process_output)
        self.mcp_process.errorOccurred.connect(self.handle_mcp_process_error)
        self.mcp_process.finished.connect(self.handle_mcp_process_finished)

        self.trans = QTranslator(self)
        self.choice_language.addItems(['简体中文', 'English', '繁體中文'])
        self.choice_language.currentTextChanged.connect(self.onchangelang)

        # 获取默认的地区设置
        language = '简体中文' if locale.getdefaultlocale()[0] == 'zh_CN' else 'English'
        self.choice_language.setCurrentText(language)
        self.onchangelang()

        get_script_list_from_dir()
        update_script_map()
        self.scripts = scripts
        self.choice_script.addItems(self.scripts)
        if self.scripts:
            self.choice_script.setCurrentIndex(0)

        PluginManager.reload()

        # Config
        self.choice_theme.addItems(['Default'])
        self.choice_theme.addItems(list_themes())
        # self.choice_theme.addItems(PluginManager.resources_paths)
        self.stimes.setValue(int(self.config.value("Config/LoopTimes")))
        self.mouse_move_interval_ms.setValue(int(self.config.value("Config/Precision")))
        self.choice_theme.setCurrentText(self.config.value("Config/Theme"))
        if self.config.value('Config/Script') is not None and self.config.value('Config/Script') in self.scripts:
            self.choice_script.setCurrentText(self.config.value('Config/Script'))
        self.stimes.valueChanged.connect(self.onconfigchange)
        self.mouse_move_interval_ms.valueChanged.connect(self.onconfigchange)
        self.mouse_move_interval_ms.valueChanged.connect(Recorder.set_interval)
        self.choice_theme.currentTextChanged.connect(self.onchangetheme)
        self.choice_script.currentTextChanged.connect(self.onconfigchange)
        self.hotkey_stop.setText(self.config.value("Config/StopHotKey"))
        self.hotkey_start.setText(self.config.value("Config/StartHotKey"))
        self.hotkey_record.setText(self.config.value("Config/RecordHotKey"))


        self.onchangetheme()

        self.textlog.textChanged.connect(lambda: self.textlog.moveCursor(QTextCursor.End))

        # For tune playing
        self.player = QSoundEffect()
        self.volumeSlider.setValue(50)
        self.volumeSlider.valueChanged.connect(
            lambda: self.player.setVolume(
                self.volumeSlider.value()/100.0))

        self.record = []

        self.actioncount = 0

        # For better thread control
        self.runthread = None

        self.btrun.clicked.connect(self.OnBtrunButton)
        self.btrecord.clicked.connect(self.OnBtrecordButton)
        self.btpauserecord.clicked.connect(self.OnPauseRecordButton)
        self.bt_open_script_files.clicked.connect(self.OnBtOpenScriptFilesButton)
        self.bt_mcp_help.clicked.connect(self.show_mcp_help)
        self.bt_mcp_toggle.clicked.connect(self.toggle_mcp_process)
        self.choice_language.installEventFilter(self)
        self.choice_script.installEventFilter(self)
        self.btrun.installEventFilter(self)
        self.btrecord.installEventFilter(self)
        self.btpauserecord.installEventFilter(self)
        self.bt_open_script_files.installEventFilter(self)

        # 组合键缓冲池，[ctrl,shift,alt,cmd/start/win]可用作组合键，但不能单独用作启动热键
        self.keys_pool: List[str] = []
        self.hotkey_set_btn = None
        self.hotkey_stop.clicked.connect(lambda: self.OnHotkeyButton(self.hotkey_stop))
        self.hotkey_start.clicked.connect(lambda: self.OnHotkeyButton(self.hotkey_start))
        self.hotkey_record.clicked.connect(lambda: self.OnHotkeyButton(self.hotkey_record))

        # 热键引发状态转移
        def check_hotkeys(key_name):
            if key_name in Recorder.globals.key_combination_trigger:
                if self.state == State.SETTING_HOT_KEYS:
                    self.hotkey_set_btn.setText('+'.join(self.keys_pool))
                return False
            key_name = '+'.join([*self.keys_pool, key_name])

            if self.state == State.SETTING_HOT_KEYS:
                for btn in [self.hotkey_start, self.hotkey_record, self.hotkey_stop]:
                    if btn is not self.hotkey_set_btn and btn.text() != '' and btn.text() == key_name:
                        self.keys_pool.clear()
                        self.hotkey_set_btn.setText('')
                        self.update_state(State.IDLE)
                        return False
                self.hotkey_set_btn.setText(key_name)
                self.update_state(State.IDLE)
                self.onconfigchange()
                return False

            start_name = self.hotkey_start.text()
            stop_name = self.hotkey_stop.text()
            record_name = self.hotkey_record.text()

            if key_name == start_name:
                if self.state == State.IDLE:
                    logger.debug('{0} host start'.format(key_name))
                    self.OnBtrunButton()
                elif self.state == State.RUNNING:
                    logger.info('Script pause')
                    logger.debug('{0} host pause'.format(key_name))
                    self.runthread.set_pause()
                    self.update_state(State.PAUSE_RUNNING)
                elif self.state == State.PAUSE_RUNNING:
                    logger.info('Script resume')
                    self.runthread.resume()
                    logger.debug('{0} host resume'.format(key_name))
                    self.update_state(State.RUNNING)
            elif key_name == stop_name:
                if self.state == State.RUNNING or self.state == State.PAUSE_RUNNING:
                    logger.info('Script stop')
                    self.tnumrd.setText('broken')
                    self.runthread.resume()
                    logger.debug('{0} host stop'.format(key_name))
                    self.update_state(State.IDLE)
                elif self.state == State.RECORDING or self.state == State.PAUSE_RECORDING:
                    self.recordMethod()
                    logger.info('Record stop')
                    logger.debug('{0} host stop record'.format(key_name))
            elif key_name == record_name:
                if self.state == State.RECORDING:
                    self.pauseRecordMethod()
                    logger.debug('{0} host pause record'.format(key_name))
                elif self.state == State.PAUSE_RECORDING:
                    self.pauseRecordMethod()
                    logger.debug('{0} host resume record'.format(key_name))
                elif self.state == State.IDLE:
                    self.recordMethod()
                    logger.debug('{0} host start record'.format(key_name))
            return key_name in [start_name, stop_name, record_name]

        @Slot(ScriptEvent)
        def on_record_event(event: ScriptEvent):
            # 判断mouse热键
            if event.event_type == "EM":
                name = event.action_type
                if 'mouse x1 down' == name and check_hotkeys('xbutton1'):
                    return
                elif 'mouse x2 down' == name and check_hotkeys('xbutton2'):
                    return
                elif 'mouse middle down' == name and check_hotkeys('middle'):
                    return
            else:
                key_name = event.action[1].lower()
                if event.action_type == 'key down':
                    if key_name in Recorder.globals.key_combination_trigger and len(self.keys_pool) < 3 and key_name not in self.keys_pool:
                        self.keys_pool.append(key_name)
                    # listen for start/stop script
                    # start_name = 'f6'  # as default
                    # stop_name = 'f9'  # as default
                    check_hotkeys(key_name)
                elif event.action_type == 'key up':
                    if key_name in Recorder.globals.key_combination_trigger and key_name in self.keys_pool:
                        self.keys_pool.remove(key_name)
                        check_hotkeys(key_name)
                # 不录制热键
                for btn in [self.hotkey_start, self.hotkey_record, self.hotkey_stop]:
                    if key_name == btn.text():
                        return
            # 录制事件
            if self.state == State.RECORDING:
                if event.event_type == 'EM' and not flag_multiplemonitor:
                    tx, ty = event.action
                    event.action = ['{0}%'.format(tx), '{0}%'.format(ty)]
                event_dict = event.__dict__
                event_dict['type'] = 'event'
                # PluginManager.call_record(event_dict)
                self.record.append(event_dict)
                self.actioncount = self.actioncount + 1
                text = '%d actions recorded' % self.actioncount
                logger.debug('Recorded %s' % event)
                self.tnumrd.setText(text)
                self.textlog.append(str(event))
        logger.debug('Initialize at thread ' + str(QThread.currentThread()))
        Recorder.setuphook()
        Recorder.set_callback(on_record_event)
        Recorder.set_cursor_pose_change(self.cursor_pos_change)
        Recorder.set_interval(self.mouse_move_interval_ms.value())
        self.update_mcp_controls(False, 'Stopped')
        QTimer.singleShot(200, self.ensure_mcp_started)

    def eventFilter(self, watched, event: QEvent):
        et: QEvent.Type = event.type()
        # print(event, et)
        if et == QEvent.KeyPress or et == QEvent.KeyRelease:
            return True
        return super(UIFunc, self).eventFilter(watched, event)

    def onconfigchange(self):
        self.config.setValue("Config/LoopTimes", self.stimes.value())
        self.config.setValue("Config/Precision", self.mouse_move_interval_ms.value())
        self.config.setValue("Config/Theme", self.choice_theme.currentText())
        self.config.setValue("Config/Script", self.choice_script.currentText())
        self.config.setValue("Config/StartHotKey", self.hotkey_start.text())
        self.config.setValue("Config/StopHotKey", self.hotkey_stop.text())
        self.config.setValue("Config/RecordHotKey", self.hotkey_record.text())

    def onchangelang(self):
        global scripts_map

        if self.choice_language.currentText() == '简体中文':
            self.trans.load(get_assets_path('i18n', 'zh-cn'))
            _app = QApplication.instance()
            _app.installTranslator(self.trans)
            self.retranslateUi(self)
        elif self.choice_language.currentText() == 'English':
            self.trans.load(get_assets_path('i18n', 'en'))
            _app = QApplication.instance()
            _app.installTranslator(self.trans)
            self.retranslateUi(self)
        elif self.choice_language.currentText() == '繁體中文':
            self.trans.load(get_assets_path('i18n', 'zh-tw'))
            _app = QApplication.instance()
            _app.installTranslator(self.trans)
            self.retranslateUi(self)
        self.retranslateUi(self)
        self.hotkey_stop.setText(self.config.value("Config/StopHotKey"))
        self.hotkey_start.setText(self.config.value("Config/StartHotKey"))
        self.hotkey_record.setText(self.config.value("Config/RecordHotKey"))
        if hasattr(self, 'mcp_process'):
            self.update_mcp_controls(self.mcp_process.state() != QProcess.NotRunning, self.label_mcp_status_value.text())

    def onchangetheme(self):
        theme = self.choice_theme.currentText()
        if theme == 'Default':
            self.apply_stylesheet(self.app, theme='default')
        else:
            self.apply_stylesheet(self.app, theme=theme)
        self.config.setValue("Config/Theme", self.choice_theme.currentText())

    @Slot(str)
    def playtune(self, filename: str):
        self.player.setSource(QUrl.fromLocalFile(get_assets_path('sounds', filename)))
        self.player.play()

    def closeEvent(self, event):
        self.config.sync()
        self.stop_mcp_process(wait_ms=1200)
        Recorder.dispose()
        if self.state == State.PAUSE_RUNNING:
            self.update_state(State.RUNNING)
        elif self.state == State.PAUSE_RECORDING:
            self.update_state(State.RECORDING)
        if self.runthread:
            self.runthread.resume()
        event.accept()

    def resizeEvent(self, event):
        self._apply_responsive_layout()
        return super(UIFunc, self).resizeEvent(event)

    def loadconfig(self):
        if not os.path.exists(to_abs_path('config.ini')):
            with open(to_abs_path('config.ini'), 'w', encoding='utf-8') as f:
                f.write('[Config]\n'
                        'StartHotKey=f6\n'
                        'StopHotKey=f9\n'
                        'RecordHotKey=f10\n'
                        'LoopTimes=1\n'
                        'Precision=200\n'
                        'MCPPort=8765\n'
                        'Language=zh-cn\n'
                        'Theme=Default\n')
        return QSettings(to_abs_path('config.ini'), QSettings.IniFormat)

    def get_script_path(self):
        i = self.choice_script.currentIndex()
        if i < 0:
            return ''
        script = self.scripts[i]
        path = os.path.join(to_abs_path('scripts'), script)
        logger.info('Script path: {0}'.format(path))
        return path

    def new_script_path(self):
        now = datetime.datetime.now()
        script = '%s.json5' % now.strftime('%m%d_%H%M')
        if script in self.scripts:
            script = '%s.json5' % now.strftime('%m%d_%H%M%S')
        self.scripts.insert(0, script)
        update_script_map()
        self.choice_script.clear()
        self.choice_script.addItems(self.scripts)
        self.choice_script.setCurrentIndex(0)
        return self.get_script_path()

    def pauseRecordMethod(self):
        if self.state == State.PAUSE_RECORDING:
            logger.info('Record resume')
            self.btpauserecord.setText(QCoreApplication.translate("UIView", 'Pause Recording', None))
            self.update_state(State.RECORDING)
        elif self.state == State.RECORDING:
            logger.info('Record pause')
            self.btpauserecord.setText(QCoreApplication.translate("UIView", 'Continue', None))
            self.tnumrd.setText('Recording paused')
            self.update_state(State.PAUSE_RECORDING)

    def OnPauseRecordButton(self):
        self.pauseRecordMethod()

    def OnBtOpenScriptFilesButton(self):
        global scripts_map

        import UIFileDialogFunc

        scripts_map['current_index'] = self.choice_script.currentIndex()
        file_dialog = UIFileDialogFunc.FileDialog()
        self.bt_open_script_files.setDisabled(True)
        self.btrecord.setDisabled(True)
        self.btrun.setDisabled(True)
        self.hotkey_start.setDisabled(True)
        self.hotkey_stop.setDisabled(True)
        self.hotkey_record.setDisabled(True)
        file_dialog.show()
        self.bt_open_script_files.setDisabled(False)
        self.btrecord.setDisabled(False)
        self.btrun.setDisabled(False)
        self.hotkey_start.setEnabled(True)
        self.hotkey_stop.setEnabled(True)
        self.hotkey_record.setEnabled(True)
        # 重新设置的为点击按钮时, 所处的位置
        self.choice_script.clear()
        self.choice_script.addItems(scripts)
        self.choice_script.setCurrentIndex(scripts_map['current_index'])

    def recordMethod(self):
        if self.state == State.RECORDING or self.state == State.PAUSE_RECORDING:
            logger.info('Record stop')
            with open(self.new_script_path(), 'w', encoding='utf-8') as f:
                json5.dump({"scripts": self.record}, indent=2, ensure_ascii=False, fp=f)
            self.btrecord.setText(QCoreApplication.translate("UIView", 'Record', None))
            self.tnumrd.setText('Recording finished')
            self.record = []
            self.actioncount = 0
            self.choice_script.setCurrentIndex(0)
            self.btpauserecord.setText(QCoreApplication.translate("UIView", 'Pause Record', None))
            self.update_state(State.IDLE)
        elif self.state == State.IDLE:
            logger.info('Record start')
            self.textlog.clear()
            status = self.tnumrd.text()
            if 'running' in status or 'recorded' in status:
                return
            self.btrecord.setText(QCoreApplication.translate("UIView", 'Finish', None))
            self.tnumrd.setText('0 actions recorded')
            self.record = []
            self.update_state(State.RECORDING)

    def OnBtrecordButton(self):
        if self.state == State.RECORDING or self.state == State.PAUSE_RECORDING:
            self.record = self.record[:-2]
        self.recordMethod()

    def OnBtrunButton(self):
        logger.info('Script start')
        self.textlog.clear()
        self.update_state(State.RUNNING)
        if self.runthread:
            self.updateStateSignal.disconnect()
        self.runthread = RunScriptClass(self)
        self.runthread.start()

    def update_state(self, state):
        self.state = state
        if state != State.SETTING_HOT_KEYS or state != State.RECORDING or state != State.PAUSE_RECORDING:
            self.updateStateSignal.emit(self.state)
        if state == State.IDLE:
            self.hotkey_start.setEnabled(True)
            self.hotkey_stop.setEnabled(True)
            self.hotkey_record.setEnabled(True)
            self.btrun.setEnabled(True)
            self.btrecord.setEnabled(True)
            self.btpauserecord.setEnabled(False)
        elif state == State.RUNNING or state == State.PAUSE_RUNNING or state == State.SETTING_HOT_KEYS:
            self.hotkey_start.setEnabled(False)
            self.hotkey_stop.setEnabled(False)
            self.hotkey_record.setEnabled(False)
            self.btrun.setEnabled(False)
            self.btrecord.setEnabled(False)
            self.btpauserecord.setEnabled(False)
        elif state == State.RECORDING or state == State.PAUSE_RECORDING:
            self.hotkey_start.setEnabled(False)
            self.hotkey_stop.setEnabled(False)
            self.hotkey_record.setEnabled(False)
            self.btrun.setEnabled(False)
            self.btrecord.setEnabled(True)
            self.btpauserecord.setEnabled(True)

    def OnHotkeyButton(self, btn_obj: QObject):
        self.hotkey_set_btn = btn_obj
        self.update_state(State.SETTING_HOT_KEYS)

    @Slot(bool)
    def handle_runscript_status(self, succeed):
        self.update_state(State.IDLE)

    @Slot(tuple)
    def cursor_pos_change(self, pos):
        self.label_cursor_pos.setText(f'Cursor: {pos}')

    def _apply_brand_icon(self):
        pixmap = QPixmap(':/pic/Mondrian.png')
        if pixmap.isNull():
            return
        scaled = pixmap.scaled(84, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_brand_icon.setPixmap(scaled)

    def _apply_responsive_layout(self):
        margin = 12
        gap = 18
        width = max(self.width(), 920)
        height = max(self.height(), 720)
        content_width = width - margin * 2
        top_width = max(896, content_width)
        self.brandPanel.setGeometry(QRect(margin, margin, top_width, 118))
        self.label_brand_flow.setGeometry(QRect(20, 84, max(500, top_width - 170), 22))
        self.label_brand_icon.setGeometry(QRect(top_width - 112, 16, 92, 86))

        lower_width = content_width
        left_width = max(500, int((lower_width - gap) * 0.56))
        right_width = max(360, lower_width - gap - left_width)
        if left_width + right_width + gap > lower_width:
            left_width = lower_width - gap - right_width
        left_x = margin
        right_x = left_x + left_width + gap

        self.groupBox_2.setGeometry(QRect(left_x, 146, left_width, 182))
        self.groupBox.setGeometry(QRect(right_x, 146, right_width, 182))
        self.horizontalLayoutWidget.setGeometry(QRect(left_x, 340, left_width, 52))
        self.groupBox_mcp.setGeometry(QRect(right_x, 340, right_width, 116))

        bottom_top = 470
        bottom_height = max(170, height - bottom_top - 54)
        self.verticalLayoutWidget.setGeometry(QRect(margin, bottom_top, lower_width, bottom_height))
        self.formLayoutWidget_3.setGeometry(QRect(margin, height - 34, min(360, lower_width), 24))

    def _get_stdio_mcp_config(self):
        if getattr(sys, 'frozen', False):
            command = os.path.normpath(sys.executable)
            args = ['--mcp-server']
            cwd = os.path.dirname(command)
        else:
            command = os.path.normpath(sys.executable)
            args = [os.path.normpath(to_abs_path('ClawMouse.py')), '--mcp-server']
            cwd = os.path.normpath(to_abs_path())
        return {
            'command': command,
            'args': args,
            'cwd': cwd,
            'env': {
                'PYTHONIOENCODING': 'utf-8',
            },
        }

    def _get_http_mcp_launch(self):
        config = self._get_stdio_mcp_config()
        launch_args = list(config['args'])
        launch_args.extend(['--transport', 'http', '--host', self.mcp_host, '--port', str(self.mcp_port)])
        return config['command'], launch_args, config['cwd']

    def _build_mcp_help_text(self):
        config = self._get_stdio_mcp_config()
        json_text = json.dumps({
            'mcpServers': {
                'clawmouse': config,
            }
        }, ensure_ascii=False, indent=2)
        args_text = '\n'.join(config['args'])
        help_text = (
            'ClawMouse MCP 配置说明\n\n'
            '当前界面启动后会默认拉起一个本地 HTTP MCP 服务，方便本机调试：\n'
            f'http://{self.mcp_host}:{self.mcp_port}\n\n'
            '如果你要在桌面版 Trae 里接入 MCP，推荐使用标准输入输出 (stdio) 方式。\n'
            '请按你当前环境使用下面这份严格 JSON：\n\n'
            f'{json_text}\n\n'
            '如果你使用 Trae 的“编辑 MCP 服务”表单：\n'
            f'服务名称：clawmouse\n'
            f'传输类型：标准输入输出 (stdio)\n'
            f'命令：{config["command"]}\n'
            f'参数：\n{args_text}\n'
            f'工作目录：{config["cwd"]}\n'
            '环境变量：PYTHONIOENCODING=utf-8\n\n'
            '如果 Trae 提示 JSON 格式错误，请检查双反斜杠、尾逗号和粘贴位置。'
        )
        return help_text

    def show_mcp_help(self):
        QMessageBox.information(self, 'ClawMouse MCP Help', self._build_mcp_help_text())

    def update_mcp_controls(self, running: bool, status_text: str):
        self.label_mcp_status_value.setText(status_text)
        self.label_mcp_endpoint.setText(f'HTTP {self.mcp_host}:{self.mcp_port}')
        if running:
            self.label_mcp_status_value.setStyleSheet('color: #16a34a; font-weight: 700;')
            self.bt_mcp_toggle.setText('Stop MCP')
        else:
            self.label_mcp_status_value.setStyleSheet('color: #dc2626; font-weight: 700;')
            self.bt_mcp_toggle.setText('Start MCP')
        self.statusbar.showMessage(f'MCP: {status_text}', 5000)

    def ensure_mcp_started(self):
        if self.mcp_process.state() != QProcess.NotRunning:
            self.update_mcp_controls(True, 'Running')
            return
        self.start_mcp_process()

    def start_mcp_process(self):
        if self.mcp_process.state() != QProcess.NotRunning:
            self.update_mcp_controls(True, 'Running')
            return
        command, args, cwd = self._get_http_mcp_launch()
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert('PYTHONIOENCODING', 'utf-8')
        self.mcp_process.setProcessEnvironment(environment)
        self.mcp_process.setProgram(command)
        self.mcp_process.setArguments(args)
        self.mcp_process.setWorkingDirectory(cwd)
        self.update_mcp_controls(False, 'Starting...')
        logger.info(f'Starting MCP process: {command} {args}')
        self.mcp_process.start()

    def stop_mcp_process(self, wait_ms: int = 800):
        if self.mcp_process.state() == QProcess.NotRunning:
            self.update_mcp_controls(False, 'Stopped')
            return
        self.mcp_process.terminate()
        if not self.mcp_process.waitForFinished(wait_ms):
            self.mcp_process.kill()
            self.mcp_process.waitForFinished(wait_ms)
        self.update_mcp_controls(False, 'Stopped')

    def toggle_mcp_process(self):
        if self.mcp_process.state() == QProcess.NotRunning:
            self.start_mcp_process()
        else:
            self.stop_mcp_process()

    @Slot()
    def handle_mcp_process_started(self):
        self.update_mcp_controls(True, 'Running')
        self.textlog.append(f'[MCP] Running on http://{self.mcp_host}:{self.mcp_port}')

    @Slot()
    def handle_mcp_process_output(self):
        content = bytes(self.mcp_process.readAllStandardOutput()).decode('utf-8', errors='ignore').strip()
        if not content:
            return
        for line in content.splitlines():
            self.textlog.append(f'[MCP] {line}')

    @Slot(QProcess.ProcessError)
    def handle_mcp_process_error(self, error):
        error_name = getattr(error, 'name', str(int(error)))
        self.update_mcp_controls(False, f'Error: {error_name}')
        self.textlog.append(f'[MCP] Process error: {error_name}')

    @Slot(int, QProcess.ExitStatus)
    def handle_mcp_process_finished(self, exit_code, exit_status):
        status_name = getattr(exit_status, 'name', str(int(exit_status)))
        self.update_mcp_controls(False, f'Stopped ({exit_code})')
        self.textlog.append(f'[MCP] Process finished: exit_code={exit_code}, exit_status={status_name}')
