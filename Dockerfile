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
    libnss3 libnspr4 libdbus-1-3 libatk1.0.0 libatk-bridge2.0 libcups2 libxkbcommon0 libx11-6 libxcomposite1 libxcursor1 libxdamage1 libxrandr2 libgbm1 libasound2 \
    && wget https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.59/linux64/chrome-linux64.zip \
    && wget https://storage.googleapis.com/chrome-for-testing-public/142.0.7444.59/linux64/chromedriver-linux64.zip \
    && unzip chrome-linux64.zip -d /usr/bin \
    && unzip chromedriver-linux64.zip -d /usr/bin \
    && rm chrome-linux64.zip chromedriver-linux64.zip \
    && apt-get remove -y wget unzip \
    && apt-get autoremove -y

ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver-linux64/chromedriver

# 安装 Python 依赖chromedriver
RUN pip install --no-cache-dir -r requirements.txt

# 使用 root 用户
USER root

# 暴露端口
# SSE 端口
EXPOSE 18080

# 启动脚本
CMD ["/bin/bash", "start.sh"]