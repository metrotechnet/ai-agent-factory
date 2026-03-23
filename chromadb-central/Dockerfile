FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY api/ api/
COPY app.py .
COPY requirements.txt .
COPY chromadb-database/ chromadb-database/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1

# Start the FastAPI app with Uvicorn
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
