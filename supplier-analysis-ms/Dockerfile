FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port the app will run on
EXPOSE 8001

# Command to run the application
CMD ["sh", "/app/docker-entrypoint.sh", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
