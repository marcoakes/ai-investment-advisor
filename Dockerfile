# AI Investment Advisor - Production Docker Image
# Multi-stage build for optimized production deployment

# ===============================================
# Stage 1: Base Python Environment
# ===============================================
FROM python:3.9-slim as base

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for financial libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    pkg-config \
    libta-lib0-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# ===============================================
# Stage 2: Dependencies Installation
# ===============================================
FROM base as dependencies

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with pinned versions
RUN pip install --upgrade pip==23.2.1 && \
    pip install --no-cache-dir -r requirements.txt

# ===============================================  
# Stage 3: Production Image
# ===============================================
FROM dependencies as production

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application files
COPY . .
COPY .env.example .env.example

# Set proper permissions
RUN chown -R appuser:appuser /app
USER appuser

# Create directories for data and outputs
RUN mkdir -p /app/data /app/outputs /app/logs

# ===============================================
# Health Check
# ===============================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import yfinance; print('Health check passed')" || exit 1

# ===============================================
# Jupyter Configuration
# ===============================================
# Generate Jupyter config
RUN jupyter notebook --generate-config

# Configure Jupyter for container environment
RUN echo "c.NotebookApp.ip = '0.0.0.0'" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 8888" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_root = False" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.password = ''" >> ~/.jupyter/jupyter_notebook_config.py

# ===============================================
# Expose Ports
# ===============================================
EXPOSE 8888

# ===============================================
# Container Entry Point
# ===============================================
# Default command starts Jupyter notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

# ===============================================
# Build Instructions
# ===============================================
# 
# Build the image:
#   docker build -t ai-investment-advisor .
#
# Run with volume mounting for data persistence:
#   docker run -p 8888:8888 -v $(pwd)/data:/app/data ai-investment-advisor
#
# Run with environment file:
#   docker run -p 8888:8888 --env-file .env ai-investment-advisor
#
# Run interactive bash session:
#   docker run -it ai-investment-advisor bash
#
# Production deployment:
#   docker run -d -p 8888:8888 --restart=unless-stopped \
#              --env-file .env \
#              -v $(pwd)/data:/app/data \
#              -v $(pwd)/logs:/app/logs \
#              ai-investment-advisor
#
# ===============================================