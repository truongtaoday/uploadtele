# Dockerfile để chạy script trong container
FROM python:3.9-slim

# Cài đặt dependencies hệ thống
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements và cài đặt Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY main.py .
COPY Dragon.txt .

# Tạo thư mục videos
RUN mkdir -p /app/videos

# Thiết lập environment variables (sẽ được override bởi docker run)
ENV TELEGRAM_API_ID=""
ENV TELEGRAM_API_HASH=""
ENV TELEGRAM_BOT_TOKEN=""
ENV TELEGRAM_CHAT_ID=""

# Thiết lập display cho headless browser
ENV DISPLAY=:99

# Chạy script
CMD ["python", "main.py"]
