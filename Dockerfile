FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg tesseract-ocr && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/chroma_db /app/static /app/templates /app/transcripts_extracted

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the application
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT}
