# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install MLX dependencies for Apple Silicon (ARM64)
RUN if [ "$(uname -m)" = "aarch64" ] || [ "$(uname -m)" = "arm64" ]; then \
        echo "Installing MLX dependencies for ARM64..."; \
        pip install --no-cache-dir mlx-audio || echo "MLX installation failed, continuing..."; \
    else \
        echo "Skipping MLX installation for non-ARM64 architecture"; \
    fi

# Install spaCy English model required by Kokoro
RUN python -m spacy download en_core_web_sm

# Copy application files
COPY app_gradio.py .
COPY script_generator/ ./script_generator/
COPY src/ ./src/
COPY .env .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser

# Create and set permissions for cache directories
RUN mkdir -p /home/appuser/.cache/huggingface && \
    chown -R appuser:appuser /home/appuser/.cache && \
    chown -R appuser:appuser /app

USER appuser

# Expose the port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run the application
CMD ["python", "app_gradio.py"] 