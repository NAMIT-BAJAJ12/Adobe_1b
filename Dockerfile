FROM python:3.9

WORKDIR /app

COPY . /app

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

# Upgrade pip separately
RUN pip install --upgrade pip

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
