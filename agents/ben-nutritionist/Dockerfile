FROM python:3.11-slim

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8080

# Run main FastAPI application
CMD ["sh", "-c", "uvicorn app_main:app --host 0.0.0.0 --port ${PORT:-8080}"]
