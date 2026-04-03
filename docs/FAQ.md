# 常见问题

## 1. 双击 exe 没反应怎么办？

- 先确认你下载的是 `ClawMouse-v0.1.0-win.exe`
- 首次运行时，Windows 可能会弹出安全提示
- 如果被系统拦截，可以在属性里解除阻止，或在 Defender 提示中选择允许
- 也可以先用命令行运行 Python 版本，确认依赖和环境没有问题

## 2. 为什么我录制了脚本，但回放效果不对？

- 目标窗口位置、分辨率、缩放比例变化都会影响回放
- 一些操作依赖焦点窗口，回放前请确保目标窗口在正确位置
- 对于非常快的操作，建议适当拉长脚本延迟
- 如果是聊天窗口或特定应用，优先使用窗口画像和 MCP 接口，而不是纯录制回放

## 3. 为什么 MCP 能发送消息，但提取不到回复？

- 当前发送链路相对稳定，但回复提取仍依赖可见聊天区域识别
- 如果 Trae 聊天区没有正确显示，OCR 就可能拿不到新文本
- poller 未运行、窗口未聚焦、区域选错，都会导致提取失败
- 建议先调用 `trae_status`，确认窗口与 poller 状态

## 4. 桌面版 Trae 里的 MCP 配置应该怎么填？

- 如果你的仓库根目录是 `C:\ClawMouse`
- 并且 Python 环境是 `C:\ProgramData\anaconda3\envs\keymousego310\python.exe`
- 那么可直接使用下面这份严格 JSON：

```json
{
  "mcpServers": {
    "clawmouse": {
      "command": "C:\\ProgramData\\anaconda3\\envs\\keymousego310\\python.exe",
      "args": [
        "C:\\ClawMouse\\mcp_server.py"
      ],
      "cwd": "C:\\ClawMouse",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

- 如果你使用桌面版 Trae 的“编辑 MCP 服务”表单，按下面填写即可：
  - 服务名称：`clawmouse`
  - 描述：`clawmouse 桌面控制、截图与聊天消息发送`
  - 传输类型：`标准输入输出 (stdio)`
  - 命令：`C:\ProgramData\anaconda3\envs\keymousego310\python.exe`
  - 参数：`C:\ClawMouse\mcp_server.py`
  - 环境变量：`PYTHONIOENCODING=utf-8`
  - 如果有工作目录字段：填 `C:\ClawMouse`
- 如果 Trae 提示 JSON 格式错误，优先检查：
  - 是否使用了严格 JSON
  - 路径是否写成 `\\`
  - 末尾是否多了逗号
  - 是否把完整对象粘到了 `mcpServers` 内部

## 5. `trae_status` 返回 degraded 是什么意思？

- 说明当前桥接环境不是完全就绪状态
- 常见原因：
  - Trae 窗口没找到
  - poller 没在运行
  - bridge 目录里残留 `.tmp` 或 `.processing.json`
- 这种情况下，建议先恢复环境，再继续委托任务

## 6. bridge poller 没启动怎么办？

- 可直接运行：

```powershell
python .\examples\bridge\trae_task_poller.py --base-dir C:\ClawMouse\ai_bridge --executor-mode window_chat
```

- 如果你只想单次处理一次任务，可以加 `--once`
- 如果启动时出现残留文件问题，先检查 `ai_bridge\tasks` 目录里的 `.tmp` 文件和 `.processing.json`

## 7. 为什么聊天发送有时要“点击后回车”？

- 一些聊天窗口即使已经聚焦，也可能因为编辑器状态、输入法或前端实现导致 Enter 不生效
- 当前仓库已经把这类策略抽象成：
  - `enter_times`
  - `enter_delay_ms`
  - `click_before_enter`
  - `click_before_enter_delay_ms`
- 对 Trae 这类窗口，通常比单纯按一次 Enter 更稳定

## 8. 桌面版 Trae 和网页版 Trae Solo 应该分别用哪个发送工具？

- 桌面版 Trae：优先用 `trae_send_message`
- 网页版 Trae Solo：优先用 `trae_solo_send_message`
- 如果两个窗口同时开着，最好显式区分，不要只靠模糊匹配
- 如果发送不稳定，先检查对应 profile 的输入框比例，而不是直接怀疑 MCP 启动配置

## 9. 如何让普通用户直接使用，不装 Python？

- 直接给他们发布 exe 即可
- 当前推荐使用：
  - `ClawMouse-v0.1.0-win.exe`
- 维护者可参考：
  - `docs/WINDOWS_RELEASE.md`
  - `scripts/build-release.ps1`

## 10. 如何重新打包 exe？

- 在仓库根目录执行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-release.ps1
```

- 默认输出到：

```text
release\ClawMouse-v0.1.0-win.exe
```

## 11. 为什么仓库里看不到 screenshots / ai_bridge / release？

- 这些目录属于运行期产物
- 当前 `.gitignore` 默认会忽略：
  - `screenshots/`
  - `ai_bridge/`
  - `release/`
  - `.venv/`
- 这样做是为了避免把个人环境数据和大体积产物直接提交到仓库

## 12. 我应该用 GUI、MCP 还是 bridge？

- GUI：适合录制 / 回放一段固定桌面操作
- MCP：适合让 AI 直接调用鼠标、键盘、窗口、截图能力
- bridge：适合让另一个本地 AI 通过任务队列继续处理工作

## 13. 如果我要接入自己的 AI Agent，推荐从哪里开始？

- 先看：
  - `README.md`
  - `examples/mcp/mcpServers.example.json`
  - `examples/mcp/lobster.example.json5`
- 如果你的目标是 Trae 风格工作流，优先使用：
  - `trae_status`
  - `trae_delegate`

## 14. 这个项目和原来的 KeymouseGo 是什么关系？

- ClawMouse 在能力设计和代码基础上借鉴并延续了 KeymouseGo 的思路
- 当前仓库是在原有桌面宏与自动化能力上，继续做 MCP、窗口控制、截图和 Trae bridge 方向的整理
- README 中已经补充了借鉴与致谢说明

## 15. 如果 FAQ 还不够，下一步看哪里？

- 如果你已经知道问题大概属于哪一类，但需要更系统地排查，继续看：
  - `docs/TROUBLESHOOTING.md`
