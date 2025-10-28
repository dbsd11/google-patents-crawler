cat > /etc/apt/sources.list << EOF 
deb https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
# deb-src https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
# deb-src https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
# deb-src https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-proposed main restricted universe multiverse
# deb-src https://mirrors.aliyun.com/ubuntu/ jammy-proposed main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
# deb-src https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
EOF

# Import Ubuntu archive signing key to fix GPG error
apt-get update --allow-insecure-repositories
apt-get install -y --allow-unauthenticated ubuntu-keyring
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C

apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

whereis chromedriver && \
    CHROMEDRIVER_PATH=$(whereis chromedriver | awk '{print $2}') && \
    echo "ChromeDriver found at: $CHROMEDRIVER_PATH"