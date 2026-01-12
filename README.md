# Google 2FA Secret Generator (谷歌两步验证密钥生成器)

一个轻量级、无状态的网页工具，用于随机生成适用于 Google Authenticator（谷歌验证器）的 32 位 Base32 密钥及对应的二维码。

本项目基于 Python Flask 框架开发，专为容器化部署（如 Koyeb, Zeabur, Render, Docker）设计。

## ✨ 项目特点

*   **无状态设计 (Stateless)**：服务器不连接数据库，不存储任何生成的密钥。每次刷新页面，密钥均在内存中临时生成，请求结束后立即释放。
*   **双格式输出**：同时提供 32 位文本密钥（Base32）和标准二维码。
*   **现代 UI**：
    *   内置 SVG 图标（无需静态文件）。
    *   响应式卡片设计，适配 PC 和移动端。
    *   一键复制密钥功能。
*   **安全**：核心算法使用 `pyotp` 标准库，配合 HTTPS 部署，确保传输安全。
*   **零依赖文件**：所有逻辑、HTML 模板、CSS 样式均包含在单文件 `app.py` 中，极易维护。

## 🛠️ 技术栈

*   **语言**: Python 3.x
*   **Web 框架**: Flask
*   **核心库**: `pyotp` (生成密钥), `qrcode` (生成二维码)
*   **服务器**: Gunicorn

## 📂 项目结构

```text
.
├── app.py              # 核心代码（包含后端逻辑与前端 HTML/CSS）
├── requirements.txt    # 依赖库列表
├── Procfile            # 生产环境启动命令
└── README.md           # 说明文档
