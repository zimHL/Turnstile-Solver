# =================================================================
#  阶段 1: 构建器 (Builder)
# =================================================================
FROM python:3.10-slim as builder
ENV DEBIAN_FRONTEND=noninteractive
ARG HTTP_PROXY
ARG HTTPS_PROXY
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y --no-install-recommends git wget libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 libasound2 libatspi2.0-0 libgtk-3-0 libx11-6 libx11-xcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxshmfence1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN git clone https://github.com/Theyka/Turnstile-Solver.git .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir camoufox -i https://pypi.tuna.tsinghua.edu.cn/simple

# =================================================================
#  阶段 2: 最终镜像 (Final Image)
# =================================================================
FROM python:3.10-slim
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y --no-install-recommends libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 libasound2 libatspi2.0-0 libgtk-3-0 libx11-6 libx11-xcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxshmfence1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app .
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
EXPOSE 5000
CMD ["python", "api_solver.py", "--browser_type", "camoufox", "--thread", "10", "--debug", "True", "--headless", "True", "--host", "0.0.0.0", "--useragent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"]
