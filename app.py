from flask import Flask, render_template_string, request
import pyotp
import qrcode
import io
import base64

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2FA 密钥生成器</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🔐</text></svg>">

    <style>
        :root {
            --primary-color: #4f46e5;
            --primary-hover: #4338ca;
            --secondary-color: #10b981;
            --secondary-hover: #059669;
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
            max-width: 420px;
            width: 90%;
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
            width: 220px;
            height: 220px;
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
            margin-bottom: 1rem;
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
            box-sizing: border-box;
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
            text-decoration: none;
        }

        .btn-copy {
            background-color: #e5e7eb;
            color: #374151;
        }
        .btn-copy:hover {
            background-color: #d1d5db;
        }

        .btn-primary {
            background-color: var(--primary-color);
            color: white;
            width: 100%;
            padding: 12px;
            margin-top: 8px;
        }
        .btn-primary:hover {
            background-color: var(--primary-hover);
        }

        .btn-secondary {
            background-color: var(--secondary-color);
            color: white;
            width: 100%;
            padding: 12px;
            margin-top: 10px;
        }
        .btn-secondary:hover {
            background-color: var(--secondary-hover);
        }

        .error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
            padding: 10px 12px;
            border-radius: 8px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }

        .footer-note {
            margin-top: 1.5rem;
            font-size: 0.75rem;
            color: #9ca3af;
            line-height: 1.4;
        }

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
        .toast.show {
            opacity: 1;
        }
    </style>
</head>
<body>

    <div class="card">
        <h1>Google 两步验证生成器</h1>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}

        <span class="label">扫描二维码添加到 App</span>
        <div class="qr-container">
            <img src="data:image/png;base64,{{ qr_data }}" alt="2FA QR Code" />
        </div>

        <form method="POST">
            <span class="label">可手动修改密钥后重新生成</span>
            <div class="secret-box">
                <input
                    type="text"
                    name="secret"
                    value="{{ secret }}"
                    class="secret-input"
                    id="secretKey"
                    placeholder="请输入 Base32 密钥"
                    autocomplete="off"
                    spellcheck="false"
                >
                <button type="button" class="btn btn-copy" onclick="copySecret()" title="复制密钥">📋</button>
            </div>

            <button type="submit" class="btn btn-primary">
                根据当前密钥重新生成二维码
            </button>
        </form>

        <button class="btn btn-secondary" onclick="window.location.href='/'">
            🔄 随机生成新密钥
        </button>

        <div class="footer-note">
            首次打开页面会随机生成一个密钥；<br>
            你也可以手动修改后，再重新生成对应二维码。
        </div>
    </div>

    <div id="toast" class="toast">已复制到剪贴板</div>

    <script>
        function copySecret() {
            var copyText = document.getElementById("secretKey");
            navigator.clipboard.writeText(copyText.value).then(function() {
                showToast();
            }).catch(function() {
                copyText.select();
                copyText.setSelectionRange(0, 99999);
                document.execCommand('copy');
                showToast();
            });
        }

        function showToast() {
            var toast = document.getElementById("toast");
            toast.classList.add("show");
            setTimeout(function() {
                toast.classList.remove("show");
            }, 2000);
        }
    </script>
</body>
</html>
"""


def make_qr_base64(data: str) -> str:
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode("utf-8")


@app.route("/", methods=["GET", "POST"])
def home():
    error = None

    if request.method == "POST":
        secret_key = request.form.get("secret", "").strip().replace(" ", "").upper()

        if not secret_key:
            secret_key = pyotp.random_base32(length=32)

        try:
            totp = pyotp.TOTP(secret_key)
            provisioning_uri = totp.provisioning_uri(
                name="SecretKey",
                issuer_name="2FA-Tool"
            )
        except Exception:
            error = "密钥格式无效，请输入正确的 Base32 密钥。"
            secret_key = pyotp.random_base32(length=32)
            totp = pyotp.TOTP(secret_key)
            provisioning_uri = totp.provisioning_uri(
                name="SecretKey",
                issuer_name="2FA-Tool"
            )
    else:
        secret_key = pyotp.random_base32(length=32)
        totp = pyotp.TOTP(secret_key)
        provisioning_uri = totp.provisioning_uri(
            name="SecretKey",
            issuer_name="2FA-Tool"
        )

    img_base64 = make_qr_base64(provisioning_uri)

    return render_template_string(
        HTML_TEMPLATE,
        secret=secret_key,
        qr_data=img_base64,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
