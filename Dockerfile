FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
# These libraries are required for mysqlclient compiling, opencv, and general AI capabilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    libx11-6 \
    libxau6 \
    libxdmcp6 \
    wget \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements file first to take advantage of caching
COPY requirements.txt .

# Install packages
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose port (Railway will override this automatically, but good to have)
# Disable TensorFlow oneDNN and set CPU variables to avoid SIGSEGV in restricted VMs
ENV TF_ENABLE_ONEDNN_OPTS=0

EXPOSE 8000

# Run using a single sync worker to prevent C-level thread conflicts in OpenCV/TF/YOLO
CMD ["sh", "-c", "gunicorn dialife.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 300"]
