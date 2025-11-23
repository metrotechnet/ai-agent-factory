FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y ffmpeg tesseract-ocr && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (including chroma_db)
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/templates /app/transcripts_extracted /app/chroma_db

# Make startup script executable
RUN chmod +x startup.sh

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the application with startup script
CMD ["./startup.sh"]
