# Windows 发布与使用

这份文档面向两类人：

- 维护者：想把 ClawMouse 打包成 exe 或单文件版本
- 普通用户：想直接下载 exe 使用

## 推荐发布形态

当前最推荐的 Windows 发布形态是：

- 单文件 GUI 程序：`ClawMouse-v0.1.0-win.exe`

这样用户不需要单独安装 Python，就可以直接双击运行。

## 本地打包

仓库已经提供 PowerShell 打包脚本：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-release.ps1
```

默认行为：

- 安装 `requirements-windows.txt`
- 安装 `pyinstaller`
- 清理 `build/` 和 `dist/`
- 用 `ClawMouse.py` 作为入口打单文件包
- 在 `release/` 目录输出最终 exe

默认产物命名：

```text
release\ClawMouse-v0.1.0-win.exe
```

## 自定义参数

可以覆盖 Python 路径、入口脚本和版本号：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-release.ps1 `
  -PythonExe "C:\Python310\python.exe" `
  -EntryScript "ClawMouse.py" `
  -AppName "ClawMouse" `
  -Version "0.1.0"
```

## GitHub Actions 打包

仓库已包含发布工作流：

- `.github/workflows/release.yml`

当前工作流会：

- 在 Windows / Linux / Linux ARM64 / macOS 上打包
- 使用 `ClawMouse.py` 作为入口
- 上传构建产物

如果你只想先把 Windows 版本做好，也可以只保留 Windows job。

## 给普通用户的使用方式

### GUI 使用

1. 下载发布页中的 `ClawMouse-v0.1.0-win.exe`
2. 双击运行
3. 点击 `录制`
4. 执行一遍你的鼠标键盘动作
5. 点击 `结束`
6. 点击 `启动` 回放

### 命令行脚本使用

如果你后续想为用户提供 CLI 版本，也可以保留 Python 方式：

```powershell
python .\ClawMouse.py .\scripts\0402_0814.json5 --runtimes 3
```

### MCP 使用

如果用户要把它接入 AI 或 MCP Host：

```powershell
python .\mcp_server.py
```

## 发布前检查

- `README.md` 与 `README_en-US.md` 已更新
- `VERSION` 与 `Changelog.md` 已更新
- `RELEASE.md` 已准备好
- `python -m py_compile` 通过
- `.gitignore` 已排除运行期产物
- 示例配置不含你的个人绝对路径

## 建议上传到 GitHub Release 的内容

- `ClawMouse-v0.1.0-win.exe`
- README 截图或 GIF
- 首发说明摘要

## 给用户的一句话说明

```text
下载 exe 后直接双击运行；如果要接入 AI 或 MCP，再按 README 启动 mcp_server.py。
```
