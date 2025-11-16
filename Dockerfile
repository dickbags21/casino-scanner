FROM python:3.11-slim

# Set working directory
WORKDIR /casino_scanner

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and browsers
RUN pip install --no-cache-dir playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p results/screenshots results/mobile_apps logs dist dashboard

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Make scripts executable
RUN chmod +x casino_scanner.py quick_casino_hunt.py gambling_app_discovery.py \
    get_shodan_key.py test_vietnam_live.py setup_casino_scanner.sh

# Initialize dashboard database
RUN python3 -c "from dashboard.database import get_db; get_db().init_db()" || true

# Default command
CMD ["python3", "casino_scanner.py"]



