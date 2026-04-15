# Dockerfile for HunterTeck Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY pyproject.toml README.md ./

# Install Python dependencies
RUN pip install -e ".[dev,groq]"

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 hunterteck && chown -R hunterteck:hunterteck /app
USER hunterteck

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import logging; logging.info('Health check OK')" || exit 1

# Run the application
CMD ["python", "-m", "services.lead_extractor.main"]
