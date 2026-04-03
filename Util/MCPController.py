import base64
import hashlib
import json
import os
import subprocess
import threading
import time
import uuid
from typing import Any, Dict, Iterable, List, Optional, Tuple

import json5
from loguru import logger
from PySide6.QtCore import QBuffer, QByteArray, Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPen

from Event import ScriptEvent
from Plugin.Manager import PluginManager
from Util.Parser import JsonObject, LegacyParser, ScriptParser

try:
    import win32api
except ImportError:
    win32api = None

try:
    import win32con
    import win32gui
except ImportError:
    win32con = None
    win32gui = None


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'scripts')
CHAT_PROFILE_CONFIG_PATH = os.path.join(ROOT_DIR, 'chat_profiles.json5')
SCREENSHOT_PROFILE_CONFIG_PATH = os.path.join(ROOT_DIR, 'screenshot_profiles.json5')
SCREENSHOTS_DIR = os.path.join(ROOT_DIR, 'screenshots')
AI_BRIDGE_BASE_DIR = os.path.join(ROOT_DIR, 'ai_bridge')


CHAT_APP_PROFILES = {
    'browser_chat': {
        'title_substring': None,
        'exact_title': None,
        'class_name': 'Chrome_WidgetWin_1',
        'submit_mode': 'enter',
        'input_ratio': {'x': 0.5, 'y': 0.94},
        'send_ratio': None,
        'focus': True,
        'enter_delay_ms': 0,
        'enter_times': 1,
        'click_before_enter': False,
        'click_before_enter_delay_ms': 120,
    },
    'trae': {
        'title_substring': 'Trae',
        'exact_title': None,
        'class_name': 'Chrome_WidgetWin_1',
        'title_keywords': ['Trae', 'Trae Solo'],
        'submit_mode': 'enter',
        'input_ratio': {'x': 0.5, 'y': 0.94},
        'send_ratio': None,
        'focus': True,
        'enter_delay_ms': 250,
        'enter_times': 2,
        'click_before_enter': True,
        'click_before_enter_delay_ms': 120,
    },
    'trae_solo': {
        'title_substring': 'Trae Solo',
        'exact_title': None,
        'class_name': 'Chrome_WidgetWin_1',
        'title_keywords': ['Trae Solo', 'Trae'],
        'submit_mode': 'enter',
        'input_ratio': {'x': 0.5, 'y': 0.94},
        'send_ratio': None,
        'focus': True,
        'enter_delay_ms': 250,
        'enter_times': 2,
        'click_before_enter': True,
        'click_before_enter_delay_ms': 120,
    },
    'wechat': {
        'title_substring': '微信',
        'exact_title': None,
        'class_name': None,
        'submit_mode': 'enter',
        'input_ratio': {'x': 0.5, 'y': 0.94},
        'send_ratio': None,
        'focus': True,
        'enter_delay_ms': 0,
        'enter_times': 1,
        'click_before_enter': False,
        'click_before_enter_delay_ms': 120,
    },
    'qq': {
        'title_substring': 'QQ',
        'exact_title': None,
        'class_name': None,
        'submit_mode': 'enter',
        'input_ratio': {'x': 0.5, 'y': 0.94},
        'send_ratio': None,
        'focus': True,
        'enter_delay_ms': 0,
        'enter_times': 1,
        'click_before_enter': False,
        'click_before_enter_delay_ms': 120,
    },
}


SCREENSHOT_APP_PROFILES = {
    'trae': {
        'title_substring': 'Trae',
        'exact_title': None,
        'class_name': 'Chrome_WidgetWin_1',
        'rows': 2,
        'cols': 2,
        'partitions': [
            {'name': 'left_header', 'left_ratio': 0.0, 'top_ratio': 0.0, 'right_ratio': 0.17, 'bottom_ratio': 0.08},
            {'name': 'left_primary', 'left_ratio': 0.0, 'top_ratio': 0.08, 'right_ratio': 0.17, 'bottom_ratio': 0.42},
            {'name': 'left_secondary', 'left_ratio': 0.0, 'top_ratio': 0.42, 'right_ratio': 0.17, 'bottom_ratio': 0.76},
            {'name': 'left_footer', 'left_ratio': 0.0, 'top_ratio': 0.76, 'right_ratio': 0.17, 'bottom_ratio': 1.0},
            {'name': 'top_left', 'left_ratio': 0.17, 'top_ratio': 0.0, 'right_ratio': 0.44, 'bottom_ratio': 0.08},
            {'name': 'top_center', 'left_ratio': 0.44, 'top_ratio': 0.0, 'right_ratio': 0.72, 'bottom_ratio': 0.08},
            {'name': 'top_right', 'left_ratio': 0.72, 'top_ratio': 0.0, 'right_ratio': 1.0, 'bottom_ratio': 0.08},
            {'name': 'main_left', 'left_ratio': 0.17, 'top_ratio': 0.08, 'right_ratio': 0.44, 'bottom_ratio': 0.76},
            {'name': 'main_center', 'left_ratio': 0.44, 'top_ratio': 0.08, 'right_ratio': 0.72, 'bottom_ratio': 0.76},
            {'name': 'main_right', 'left_ratio': 0.72, 'top_ratio': 0.08, 'right_ratio': 1.0, 'bottom_ratio': 0.76},
            {'name': 'bottom_left', 'left_ratio': 0.17, 'top_ratio': 0.76, 'right_ratio': 0.44, 'bottom_ratio': 1.0},
            {'name': 'bottom_center', 'left_ratio': 0.44, 'top_ratio': 0.76, 'right_ratio': 0.72, 'bottom_ratio': 1.0},
            {'name': 'bottom_right', 'left_ratio': 0.72, 'top_ratio': 0.76, 'right_ratio': 1.0, 'bottom_ratio': 1.0},
        ],
        'focus': True,
        'wait_after_focus_ms': 150,
    },
    'vscode': {
        'title_substring': 'Visual Studio Code',
        'exact_title': None,
        'class_name': 'Chrome_WidgetWin_1',
        'rows': 2,
        'cols': 2,
        'partitions': [
            {'name': 'left_header', 'left_ratio': 0.0, 'top_ratio': 0.0, 'right_ratio': 0.17, 'bottom_ratio': 0.08},
            {'name': 'left_primary', 'left_ratio': 0.0, 'top_ratio': 0.08, 'right_ratio': 0.17, 'bottom_ratio': 0.42},
            {'name': 'left_secondary', 'left_ratio': 0.0, 'top_ratio': 0.42, 'right_ratio': 0.17, 'bottom_ratio': 0.76},
            {'name': 'left_footer', 'left_ratio': 0.0, 'top_ratio': 0.76, 'right_ratio': 0.17, 'bottom_ratio': 1.0},
            {'name': 'top_left', 'left_ratio': 0.17, 'top_ratio': 0.0, 'right_ratio': 0.44, 'bottom_ratio': 0.08},
            {'name': 'top_center', 'left_ratio': 0.44, 'top_ratio': 0.0, 'right_ratio': 0.72, 'bottom_ratio': 0.08},
            {'name': 'top_right', 'left_ratio': 0.72, 'top_ratio': 0.0, 'right_ratio': 1.0, 'bottom_ratio': 0.08},
            {'name': 'main_left', 'left_ratio': 0.17, 'top_ratio': 0.08, 'right_ratio': 0.44, 'bottom_ratio': 0.76},
            {'name': 'main_center', 'left_ratio': 0.44, 'top_ratio': 0.08, 'right_ratio': 0.72, 'bottom_ratio': 0.76},
            {'name': 'main_right', 'left_ratio': 0.72, 'top_ratio': 0.08, 'right_ratio': 1.0, 'bottom_ratio': 0.76},
            {'name': 'bottom_left', 'left_ratio': 0.17, 'top_ratio': 0.76, 'right_ratio': 0.44, 'bottom_ratio': 1.0},
            {'name': 'bottom_center', 'left_ratio': 0.44, 'top_ratio': 0.76, 'right_ratio': 0.72, 'bottom_ratio': 1.0},
            {'name': 'bottom_right', 'left_ratio': 0.72, 'top_ratio': 0.76, 'right_ratio': 1.0, 'bottom_ratio': 1.0},
        ],
        'focus': True,
        'wait_after_focus_ms': 150,
    },
    'code': {
        'title_substring': 'Code',
        'exact_title': None,
        'class_name': 'Chrome_WidgetWin_1',
        'rows': 2,
        'cols': 2,
        'partitions': [
            {'name': 'left_header', 'left_ratio': 0.0, 'top_ratio': 0.0, 'right_ratio': 0.17, 'bottom_ratio': 0.08},
            {'name': 'left_primary', 'left_ratio': 0.0, 'top_ratio': 0.08, 'right_ratio': 0.17, 'bottom_ratio': 0.42},
            {'name': 'left_secondary', 'left_ratio': 0.0, 'top_ratio': 0.42, 'right_ratio': 0.17, 'bottom_ratio': 0.76},
            {'name': 'left_footer', 'left_ratio': 0.0, 'top_ratio': 0.76, 'right_ratio': 0.17, 'bottom_ratio': 1.0},
            {'name': 'top_left', 'left_ratio': 0.17, 'top_ratio': 0.0, 'right_ratio': 0.44, 'bottom_ratio': 0.08},
            {'name': 'top_center', 'left_ratio': 0.44, 'top_ratio': 0.0, 'right_ratio': 0.72, 'bottom_ratio': 0.08},
            {'name': 'top_right', 'left_ratio': 0.72, 'top_ratio': 0.0, 'right_ratio': 1.0, 'bottom_ratio': 0.08},
            {'name': 'main_left', 'left_ratio': 0.17, 'top_ratio': 0.08, 'right_ratio': 0.44, 'bottom_ratio': 0.76},
            {'name': 'main_center', 'left_ratio': 0.44, 'top_ratio': 0.08, 'right_ratio': 0.72, 'bottom_ratio': 0.76},
            {'name': 'main_right', 'left_ratio': 0.72, 'top_ratio': 0.08, 'right_ratio': 1.0, 'bottom_ratio': 0.76},
            {'name': 'bottom_left', 'left_ratio': 0.17, 'top_ratio': 0.76, 'right_ratio': 0.44, 'bottom_ratio': 1.0},
            {'name': 'bottom_center', 'left_ratio': 0.44, 'top_ratio': 0.76, 'right_ratio': 0.72, 'bottom_ratio': 1.0},
            {'name': 'bottom_right', 'left_ratio': 0.72, 'top_ratio': 0.76, 'right_ratio': 1.0, 'bottom_ratio': 1.0},
        ],
        'focus': True,
        'wait_after_focus_ms': 150,
    },
}


KEY_ALIASES = {
    'control': 'ctrl',
    'return': 'enter',
    'escape': 'esc',
    'command': 'win',
    'cmd': 'win',
    'windows': 'win',
    'page_up': 'pageup',
    'page-down': 'pagedown',
    'page_down': 'pagedown',
    'caps_lock': 'capslock',
}


