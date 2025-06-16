FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy quantum chemistry code
COPY my_hf_program /app/my_hf_program

# Copy streamlit app
COPY deployment/streamlit_app.py /app/streamlit/app.py
COPY deployment/streamlit_requirements.txt /app/streamlit/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/streamlit/requirements.txt

# Set environment variables
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Expose port
EXPOSE 8501

# Run the streamlit app
CMD ["streamlit", "run", "/app/streamlit/app.py"]
