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

## 🚀 部署流程 (Koyeb 示例)

本项目已配置好，非常适合在 [Koyeb](https://www.koyeb.com/) 上进行免费部署。

### 1. 准备代码

确保你的 GitHub 仓库中包含以下三个关键文件：

*   `app.py`
*   `requirements.txt`
*   `Procfile` (内容为: `web: gunicorn app:app`)

### 2. 在 Koyeb 上创建应用

1.  登录 Koyeb 控制台，点击 **Create App**。
2.  选择 **GitHub** 作为部署源。
3.  搜索并选中本项目仓库。
4.  **Builder Settings**:
    *   Koyeb 通常会自动识别为 Python 项目。
    *   如果没有，手动选择 **Python**。
5.  **Run Command**:
    *   如果仓库里有 `Procfile`，留空即可（自动读取）。
    *   如果没有，请在 **Override** 处填写：`gunicorn app:app`
6.  点击 **Deploy**。

等待几分钟，当状态变为 **Healthy**，点击分配的域名（例如 `https://xyz.koyeb.app`）即可使用。

## 💻 本地运行

如果你想在本地电脑上运行：

1.  克隆仓库：
    ```bash
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    ```

2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

3.  运行：
    ```bash
    python app.py
    ```

4.  打开浏览器访问 `http://127.0.0.1:5000`

## ⚠️ 安全免责声明

本工具仅用于生成随机密钥方便测试或自用配置。

*   **服务器不存储**：所有的密钥生成都在内存中进行，页面刷新即销毁。
*   **传输安全**：请务必在支持 **HTTPS** 的环境下使用（Koyeb 默认提供 HTTPS），以防止密钥在网络传输中被拦截。
