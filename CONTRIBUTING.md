# 贡献指南

感谢你关注 ClawMouse。

这个仓库当前同时承载三类能力：

- 桌面宏录制与回放
- MCP 自动化服务
- Trae / Lobster / OpenClaw 风格桥接

为了让仓库长期可维护，提交变更时请尽量遵循下面的约定。

## 建议提交流程

- 先开 Issue，描述问题、使用场景和预期行为
- 功能较大时先说明设计方向，再开始实现
- 提交前至少做一次本地编译或最小冒烟验证
- 尽量把“功能改动”和“纯格式整理”拆开提交

## 仓库约定

### 目录职责

- `KeymouseGo.py`：GUI 入口
- `mcp_server.py`：MCP 服务入口
- `Util/MCPController.py`：窗口、输入、截图、桥接的核心控制器
- `examples/bridge/`：Trae 桥接轮询器与示例工作流
- `examples/mcp/`：MCP Host 示例配置

### 运行时数据

以下内容属于运行期产物，不建议提交：

- `screenshots/`
- `ai_bridge/`
- `ai_bridge_*`
- `*.tmp`

### 配置原则

- 示例配置写成可移植占位形式，不要提交你的本机绝对路径
- 路径示例优先使用 `C:/path/to/ClawMouse` 这类中性表达
- 新增 profile 或 bridge 配置时，优先补充到 `examples/` 和 README

## 代码风格

- 保持与现有文件一致的命名和结构
- 优先扩展现有控制器和工具，而不是平行再造一套
- 面向上层调用时，优先补高层接口，例如 `trae_status`、`trae_delegate`
- 面向底层行为时，再扩展具体鼠标、键盘、窗口、截图能力

## 文档要求

如果改动影响到以下任一项，请同步更新文档：

- MCP 工具名称或参数
- 桥接工作流
- 示例配置
- 运行方式
- 仓库结构

至少检查：

- `README.md`
- `README_en-US.md`
- `examples/bridge/lobster_bridge_workflow.md`
- `examples/mcp/`

## 最小校验

Python 改动提交前建议至少执行：

```bash
python -m py_compile Util/MCPController.py mcp_server.py examples/bridge/trae_executor.py examples/bridge/trae_task_poller.py
```

如果你改的是桥接接口，建议额外做一次最小调用验证：

- `trae_status`
- `trae_delegate`

## 优先欢迎的方向

- 回复提取稳定性
- bridge 队列自愈能力
- Windows / macOS / Linux 兼容性
- MCP 文档与示例完善
- Trae / OpenClaw 风格集成
