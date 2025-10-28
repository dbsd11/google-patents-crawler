# Google Patents Crawler MCP Server Docker Image
# 基于 Python 3.11 构建

FROM --platform=amd64 python:3.11.14-bookworm

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 复制项目文件
COPY . .

RUN sh install_chrome_driver.sh

ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建非 root 用户
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# 暴露端口
# SSE 端口
EXPOSE 18080

# 启动脚本
CMD ["/app/set_chromedriver_env.sh", "python", "start_mcp_server.py", "--host", "0.0.0.0", "--port", "18080", "--transport", "sse"]