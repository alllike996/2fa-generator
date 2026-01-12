from flask import Flask, render_template_string
import pyotp
import qrcode
import io
import base64

app = Flask(__name__)

# ------------------------------------------------------------------------------
# 前端 HTML/CSS/JS 模板
# ------------------------------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2FA 密钥生成器</title>
    <!-- 使用 Emoji 作为网站图标 (Favicon)，无需额外文件 -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🔐</text></svg>">
    
    <style>
        :root {
            --primary-color: #4f46e5;
            --primary-hover: #4338ca;
            --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-gradient);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            color: #333;
        }

        .card {
            background: white;
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 400px;
            width: 90%;
            transition: transform 0.2s;
        }

        h1 {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: #1f2937;
        }

        .qr-container {
            background: #f3f4f6;
            padding: 1rem;
            border-radius: 8px;
            display: inline-block;
            margin-bottom: 1.5rem;
            border: 1px solid #e5e7eb;
        }

        .qr-container img {
            display: block;
            width: 200px;
            height: 200px;
        }

        .label {
            font-size: 0.875rem;
            color: #6b7280;
            margin-bottom: 0.5rem;
            display: block;
        }

        .secret-box {
            display: flex;
            gap: 8px;
            margin-bottom: 1.5rem;
        }

        .secret-input {
            width: 100%;
            padding: 10px 12px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 1rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: #f9fafb;
            color: #374151;
            text-align: center;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 10px 16px;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
            font-size: 0.95rem;
        }

        .btn-copy {
            background-color: #e5e7eb;
            color: #374151;
        }
        .btn-copy:hover { background-color: #d1d5db; }

        .btn-refresh {
            background-color: var(--primary-color);
            color: white;
            width: 100%;
            padding: 12px;
            margin-top: 10px;
        }
        .btn-refresh:hover { background-color: var(--primary-hover); }

        .footer-note {
            margin-top: 1.5rem;
            font-size: 0.75rem;
            color: #9ca3af;
            line-height: 1.4;
        }

        /* 复制成功的提示动画 */
        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 0.875rem;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }
        .toast.show { opacity: 1; }
    </style>
</head>
<body>

    <div class="card">
        <h1>Google 两步验证生成器</h1>

        <span class="label">扫描二维码添加到 App</span>
        <div class="qr-container">
            <img src="data:image/png;base64,{{ qr_data }}" alt="2FA QR Code" />
        </div>

        <span class="label">或手动输入密钥</span>
        <div class="secret-box">
            <input type="text" value="{{ secret }}" readonly class="secret-input" id="secretKey">
            <button class="btn btn-copy" onclick="copySecret()" title="复制密钥">
                📋
            </button>
        </div>

        <button class="btn btn-refresh" onclick="window.location.reload();">
            🔄 生成新的密钥
        </button>

        <div class="footer-note">
            此工具生成的密钥是随机的且不会被存储。<br>
            刷新页面后当前密钥即永久丢失。
        </div>
    </div>

    <div id="toast" class="toast">已复制到剪贴板</div>

    <script>
        function copySecret() {
            var copyText = document.getElementById("secretKey");
            copyText.select();
            copyText.setSelectionRange(0, 99999); // 适配移动端
            
            navigator.clipboard.writeText(copyText.value).then(function() {
                showToast();
            }, function(err) {
                // 如果 clipboard API 失败，尝试传统方法
                document.execCommand('copy');
                showToast();
            });
        }

        function showToast() {
            var toast = document.getElementById("toast");
            toast.classList.add("show");
            setTimeout(function(){ toast.classList.remove("show"); }, 2000);
        }
    </script>
</body>
</html>
"""

# ------------------------------------------------------------------------------
# 后端逻辑
# ------------------------------------------------------------------------------
@app.route('/')
def home():
    # 1. 生成 32 位随机 Base32 密钥
    secret_key = pyotp.random_base32(length=32)

    # 2. 生成 URI
    # 这里将 issuer 改为 generic 的名称，扫描后手机上会显示 "MySecret: <Hash>" 
    # 你可以修改 issuer_name 为你想显示的任何名字
    totp = pyotp.TOTP(secret_key)
    provisioning_uri = totp.provisioning_uri(name="SecretKey", issuer_name="2FA-Tool")

    # 3. 生成二维码
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 4. 转 Base64
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    return render_template_string(HTML_TEMPLATE, secret=secret_key, qr_data=img_base64)

if __name__ == '__main__':
    app.run(debug=True)
