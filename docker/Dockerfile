# Use Python 3.11 slim base image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for XML processing and graphviz
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    graphviz \
    graphviz-dev \
    pkg-config \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY config/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Make the entry point script executable while still root
RUN chmod +x /app/docker/docker-entrypoint.sh

# Create a non-root user for security
RUN useradd -m -u 1000 xsduser && \
    chown -R xsduser:xsduser /app

USER xsduser

# Set Python path to include src directory
ENV PYTHONPATH=/app:/app/src

# Set the entrypoint
ENTRYPOINT ["/app/docker/docker-entrypoint.sh"]
