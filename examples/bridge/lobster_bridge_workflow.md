## Lobster 侧完整桥接工作流示例（ClawMouse 文件桥接）

这个工作流的目标是：Lobster 不再依赖“往 Trae 窗口输入框发消息”，而是通过 ClawMouse 的 MCP 工具写入任务文件、等待回复文件，实现稳定的异步协作。

文中所有 `C:/path/to/ClawMouse` 都应替换为你自己的本地仓库目录。

### 0. 前置条件

- Lobster 已配置并启用 `clawmouse` MCP Server。
- Trae 侧已启动轮询器（任选其一）：
  - 单次处理：`python examples/bridge/trae_task_poller.py --base-dir C:/path/to/ClawMouse/ai_bridge --executor-mode trae_cli --once`
  - 持续轮询：`python examples/bridge/trae_task_poller.py --base-dir C:/path/to/ClawMouse/ai_bridge --executor-mode trae_cli`
- Trae 侧真实执行器位于 `examples/bridge/trae_executor.py`，轮询器会优先读取以下环境变量：
  - `TRAE_EXECUTOR_MODE=auto|trae_cli|rules|http|external`
  - `TRAE_EXECUTOR_HTTP_ENDPOINT`
  - `TRAE_EXECUTOR_HTTP_HEADERS_JSON`
  - `TRAE_EXECUTOR_COMMAND`
  - `TRAE_EXECUTOR_ARGS_JSON`
  - `TRAE_EXECUTOR_TRAE_EXE`
  - `TRAE_EXECUTOR_TRAE_CLI_JS`
  - `TRAE_EXECUTOR_TRAE_LOGS_DIR`
  - `TRAE_EXECUTOR_TIMEOUT_S`

### 0.1 执行器模式说明

- `auto`
  - 轮询器默认模式
  - 优先接入本机 Trae CLI，找不到 CLI 才回退到 `rules`
- `trae_cli`
  - 直接调用本机 `Trae.exe ... cli.js chat ...`
  - 会把 Trae 日志命中情况作为桥接执行证据返回
- `rules`
  - 不再回显 chat 文本，而是返回结构化结果
  - 适合先验证桥接协议、Host 解析与任务流转
- `http`
  - 把整个 task JSON POST 到指定 HTTP 端点
  - 适合 Trae 暴露本地 HTTP/服务端执行入口
- `external`
  - 把整个 task JSON 通过 stdin 交给外部命令处理，并从 stdout 读取 JSON 结果
  - 适合 Trae 有 CLI/本地脚本入口时接入

### 1. 检查桥接目录状态

在 Lobster 中调用：

- `get_bridge_status(base_dir="C:/path/to/ClawMouse/ai_bridge")`

你应能看到 `tasks/replies/archive` 的目录路径与当前计数。

### 2. 发送任务（Lobster -> Trae）

在 Lobster 中调用：

- `send_bridge_task(task_type="chat", content="请确认你已接管 bridge 任务，并返回一句简短结论", task_id="test-001", base_dir="C:/path/to/ClawMouse/ai_bridge")`

返回值里会包含：
- `task_id`
- `task_file`

### 3. 等待回复（Trae -> Lobster）

在 Lobster 中调用：

- `wait_bridge_reply(task_id="test-001", timeout_s=120, base_dir="C:/path/to/ClawMouse/ai_bridge")`

成功后返回 `reply`，其中包含：
- `reply.header.status`
- `reply.body.result`

### 4. code_review 任务示例（带上下文）

在 Lobster 中调用：

- `send_bridge_task(task_type="code_review", content="请审查 bridge 轮询器实现", task_id="review-001", context={ "examples/bridge/trae_task_poller.py": "C:/path/to/ClawMouse/examples/bridge/trae_task_poller.py" }, base_dir="C:/path/to/ClawMouse/ai_bridge")`

然后调用：

- `wait_bridge_reply(task_id="review-001", timeout_s=120, base_dir="C:/path/to/ClawMouse/ai_bridge")`

### 5. 领取与归档（可选）

如果你希望 Trae 侧手动领取任务，也可以在 Trae 侧调用：
- `claim_bridge_task(task_id="...", base_dir="C:/path/to/ClawMouse/ai_bridge")`

任务完成后可在任意侧归档：
- `archive_bridge_task(task_id="...", base_dir="C:/path/to/ClawMouse/ai_bridge")`

### 6. 失败处理建议

- 回复超时：
  - 先调用 `get_bridge_status` 确认目录中 `replies` 是否增长
  - 再调用 `list_bridge_tasks` 检查是否存在仍为 `pending/processing` 的任务
- 仅当文件桥接不可用时，才退回窗口链路：
  - `capture_profile_window(profile_name="trae")`
  - `trae_send_message(...)`
