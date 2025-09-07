# Gitpod Dockerfile for AI Investment Research Assistant
FROM gitpod/workspace-python-3.11

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    python3-tk \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to gitpod user
USER gitpod

# Install Python packages globally available in Gitpod
RUN pip install --user \
    pandas>=2.0.0 \
    numpy>=1.24.0 \
    matplotlib>=3.7.0 \
    seaborn>=0.12.0 \
    yfinance>=0.2.20 \
    reportlab>=4.0.0 \
    python-pptx>=0.6.21 \
    requests>=2.31.0 \
    scipy>=1.10.0 \
    plotly>=5.15.0 \
    streamlit>=1.28.0 \
    jupyter

# Set matplotlib backend for headless environment
ENV MPLBACKEND=Agg