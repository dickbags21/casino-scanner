# Development container Dockerfile for Casino Scanner Pro
# Based on Python 3.11 with all development tools

FROM python:3.11-slim

# Set working directory
WORKDIR /workspace

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    git \
    build-essential \
    vim \
    nano \
    htop \
    net-tools \
    iputils-ping \
    dnsutils \
    jq \
    yamllint \
    && rm -rf /var/lib/apt/lists/*

# Install Python development tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install Playwright and browsers (for browser automation)
RUN pip install --no-cache-dir playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install additional development dependencies
RUN pip install --no-cache-dir \
    ipython \
    ipdb \
    pytest \
    pytest-asyncio \
    black \
    flake8 \
    mypy \
    pylint

# Create necessary directories
RUN mkdir -p /workspace/results/screenshots \
    /workspace/results/mobile_apps \
    /workspace/logs \
    /workspace/dist \
    /workspace/alerts \
    /workspace/exploits/templates \
    /workspace/exploits/generated \
    /workspace/nuclei_templates/casino \
    /workspace/wordlists/api

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV PYTHONPATH=/workspace:/workspace/tools

# Make scripts executable
RUN chmod +x /workspace/*.py /workspace/*.sh 2>/dev/null || true

# Default command (can be overridden)
CMD ["/bin/bash"]




