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

# RUN sh install_chrome_driver.sh

# todo 安装chrome和chromedriver
# https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.59/linux64/chrome-linux64.zip
# https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.59/linux64/chromedriver-linux64.zip

# 安装 Chrome 和 Chromedriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && wget https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.59/linux64/chrome-linux64.zip \
    && wget https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.59/linux64/chromedriver-linux64.zip \
    && unzip chrome-linux64.zip -d /usr/bin \
    && unzip chromedriver-linux64.zip -d /usr/bin \
    && rm chrome-linux64.zip chromedriver-linux64.zip \
    && apt-get remove -y wget unzip \
    && apt-get autoremove -y

ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

USER root

# 暴露端口
# SSE 端口
EXPOSE 18080

# 启动脚本
CMD ["python", "start_mcp_server.py", "--host", "0.0.0.0", "--port", "18080", "--transport", "sse"]