KEY_CODES = {
    'backspace': 8,
    'tab': 9,
    'enter': 13,
    'shift': 16,
    'ctrl': 17,
    'alt': 18,
    'pause': 19,
    'capslock': 20,
    'esc': 27,
    'space': 32,
    'pageup': 33,
    'pagedown': 34,
    'end': 35,
    'home': 36,
    'left': 37,
    'up': 38,
    'right': 39,
    'down': 40,
    'printscreen': 44,
    'insert': 45,
    'delete': 46,
    '0': 48,
    '1': 49,
    '2': 50,
    '3': 51,
    '4': 52,
    '5': 53,
    '6': 54,
    '7': 55,
    '8': 56,
    '9': 57,
    'a': 65,
    'b': 66,
    'c': 67,
    'd': 68,
    'e': 69,
    'f': 70,
    'g': 71,
    'h': 72,
    'i': 73,
    'j': 74,
    'k': 75,
    'l': 76,
    'm': 77,
    'n': 78,
    'o': 79,
    'p': 80,
    'q': 81,
    'r': 82,
    's': 83,
    't': 84,
    'u': 85,
    'v': 86,
    'w': 87,
    'x': 88,
    'y': 89,
    'z': 90,
    'win': 91,
    'apps': 93,
    'num0': 96,
    'num1': 97,
    'num2': 98,
    'num3': 99,
    'num4': 100,
    'num5': 101,
    'num6': 102,
    'num7': 103,
    'num8': 104,
    'num9': 105,
    'multiply': 106,
    'add': 107,
    'separator': 108,
    'subtract': 109,
    'decimal': 110,
    'divide': 111,
    'f1': 112,
    'f2': 113,
    'f3': 114,
    'f4': 115,
    'f5': 116,
    'f6': 117,
    'f7': 118,
    'f8': 119,
    'f9': 120,
    'f10': 121,
    'f11': 122,
    'f12': 123,
    'f13': 124,
    'f14': 125,
    'f15': 126,
    'f16': 127,
    'f17': 128,
    'f18': 129,
    'f19': 130,
    'f20': 131,
    'f21': 132,
    'f22': 133,
    'f23': 134,
    'f24': 135,
    'numlock': 144,
    'scrolllock': 145,
    ';': 186,
    '=': 187,
    ',': 188,
    '-': 189,
    '.': 190,
    '/': 191,
    '`': 192,
    '[': 219,
    '\\': 220,
    ']': 221,
    "'": 222,
}


EXTENDED_KEYS = {
    'insert',
    'delete',
    'home',
    'end',
    'pageup',
    'pagedown',
    'left',
    'up',
    'right',
    'down',
    'divide',
    'numlock',
    'printscreen',
    'win',
    'apps',
}


class ExecutionStopped(RuntimeError):
    pass


