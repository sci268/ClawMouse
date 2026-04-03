# GitHub 仓库初始化建议

在把 `C:\ClawMouse` 推到你自己的 GitHub 仓库前，建议先完成下面这些设置。

## 仓库基础信息

### 推荐仓库名

```text
ClawMouse
```

### 推荐简介

```text
Desktop automation, MCP tools, screenshots, window control, and Trae bridge workflows for AI-assisted desktop operation.
```

### 推荐 Topics

```text
desktop-automation
mcp
python
gui-automation
windows
pyinstaller
trae
openclaw
```

## 首发版本

- 版本号：`v0.1.0`
- 根目录：`C:\ClawMouse`

## 建议你在创建仓库后立即检查的文件

- `README.md`
- `README_en-US.md`
- `RELEASE.md`
- `VERSION`
- `Changelog.md`
- `.github/workflows/release.yml`

## 当前仓库地址

当前默认按下面这个仓库地址整理：

```text
https://github.com/sci268/ClawMouse
```

## 推荐的首个提交与首发流程

```bash
cd C:\ClawMouse
git init
git add .
git commit -m "chore: prepare ClawMouse v0.1.0 release"
git branch -M main
git remote add origin https://github.com/sci268/ClawMouse.git
git push -u origin main
```

然后：

1. 创建 `v0.1.0` tag
2. 根据 `RELEASE.md` 填写 Release 文案
3. 上传 exe 或等待 GitHub Actions 构建产物

## 建议的首发 release 附件

- `ClawMouse-v0.1.0-win.exe`
- 一张主界面截图
- 一张 MCP / bridge 使用说明截图

## 发布后建议

- 增加 GIF 演示
- 增加 FAQ
- 继续清理历史 `KeymouseGo` 命名痕迹
- 增加更完整的 Windows 安装与权限说明
