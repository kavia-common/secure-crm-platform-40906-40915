# Use a lightweight official Python base image
FROM python:3.11-slim

# Ensure Python output is unbuffered and no .pyc files are written
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install runtime dependencies first to leverage Docker layer caching
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy application source code
COPY . /app

# Expose the service port
EXPOSE 3001

# Default environment (can be overridden at runtime)
ENV APP_HOST=0.0.0.0 \
    APP_PORT=3001

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
