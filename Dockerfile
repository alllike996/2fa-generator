# 1. 使用官方 Python 轻量级镜像作为基础
FROM python:3.9-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 复制核心代码
COPY app.py .

# 5. 暴露端口 (Gunicorn 默认端口)
EXPOSE 8000

# 6. 启动命令：使用 Gunicorn 运行 Flask
# -w 4: 开启4个工作进程
# -b 0.0.0.0:8000: 绑定到所有IP的8000端口 (Docker 必须)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