class KeymouseGoController:
    def __init__(self):
        self._run_lock = threading.RLock()
        self._state_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._qt_app: Optional[QGuiApplication] = None
        self._window_guard: Optional[Dict[str, Any]] = None
        self._status: Dict[str, Any] = {
            'state': 'idle',
            'job_id': None,
            'running': False,
            'mode': None,
            'script_paths': [],
            'runtimes': 0,
            'error': None,
        }

    def sleep(self, msecs: int):
        seconds = max(0, int(msecs)) / 1000.0
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if self._stop_event.is_set():
                raise ExecutionStopped('Execution stopped')
            time.sleep(min(0.05, deadline - time.monotonic()))

    def list_scripts(self) -> List[str]:
        if not os.path.exists(SCRIPTS_DIR):
            os.makedirs(SCRIPTS_DIR, exist_ok=True)
        return sorted(
            [
                file_name
                for file_name in os.listdir(SCRIPTS_DIR)
                if file_name.endswith('.json5') or file_name.endswith('.txt')
            ]
        )

    def status(self) -> Dict[str, Any]:
        with self._state_lock:
            running = self._worker is not None and self._worker.is_alive()
            result = dict(self._status)
            result['running'] = running
            if running:
                result['state'] = 'running'
            elif result['state'] == 'running':
                result['state'] = 'idle'
            return result

    def validate_script(self, script_path: str) -> Dict[str, Any]:
        abs_path = self._normalize_script_path(script_path)
        head_object = self._parse_script(abs_path)
        return {
            'ok': True,
            'script_path': abs_path,
            'object_count': self._count_objects(head_object),
        }

    def run_script(self, script_path: str, runtimes: int = 1) -> Dict[str, Any]:
        abs_path = self._normalize_script_path(script_path)
        self._assert_not_running()
        with self._run_lock:
            job_id = self._begin_run('sync', [abs_path], runtimes)
            try:
                self._run_paths([abs_path], runtimes)
            except ExecutionStopped:
                self._finish_run('stopped')
                return self.status()
            except Exception as exc:
                self._finish_run('error', str(exc))
                raise
            self._finish_run('completed')
            result = self.status()
            result['job_id'] = job_id
            return result

    def start_script(self, script_path: str, runtimes: int = 1) -> Dict[str, Any]:
        abs_path = self._normalize_script_path(script_path)
        self._assert_not_running()
        job_id = self._begin_run('background', [abs_path], runtimes)

        def target():
            with self._run_lock:
                try:
                    self._run_paths([abs_path], runtimes)
                except ExecutionStopped:
                    self._finish_run('stopped')
                except Exception as exc:
                    logger.exception(exc)
                    self._finish_run('error', str(exc))
                else:
                    self._finish_run('completed')

        worker = threading.Thread(target=target, name='keymousego-mcp-runner', daemon=True)
        with self._state_lock:
            self._worker = worker
        worker.start()
        result = self.status()
        result['job_id'] = job_id
        return result

    def stop(self) -> Dict[str, Any]:
        self._stop_event.set()
        return self.status()

    def execute_event(self, event_type: str, action_type: str, action: Any, delay: int = 0) -> Dict[str, Any]:
        self._assert_not_running()
        self._ensure_action_allowed()
        with self._run_lock:
            self._stop_event.clear()
            event = ScriptEvent({
                'delay': delay,
                'event_type': event_type,
                'action_type': action_type,
                'action': action,
            })
            event.execute(self)
        return {
            'ok': True,
            'event_type': event_type,
            'action_type': action_type,
            'action': action,
            'delay': delay,
        }

    def mouse_move(self, x: int, y: int, delay: int = 0) -> Dict[str, Any]:
        self._ensure_action_allowed()
        return self.execute_event('EM', 'mouse move', [int(x), int(y)], delay)

    def mouse_click(
        self,
        button: str = 'left',
        x: Optional[int] = None,
        y: Optional[int] = None,
        times: int = 1,
        hold_ms: int = 50,
        delay: int = 0,
    ) -> Dict[str, Any]:
        button = button.lower()
        if button not in {'left', 'right', 'middle'}:
            raise ValueError('button only supports left, right, middle')
        self._assert_not_running()
        self._ensure_action_allowed()
        with self._run_lock:
            self._stop_event.clear()
            position = [int(x), int(y)] if x is not None and y is not None else [-1, -1]
            for _ in range(max(1, int(times))):
                ScriptEvent({
                    'delay': delay,
                    'event_type': 'EM',
                    'action_type': f'mouse {button} down',
                    'action': position,
                }).execute(self)
                ScriptEvent({
                    'delay': max(0, int(hold_ms)),
                    'event_type': 'EM',
                    'action_type': f'mouse {button} up',
                    'action': [-1, -1],
                }).execute(self)
        return {
            'ok': True,
            'button': button,
            'position': position,
            'times': max(1, int(times)),
        }

    def mouse_scroll(self, direction: str = 'up', times: int = 1, delay: int = 0) -> Dict[str, Any]:
        direction = direction.lower()
        if direction not in {'up', 'down'}:
            raise ValueError('direction only supports up or down')
        self._assert_not_running()
        self._ensure_action_allowed()
        with self._run_lock:
            self._stop_event.clear()
            for _ in range(max(1, int(times))):
                ScriptEvent({
                    'delay': delay,
                    'event_type': 'EM',
                    'action_type': f'mouse wheel {direction}',
                    'action': [-1, -1],
                }).execute(self)
        return {
            'ok': True,
            'direction': direction,
            'times': max(1, int(times)),
        }

    def key_down(self, key: str, key_code: Optional[int] = None, extended: Optional[bool] = None, delay: int = 0) -> Dict[str, Any]:
        action = list(self._resolve_key(key, key_code, extended))
        self._ensure_action_allowed()
        return self.execute_event('EK', 'key down', action, delay)

    def key_up(self, key: str, key_code: Optional[int] = None, extended: Optional[bool] = None, delay: int = 0) -> Dict[str, Any]:
        action = list(self._resolve_key(key, key_code, extended))
        self._ensure_action_allowed()
        return self.execute_event('EK', 'key up', action, delay)

    def key_tap(
        self,
        key: str,
        key_code: Optional[int] = None,
        extended: Optional[bool] = None,
        times: int = 1,
        hold_ms: int = 50,
        delay: int = 0,
    ) -> Dict[str, Any]:
        action = list(self._resolve_key(key, key_code, extended))
        self._assert_not_running()
        self._ensure_action_allowed()
        with self._run_lock:
            self._stop_event.clear()
            for _ in range(max(1, int(times))):
                ScriptEvent({
                    'delay': delay,
                    'event_type': 'EK',
                    'action_type': 'key down',
                    'action': action,
                }).execute(self)
                ScriptEvent({
                    'delay': max(0, int(hold_ms)),
                    'event_type': 'EK',
                    'action_type': 'key up',
                    'action': action,
                }).execute(self)
        return {
            'ok': True,
            'key': action[1],
            'key_code': action[0],
            'times': max(1, int(times)),
        }

    def hotkey(self, keys: List[str], hold_ms: int = 50, delay: int = 0) -> Dict[str, Any]:
        normalized_keys = [key for key in keys if key and key.strip()]
        if len(normalized_keys) == 0:
            raise ValueError('keys cannot be empty')
        self._assert_not_running()
        self._ensure_action_allowed()
        with self._run_lock:
            self._stop_event.clear()
            for index, key in enumerate(normalized_keys):
                current_delay = delay if index == 0 else 0
                self.key_down(key, delay=current_delay)
            self.sleep(max(0, int(hold_ms)))
            for key in reversed(normalized_keys):
                self.key_up(key)
        return {
            'ok': True,
            'keys': normalized_keys,
        }

    def wait_ms(self, ms: int) -> Dict[str, Any]:
        self._assert_not_running()
        self._stop_event.clear()
        self.sleep(ms)
        return {
            'ok': True,
            'waited_ms': max(0, int(ms)),
        }

    def wait_until_idle(self, timeout_ms: int = 0, poll_ms: int = 100) -> Dict[str, Any]:
        deadline = None if timeout_ms <= 0 else time.monotonic() + (timeout_ms / 1000.0)
        interval = max(10, int(poll_ms))
        while True:
            status = self.status()
            if not status['running']:
                return {
                    'ok': True,
                    'idle': True,
                    'status': status,
                }
            if deadline is not None and time.monotonic() >= deadline:
                return {
                    'ok': False,
                    'idle': False,
                    'status': status,
                }
            time.sleep(interval / 1000.0)

    def text_input(self, text: str, delay: int = 0) -> Dict[str, Any]:
        self._ensure_action_allowed()
        return self.execute_event('EX', 'input', text, delay)

    def type_and_enter(self, text: str, delay: int = 0, hold_ms: int = 50) -> Dict[str, Any]:
        self._assert_not_running()
        self._ensure_action_allowed()
        with self._run_lock:
            self._stop_event.clear()
            self.text_input(text, delay)
            self.key_tap('enter', hold_ms=hold_ms)
        return {
            'ok': True,
            'text': text,
        }

    def double_click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = 'left',
        hold_ms: int = 50,
        delay: int = 0,
    ) -> Dict[str, Any]:
        return self.mouse_click(button=button, x=x, y=y, times=2, hold_ms=hold_ms, delay=delay)

    def drag(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        button: str = 'left',
        hold_ms: int = 50,
        move_delay: int = 0,
        release_delay: int = 0,
    ) -> Dict[str, Any]:
        button = button.lower()
        if button not in {'left', 'right', 'middle'}:
            raise ValueError('button only supports left, right, middle')
        self._assert_not_running()
        self._ensure_action_allowed()
        with self._run_lock:
            self._stop_event.clear()
            self.mouse_move(from_x, from_y)
            self.execute_event('EM', f'mouse {button} down', [-1, -1], 0)
            self.sleep(max(0, int(hold_ms)))
            self.mouse_move(to_x, to_y, move_delay)
            self.execute_event('EM', f'mouse {button} up', [-1, -1], release_delay)
        return {
            'ok': True,
            'button': button,
            'from': [int(from_x), int(from_y)],
            'to': [int(to_x), int(to_y)],
        }

    def get_cursor_pos(self) -> Dict[str, Any]:
        if win32api is None:
            raise RuntimeError('get_cursor_pos is only available on Windows')
        x, y = win32api.GetCursorPos()
        return {'x': x, 'y': y}

    def get_foreground_window(self) -> Dict[str, Any]:
        self._ensure_window_api()
        hwnd = win32gui.GetForegroundWindow()
        return self._window_info(hwnd)

    def list_windows(
        self,
        title_filter: str = '',
        visible_only: bool = True,
        limit: int = 50,
    ) -> Dict[str, Any]:
        self._ensure_window_api()
        windows = self._enumerate_windows(
            title_filter=title_filter,
            exact_title=None,
            class_name=None,
            visible_only=visible_only,
            limit=limit,
        )
        return {
            'windows': windows,
        }

    def find_window(
        self,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        limit: int = 20,
    ) -> Dict[str, Any]:
        self._ensure_window_api()
        windows = self._enumerate_windows(
            title_filter=title_substring or '',
            exact_title=exact_title,
            class_name=class_name,
            visible_only=visible_only,
            limit=limit,
        )
        return {
            'windows': windows,
            'matched': len(windows) > 0,
        }

    def focus_window(self, hwnd: int, restore: bool = True) -> Dict[str, Any]:
        self._ensure_window_api()
        handle = int(hwnd)
        if not win32gui.IsWindow(handle):
            raise ValueError(f'Invalid hwnd: {hwnd}')
        if restore and win32gui.IsIconic(handle):
            win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(handle)
        return {
            'ok': True,
            'window': self._window_info(handle),
        }

    def move_window(
        self,
        x: int,
        y: int,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        restore: bool = True,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Dict[str, Any]:
        self._ensure_window_api()
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        handle = int(window['hwnd'])
        if restore and win32gui.IsIconic(handle):
            win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        target_width = window['rect']['width'] if width is None else max(1, int(width))
        target_height = window['rect']['height'] if height is None else max(1, int(height))
        win32gui.MoveWindow(handle, int(x), int(y), target_width, target_height, True)
        return {
            'ok': True,
            'before': window,
            'after': self._window_info(handle),
        }

    def drag_window(
        self,
        to_x: int,
        to_y: int,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        restore: bool = True,
    ) -> Dict[str, Any]:
        return self.move_window(
            x=to_x,
            y=to_y,
            hwnd=hwnd,
            title_substring=title_substring,
            exact_title=exact_title,
            class_name=class_name,
            visible_only=visible_only,
            restore=restore,
        )

    def focus_window_by_title(
        self,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        restore: bool = True,
    ) -> Dict[str, Any]:
        self._ensure_window_api()
        windows = self._enumerate_windows(
            title_filter=title_substring or '',
            exact_title=exact_title,
            class_name=class_name,
            visible_only=visible_only,
            limit=1,
        )
        if len(windows) == 0:
            raise ValueError('No window matched the given condition')
        return self.focus_window(windows[0]['hwnd'], restore)

    def set_window_guard(
        self,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        focus: bool = False,
        restore: bool = True,
    ) -> Dict[str, Any]:
        self._ensure_window_api()
        if hwnd is not None:
            window = self._window_info(hwnd)
        else:
            windows = self._enumerate_windows(
                title_filter=title_substring or '',
                exact_title=exact_title,
                class_name=class_name,
                visible_only=visible_only,
                limit=1,
            )
            if len(windows) == 0:
                raise ValueError('No window matched the given condition')
            window = windows[0]
        if focus:
            focus_result = self.focus_window(window['hwnd'], restore)
            window = focus_result['window']
        with self._state_lock:
            self._window_guard = {
                'hwnd': window['hwnd'],
                'title': window['title'],
                'class_name': window['class_name'],
            }
        return {
            'ok': True,
            'guard': self.get_window_guard()['guard'],
        }

    def clear_window_guard(self) -> Dict[str, Any]:
        with self._state_lock:
            self._window_guard = None
        return {
            'ok': True,
            'guard': None,
        }

    def get_window_guard(self) -> Dict[str, Any]:
        with self._state_lock:
            guard = None if self._window_guard is None else dict(self._window_guard)
        return {
            'guard': guard,
            'enabled': guard is not None,
        }

    def list_screenshot_profiles(self) -> Dict[str, Any]:
        overrides = self._load_screenshot_profile_overrides()
        return {
            'profiles': {
                profile_name: self._merge_screenshot_profile(profile_name, overrides)
                for profile_name in SCREENSHOT_APP_PROFILES.keys()
            },
        }

    def get_bridge_status(self, base_dir: Optional[str] = None) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        return {
            'base_dir': bridge['base_dir'],
            'tasks_dir': bridge['tasks_dir'],
            'replies_dir': bridge['replies_dir'],
            'archive_tasks_dir': bridge['archive_tasks_dir'],
            'archive_replies_dir': bridge['archive_replies_dir'],
            'counts': {
                'tasks': self._count_json_files(bridge['tasks_dir']),
                'replies': self._count_json_files(bridge['replies_dir']),
                'archive_tasks': self._count_json_files(bridge['archive_tasks_dir']),
                'archive_replies': self._count_json_files(bridge['archive_replies_dir']),
            },
        }

    def trae_status(
        self,
        base_dir: Optional[str] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        sample_limit: int = 3,
    ) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        profile = self._get_chat_profile('trae')
        resolved_title_substring = profile['title_substring'] if title_substring is None else title_substring
        resolved_exact_title = profile['exact_title'] if exact_title is None else exact_title
        resolved_class_name = profile['class_name'] if class_name is None else class_name
        window_search = self.find_window(
            title_substring=resolved_title_substring,
            exact_title=resolved_exact_title,
            class_name=resolved_class_name,
            visible_only=visible_only,
            limit=max(5, int(sample_limit)),
        )
        preferred_window = self._select_preferred_trae_window(window_search.get('windows', []))
        task_entries = sorted(os.listdir(bridge['tasks_dir']))
        reply_entries = sorted(os.listdir(bridge['replies_dir']))
        temp_task_files = [name for name in task_entries if name.endswith('.tmp')]
        processing_task_files = [name for name in task_entries if name.endswith('.processing.json')]
        pending_task_files = [name for name in task_entries if name.endswith('.json') and not name.endswith('.processing.json')]
        try:
            poller = self._detect_trae_task_poller()
        except Exception as exc:
            poller = {
                'running': False,
                'error': str(exc),
                'processes': [],
            }
        summary_status = 'ready'
        if not window_search.get('matched'):
            summary_status = 'degraded'
        if temp_task_files:
            summary_status = 'degraded'
        if not poller.get('running', False):
            summary_status = 'degraded'
        return {
            'ok': True,
            'status': summary_status,
            'window_ready': preferred_window is not None,
            'poller_running': bool(poller.get('running', False)),
            'profile_name': 'trae',
            'profile': profile,
            'preferred_window': preferred_window,
            'window_match': window_search,
            'bridge': {
                'base_dir': bridge['base_dir'],
                'tasks_dir': bridge['tasks_dir'],
                'replies_dir': bridge['replies_dir'],
                'counts': {
                    'pending_tasks': len(pending_task_files),
                    'processing_tasks': len(processing_task_files),
                    'reply_files': len([name for name in reply_entries if name.endswith('.json')]),
                    'temp_task_files': len(temp_task_files),
                },
                'samples': {
                    'pending_tasks': pending_task_files[:max(0, int(sample_limit))],
                    'processing_tasks': processing_task_files[:max(0, int(sample_limit))],
                    'reply_files': reply_entries[:max(0, int(sample_limit))],
                    'temp_task_files': temp_task_files[:max(0, int(sample_limit))],
                },
            },
            'poller': poller,
            'capabilities': {
                'delegate_modes': ['bridge_task', 'window_message'],
                'reply_extraction': 'ocr_visible_chat_region',
            },
        }

    def trae_delegate(
        self,
        content: str,
        task_id: Optional[str] = None,
        expected_reply: Optional[str] = None,
        mode: str = 'bridge_task',
        context: Optional[Dict[str, Any]] = None,
        expectation: Optional[Dict[str, Any]] = None,
        from_agent: str = 'LobsterAI',
        to_agent: str = 'Trae',
        base_dir: Optional[str] = None,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        submit_mode: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        resolved_mode = (mode or 'bridge_task').strip().lower()
        expectation_payload = dict(expectation or {})
        if expected_reply:
            expectation_payload['exact_reply'] = str(expected_reply)
        resolved_task_id = str(task_id or uuid.uuid4().hex)
        if resolved_mode in {'bridge', 'bridge_task', 'queue'}:
            task_result = self.send_bridge_task(
                task_type='chat',
                content=content,
                task_id=resolved_task_id,
                context=context,
                expectation=expectation_payload,
                from_agent=from_agent,
                to_agent=to_agent,
                base_dir=base_dir,
            )
            prompt_preview = self.build_trae_bridge_prompt(
                resolved_task_id,
                content,
                expected_reply=expectation_payload.get('exact_reply'),
            )
            return {
                'ok': True,
                'mode': 'bridge_task',
                'task_id': resolved_task_id,
                'task_result': task_result,
                'prompt_preview': prompt_preview,
            }
        if resolved_mode in {'window', 'window_message', 'direct'}:
            send_result = self.trae_send_bridge_message(
                task_id=resolved_task_id,
                content=content,
                expected_reply=expectation_payload.get('exact_reply'),
                hwnd=hwnd,
                title_substring=title_substring,
                exact_title=exact_title,
                input_offset_x=input_offset_x,
                input_offset_y=input_offset_y,
                submit_mode=submit_mode,
                visible_only=visible_only,
                focus=focus,
                restore=restore,
                hold_ms=hold_ms,
                input_ready_delay_ms=input_ready_delay_ms,
                click_delay_ms=click_delay_ms,
                enter_delay_ms=enter_delay_ms,
                enter_times=enter_times,
                click_before_enter=click_before_enter,
                click_before_enter_delay_ms=click_before_enter_delay_ms,
            )
            return {
                'ok': True,
                'mode': 'window_message',
                'task_id': resolved_task_id,
                'send_result': send_result,
            }
        raise ValueError('mode only supports bridge_task or window_message')

    def send_bridge_task(
        self,
        task_type: str,
        content: str,
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        expectation: Optional[Dict[str, Any]] = None,
        from_agent: str = 'LobsterAI',
        to_agent: str = 'Trae',
        base_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        resolved_task_id = task_id or uuid.uuid4().hex
        task = {
            'header': {
                'protocol_version': '1.0',
                'from': from_agent,
                'to': to_agent,
                'task_id': resolved_task_id,
                'type': task_type,
                'timestamp': time.time(),
                'status': 'pending',
            },
            'body': {
                'content': content,
                'context': context or {},
                'expectation': expectation or {},
            },
        }
        task['header']['checksum'] = self._compute_payload_checksum(task)
        file_path = os.path.join(bridge['tasks_dir'], f'{resolved_task_id}.json')
        self._write_json_atomic(file_path, task)
        return {
            'ok': True,
            'task_id': resolved_task_id,
            'task_file': file_path,
            'task': task,
        }

    def build_trae_bridge_prompt(
        self,
        task_id: str,
        content: str,
        expected_reply: Optional[str] = None,
    ) -> Dict[str, Any]:
        resolved_task_id = str(task_id or uuid.uuid4().hex)
        marker_id = hashlib.sha256(resolved_task_id.encode('utf-8')).hexdigest()[:8].upper()
        begin_marker = f'BRIDGEBEGIN{marker_id}'
        end_marker = f'BRIDGEEND{marker_id}'
        lines = [f'[{resolved_task_id}]', str(content), '仅输出：', begin_marker]
        lines.append(str(expected_reply).strip() if expected_reply else '简洁回复')
        lines.append(end_marker)
        return {
            'ok': True,
            'task_id': resolved_task_id,
            'begin_marker': begin_marker,
            'end_marker': end_marker,
            'prompt': '\n'.join(lines),
        }

    def trae_send_bridge_message(
        self,
        task_id: str,
        content: str,
        expected_reply: Optional[str] = None,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        submit_mode: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload = self.build_trae_bridge_prompt(task_id, content, expected_reply)
        send_result = self.trae_send_message(
            payload['prompt'],
            hwnd=hwnd,
            title_substring=title_substring,
            exact_title=exact_title,
            input_offset_x=input_offset_x,
            input_offset_y=input_offset_y,
            submit_mode=submit_mode,
            visible_only=visible_only,
            focus=focus,
            restore=restore,
            hold_ms=hold_ms,
            input_ready_delay_ms=input_ready_delay_ms,
            click_delay_ms=click_delay_ms,
            enter_delay_ms=enter_delay_ms,
            enter_times=enter_times,
            click_before_enter=click_before_enter,
            click_before_enter_delay_ms=click_before_enter_delay_ms,
        )
        return {
            'ok': True,
            'task_id': payload['task_id'],
            'begin_marker': payload['begin_marker'],
            'end_marker': payload['end_marker'],
            'prompt': payload['prompt'],
            'send_result': send_result,
        }

    def list_bridge_tasks(self, status: Optional[str] = None, base_dir: Optional[str] = None) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        items = self._read_bridge_directory(bridge['tasks_dir'], status)
        return {
            'tasks': items,
            'count': len(items),
            'base_dir': bridge['base_dir'],
        }

    def list_bridge_replies(self, status: Optional[str] = None, base_dir: Optional[str] = None) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        items = self._read_bridge_directory(bridge['replies_dir'], status)
        return {
            'replies': items,
            'count': len(items),
            'base_dir': bridge['base_dir'],
        }

    def read_bridge_reply(
        self,
        task_id: str,
        archive_on_read: bool = False,
        base_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        file_path = os.path.join(bridge['replies_dir'], f'{task_id}.json')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Reply not found: {task_id}')
        payload = self._read_json_file(file_path)
        if archive_on_read:
            archive_path = os.path.join(bridge['archive_replies_dir'], os.path.basename(file_path))
            self._move_to_archive(file_path, archive_path)
        return {
            'ok': True,
            'task_id': task_id,
            'reply_file': file_path,
            'reply': payload,
            'archived': bool(archive_on_read),
        }

    def wait_bridge_reply(
        self,
        task_id: str,
        timeout_s: int = 60,
        initial_poll_ms: int = 200,
        max_poll_ms: int = 2000,
        archive_on_read: bool = False,
        base_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        reply_file = os.path.join(bridge['replies_dir'], f'{task_id}.json')
        deadline = time.time() + max(1, int(timeout_s))
        poll_ms = max(50, int(initial_poll_ms))
        poll_ms_limit = max(poll_ms, int(max_poll_ms))
        while time.time() < deadline:
            if os.path.exists(reply_file):
                return self.read_bridge_reply(task_id, archive_on_read, base_dir)
            time.sleep(poll_ms / 1000.0)
            poll_ms = min(poll_ms_limit, max(poll_ms + 1, int(poll_ms * 2.5)))
        return {
            'ok': False,
            'task_id': task_id,
            'error': 'timeout',
            'reply_file': reply_file,
        }

    def write_bridge_reply(
        self,
        task_id: str,
        result: Any,
        status: str = 'success',
        from_agent: str = 'Trae',
        to_agent: str = 'LobsterAI',
        error: Optional[str] = None,
        base_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        reply = {
            'header': {
                'protocol_version': '1.0',
                'from': from_agent,
                'to': to_agent,
                'task_id': task_id,
                'timestamp': time.time(),
                'status': status,
            },
            'body': {
                'result': result,
                'error': error,
            },
        }
        reply['header']['checksum'] = self._compute_payload_checksum(reply)
        file_path = os.path.join(bridge['replies_dir'], f'{task_id}.json')
        self._write_json_atomic(file_path, reply)
        return {
            'ok': True,
            'task_id': task_id,
            'reply_file': file_path,
            'reply': reply,
        }

    def claim_bridge_task(self, task_id: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        pending_file = os.path.join(bridge['tasks_dir'], f'{task_id}.json')
        processing_file = os.path.join(bridge['tasks_dir'], f'{task_id}.processing.json')
        if not os.path.exists(pending_file):
            raise FileNotFoundError(f'Task not found: {task_id}')
        os.replace(pending_file, processing_file)
        payload = self._read_json_file(processing_file)
        payload['header']['status'] = 'processing'
        payload['header']['claimed_at'] = time.time()
        self._write_json_atomic(processing_file, payload)
        return {
            'ok': True,
            'task_id': task_id,
            'task_file': processing_file,
            'task': payload,
        }

    def archive_bridge_task(self, task_id: str, base_dir: Optional[str] = None) -> Dict[str, Any]:
        bridge = self._ensure_bridge_dirs(base_dir)
        task_file = os.path.join(bridge['tasks_dir'], f'{task_id}.processing.json')
        if not os.path.exists(task_file):
            task_file = os.path.join(bridge['tasks_dir'], f'{task_id}.json')
        if not os.path.exists(task_file):
            raise FileNotFoundError(f'Task not found: {task_id}')
        archive_file = os.path.join(bridge['archive_tasks_dir'], os.path.basename(task_file).replace('.processing', '.done'))
        self._move_to_archive(task_file, archive_file)
        return {
            'ok': True,
            'task_id': task_id,
            'archive_file': archive_file,
        }

    def prepare_layout_analysis(
        self,
        profile_name: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        wait_after_focus_ms: Optional[int] = None,
        prefix: Optional[str] = None,
        include_inline_image: bool = True,
        preview_max_width: int = 1280,
    ) -> Dict[str, Any]:
        profile = self._get_screenshot_profile(profile_name)
        resolved_focus = profile['focus'] if focus is None else focus
        resolved_wait_after_focus_ms = profile['wait_after_focus_ms'] if wait_after_focus_ms is None else wait_after_focus_ms
        resolved_prefix = f'{profile_name}_analysis' if prefix is None else prefix
        window = self._resolve_window_target(
            hwnd,
            title_substring if title_substring is not None else profile['title_substring'],
            exact_title if exact_title is not None else profile['exact_title'],
            class_name if class_name is not None else profile['class_name'],
            visible_only,
        )
        if resolved_focus:
            window = self.focus_window(window['hwnd'], restore)['window']
            if resolved_wait_after_focus_ms > 0:
                self.wait_ms(resolved_wait_after_focus_ms)
        capture = self._capture_window_client(window)
        image_path = self._save_pixmap(capture['pixmap'], resolved_prefix)
        inline_image = None
        if include_inline_image:
            inline_image = self._pixmap_to_data_url(capture['pixmap'], preview_max_width)
        guidance = [
            '请根据截图识别软件自然分区，按软件功能区域划分而不是均分网格。',
            '请输出从上到下、从左到右可读的分区顺序。',
            '每个分区请给出 name、left_ratio、top_ratio、right_ratio、bottom_ratio，比例范围 0 到 1。',
            'left_ratio < right_ratio，top_ratio < bottom_ratio。',
            '优先识别：左侧边栏、顶部标签栏、主编辑区、底部终端/输入区、右侧面板。',
        ]
        return {
            'ok': True,
            'profile': profile_name,
            'window': window,
            'image_path': image_path,
            'image_data_url': inline_image,
            'client_rect': capture['client_rect'],
            'suggested_prompt': '\n'.join(guidance),
            'current_partitions': profile.get('partitions'),
        }

    def save_screenshot_profile_partitions(
        self,
        profile_name: str,
        partitions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if profile_name not in SCREENSHOT_APP_PROFILES:
            raise ValueError(f'Unsupported screenshot profile: {profile_name}')
        normalized = self._normalize_partition_specs(partitions)
        overrides = self._load_screenshot_profile_overrides()
        override = dict(overrides.get(profile_name, {}))
        override['partitions'] = normalized
        overrides[profile_name] = override
        self._save_screenshot_profile_overrides(overrides)
        return self.get_screenshot_profile(profile_name)

    def get_screenshot_profile(self, profile_name: str) -> Dict[str, Any]:
        return {
            'profile_name': profile_name,
            'profile': self._get_screenshot_profile(profile_name),
        }

    def reset_screenshot_profile(self, profile_name: str) -> Dict[str, Any]:
        if profile_name not in SCREENSHOT_APP_PROFILES:
            raise ValueError(f'Unsupported screenshot profile: {profile_name}')
        overrides = self._load_screenshot_profile_overrides()
        if profile_name in overrides:
            overrides.pop(profile_name)
            self._save_screenshot_profile_overrides(overrides)
        return self.get_screenshot_profile(profile_name)

    def capture_profile_window(
        self,
        profile_name: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        wait_after_focus_ms: Optional[int] = None,
        prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        profile = self._get_screenshot_profile(profile_name)
        resolved_focus = profile['focus'] if focus is None else focus
        resolved_wait_after_focus_ms = profile['wait_after_focus_ms'] if wait_after_focus_ms is None else wait_after_focus_ms
        resolved_prefix = profile_name if prefix is None else prefix
        return self.capture_window(
            hwnd=hwnd,
            title_substring=title_substring if title_substring is not None else profile['title_substring'],
            exact_title=exact_title if exact_title is not None else profile['exact_title'],
            class_name=class_name if class_name is not None else profile['class_name'],
            visible_only=visible_only,
            focus=resolved_focus,
            restore=restore,
            wait_after_focus_ms=resolved_wait_after_focus_ms,
            prefix=resolved_prefix,
        )

    def capture_profile_region(
        self,
        profile_name: str,
        offset_x: int,
        offset_y: int,
        width: int,
        height: int,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        wait_after_focus_ms: Optional[int] = None,
        prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        profile = self._get_screenshot_profile(profile_name)
        resolved_focus = profile['focus'] if focus is None else focus
        resolved_wait_after_focus_ms = profile['wait_after_focus_ms'] if wait_after_focus_ms is None else wait_after_focus_ms
        resolved_prefix = f'{profile_name}_region' if prefix is None else prefix
        return self.capture_window_region(
            offset_x=offset_x,
            offset_y=offset_y,
            width=width,
            height=height,
            hwnd=hwnd,
            title_substring=title_substring if title_substring is not None else profile['title_substring'],
            exact_title=exact_title if exact_title is not None else profile['exact_title'],
            class_name=class_name if class_name is not None else profile['class_name'],
            visible_only=visible_only,
            focus=resolved_focus,
            restore=restore,
            wait_after_focus_ms=resolved_wait_after_focus_ms,
            prefix=resolved_prefix,
        )

    def capture_profile_partition_map(
        self,
        profile_name: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        wait_after_focus_ms: Optional[int] = None,
        prefix: Optional[str] = None,
    ) -> Dict[str, Any]:
        profile = self._get_screenshot_profile(profile_name)
        resolved_focus = profile['focus'] if focus is None else focus
        resolved_wait_after_focus_ms = profile['wait_after_focus_ms'] if wait_after_focus_ms is None else wait_after_focus_ms
        resolved_rows = profile['rows'] if rows is None else rows
        resolved_cols = profile['cols'] if cols is None else cols
        resolved_prefix = f'{profile_name}_partition' if prefix is None else prefix
        result = self.capture_window_partition_map(
            hwnd=hwnd,
            title_substring=title_substring if title_substring is not None else profile['title_substring'],
            exact_title=exact_title if exact_title is not None else profile['exact_title'],
            class_name=class_name if class_name is not None else profile['class_name'],
            rows=resolved_rows,
            cols=resolved_cols,
            visible_only=visible_only,
            focus=resolved_focus,
            restore=restore,
            wait_after_focus_ms=resolved_wait_after_focus_ms,
            prefix=resolved_prefix,
            partitions=profile.get('partitions'),
        )
        result['profile'] = profile_name
        return result

    def capture_window(
        self,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        focus: bool = False,
        restore: bool = True,
        wait_after_focus_ms: int = 150,
        prefix: str = 'window',
    ) -> Dict[str, Any]:
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        if focus:
            window = self.focus_window(window['hwnd'], restore)['window']
            if wait_after_focus_ms > 0:
                self.wait_ms(wait_after_focus_ms)
        capture = self._capture_window_client(window)
        image_path = self._save_pixmap(capture['pixmap'], prefix)
        return {
            'ok': True,
            'image_path': image_path,
            'window': window,
            'capture_rect': capture['capture_rect'],
            'client_rect': capture['client_rect'],
        }

    def capture_window_region(
        self,
        offset_x: int,
        offset_y: int,
        width: int,
        height: int,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        focus: bool = False,
        restore: bool = True,
        wait_after_focus_ms: int = 150,
        prefix: str = 'window_region',
    ) -> Dict[str, Any]:
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        if focus:
            window = self.focus_window(window['hwnd'], restore)['window']
            if wait_after_focus_ms > 0:
                self.wait_ms(wait_after_focus_ms)
        capture = self._capture_window_client(window)
        region = self._normalize_capture_region(capture['client_rect'], offset_x, offset_y, width, height)
        pixmap = capture['pixmap'].copy(region['offset_x'], region['offset_y'], region['width'], region['height'])
        image_path = self._save_pixmap(pixmap, prefix)
        return {
            'ok': True,
            'image_path': image_path,
            'window': window,
            'capture_rect': region,
            'client_rect': capture['client_rect'],
        }

    def capture_window_partition_map(
        self,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        rows: int = 2,
        cols: int = 2,
        visible_only: bool = True,
        focus: bool = False,
        restore: bool = True,
        wait_after_focus_ms: int = 150,
        prefix: str = 'window_partition',
        partitions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        if focus:
            window = self.focus_window(window['hwnd'], restore)['window']
            if wait_after_focus_ms > 0:
                self.wait_ms(wait_after_focus_ms)
        capture = self._capture_window_client(window)
        pixmap = capture['pixmap']
        partition_rows = max(1, int(rows))
        partition_cols = max(1, int(cols))
        if partitions:
            partition_items = self._build_natural_partitions(capture['client_rect'], partitions)
            partition_rows = None
            partition_cols = None
        else:
            partition_items = self._build_grid_partitions(capture['client_rect'], partition_rows, partition_cols)
        annotated = self._annotate_partitions(pixmap, partition_items)
        image_path = self._save_pixmap(annotated, prefix)
        return {
            'ok': True,
            'image_path': image_path,
            'window': window,
            'client_rect': capture['client_rect'],
            'rows': partition_rows,
            'cols': partition_cols,
            'partitions': partition_items,
        }

    def click_window_center(
        self,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        button: str = 'left',
        double: bool = False,
        visible_only: bool = True,
        focus: bool = False,
        restore: bool = True,
        hold_ms: int = 50,
        delay: int = 0,
    ) -> Dict[str, Any]:
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        if focus:
            window = self.focus_window(window['hwnd'], restore)['window']
        rect = window['rect']
        x = rect['left'] + rect['width'] // 2
        y = rect['top'] + rect['height'] // 2
        if double:
            self.double_click(x=x, y=y, button=button, hold_ms=hold_ms, delay=delay)
        else:
            self.mouse_click(button=button, x=x, y=y, hold_ms=hold_ms, delay=delay)
        return {
            'ok': True,
            'window': window,
            'point': {'x': x, 'y': y},
            'double': bool(double),
            'button': button,
        }

    def click_in_window(
        self,
        offset_x: int,
        offset_y: int,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        button: str = 'left',
        double: bool = False,
        visible_only: bool = True,
        focus: bool = False,
        restore: bool = True,
        hold_ms: int = 50,
        delay: int = 0,
    ) -> Dict[str, Any]:
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        if focus:
            window = self.focus_window(window['hwnd'], restore)['window']
        x, y = self._window_offset_to_screen(window, offset_x, offset_y)
        if double:
            self.double_click(x=x, y=y, button=button, hold_ms=hold_ms, delay=delay)
        else:
            self.mouse_click(button=button, x=x, y=y, hold_ms=hold_ms, delay=delay)
        return {
            'ok': True,
            'window': window,
            'point': {'x': x, 'y': y},
            'offset': {'x': int(offset_x), 'y': int(offset_y)},
            'double': bool(double),
            'button': button,
        }

    def drag_in_window(
        self,
        from_offset_x: int,
        from_offset_y: int,
        to_offset_x: int,
        to_offset_y: int,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        button: str = 'left',
        visible_only: bool = True,
        focus: bool = False,
        restore: bool = True,
        hold_ms: int = 50,
        move_delay: int = 0,
        release_delay: int = 0,
    ) -> Dict[str, Any]:
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        if focus:
            window = self.focus_window(window['hwnd'], restore)['window']
        from_x, from_y = self._window_offset_to_screen(window, from_offset_x, from_offset_y)
        to_x, to_y = self._window_offset_to_screen(window, to_offset_x, to_offset_y)
        self.drag(from_x, from_y, to_x, to_y, button=button, hold_ms=hold_ms, move_delay=move_delay, release_delay=release_delay)
        return {
            'ok': True,
            'window': window,
            'from': {'x': from_x, 'y': from_y},
            'to': {'x': to_x, 'y': to_y},
            'from_offset': {'x': int(from_offset_x), 'y': int(from_offset_y)},
            'to_offset': {'x': int(to_offset_x), 'y': int(to_offset_y)},
            'button': button,
        }

    def send_message_to_window(
        self,
        text: str,
        input_offset_x: int,
        input_offset_y: int,
        send_button_offset_x: Optional[int] = None,
        send_button_offset_y: Optional[int] = None,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        submit_mode: str = 'click',
        visible_only: bool = True,
        focus: bool = True,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: int = 0,
        enter_times: int = 1,
        click_before_enter: bool = False,
        click_before_enter_delay_ms: int = 120,
    ) -> Dict[str, Any]:
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        if focus:
            window = self.focus_window(window['hwnd'], restore)['window']
        submit_mode = submit_mode.lower()
        if submit_mode not in {'click', 'enter'}:
            raise ValueError('submit_mode only supports click or enter')
        if submit_mode == 'click' and (send_button_offset_x is None or send_button_offset_y is None):
            raise ValueError('send_button_offset_x and send_button_offset_y are required when submit_mode=click')
        previous_guard = None
        with self._state_lock:
            previous_guard = None if self._window_guard is None else dict(self._window_guard)
            self._window_guard = {
                'hwnd': window['hwnd'],
                'title': window['title'],
                'class_name': window['class_name'],
            }
        try:
            self.click_in_window(
                offset_x=int(input_offset_x),
                offset_y=int(input_offset_y),
                hwnd=window['hwnd'],
                button='left',
                double=False,
                visible_only=visible_only,
                focus=False,
                restore=restore,
                hold_ms=hold_ms,
                delay=click_delay_ms,
            )
            if input_ready_delay_ms > 0:
                self.wait_ms(input_ready_delay_ms)
            self.text_input(text)
            if submit_mode == 'enter':
                resolved_enter_times = max(1, int(enter_times))
                resolved_enter_delay_ms = max(0, int(enter_delay_ms))
                resolved_click_before_enter = bool(click_before_enter)
                resolved_click_before_enter_delay_ms = max(0, int(click_before_enter_delay_ms))
                for index in range(resolved_enter_times):
                    if index > 0 and resolved_enter_delay_ms > 0:
                        self.wait_ms(resolved_enter_delay_ms)
                    if resolved_click_before_enter:
                        self.click_in_window(
                            offset_x=int(input_offset_x),
                            offset_y=int(input_offset_y),
                            hwnd=window['hwnd'],
                            button='left',
                            double=False,
                            visible_only=visible_only,
                            focus=False,
                            restore=restore,
                            hold_ms=hold_ms,
                            delay=click_delay_ms,
                        )
                        if resolved_click_before_enter_delay_ms > 0:
                            self.wait_ms(resolved_click_before_enter_delay_ms)
                    self.key_tap('enter', hold_ms=hold_ms)
            else:
                self.click_in_window(
                    offset_x=int(send_button_offset_x),
                    offset_y=int(send_button_offset_y),
                    hwnd=window['hwnd'],
                    button='left',
                    double=False,
                    visible_only=visible_only,
                    focus=False,
                    restore=restore,
                    hold_ms=hold_ms,
                    delay=click_delay_ms,
                )
        finally:
            with self._state_lock:
                self._window_guard = previous_guard
        return {
            'ok': True,
            'window': window,
            'submit_mode': submit_mode,
            'input_offset': {'x': int(input_offset_x), 'y': int(input_offset_y)},
            'send_offset': None if submit_mode == 'enter' else {
                'x': int(send_button_offset_x),
                'y': int(send_button_offset_y),
            },
            'enter_delay_ms': max(0, int(enter_delay_ms)),
            'enter_times': max(1, int(enter_times)),
            'click_before_enter': bool(click_before_enter),
            'click_before_enter_delay_ms': max(0, int(click_before_enter_delay_ms)),
            'text_length': len(text),
        }

    def list_chat_profiles(self) -> Dict[str, Any]:
        overrides = self._load_chat_profile_overrides()
        return {
            'profiles': {
                profile_name: self._merge_chat_profile(profile_name, overrides)
                for profile_name in CHAT_APP_PROFILES.keys()
            },
        }

    def get_chat_profile(self, profile_name: str) -> Dict[str, Any]:
        return {
            'profile_name': profile_name,
            'profile': self._get_chat_profile(profile_name),
        }

    def save_chat_profile(
        self,
        profile_name: str,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        submit_mode: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        send_button_offset_x: Optional[int] = None,
        send_button_offset_y: Optional[int] = None,
        input_ratio_x: Optional[float] = None,
        input_ratio_y: Optional[float] = None,
        send_ratio_x: Optional[float] = None,
        send_ratio_y: Optional[float] = None,
        focus: Optional[bool] = None,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        self._get_chat_profile(profile_name)
        overrides = self._load_chat_profile_overrides()
        profile_override = dict(overrides.get(profile_name, {}))
        for key, value in {
            'title_substring': title_substring,
            'exact_title': exact_title,
            'class_name': class_name,
            'submit_mode': submit_mode,
            'focus': focus,
            'enter_delay_ms': enter_delay_ms,
            'enter_times': enter_times,
            'click_before_enter': click_before_enter,
            'click_before_enter_delay_ms': click_before_enter_delay_ms,
        }.items():
            if value is not None:
                profile_override[key] = value
        if input_offset_x is not None and input_offset_y is not None:
            profile_override['input_offset'] = {'x': int(input_offset_x), 'y': int(input_offset_y)}
            profile_override.pop('input_ratio', None)
        if send_button_offset_x is not None and send_button_offset_y is not None:
            profile_override['send_offset'] = {'x': int(send_button_offset_x), 'y': int(send_button_offset_y)}
            profile_override.pop('send_ratio', None)
        if input_ratio_x is not None and input_ratio_y is not None:
            profile_override['input_ratio'] = {'x': float(input_ratio_x), 'y': float(input_ratio_y)}
            profile_override.pop('input_offset', None)
        if send_ratio_x is not None and send_ratio_y is not None:
            profile_override['send_ratio'] = {'x': float(send_ratio_x), 'y': float(send_ratio_y)}
            profile_override.pop('send_offset', None)
        overrides[profile_name] = profile_override
        self._save_chat_profile_overrides(overrides)
        return self.get_chat_profile(profile_name)

    def reset_chat_profile(self, profile_name: str) -> Dict[str, Any]:
        self._get_chat_profile(profile_name)
        overrides = self._load_chat_profile_overrides()
        if profile_name in overrides:
            overrides.pop(profile_name)
            self._save_chat_profile_overrides(overrides)
        return self.get_chat_profile(profile_name)

    def inspect_cursor_in_window(
        self,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
    ) -> Dict[str, Any]:
        if win32api is None:
            raise RuntimeError('inspect_cursor_in_window is only available on Windows')
        self._ensure_window_api()
        window = self._resolve_window_target(hwnd, title_substring, exact_title, class_name, visible_only)
        cursor = self.get_cursor_pos()
        client_rect_raw = win32gui.GetClientRect(window['hwnd'])
        client_origin = win32gui.ClientToScreen(window['hwnd'], (0, 0))
        width = max(1, int(client_rect_raw[2] - client_rect_raw[0]))
        height = max(1, int(client_rect_raw[3] - client_rect_raw[1]))
        offset_x = int(cursor['x']) - int(client_origin[0])
        offset_y = int(cursor['y']) - int(client_origin[1])
        inside = 0 <= offset_x < width and 0 <= offset_y < height
        raw_ratio_x = offset_x / width
        raw_ratio_y = offset_y / height
        ratio_x = max(0.0, min(1.0, raw_ratio_x))
        ratio_y = max(0.0, min(1.0, raw_ratio_y))
        return {
            'window': window,
            'client_rect': {
                'left': int(client_origin[0]),
                'top': int(client_origin[1]),
                'right': int(client_origin[0]) + width,
                'bottom': int(client_origin[1]) + height,
                'width': width,
                'height': height,
            },
            'cursor': cursor,
            'offset': {'x': offset_x, 'y': offset_y},
            'inside': inside,
            'ratio': {'x': ratio_x, 'y': ratio_y},
            'raw_ratio': {'x': raw_ratio_x, 'y': raw_ratio_y},
        }

    def calibrate_chat_profile_point(
        self,
        profile_name: str,
        point_name: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        visible_only: bool = True,
        use_ratio: bool = True,
    ) -> Dict[str, Any]:
        point = point_name.lower()
        if point not in {'input', 'send'}:
            raise ValueError('point_name only supports input or send')
        cursor_info = self.inspect_cursor_in_window(hwnd, title_substring, exact_title, class_name, visible_only)
        if not cursor_info.get('inside', False):
            raise ValueError('Cursor is outside the window client area. Move cursor inside the target input/send area and retry.')
        profile = self._get_chat_profile(profile_name)
        overrides = self._load_chat_profile_overrides()
        profile_override = dict(overrides.get(profile_name, {}))
        if cursor_info['window']['title']:
            profile_override['title_substring'] = cursor_info['window']['title']
        if cursor_info['window']['class_name']:
            profile_override['class_name'] = cursor_info['window']['class_name']
        if use_ratio:
            profile_override[f'{point}_ratio'] = {
                'x': float(cursor_info['ratio']['x']),
                'y': float(cursor_info['ratio']['y']),
            }
            profile_override.pop(f'{point}_offset', None)
        else:
            profile_override[f'{point}_offset'] = {
                'x': int(cursor_info['offset']['x']),
                'y': int(cursor_info['offset']['y']),
            }
            profile_override.pop(f'{point}_ratio', None)
        if point == 'send' and profile.get('submit_mode', 'enter') == 'enter':
            profile_override['submit_mode'] = 'click'
        overrides[profile_name] = profile_override
        self._save_chat_profile_overrides(overrides)
        return {
            'ok': True,
            'profile_name': profile_name,
            'point_name': point,
            'use_ratio': bool(use_ratio),
            'cursor': cursor_info,
            'profile': self._get_chat_profile(profile_name),
        }

    def send_message_with_profile(
        self,
        profile_name: str,
        text: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        class_name: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        send_button_offset_x: Optional[int] = None,
        send_button_offset_y: Optional[int] = None,
        submit_mode: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        requested_profile_name = profile_name
        profile = self._get_chat_profile(profile_name)
        resolved_title_substring = title_substring if title_substring is not None else profile['title_substring']
        resolved_exact_title = exact_title if exact_title is not None else profile['exact_title']
        resolved_class_name = class_name if class_name is not None else profile['class_name']
        window = self._resolve_chat_window(
            requested_profile_name,
            hwnd,
            resolved_title_substring,
            resolved_exact_title,
            resolved_class_name,
            visible_only,
        )
        effective_profile_name = requested_profile_name
        if requested_profile_name == 'trae' and self._looks_like_trae_solo_window(window):
            effective_profile_name = 'trae_solo'
            profile = self._get_chat_profile(effective_profile_name)
            resolved_title_substring = title_substring if title_substring is not None else profile['title_substring']
            resolved_exact_title = exact_title if exact_title is not None else profile['exact_title']
            resolved_class_name = class_name if class_name is not None else profile['class_name']
        resolved_focus = profile['focus'] if focus is None else focus
        resolved_submit_mode = profile['submit_mode'] if submit_mode is None else submit_mode
        resolved_enter_delay_ms = profile.get('enter_delay_ms', 0) if enter_delay_ms is None else enter_delay_ms
        resolved_enter_times = profile.get('enter_times', 1) if enter_times is None else enter_times
        resolved_click_before_enter = profile.get('click_before_enter', False) if click_before_enter is None else click_before_enter
        resolved_click_before_enter_delay_ms = profile.get('click_before_enter_delay_ms', 120) if click_before_enter_delay_ms is None else click_before_enter_delay_ms
        if input_offset_x is not None and input_offset_y is not None:
            computed_input_offset_x = int(input_offset_x)
            computed_input_offset_y = int(input_offset_y)
        elif profile.get('input_offset') is not None:
            computed_input_offset_x = int(profile['input_offset']['x'])
            computed_input_offset_y = int(profile['input_offset']['y'])
        else:
            computed_input_offset_x = self._ratio_to_offset(window, profile['input_ratio']['x'], 'x')
            computed_input_offset_y = self._ratio_to_offset(window, profile['input_ratio']['y'], 'y')
        computed_send_offset_x = send_button_offset_x
        computed_send_offset_y = send_button_offset_y
        if resolved_submit_mode.lower() == 'click':
            if computed_send_offset_x is None or computed_send_offset_y is None:
                if profile.get('send_offset') is not None:
                    computed_send_offset_x = int(profile['send_offset']['x'])
                    computed_send_offset_y = int(profile['send_offset']['y'])
                elif profile['send_ratio'] is None:
                    raise ValueError(f'Profile {profile_name} requires explicit send button offsets for click submit mode')
                else:
                    computed_send_offset_x = self._ratio_to_offset(window, profile['send_ratio']['x'], 'x')
                    computed_send_offset_y = self._ratio_to_offset(window, profile['send_ratio']['y'], 'y')
        result = self.send_message_to_window(
            text=text,
            input_offset_x=computed_input_offset_x,
            input_offset_y=computed_input_offset_y,
            send_button_offset_x=None if computed_send_offset_x is None else int(computed_send_offset_x),
            send_button_offset_y=None if computed_send_offset_y is None else int(computed_send_offset_y),
            hwnd=window['hwnd'],
            title_substring=None,
            exact_title=None,
            class_name=None,
            submit_mode=resolved_submit_mode,
            visible_only=visible_only,
            focus=resolved_focus,
            restore=restore,
            hold_ms=hold_ms,
            input_ready_delay_ms=input_ready_delay_ms,
            click_delay_ms=click_delay_ms,
            enter_delay_ms=resolved_enter_delay_ms,
            enter_times=resolved_enter_times,
            click_before_enter=resolved_click_before_enter,
            click_before_enter_delay_ms=resolved_click_before_enter_delay_ms,
        )
        result['profile'] = effective_profile_name
        result['requested_profile'] = requested_profile_name
        return result

    def browser_chat_send_message(
        self,
        text: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        submit_mode: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self.send_message_with_profile(
            'browser_chat',
            text,
            hwnd=hwnd,
            title_substring=title_substring,
            exact_title=exact_title,
            input_offset_x=input_offset_x,
            input_offset_y=input_offset_y,
            submit_mode=submit_mode,
            visible_only=visible_only,
            focus=focus,
            restore=restore,
            hold_ms=hold_ms,
            input_ready_delay_ms=input_ready_delay_ms,
            click_delay_ms=click_delay_ms,
            enter_delay_ms=enter_delay_ms,
            enter_times=enter_times,
            click_before_enter=click_before_enter,
            click_before_enter_delay_ms=click_before_enter_delay_ms,
        )

    def trae_send_message(
        self,
        text: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        submit_mode: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        resolved_submit_mode = 'enter' if submit_mode is None else submit_mode
        return self.send_message_with_profile(
            'trae',
            text,
            hwnd=hwnd,
            title_substring=title_substring,
            exact_title=exact_title,
            input_offset_x=input_offset_x,
            input_offset_y=input_offset_y,
            submit_mode=resolved_submit_mode,
            visible_only=visible_only,
            focus=focus,
            restore=restore,
            hold_ms=hold_ms,
            input_ready_delay_ms=input_ready_delay_ms,
            click_delay_ms=click_delay_ms,
            enter_delay_ms=enter_delay_ms,
            enter_times=enter_times,
            click_before_enter=click_before_enter,
            click_before_enter_delay_ms=click_before_enter_delay_ms,
        )

    def trae_solo_send_message(
        self,
        text: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        submit_mode: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        resolved_submit_mode = 'enter' if submit_mode is None else submit_mode
        return self.send_message_with_profile(
            'trae_solo',
            text,
            hwnd=hwnd,
            title_substring=title_substring,
            exact_title=exact_title,
            input_offset_x=input_offset_x,
            input_offset_y=input_offset_y,
            submit_mode=resolved_submit_mode,
            visible_only=visible_only,
            focus=focus,
            restore=restore,
            hold_ms=hold_ms,
            input_ready_delay_ms=input_ready_delay_ms,
            click_delay_ms=click_delay_ms,
            enter_delay_ms=enter_delay_ms,
            enter_times=enter_times,
            click_before_enter=click_before_enter,
            click_before_enter_delay_ms=click_before_enter_delay_ms,
        )

    def wechat_send_message(
        self,
        text: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        submit_mode: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self.send_message_with_profile(
            'wechat',
            text,
            hwnd=hwnd,
            title_substring=title_substring,
            exact_title=exact_title,
            input_offset_x=input_offset_x,
            input_offset_y=input_offset_y,
            submit_mode=submit_mode,
            visible_only=visible_only,
            focus=focus,
            restore=restore,
            hold_ms=hold_ms,
            input_ready_delay_ms=input_ready_delay_ms,
            click_delay_ms=click_delay_ms,
            enter_delay_ms=enter_delay_ms,
            enter_times=enter_times,
            click_before_enter=click_before_enter,
            click_before_enter_delay_ms=click_before_enter_delay_ms,
        )

    def qq_send_message(
        self,
        text: str,
        hwnd: Optional[int] = None,
        title_substring: Optional[str] = None,
        exact_title: Optional[str] = None,
        input_offset_x: Optional[int] = None,
        input_offset_y: Optional[int] = None,
        submit_mode: Optional[str] = None,
        visible_only: bool = True,
        focus: Optional[bool] = None,
        restore: bool = True,
        hold_ms: int = 50,
        input_ready_delay_ms: int = 100,
        click_delay_ms: int = 0,
        enter_delay_ms: Optional[int] = None,
        enter_times: Optional[int] = None,
        click_before_enter: Optional[bool] = None,
        click_before_enter_delay_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        return self.send_message_with_profile(
            'qq',
            text,
            hwnd=hwnd,
            title_substring=title_substring,
            exact_title=exact_title,
            input_offset_x=input_offset_x,
            input_offset_y=input_offset_y,
            submit_mode=submit_mode,
            visible_only=visible_only,
            focus=focus,
            restore=restore,
            hold_ms=hold_ms,
            input_ready_delay_ms=input_ready_delay_ms,
            click_delay_ms=click_delay_ms,
            enter_delay_ms=enter_delay_ms,
            enter_times=enter_times,
            click_before_enter=click_before_enter,
            click_before_enter_delay_ms=click_before_enter_delay_ms,
        )

    def _run_paths(self, script_paths: Iterable[str], runtimes: int):
        PluginManager.reload()
        self._stop_event.clear()
        for path in script_paths:
            self._run_single_path(path, runtimes)

    def _run_single_path(self, script_path: str, runtimes: int):
        head_object = self._parse_script(script_path)
        loop_count = 0
        while loop_count < runtimes or runtimes == 0:
            if self._stop_event.is_set():
                raise ExecutionStopped('Execution stopped')
            self._run_script_from_objects(head_object)
            loop_count += 1

    def _run_script_from_objects(self, head_object: JsonObject, attach: Optional[List[str]] = None):
        current_object = head_object
        while current_object is not None:
            if self._stop_event.is_set():
                raise ExecutionStopped('Execution stopped')
            if attach:
                PluginManager.call_group(attach, current_object)
            current_object = self._run_object(current_object)

    def _run_object(self, json_object: JsonObject):
        object_type = json_object.content.get('type', None)
        call_group = json_object.content.get('call', None)
        if call_group:
            PluginManager.call_group(call_group, json_object)
        if object_type == 'event':
            self._ensure_action_allowed()
            ScriptEvent(json_object.content).execute(self)
        elif object_type == 'sequence':
            self._run_script_from_objects(json_object.content['events'], json_object.content.get('attach'))
        elif object_type == 'if':
            result = PluginManager.call(json_object.content['judge'], json_object)
            if result:
                return json_object.next_object
            return json_object.next_object_if_false
        elif object_type == 'subroutine':
            sub_paths = [self._normalize_script_path(path) for path in json_object.content['path']]
            for path in sub_paths:
                self._run_single_path(path, 1)
        return json_object.next_object

    def _parse_script(self, script_path: str) -> JsonObject:
        try:
            head_object = ScriptParser.parse(script_path)
        except Exception:
            logger.warning('Failed to parse script, maybe it is using legacy grammar')
            head_object = LegacyParser.parse(script_path)
        if head_object is None:
            raise ValueError(f'Unable to parse script: {script_path}')
        return head_object

    def _normalize_script_path(self, script_path: str) -> str:
        candidate = script_path
        if not os.path.isabs(candidate):
            candidate = os.path.join(SCRIPTS_DIR, candidate)
        candidate = os.path.abspath(candidate)
        if not os.path.exists(candidate):
            raise FileNotFoundError(candidate)
        return candidate

    def _resolve_key(
        self,
        key: str,
        key_code: Optional[int] = None,
        extended: Optional[bool] = None,
    ) -> Tuple[int, str, int]:
        normalized = key.strip().lower()
        normalized = KEY_ALIASES.get(normalized, normalized)
        if key_code is None:
            key_code = KEY_CODES.get(normalized)
        if key_code is None:
            raise ValueError(f'Unsupported key: {key}')
        if extended is None:
            extended = normalized in EXTENDED_KEYS
        if len(key.strip()) == 1:
            display_name = key.strip().upper()
        else:
            display_name = normalized.upper()
        return int(key_code), display_name, int(bool(extended))

    def _count_objects(self, head_object: JsonObject) -> int:
        seen = set()
        stack = [head_object]
        while stack:
            current = stack.pop()
            if current is None:
                continue
            current_id = id(current)
            if current_id in seen:
                continue
            seen.add(current_id)
            content = current.content
            if content.get('type') == 'sequence' and content.get('events') is not None:
                stack.append(content.get('events'))
            stack.append(current.next_object)
            stack.append(current.next_object_if_false)
        return len(seen)

    def _ensure_action_allowed(self):
        guard = None
        with self._state_lock:
            if self._window_guard is not None:
                guard = dict(self._window_guard)
        if guard is None:
            return
        current_hwnd = self._get_foreground_window_handle()
        if current_hwnd != guard['hwnd']:
            current_title = ''
            if current_hwnd and win32gui is not None and win32gui.IsWindow(current_hwnd):
                current_title = win32gui.GetWindowText(current_hwnd)
            raise RuntimeError(
                f"Window guard blocked action. Expected hwnd={guard['hwnd']} title='{guard['title']}', "
                f"current hwnd={current_hwnd} title='{current_title}'"
            )

    def _ensure_window_api(self):
        if win32gui is None or win32con is None:
            raise RuntimeError('Window tools are only available on Windows')

    def _get_foreground_window_handle(self) -> int:
        self._ensure_window_api()
        return int(win32gui.GetForegroundWindow())

    def _resolve_window_target(
        self,
        hwnd: Optional[int],
        title_substring: Optional[str],
        exact_title: Optional[str],
        class_name: Optional[str],
        visible_only: bool,
    ) -> Dict[str, Any]:
        self._ensure_window_api()
        if hwnd is not None:
            return self._window_info(hwnd)
        windows = self._enumerate_windows(
            title_filter=title_substring or '',
            exact_title=exact_title,
            class_name=class_name,
            visible_only=visible_only,
            limit=1,
        )
        if len(windows) == 0:
            raise ValueError('No window matched the given condition')
        return windows[0]

    def _get_chat_profile(self, profile_name: str) -> Dict[str, Any]:
        if profile_name not in CHAT_APP_PROFILES:
            raise ValueError(f'Unsupported chat profile: {profile_name}')
        overrides = self._load_chat_profile_overrides()
        return self._merge_chat_profile(profile_name, overrides)

    def _get_screenshot_profile(self, profile_name: str) -> Dict[str, Any]:
        if profile_name not in SCREENSHOT_APP_PROFILES:
            raise ValueError(f'Unsupported screenshot profile: {profile_name}')
        overrides = self._load_screenshot_profile_overrides()
        return self._merge_screenshot_profile(profile_name, overrides)

    def _merge_chat_profile(self, profile_name: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(CHAT_APP_PROFILES[profile_name])
        override = overrides.get(profile_name, {})
        if not isinstance(override, dict):
            return merged
        for key, value in override.items():
            if isinstance(value, dict):
                merged[key] = dict(value)
            else:
                merged[key] = value
        return merged

    def _merge_screenshot_profile(self, profile_name: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(SCREENSHOT_APP_PROFILES[profile_name])
        override = overrides.get(profile_name, {})
        if not isinstance(override, dict):
            return merged
        for key, value in override.items():
            if isinstance(value, list):
                merged[key] = [dict(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, dict):
                merged[key] = dict(value)
            else:
                merged[key] = value
        return merged

    def _load_chat_profile_overrides(self) -> Dict[str, Any]:
        if not os.path.exists(CHAT_PROFILE_CONFIG_PATH):
            return {}
        with open(CHAT_PROFILE_CONFIG_PATH, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        if content == '':
            return {}
        data = json5.loads(content)
        if not isinstance(data, dict):
            return {}
        profiles = data.get('profiles', {})
        if not isinstance(profiles, dict):
            return {}
        return profiles

    def _save_chat_profile_overrides(self, overrides: Dict[str, Any]):
        with open(CHAT_PROFILE_CONFIG_PATH, 'w', encoding='utf-8') as file:
            json5.dump({'profiles': overrides}, file, ensure_ascii=False, quote_keys=True, indent=2)

    def _load_screenshot_profile_overrides(self) -> Dict[str, Any]:
        if not os.path.exists(SCREENSHOT_PROFILE_CONFIG_PATH):
            return {}
        with open(SCREENSHOT_PROFILE_CONFIG_PATH, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        if content == '':
            return {}
        data = json5.loads(content)
        if not isinstance(data, dict):
            return {}
        profiles = data.get('profiles', {})
        if not isinstance(profiles, dict):
            return {}
        return profiles

    def _save_screenshot_profile_overrides(self, overrides: Dict[str, Any]):
        with open(SCREENSHOT_PROFILE_CONFIG_PATH, 'w', encoding='utf-8') as file:
            json5.dump({'profiles': overrides}, file, ensure_ascii=False, quote_keys=True, indent=2)

    def _normalize_partition_specs(self, partitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(partitions, list) or len(partitions) == 0:
            raise ValueError('partitions must be a non-empty list')
        result: List[Dict[str, Any]] = []
        for item in partitions:
            if not isinstance(item, dict):
                raise ValueError('each partition must be an object')
            name = item.get('name')
            if not name:
                raise ValueError('partition name is required')
            left_ratio = float(item.get('left_ratio'))
            top_ratio = float(item.get('top_ratio'))
            right_ratio = float(item.get('right_ratio'))
            bottom_ratio = float(item.get('bottom_ratio'))
            if not (0 <= left_ratio < right_ratio <= 1):
                raise ValueError(f'invalid horizontal ratios in partition: {name}')
            if not (0 <= top_ratio < bottom_ratio <= 1):
                raise ValueError(f'invalid vertical ratios in partition: {name}')
            result.append({
                'name': str(name),
                'left_ratio': left_ratio,
                'top_ratio': top_ratio,
                'right_ratio': right_ratio,
                'bottom_ratio': bottom_ratio,
            })
        return result

    def _ensure_bridge_dirs(self, base_dir: Optional[str]) -> Dict[str, str]:
        resolved_base_dir = os.path.abspath(base_dir or AI_BRIDGE_BASE_DIR)
        tasks_dir = os.path.join(resolved_base_dir, 'tasks')
        replies_dir = os.path.join(resolved_base_dir, 'replies')
        archive_dir = os.path.join(resolved_base_dir, 'archive')
        archive_tasks_dir = os.path.join(archive_dir, 'tasks')
        archive_replies_dir = os.path.join(archive_dir, 'replies')
        for path in [resolved_base_dir, tasks_dir, replies_dir, archive_dir, archive_tasks_dir, archive_replies_dir]:
            os.makedirs(path, exist_ok=True)
        return {
            'base_dir': resolved_base_dir,
            'tasks_dir': tasks_dir,
            'replies_dir': replies_dir,
            'archive_tasks_dir': archive_tasks_dir,
            'archive_replies_dir': archive_replies_dir,
        }

    def _count_json_files(self, directory: str) -> int:
        count = 0
        for name in os.listdir(directory):
            if name.endswith('.json'):
                count += 1
        return count

    def _compute_payload_checksum(self, payload: Dict[str, Any]) -> str:
        payload_copy = json.loads(json.dumps(payload, ensure_ascii=False))
        header = payload_copy.get('header', {})
        if isinstance(header, dict):
            header.pop('checksum', None)
        canonical = json.dumps(payload_copy, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"

    def _write_json_atomic(self, file_path: str, payload: Dict[str, Any]):
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
        temp_path = f'{file_path}.{uuid.uuid4().hex}.tmp'
        with open(temp_path, 'w', encoding='utf-8') as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, file_path)

    def _read_json_file(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _read_bridge_directory(self, directory: str, status: Optional[str]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for name in sorted(os.listdir(directory)):
            if not name.endswith('.json'):
                continue
            file_path = os.path.join(directory, name)
            payload = self._read_json_file(file_path)
            payload_header = payload.get('header', {})
            payload_status = payload_header.get('status')
            if status is not None and payload_status != status:
                continue
            items.append({
                'file_name': name,
                'file_path': file_path,
                'header': payload_header,
                'body': payload.get('body', {}),
            })
        return items

    def _move_to_archive(self, source_path: str, target_path: str):
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        if os.path.exists(target_path):
            root, ext = os.path.splitext(target_path)
            target_path = f'{root}_{uuid.uuid4().hex[:8]}{ext}'
        os.replace(source_path, target_path)

    def _detect_trae_task_poller(self) -> Dict[str, Any]:
        command = [
            'powershell',
            '-NoProfile',
            '-Command',
            "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like '*trae_task_poller.py*' } | Select-Object ProcessId, CommandLine | ConvertTo-Json -Compress",
        ]
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, creationflags=0)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode('utf-8', errors='ignore')[:1000] or 'Failed to inspect trae_task_poller process')
        raw = proc.stdout.decode('utf-8', errors='ignore').strip()
        if not raw:
            return {
                'running': False,
                'processes': [],
            }
        payload = json.loads(raw)
        processes = payload if isinstance(payload, list) else [payload]
        normalized = []
        for item in processes:
            if not item:
                continue
            normalized.append({
                'process_id': item.get('ProcessId'),
                'command_line': item.get('CommandLine'),
            })
        return {
            'running': len(normalized) > 0,
            'processes': normalized,
        }

    def _select_preferred_trae_window(self, windows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        return self._select_preferred_chat_window('trae', windows)

    def _resolve_chat_window(
        self,
        profile_name: str,
        hwnd: Optional[int],
        title_substring: Optional[str],
        exact_title: Optional[str],
        class_name: Optional[str],
        visible_only: bool,
    ) -> Dict[str, Any]:
        self._ensure_window_api()
        if hwnd is not None:
            return self._window_info(hwnd)
        profile = self._get_chat_profile(profile_name)
        if exact_title is not None:
            return self._resolve_window_target(None, '', exact_title, class_name, visible_only)
        search_terms: List[str] = []
        if title_substring is not None:
            search_terms.append(str(title_substring))
        default_title = profile.get('title_substring')
        profile_keywords = profile.get('title_keywords')
        if title_substring == default_title and isinstance(profile_keywords, list):
            for keyword in profile_keywords:
                normalized_keyword = str(keyword or '').strip()
                if normalized_keyword and normalized_keyword not in search_terms:
                    search_terms.append(normalized_keyword)
        if len(search_terms) == 0:
            search_terms.append('')
        candidates_by_hwnd: Dict[int, Dict[str, Any]] = {}
        for term in search_terms:
            windows = self._enumerate_windows(
                title_filter=term,
                exact_title=None,
                class_name=class_name,
                visible_only=visible_only,
                limit=20,
            )
            for window in windows:
                candidates_by_hwnd[int(window['hwnd'])] = window
        candidates = list(candidates_by_hwnd.values())
        if len(candidates) == 0:
            raise ValueError('No window matched the given condition')
        selected = self._select_preferred_chat_window(profile_name, candidates)
        if selected is None:
            raise ValueError('No window matched the given condition')
        return selected

    def _select_preferred_chat_window(
        self,
        profile_name: str,
        windows: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if not windows:
            return None
        scored: List[Tuple[int, Dict[str, Any]]] = []
        for window in windows:
            title = str(window.get('title') or '')
            title_lower = title.lower()
            class_name = str(window.get('class_name') or '').lower()
            rect = window.get('rect', {}) if isinstance(window.get('rect', {}), dict) else {}
            width = max(0, int(rect.get('width', 0)))
            height = max(0, int(rect.get('height', 0)))
            score = 0
            if window.get('foreground'):
                score += 40
            if width > 0 and height > 0:
                score += min(10, int((width * height) / 250000))
            if class_name == 'chrome_widgetwin_1':
                score += 3
            if profile_name == 'trae':
                if title == 'Trae':
                    score += 20
                if title.endswith(' - Trae'):
                    score += 16
                if ' - trae' in title_lower:
                    score += 10
                if 'trae solo' in title_lower:
                    score += 18
                elif 'trae' in title_lower:
                    score += 12
                if any(name in title_lower for name in ['chrome', 'edge', 'browser', '网页']):
                    score += 6
            elif profile_name == 'trae_solo':
                if 'trae solo' in title_lower:
                    score += 60
                elif 'trae' in title_lower:
                    score += 10
                if any(name in title_lower for name in ['chrome', 'edge', 'browser', '网页']):
                    score += 18
            elif profile_name == 'browser_chat':
                if any(name in title_lower for name in ['chrome', 'edge', 'browser', '网页']):
                    score += 10
            scored.append((score, window))
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def _looks_like_trae_solo_window(self, window: Dict[str, Any]) -> bool:
        title = str(window.get('title') or '').lower()
        if 'trae solo' in title:
            return True
        return 'trae' in title and any(name in title for name in ['chrome', 'edge', 'browser', '网页'])

    def _ratio_to_offset(self, window: Dict[str, Any], ratio: float, axis: str) -> int:
        rect = window['rect']
        if axis == 'x':
            size = rect['width']
        else:
            size = rect['height']
        if size <= 0:
            raise ValueError('Window size is invalid')
        offset = int(round(size * float(ratio)))
        return max(0, min(size - 1, offset))

    def _window_offset_to_screen(self, window: Dict[str, Any], offset_x: int, offset_y: int) -> Tuple[int, int]:
        rect = window['rect']
        return rect['left'] + int(offset_x), rect['top'] + int(offset_y)

    def _ensure_qt_application(self) -> QGuiApplication:
        app = QGuiApplication.instance()
        if app is not None:
            return app
        if self._qt_app is None:
            self._qt_app = QGuiApplication([])
        return self._qt_app

    def _capture_window_client(self, window: Dict[str, Any]) -> Dict[str, Any]:
        self._ensure_window_api()
        app = self._ensure_qt_application()
        client_rect = win32gui.GetClientRect(window['hwnd'])
        client_origin = win32gui.ClientToScreen(window['hwnd'], (0, 0))
        width = int(client_rect[2] - client_rect[0])
        height = int(client_rect[3] - client_rect[1])
        if width <= 0 or height <= 0:
            raise ValueError('Window client area is empty')
        screen = app.primaryScreen()
        if screen is None:
            raise RuntimeError('Unable to access primary screen')
        pixmap = screen.grabWindow(0, int(client_origin[0]), int(client_origin[1]), width, height)
        if pixmap.isNull():
            raise RuntimeError('Window capture failed')
        return {
            'pixmap': pixmap,
            'capture_rect': {
                'left': int(client_origin[0]),
                'top': int(client_origin[1]),
                'right': int(client_origin[0]) + width,
                'bottom': int(client_origin[1]) + height,
                'width': width,
                'height': height,
            },
            'client_rect': {
                'left': 0,
                'top': 0,
                'right': width,
                'bottom': height,
                'width': width,
                'height': height,
            },
        }

    def _normalize_capture_region(
        self,
        client_rect: Dict[str, Any],
        offset_x: int,
        offset_y: int,
        width: int,
        height: int,
    ) -> Dict[str, Any]:
        normalized_width = int(width)
        normalized_height = int(height)
        if normalized_width <= 0 or normalized_height <= 0:
            raise ValueError('width and height must be positive')
        left = max(0, int(offset_x))
        top = max(0, int(offset_y))
        if left >= client_rect['width'] or top >= client_rect['height']:
            raise ValueError('Capture region starts outside the window client area')
        clipped_width = min(normalized_width, client_rect['width'] - left)
        clipped_height = min(normalized_height, client_rect['height'] - top)
        return {
            'offset_x': left,
            'offset_y': top,
            'width': clipped_width,
            'height': clipped_height,
            'left': left,
            'top': top,
            'right': left + clipped_width,
            'bottom': top + clipped_height,
        }

    def _save_pixmap(self, pixmap, prefix: str) -> str:
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(SCREENSHOTS_DIR, f'{prefix}_{timestamp}_{uuid.uuid4().hex[:8]}.png')
        if not pixmap.save(file_path, 'PNG'):
            raise RuntimeError(f'Failed to save screenshot: {file_path}')
        return file_path

    def _pixmap_to_data_url(self, pixmap, max_width: int) -> str:
        target = pixmap
        target_max_width = max(320, int(max_width))
        if target.width() > target_max_width:
            target = target.scaledToWidth(
                target_max_width,
                Qt.TransformationMode.SmoothTransformation,
            )
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QBuffer.OpenModeFlag.WriteOnly)
        target.save(buffer, 'PNG')
        buffer.close()
        encoded = base64.b64encode(bytes(data)).decode('ascii')
        return f'data:image/png;base64,{encoded}'

    def _build_grid_partitions(self, client_rect: Dict[str, Any], rows: int, cols: int) -> List[Dict[str, Any]]:
        base_width = int(client_rect['width'])
        base_height = int(client_rect['height'])
        partition_rows = max(1, int(rows))
        partition_cols = max(1, int(cols))
        result: List[Dict[str, Any]] = []
        for row in range(partition_rows):
            top = int(round(base_height * row / partition_rows))
            bottom = int(round(base_height * (row + 1) / partition_rows))
            for col in range(partition_cols):
                left = int(round(base_width * col / partition_cols))
                right = int(round(base_width * (col + 1) / partition_cols))
                width_value = max(1, right - left)
                height_value = max(1, bottom - top)
                result.append({
                    'id': 0,
                    'name': None,
                    'rect': {
                        'left': left,
                        'top': top,
                        'right': left + width_value,
                        'bottom': top + height_value,
                        'width': width_value,
                        'height': height_value,
                    },
                })
        return self._assign_partition_ids(result)

    def _build_natural_partitions(self, client_rect: Dict[str, Any], specs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        base_width = int(client_rect['width'])
        base_height = int(client_rect['height'])
        result: List[Dict[str, Any]] = []
        for spec in specs:
            left = int(round(base_width * float(spec.get('left_ratio', 0.0))))
            top = int(round(base_height * float(spec.get('top_ratio', 0.0))))
            right = int(round(base_width * float(spec.get('right_ratio', 1.0))))
            bottom = int(round(base_height * float(spec.get('bottom_ratio', 1.0))))
            left = max(0, min(base_width - 1, left))
            top = max(0, min(base_height - 1, top))
            right = max(left + 1, min(base_width, right))
            bottom = max(top + 1, min(base_height, bottom))
            result.append({
                'id': 0,
                'name': spec.get('name'),
                'rect': {
                    'left': left,
                    'top': top,
                    'right': right,
                    'bottom': bottom,
                    'width': right - left,
                    'height': bottom - top,
                },
            })
        return self._assign_partition_ids(result)

    def _assign_partition_ids(self, partitions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for index, item in enumerate(partitions):
            copied = dict(item)
            copied['id'] = index + 1
            result.append(copied)
        return result

    def _annotate_partitions(self, pixmap, partitions: List[Dict[str, Any]]):
        annotated = pixmap.copy()
        painter = QPainter(annotated)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        border_pen = QPen(QColor(255, 0, 0), 3)
        text_pen = QPen(QColor(255, 0, 0), 6)
        painter.setPen(border_pen)
        font = QFont()
        font.setBold(True)
        font.setPointSize(max(18, min(42, int(min(annotated.width(), annotated.height()) / 12))))
        painter.setFont(font)
        for item in partitions:
            rect = item['rect']
            left = int(rect['left'])
            top = int(rect['top'])
            width_value = int(rect['width'])
            height_value = int(rect['height'])
            painter.setPen(border_pen)
            painter.drawRect(left, top, width_value, height_value)
            painter.setPen(text_pen)
            painter.drawText(left + 18, top + 46, str(item['id']))
        painter.end()
        return annotated

    def _enumerate_windows(
        self,
        title_filter: str,
        exact_title: Optional[str],
        class_name: Optional[str],
        visible_only: bool,
        limit: int,
    ) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        normalized_filter = title_filter.lower().strip()
        normalized_exact = exact_title.lower().strip() if exact_title else None
        normalized_class = class_name.lower().strip() if class_name else None
        target_limit = max(1, int(limit))

        def callback(hwnd, _):
            if len(result) >= target_limit:
                return True
            if visible_only and not win32gui.IsWindowVisible(hwnd):
                return True
            title = win32gui.GetWindowText(hwnd)
            window_class = win32gui.GetClassName(hwnd)
            if normalized_exact is not None and title.lower() != normalized_exact:
                return True
            if normalized_filter and normalized_filter not in title.lower():
                return True
            if normalized_class is not None and window_class.lower() != normalized_class:
                return True
            result.append(self._window_info(hwnd, title=title, class_name=window_class))
            return True

        win32gui.EnumWindows(callback, None)
        return result[:target_limit]

    def _window_info(
        self,
        hwnd: int,
        title: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._ensure_window_api()
        handle = int(hwnd)
        if not win32gui.IsWindow(handle):
            raise ValueError(f'Invalid hwnd: {hwnd}')
        actual_title = win32gui.GetWindowText(handle) if title is None else title
        actual_class = win32gui.GetClassName(handle) if class_name is None else class_name
        left, top, right, bottom = win32gui.GetWindowRect(handle)
        return {
            'hwnd': handle,
            'title': actual_title,
            'class_name': actual_class,
            'visible': bool(win32gui.IsWindowVisible(handle)),
            'minimized': bool(win32gui.IsIconic(handle)),
            'foreground': handle == win32gui.GetForegroundWindow(),
            'rect': {
                'left': left,
                'top': top,
                'right': right,
                'bottom': bottom,
                'width': right - left,
                'height': bottom - top,
            },
        }

    def _assert_not_running(self):
        worker = None
        with self._state_lock:
            worker = self._worker
        if worker is not None and worker.is_alive():
            raise RuntimeError('Another execution is already running')

    def _begin_run(self, mode: str, script_paths: List[str], runtimes: int) -> str:
        self._stop_event.clear()
        job_id = str(uuid.uuid4())
        with self._state_lock:
            self._status = {
                'state': 'running',
                'job_id': job_id,
                'running': True,
                'mode': mode,
                'script_paths': script_paths,
                'runtimes': runtimes,
                'error': None,
            }
        return job_id

    def _finish_run(self, state: str, error: Optional[str] = None):
        with self._state_lock:
            self._status['state'] = state
            self._status['running'] = False
            self._status['error'] = error
            worker = self._worker
            if worker is None or not worker.is_alive():
                self._worker = None
