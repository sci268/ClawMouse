import argparse
import hashlib
import json
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from trae_executor import TraeTaskExecutor

DEFAULT_BASE_DIR = str(Path(__file__).resolve().parents[2] / 'ai_bridge')


class TraeTaskPoller:
    def __init__(self, base_dir: str = DEFAULT_BASE_DIR, executor: Optional[TraeTaskExecutor] = None):
        self.base_dir = Path(base_dir)
        self.tasks_dir = self.base_dir / 'tasks'
        self.replies_dir = self.base_dir / 'replies'
        self.archive_tasks_dir = self.base_dir / 'archive' / 'tasks'
        self.archive_replies_dir = self.base_dir / 'archive' / 'replies'
        self.executor = executor or TraeTaskExecutor.from_env()
        for directory in [
            self.base_dir,
            self.tasks_dir,
            self.replies_dir,
            self.archive_tasks_dir,
            self.archive_replies_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def run_forever(self, initial_poll_ms: int = 200, max_poll_ms: int = 2000):
        poll_ms = max(50, int(initial_poll_ms))
        poll_ms_limit = max(poll_ms, int(max_poll_ms))
        while True:
            handled = self.run_once()
            if handled:
                poll_ms = max(50, int(initial_poll_ms))
            else:
                time.sleep(poll_ms / 1000.0)
                poll_ms = min(poll_ms_limit, max(poll_ms + 1, int(poll_ms * 2.5)))

    def run_once(self) -> bool:
        task_file = self._find_pending_task()
        if task_file is None:
            return False
        processing_file = self._claim_task(task_file)
        task = self._read_json(processing_file)
        try:
            result = self.handle_task(task)
            self._write_reply(task, result=result, status='success', error=None)
        except Exception as exc:
            self._write_reply(task, result=None, status='error', error=str(exc))
        self._archive_task(processing_file)
        return True

    def handle_task(self, task: Dict[str, Any]) -> Any:
        return self.executor.execute(task)

    def _find_pending_task(self) -> Optional[Path]:
        for file_path in sorted(self.tasks_dir.glob('*.json')):
            if file_path.name.endswith('.processing.json'):
                continue
            return file_path
        return None

    def _claim_task(self, file_path: Path) -> Path:
        processing_file = file_path.with_name(file_path.stem + '.processing.json')
        os.replace(file_path, processing_file)
        payload = self._read_json(processing_file)
        header = payload.setdefault('header', {})
        header['status'] = 'processing'
        header['claimed_at'] = time.time()
        header['checksum'] = self._checksum(payload)
        self._write_json_atomic(processing_file, payload)
        return processing_file

    def _write_reply(self, task: Dict[str, Any], result: Any, status: str, error: Optional[str]):
        task_id = task['header']['task_id']
        reply = {
            'header': {
                'protocol_version': '1.0',
                'from': 'Trae',
                'to': task['header'].get('from', 'LobsterAI'),
                'task_id': task_id,
                'timestamp': time.time(),
                'status': status,
            },
            'body': {
                'result': result,
                'error': error,
            },
        }
        reply['header']['checksum'] = self._checksum(reply)
        reply_file = self.replies_dir / f'{task_id}.json'
        self._write_json_atomic(reply_file, reply)

    def _archive_task(self, processing_file: Path):
        target = self.archive_tasks_dir / processing_file.name.replace('.processing.json', '.done.json')
        self._move_unique(processing_file, target)

    def _write_json_atomic(self, file_path: Path, payload: Dict[str, Any]):
        temp_path = file_path.with_name(f'{file_path.name}.{uuid.uuid4().hex}.tmp')
        with open(temp_path, 'w', encoding='utf-8') as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, file_path)

    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _checksum(self, payload: Dict[str, Any]) -> str:
        payload_copy = json.loads(json.dumps(payload, ensure_ascii=False))
        header = payload_copy.get('header', {})
        if isinstance(header, dict):
            header.pop('checksum', None)
        canonical = json.dumps(payload_copy, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"

    def _move_unique(self, source_path: Path, target_path: Path):
        if target_path.exists():
            target_path = target_path.with_name(f'{target_path.stem}_{uuid.uuid4().hex[:8]}{target_path.suffix}')
        shutil.move(str(source_path), str(target_path))


def build_executor_from_args(args: argparse.Namespace) -> TraeTaskExecutor:
    env_executor = TraeTaskExecutor.from_env()
    return TraeTaskExecutor(
        mode=args.executor_mode or env_executor.mode,
        http_endpoint=args.http_endpoint or env_executor.http_endpoint,
        http_headers_json=args.http_headers_json or env_executor.http_headers_json,
        external_command=args.external_command or env_executor.external_command,
        external_args_json=args.external_args_json or env_executor.external_args_json,
        trae_exe=args.trae_exe or env_executor.trae_exe,
        trae_cli_js=args.trae_cli_js or env_executor.trae_cli_js,
        trae_logs_dir=args.trae_logs_dir or env_executor.trae_logs_dir,
        timeout_s=args.timeout_s or env_executor.timeout_s,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-dir', default=DEFAULT_BASE_DIR)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--initial-poll-ms', type=int, default=200)
    parser.add_argument('--max-poll-ms', type=int, default=2000)
    parser.add_argument('--executor-mode')
    parser.add_argument('--http-endpoint')
    parser.add_argument('--http-headers-json')
    parser.add_argument('--external-command')
    parser.add_argument('--external-args-json')
    parser.add_argument('--trae-exe')
    parser.add_argument('--trae-cli-js')
    parser.add_argument('--trae-logs-dir')
    parser.add_argument('--timeout-s', type=int)
    args = parser.parse_args()
    poller = TraeTaskPoller(args.base_dir, executor=build_executor_from_args(args))
    if args.once:
        handled = poller.run_once()
        print(json.dumps({'handled': handled}, ensure_ascii=False))
    else:
        poller.run_forever(args.initial_poll_ms, args.max_poll_ms)


if __name__ == '__main__':
    main()
