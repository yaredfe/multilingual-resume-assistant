# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies with retry logic
RUN apt-get update --fix-missing || apt-get update --fix-missing || apt-get update --fix-missing
RUN apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set pip configuration for better reliability
ENV PIP_TIMEOUT=300
ENV PIP_RETRIES=3
ENV PIP_DEFAULT_TIMEOUT=300

# Copy requirements first for better caching
COPY requirements-docker.txt .

# Install Python dependencies with better error handling
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install all dependencies from requirements-docker.txt
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy the entire application
COPY . .

# Create static directory
RUN mkdir -p static

# Create data directories
RUN mkdir -p data/resumes data/parsed data/chroma_db data/translated data/match_results data/interview_questions data/model_cache

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Preload sentence transformer models to avoid runtime downloads
RUN python Scripts/preload_models.py

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 