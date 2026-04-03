# 首发发布说明

当前建议把 ClawMouse 的首个公开版本定义为：

- 版本号：`v0.1.0`
- 推荐根目录：`C:\ClawMouse`

## 当前版本结论

- 这一版已经可以标记为一个很成功的阶段性版本
- 品牌入口、主界面、MCP 接入、Trae / Lobster 工作流、Windows 单文件 exe 已经打通
- GUI 内已经提供 MCP 帮助说明、默认自动启动和显式启停控制
- 当前版本适合作为后续继续扩展“双 Trae 协作”和“手机编程工作流”的稳定基线

## 首发重点

- 保留原有宏录制 / 回放能力
- 补齐 MCP 服务与示例配置
- 提供 Windows 单文件打包脚本与使用说明
- 增加 Trae 风格的高层接口：
  - `trae_status`
  - `trae_delegate`
- 提供 bridge 轮询器与工作流示例
- 补全文档、贡献说明、安全说明和行为准则

## 发布前检查

- 确认 README 与 README_en-US 已更新
- 确认示例路径不包含个人本机绝对路径
- 确认 `.gitignore` 已排除运行期产物
- 确认 `python -m py_compile` 通过
- 确认 `trae_status` 可以正常返回状态

## 建议的 GitHub Release 文案

### 标题

```text
ClawMouse v0.1.0
```

### 简介

```text
ClawMouse 是一个面向桌面自动化的 Python 项目，支持宏录制与回放、MCP 自动化服务，以及面向 Trae 的桥接与委托工作流。
```

### 首发亮点

- 新的品牌化入口 `ClawMouse.py`
- MCP 自动化能力与示例配置
- Windows 单文件发布脚本与文档
- Trae 状态检查与任务委托接口
- bridge 工作流与文档补齐

## 发布后建议

- 补充第一批使用截图或 GIF
- 增加 Windows 环境快速安装说明
- 增加一个最小演示视频或录屏
- 继续清理历史 `KeymouseGo` 命名痕迹

## 下一步计划

- 继续优化主界面布局与细节，包括窗口缩放下的自适应体验和图标呈现
- 增加国内版 / 国际版 Trae 双实例协作的高层路由能力
- 把微信、Lobster、Trae、ClawMouse 截图回传串成更完整的手机编程闭环
- 准备下一个稳定小版本，并补齐对应的 Release 文案、截图和演示材料
