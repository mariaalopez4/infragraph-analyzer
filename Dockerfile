FROM python:3.11-slim

# Prevent Python from writing .pyc files to disk and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package configuration and source directory
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Upgrade pip and install package with all dependencies from pyproject.toml
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Expose default application port
EXPOSE 8000

# Start FastAPI server using Uvicorn
CMD ["uvicorn", "src.infragraph.main:app", "--host", "0.0.0.0", "--port", "8000"]
