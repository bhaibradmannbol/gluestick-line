# Use a lightweight Python 3.11 base image
# cspell:words uvicorn
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies first (Docker caches this layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend source files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
