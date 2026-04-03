<div align="center">

# ClawMouse

<br>
<img src="Preview.png" width="50%" height="50%" />
<div>
    <img alt="platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blueviolet">
</div>
<div>
    <img alt="license" src="https://img.shields.io/badge/license-MIT-blue.svg">
    <img alt="language" src="https://img.shields.io/badge/python-%3E%3D%203.7-green">
    <img alt="mcp" src="https://img.shields.io/badge/MCP-enabled-brightgreen">
</div>
<br>

[简体中文](README.md) | [English](README_en-US.md)

</div>

ClawMouse is a desktop automation project written in Python. It works both as a traditional macro recorder/replayer and as an MCP-powered automation service that AI agents can call.

For a long-lived Windows setup and public repository maintenance, the recommended project root is:

```text
C:\ClawMouse
```

The suggested first public release is `v0.1.0`, tracked by:

- `VERSION`
- `Changelog.md`
- `RELEASE.md`

## What this repository includes

- Macro recording and replay
- Script execution from GUI and CLI
- Window automation, input automation, and screenshots
- MCP tools for desktop control
- Trae bridge workflow with status/delegate style APIs

## Core entry points

- `KeymouseGo.py`: legacy GUI entry point kept for backward compatibility
- `ClawMouse.py`: recommended branded launcher for GUI and CLI usage
- `mcp_server.py`: MCP server entry point
- `Util/MCPController.py`: main controller for desktop actions, screenshots, profiles, and bridge logic
- `examples/bridge/trae_executor.py`: Trae-facing task executor
- `examples/bridge/trae_task_poller.py`: bridge task poller

## Quick start

### Desktop app

```bash
pip install -r requirements-windows.txt
python ClawMouse.py
```

### MCP server

```bash
pip install -r requirements-mcp.txt
python mcp_server.py
```

### HTTP transport

```bash
python mcp_server.py --transport http --host 127.0.0.1 --port 8000
```

## Windows release build

For a user-friendly Windows single-file build, use the included script:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-release.ps1
```

The default output file is:

```text
release\ClawMouse-v0.1.0-win.exe
```

See `docs/WINDOWS_RELEASE.md` for release and distribution guidance.

## MCP highlights

### Desktop control

- mouse and keyboard input
- window discovery and focus
- in-window clicking and dragging
- text input and send strategies

### Visual automation

- full-window capture
- region capture
- partition map capture
- profile-based screenshot layouts

### Bridge workflow

- `get_bridge_status`
- `send_bridge_task`
- `wait_bridge_reply`
- `read_bridge_reply`

### Trae-style high-level APIs

- `trae_status`
- `trae_delegate`
- `build_trae_bridge_prompt`
- `trae_send_bridge_message`

These APIs reduce the need for callers to manually combine low-level window automation primitives.

## Suggested Trae workflow

1. Call `trae_status`
2. Verify Trae window and poller health
3. Call `trae_delegate(mode='bridge_task')` for queue-based delegation
4. Or call `trae_delegate(mode='window_message')` for direct window delivery
5. Read replies from the bridge queue if needed

## Script format

Scripts are stored in JSON5:

```json5
{
  scripts: [
    {type: "event", event_type: "EM", delay: 3000, action_type: "mouse right down", action: ["0.05208%", "0.1852%"]},
    {type: "event", event_type: "EM", delay: 50, action_type: "mouse right up", action: [-1, -1]},
    {type: "event", event_type: "EK", delay: 1000, action_type: "key down", action: [70, "F", 0]},
    {type: "event", event_type: "EX", delay: 100, action_type: "input", action: "Hello world"}
  ]
}
```

## Open-source cleanup policy

- Runtime artifacts are ignored, including `screenshots/`, `ai_bridge/`, and temporary queue files
- Example configs live under `examples/`
- Higher-level APIs are preferred over fragile low-level call chains

## Contributing

Please see `CONTRIBUTING.md`.

For a system overview, see `docs/ARCHITECTURE.md`.

For release preparation, see:

- `RELEASE.md`
- `docs/WINDOWS_RELEASE.md`
- `docs/REPOSITORY_SETUP.md`
