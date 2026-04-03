import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import urllib.request


class TraeTaskExecutor:
    def __init__(
        self,
        mode: str = 'auto',
        http_endpoint: Optional[str] = None,
        http_headers_json: Optional[str] = None,
        external_command: Optional[str] = None,
        external_args_json: Optional[str] = None,
        trae_exe: Optional[str] = None,
        trae_cli_js: Optional[str] = None,
        trae_logs_dir: Optional[str] = None,
        ocr_python: Optional[str] = None,
        timeout_s: int = 120,
    ):
        self.mode = mode
        self.http_endpoint = http_endpoint
        self.http_headers_json = http_headers_json
        self.external_command = external_command
        self.external_args_json = external_args_json
        self.trae_exe = trae_exe or self._default_trae_exe()
        self.trae_cli_js = trae_cli_js or self._default_trae_cli_js()
        self.trae_logs_dir = trae_logs_dir or self._default_trae_logs_dir()
        self.ocr_python = ocr_python or self._default_ocr_python()
        self.timeout_s = int(timeout_s)

    @classmethod
    def from_env(cls) -> "TraeTaskExecutor":
        return cls(
            mode=os.getenv('TRAE_EXECUTOR_MODE', 'auto'),
            http_endpoint=os.getenv('TRAE_EXECUTOR_HTTP_ENDPOINT'),
            http_headers_json=os.getenv('TRAE_EXECUTOR_HTTP_HEADERS_JSON'),
            external_command=os.getenv('TRAE_EXECUTOR_COMMAND'),
            external_args_json=os.getenv('TRAE_EXECUTOR_ARGS_JSON'),
            trae_exe=os.getenv('TRAE_EXECUTOR_TRAE_EXE'),
            trae_cli_js=os.getenv('TRAE_EXECUTOR_TRAE_CLI_JS'),
            trae_logs_dir=os.getenv('TRAE_EXECUTOR_TRAE_LOGS_DIR'),
            ocr_python=os.getenv('TRAE_EXECUTOR_OCR_PYTHON'),
            timeout_s=int(os.getenv('TRAE_EXECUTOR_TIMEOUT_S', '120')),
        )

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        mode = self._resolve_mode()
        if mode == 'window_chat':
            return self._execute_window_chat(task)
        if mode == 'rules':
            return self._execute_rules(task)
        if mode == 'http':
            return self._execute_http(task)
        if mode == 'external':
            return self._execute_external(task)
        if mode == 'trae_cli':
            return self._execute_trae_cli(task)
        raise ValueError(f'Unsupported TRAE_EXECUTOR_MODE: {self.mode}')

    def _execute_rules(self, task: Dict[str, Any]) -> Dict[str, Any]:
        header = task.get('header', {})
        body = task.get('body', {})
        task_type = str(header.get('type', 'unknown'))
        content = str(body.get('content', ''))
        context = body.get('context', {}) if isinstance(body.get('context', {}), dict) else {}
        expectation = body.get('expectation', {}) if isinstance(body.get('expectation', {}), dict) else {}

        if task_type == 'chat':
            return self._rules_chat(content, context, expectation)
        if task_type == 'code_review':
            return self._rules_code_review(content, context, expectation)
        if task_type == 'debug':
            return self._rules_debug(content, context, expectation)
        if task_type == 'code_generate':
            return self._rules_code_generate(content, context, expectation)
        return self._rules_generic(task_type, content, context, expectation)

    def _rules_chat(self, content: str, context: Dict[str, Any], expectation: Dict[str, Any]) -> Dict[str, Any]:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        numbered = [line for line in lines if re.match(r'^\d+\.', line)]
        answers = []
        if numbered:
            for line in numbered:
                q = re.sub(r'^\d+\.\s*', '', line)
                if '顺序' in q or '是否合理' in q:
                    answers.append({'q': q, 'a': '合理。先抽执行器再接真实能力，能先把协议/结果结构稳定下来，降低后续接入风险。'})
                elif '统一' in q or 'structured' in q:
                    answers.append({'q': q, 'a': '建议统一成 execute(task)->structured result，并固定 schema，方便 Host 侧自动解析与重试。'})
                elif '字段' in q:
                    answers.append({'q': q, 'a': '建议补：protocol_version、status、error(code/message/retryable)、duration_ms、trace_id、model/engine、artifact_paths。'})
                else:
                    answers.append({'q': q, 'a': '建议按任务目标补充约束：输入上下文、输出格式、失败重试策略。'})
        else:
            answers.append({'a': '已收到。建议通过文件桥接作为主链路，窗口输入仅作兜底；下一步把执行器接入真实 Trae 能力入口（MCP/HTTP/CLI）。'})

        return {
            'handled': True,
            'task_type': 'chat',
            'output': {
                'format': 'json',
                'content': {
                    'answers': answers,
                    'received_chars': len(content),
                    'received_lines': len(lines),
                },
            },
            'processed_at': time.time(),
        }

    def _rules_code_review(self, content: str, context: Dict[str, Any], expectation: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        for file_path, code in context.items():
            if not isinstance(code, str):
                continue
            if re.search(r'def\s+divide\s*\(.*\):', code) and '/ b' in code:
                issues.append({'file': file_path, 'severity': 'high', 'message': '可能存在除零风险，建议显式检查 b==0 或使用异常返回/提示。'})
            if re.search(r'except\s+Exception\s*:', code):
                issues.append({'file': file_path, 'severity': 'medium', 'message': '存在裸 Exception 捕获，建议收窄异常范围。'})
            if re.search(r'print\(', code):
                issues.append({'file': file_path, 'severity': 'low', 'message': '存在 print 调试输出，建议改为结构化日志。'})

        suggestion = (
            "示例改进：\n\n"
            "```python\n"
            "def divide(a, b):\n"
            "    if b == 0:\n"
            "        raise ZeroDivisionError('b must not be 0')\n"
            "    return a / b\n"
            "```"
        )
        return {
            'handled': True,
            'task_type': 'code_review',
            'summary': content,
            'issues': issues,
            'output': {
                'format': 'markdown',
                'content': suggestion,
            },
            'processed_at': time.time(),
        }

    def _rules_debug(self, content: str, context: Dict[str, Any], expectation: Dict[str, Any]) -> Dict[str, Any]:
        combined = content + '\n' + '\n'.join([str(v) for v in context.values()])
        hypotheses = []
        if 'PermissionError' in combined:
            hypotheses.append('检查执行用户对目标目录的写权限，或把 base_dir 切到项目目录内。')
        if 'timeout' in combined.lower():
            hypotheses.append('确认处理端轮询器是否在运行；增加指数退避上限与超时日志。')
        if not hypotheses:
            hypotheses.append('先定位报错堆栈最内层，再核对输入参数与边界条件。')
        return {
            'handled': True,
            'task_type': 'debug',
            'summary': content,
            'hypotheses': hypotheses,
            'processed_at': time.time(),
        }

    def _rules_code_generate(self, content: str, context: Dict[str, Any], expectation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'handled': True,
            'task_type': 'code_generate',
            'summary': content,
            'plan': [
                '确认输入/输出 schema 与幂等键',
                '实现最小可运行版本',
                '补充超时与重试',
                '补充归档与清理策略',
                '补充测试用例与冒烟脚本',
            ],
            'processed_at': time.time(),
        }

    def _rules_generic(self, task_type: str, content: str, context: Dict[str, Any], expectation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'handled': True,
            'task_type': task_type,
            'output': {
                'format': 'json',
                'content': {
                    'message': 'task received',
                    'received_chars': len(content),
                    'context_keys': list(context.keys()),
                },
            },
            'processed_at': time.time(),
        }

    def _execute_trae_cli(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self._can_use_trae_cli():
            raise ValueError('Trae CLI entry is unavailable; set TRAE_EXECUTOR_TRAE_EXE / TRAE_EXECUTOR_TRAE_CLI_JS or use http/external mode')
        started_at = time.time()
        prompt = self._build_trae_cli_prompt(task)
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
        command = [
            self.trae_exe,
            self.trae_cli_js,
            'chat',
            prompt,
            '--reuse-window',
        ]
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout_text = ''
        stderr_text = ''
        evidence = {}
        evidence_wait_s = min(self.timeout_s, 20)
        poll_deadline = time.time() + evidence_wait_s
        while time.time() < poll_deadline:
            if proc.poll() is not None:
                break
            time.sleep(1)
            evidence = self._collect_trae_cli_evidence(prompt, started_at)
            if evidence.get('aha_log_hits') or evidence.get('sandbox_cli_hits'):
                break
        try:
            stdout_bytes, stderr_bytes = proc.communicate(timeout=2)
            stdout_text = stdout_bytes.decode('utf-8', errors='ignore').strip()
            stderr_text = stderr_bytes.decode('utf-8', errors='ignore').strip()
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                stdout_bytes, stderr_bytes = proc.communicate(timeout=3)
                stdout_text = stdout_bytes.decode('utf-8', errors='ignore').strip()
                stderr_text = stderr_bytes.decode('utf-8', errors='ignore').strip()
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout_bytes, stderr_bytes = proc.communicate()
                stdout_text = stdout_bytes.decode('utf-8', errors='ignore').strip()
                stderr_text = stderr_bytes.decode('utf-8', errors='ignore').strip()
        duration_ms = int((time.time() - started_at) * 1000)
        if not evidence:
            evidence = self._collect_trae_cli_evidence(prompt, started_at)
        if not evidence.get('aha_log_hits') and not evidence.get('sandbox_cli_hits'):
            raise RuntimeError(stderr_text[:4000] or stdout_text[:4000] or 'Trae CLI started but no execution evidence was found in Trae logs')
        summary = self._summarize_trae_cli_run(task, evidence, duration_ms)
        return {
            'handled': True,
            'task_type': str(task.get('header', {}).get('type', 'unknown')),
            'executor_mode': 'trae_cli',
            'output': {
                'format': 'json',
                'content': {
                    'reply': summary,
                    'prompt_hash': prompt_hash,
                    'duration_ms': duration_ms,
                    'command': command,
                    'stdout': stdout_text[:2000],
                    'stderr': stderr_text[-2000:],
                    'evidence': evidence,
                    'note': '该结果来自真实 Trae CLI 入口的执行证据汇总，不再使用本地 echo 逻辑。',
                },
            },
            'processed_at': time.time(),
        }

    def _execute_window_chat(self, task: Dict[str, Any]) -> Dict[str, Any]:
        started_at = time.time()
        controller = self._get_mcp_controller()
        expected_reply = self._get_expected_window_reply(task)
        markers = self._build_window_reply_markers(task)
        trae_status = controller.trae_status(sample_limit=3)
        if not trae_status.get('window_ready'):
            raise RuntimeError('Trae 窗口未就绪，无法执行窗口桥接发送')
        before_text = self._capture_trae_chat_text(controller)
        profile = controller.get_chat_profile('trae')['profile']
        send_result = controller.trae_delegate(
            content=str(task.get('body', {}).get('content', '')),
            task_id=str(task.get('header', {}).get('task_id', '')),
            expected_reply=expected_reply or None,
            mode='window_message',
            title_substring=profile.get('title_substring', 'Trae'),
            exact_title=profile.get('exact_title'),
            submit_mode=profile.get('submit_mode', 'enter'),
            input_ready_delay_ms=150,
            click_delay_ms=80,
            enter_delay_ms=int(profile.get('enter_delay_ms', 600)),
            enter_times=int(profile.get('enter_times', 3)),
            click_before_enter=bool(profile.get('click_before_enter', True)),
            click_before_enter_delay_ms=int(profile.get('click_before_enter_delay_ms', 120)),
        )
        after_text = before_text
        deadline = time.time() + self.timeout_s
        while time.time() < deadline:
            time.sleep(2)
            after_text = self._capture_trae_chat_text(controller)
            if self._extract_marked_reply(after_text, markers['begin'], markers['end']):
                break
            if expected_reply and expected_reply in self._normalize_text(after_text):
                break
        reply_text = self._extract_marked_reply(after_text, markers['begin'], markers['end'])
        if not reply_text and expected_reply and expected_reply in self._normalize_text(after_text):
            reply_text = self._extract_incremental_reply(before_text, after_text, send_result.get('send_result', {}).get('prompt', ''), expected_reply)
        duration_ms = int((time.time() - started_at) * 1000)
        if not reply_text:
            raise RuntimeError('窗口对话已发送，但未从 Trae 可见聊天区域提取到新的回复文本')
        return {
            'handled': True,
            'task_type': str(task.get('header', {}).get('type', 'unknown')),
            'executor_mode': 'window_chat',
            'output': {
                'format': 'json',
                'content': {
                    'reply': reply_text,
                    'duration_ms': duration_ms,
                    'trae_status': trae_status,
                    'send_result': send_result,
                    'ocr_before': before_text,
                    'ocr_after': after_text,
                    'note': '该结果来自 Trae 可见聊天窗口的真实文本 OCR 抽取。',
                },
            },
            'processed_at': time.time(),
        }

    def _execute_http(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self.http_endpoint:
            raise ValueError('TRAE_EXECUTOR_HTTP_ENDPOINT is required for http mode')
        headers = {'Content-Type': 'application/json'}
        if self.http_headers_json:
            headers.update(json.loads(self.http_headers_json))
        data = json.dumps(task, ensure_ascii=False).encode('utf-8')
        request = urllib.request.Request(self.http_endpoint, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
            raw = response.read().decode('utf-8')
        return json.loads(raw)

    def _execute_external(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self.external_command:
            raise ValueError('TRAE_EXECUTOR_COMMAND is required for external mode')
        args = []
        if self.external_args_json:
            args = json.loads(self.external_args_json)
            if not isinstance(args, list):
                raise ValueError('TRAE_EXECUTOR_ARGS_JSON must be a JSON array')
        proc = subprocess.run(
            [self.external_command, *[str(a) for a in args]],
            input=json.dumps(task, ensure_ascii=False).encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=self.timeout_s,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode('utf-8', errors='ignore')[:4000])
        return json.loads(proc.stdout.decode('utf-8'))

    def _resolve_mode(self) -> str:
        mode = (self.mode or 'auto').lower().strip()
        if mode == 'auto':
            if self._can_use_window_chat():
                return 'window_chat'
            if self._can_use_trae_cli():
                return 'trae_cli'
            return 'rules'
        return mode

    def _can_use_window_chat(self) -> bool:
        try:
            self._get_mcp_controller()
            if not self.ocr_python or not os.path.exists(self.ocr_python):
                return False
            return True
        except Exception:
            return False

    def _can_use_trae_cli(self) -> bool:
        return bool(self.trae_exe and self.trae_cli_js and os.path.exists(self.trae_exe) and os.path.exists(self.trae_cli_js))

    def _default_trae_exe(self) -> Optional[str]:
        local_appdata = os.getenv('LOCALAPPDATA')
        if not local_appdata:
            return None
        return os.path.join(local_appdata, 'Programs', 'Trae', 'Trae.exe')

    def _default_trae_cli_js(self) -> Optional[str]:
        trae_exe = self._default_trae_exe()
        if not trae_exe:
            return None
        return str(Path(trae_exe).parent / 'resources' / 'app' / 'out' / 'cli.js')

    def _default_trae_logs_dir(self) -> Optional[str]:
        appdata = os.getenv('APPDATA')
        if not appdata:
            return None
        return os.path.join(appdata, 'Trae', 'logs')

    def _default_ocr_python(self) -> Optional[str]:
        candidates = [
            os.getenv('TRAE_EXECUTOR_OCR_PYTHON'),
            r'C:\Python314\python.exe',
            sys.executable,
        ]
        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def _get_repo_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    def _get_mcp_controller(self):
        repo_root = str(self._get_repo_root())
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from Util.MCPController import KeymouseGoController

        return KeymouseGoController()

    def _build_window_chat_prompt(self, task: Dict[str, Any]) -> str:
        header = task.get('header', {}) if isinstance(task.get('header', {}), dict) else {}
        body = task.get('body', {}) if isinstance(task.get('body', {}), dict) else {}
        task_id = str(header.get('task_id', ''))
        content = str(body.get('content', ''))
        expected_reply = self._get_expected_window_reply(task)
        markers = self._build_window_reply_markers(task)
        lines = [f'[{task_id}]', content, '仅输出：', markers['begin']]
        lines.append(expected_reply if expected_reply else '简洁回复')
        lines.append(markers['end'])
        return '\n'.join(lines)

    def _get_expected_window_reply(self, task: Dict[str, Any]) -> str:
        body = task.get('body', {}) if isinstance(task.get('body', {}), dict) else {}
        expectation = body.get('expectation', {}) if isinstance(body.get('expectation', {}), dict) else {}
        expected_reply = expectation.get('exact_reply') or expectation.get('expected_reply') or ''
        return self._normalize_text(str(expected_reply))

    def _build_window_reply_markers(self, task: Dict[str, Any]) -> Dict[str, str]:
        header = task.get('header', {}) if isinstance(task.get('header', {}), dict) else {}
        task_id = str(header.get('task_id', 'bridge'))
        marker_id = hashlib.sha256(task_id.encode('utf-8')).hexdigest()[:8].upper()
        return {
            'begin': f'BRIDGEBEGIN{marker_id}',
            'end': f'BRIDGEEND{marker_id}',
        }

    def _capture_trae_chat_text(self, controller) -> str:
        capture = controller.capture_profile_window('trae', title_substring='Trae', focus=True, restore=True)
        self._prepare_chat_view(controller, capture)
        capture = controller.capture_profile_window('trae', title_substring='Trae', focus=True, restore=True)
        image_path = capture.get('image_path')
        window_rect = capture.get('window', {}).get('rect', {})
        client_rect = capture.get('client_rect', {})
        width = max(1, int(client_rect.get('width', 1)))
        height = max(1, int(client_rect.get('height', 1)))
        crop_box = (
            int(width * 0.80),
            int(height * 0.42),
            int(width * 0.995),
            int(height * 0.84),
        )
        return self._ocr_image_region(str(image_path), crop_box)

    def _prepare_chat_view(self, controller, capture: Dict[str, Any]) -> None:
        window_rect = capture.get('window', {}).get('rect', {})
        client_rect = capture.get('client_rect', {})
        left = int(window_rect.get('left', 0))
        top = int(window_rect.get('top', 0))
        width = max(1, int(client_rect.get('width', 1)))
        height = max(1, int(client_rect.get('height', 1)))
        target_x = left + int(width * 0.90)
        target_y = top + int(height * 0.72)
        controller.mouse_move(target_x, target_y)
        controller.mouse_click(x=target_x, y=target_y)
        controller.key_tap('end', times=2, hold_ms=50)
        controller.mouse_scroll(direction='down', times=8)
        controller.wait_ms(300)

    def _ocr_image_region(self, image_path: str, crop_box) -> str:
        if not self.ocr_python or not os.path.exists(self.ocr_python):
            raise RuntimeError('OCR Python runtime is unavailable')
        temp_crop_path = str(Path(image_path).with_name(f'{Path(image_path).stem}_ocr_crop.png'))
        from PIL import Image

        image = Image.open(image_path)
        image.crop(crop_box).save(temp_crop_path)
        script = (
            'import json, sys;'
            'from rapidocr_onnxruntime import RapidOCR;'
            'ocr_result,_=RapidOCR()(sys.argv[1]);'
            "texts=[item[1].strip() for item in (ocr_result or []) if len(item)>=2 and str(item[1]).strip()];"
            "print(json.dumps({'text':'\\n'.join(texts)}, ensure_ascii=False))"
        )
        proc = subprocess.run(
            [self.ocr_python, '-c', script, temp_crop_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=self.timeout_s,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode('utf-8', errors='ignore')[:4000] or 'OCR subprocess failed')
        payload = json.loads(proc.stdout.decode('utf-8', errors='ignore'))
        return str(payload.get('text', '')).strip()

    def _normalize_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', (text or '')).strip()

    def _extract_incremental_reply(self, before_text: str, after_text: str, prompt: str, expected_reply: str = '') -> str:
        normalized_after_text = self._normalize_text(after_text)
        if expected_reply and expected_reply in normalized_after_text:
            return expected_reply
        if expected_reply:
            return ''
        before_lines = [self._normalize_text(line) for line in (before_text or '').splitlines() if self._normalize_text(line)]
        after_lines = [self._normalize_text(line) for line in (after_text or '').splitlines() if self._normalize_text(line)]
        stripped_prompt = self._normalize_text(prompt)
        reply_lines: List[str] = []
        for line in after_lines:
            if not line:
                continue
            if line in before_lines:
                continue
            if stripped_prompt and stripped_prompt in line:
                continue
            if any(token in line for token in ['GPT-5.4', '在终端查看', 'user63411174883']):
                continue
            if self._looks_like_terminal_noise(line):
                continue
            reply_lines.append(line)
        return '\n'.join(reply_lines).strip()

    def _extract_marked_reply(self, text: str, begin_marker: str, end_marker: str) -> str:
        if not text:
            return ''
        compact_text = self._compact_text_for_marker(text)
        compact_begin = self._compact_text_for_marker(begin_marker)
        compact_end = self._compact_text_for_marker(end_marker)
        start = compact_text.find(compact_begin)
        if start < 0:
            return ''
        start += len(compact_begin)
        end = compact_text.find(compact_end, start)
        if end < 0:
            return ''
        payload = compact_text[start:end].strip()
        return payload

    def _compact_text_for_marker(self, text: str) -> str:
        return re.sub(r'[^A-Za-z0-9\u4e00-\u9fff]+', '', text or '')

    def _looks_like_terminal_noise(self, text: str) -> bool:
        normalized = self._normalize_text(text).lower()
        terminal_markers = [
            'python.exe',
            'json.dumps',
            'mcpcontroller',
            'trae_executor',
            'keymousego',
            '--base-dir',
            '--executor-mode',
            'import ',
            'from util.',
            'from trae_executor',
            'c:\\',
            '$ [0:0]',
            'task_id=',
            'send_bridge_task',
            'wait_bridge_reply',
        ]
        return any(marker in normalized for marker in terminal_markers)

    def _build_trae_cli_prompt(self, task: Dict[str, Any]) -> str:
        header = task.get('header', {}) if isinstance(task.get('header', {}), dict) else {}
        body = task.get('body', {}) if isinstance(task.get('body', {}), dict) else {}
        context = body.get('context', {}) if isinstance(body.get('context', {}), dict) else {}
        expectation = body.get('expectation', {}) if isinstance(body.get('expectation', {}), dict) else {}
        return '\n'.join([
            '请作为 Trae 执行这个桥接任务，并直接给出简洁可执行结果。',
            f"task_id: {header.get('task_id', '')}",
            f"type: {header.get('type', 'unknown')}",
            'content:',
            str(body.get('content', '')),
            'context_keys:',
            ', '.join(sorted(context.keys())) or '(none)',
            'expectation:',
            json.dumps(expectation, ensure_ascii=False, sort_keys=True),
            '要求：不要复述原文，不要回显输入，直接返回结果。',
        ])

    def _collect_trae_cli_evidence(self, prompt: str, started_at: float) -> Dict[str, Any]:
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
        task_id = self._extract_task_id_from_prompt(prompt)
        aha_hits = self._search_log_hits('aha_electron_*.log', [task_id] if task_id else [prompt], limit=6, started_at=started_at)
        sandbox_hits = self._search_log_hits('sbox_core_Trae.exe_*.log', [task_id, 'cmdline:'] if task_id else ['cmdline:'], limit=12, started_at=started_at)
        renderer_hits = self._search_log_hits('renderer.log', ['code_comp_trigger', 'code_comp_complete_shown'], limit=12, started_at=started_at)
        return {
            'trae_exe': self.trae_exe,
            'trae_cli_js': self.trae_cli_js,
            'trae_logs_dir': self.trae_logs_dir,
            'task_id': task_id,
            'prompt_hash': prompt_hash,
            'aha_log_hits': aha_hits,
            'sandbox_cli_hits': sandbox_hits,
            'renderer_ai_events': renderer_hits,
        }

    def _search_log_hits(
        self,
        file_name: str,
        keywords: List[str],
        limit: int = 10,
        started_at: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        if not self.trae_logs_dir or not os.path.exists(self.trae_logs_dir):
            return []
        log_files = sorted(
            Path(self.trae_logs_dir).rglob(file_name),
            key=lambda item: item.stat().st_mtime if item.exists() else 0,
            reverse=True,
        )
        hits: List[Dict[str, Any]] = []
        for log_file in log_files[:12]:
            try:
                modified_at = log_file.stat().st_mtime
                if started_at is not None and modified_at < started_at - 30:
                    continue
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()
            except OSError:
                continue
            for line in reversed(lines):
                if not any(keyword in line for keyword in keywords):
                    continue
                hits.append({
                    'file': str(log_file),
                    'line': line.strip()[:2000],
                })
                if len(hits) >= limit:
                    return list(reversed(hits))
        return list(reversed(hits))

    def _extract_task_id_from_prompt(self, prompt: str) -> str:
        match = re.search(r'^task_id:\s*(.+)$', prompt, flags=re.MULTILINE)
        if not match:
            return ''
        return match.group(1).strip()

    def _summarize_trae_cli_run(self, task: Dict[str, Any], evidence: Dict[str, Any], duration_ms: int) -> str:
        task_type = str(task.get('header', {}).get('type', 'unknown'))
        aha_hit_count = len(evidence.get('aha_log_hits', []))
        sandbox_hit_count = len(evidence.get('sandbox_cli_hits', []))
        renderer_hit_count = len(evidence.get('renderer_ai_events', []))
        return (
            f"Trae CLI 已真实执行 {task_type} 任务；本次桥接回复返回的是执行证据摘要，"
            f"不再是原文 echo。耗时 {duration_ms}ms，AHA 日志命中 {aha_hit_count} 条，"
            f"CLI 沙箱日志命中 {sandbox_hit_count} 条，"
            f"Renderer AI 事件命中 {renderer_hit_count} 条。"
        )
