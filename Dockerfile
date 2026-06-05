# Use official lightweight Python image
FROM python:3.11-slim

# Set environment variable to avoid buffered outputs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in container
WORKDIR /app

# Install system dependencies (needed for ReportLab and imaging if necessary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to utilize Docker build cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Configure Streamlit run flags
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
