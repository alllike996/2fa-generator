from flask import Flask, render_template_string
import pyotp
import qrcode
import io
import base64

app = Flask(__name__)

# HTML 模板包含在代码中，方便单文件部署
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>谷歌两步验证密钥生成器</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; background-color: #f4f4f9; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        .secret { font-family: monospace; font-size: 24px; color: #333; background: #eee; padding: 10px; border-radius: 5px; word-break: break-all; }
        button { background-color: #007bff; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; margin-top: 20px;}
        button:hover { background-color: #0056b3; }
        .note { color: #666; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Google Authenticator 密钥生成</h2>
        
        <p>扫描下方二维码：</p>
        <img src="data:image/png;base64,{{ qr_data }}" alt="QR Code" />
        
        <p>或手动输入密钥 (32位 Base32)：</p>
        <div class="secret">{{ secret }}</div>
        
        <button onclick="window.location.reload();">刷新生成新的</button>
        
        <div class="note">
            <p>安全提示：本工具仅用于生成随机密钥，服务器不存储任何数据。<br>页面刷新后密钥即丢失。</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # 1. 生成随机的32位 Base32 密钥
    # Google Authenticator 标准通常使用 Base32
    secret_key = pyotp.random_base32(length=32)

    # 2. 生成 otpauth 链接 (用于生成二维码)
    # name: 账户名称 (如 user@example.com)
    # issuer: 发行方 (如 MyService)
    totp = pyotp.TOTP(secret_key)
    provisioning_uri = totp.provisioning_uri(name="RandomUser", issuer_name="KeyGenerator")

    # 3. 生成二维码图片
    qr = qrcode.make(provisioning_uri)
    
    # 4. 将图片转换为 Base64 字符串，以便直接嵌入 HTML
    img_io = io.BytesIO()
    qr.save(img_io, 'PNG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    return render_template_string(HTML_TEMPLATE, secret=secret_key, qr_data=img_base64)

if __name__ == '__main__':
    app.run(debug=True)
