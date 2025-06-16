FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy quantum chemistry code
COPY my_hf_program /app/my_hf_program

# Copy API server code
COPY deployment/api_server /app/api_server

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/api_server/requirements.txt

# Set environment variables
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Expose port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "api_server.api:app", "--host", "0.0.0.0", "--port", "8000"]
