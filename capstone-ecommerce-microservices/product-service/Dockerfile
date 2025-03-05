# Use Python 3.11 slim image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files to the correct location
COPY ./product_prj /app/

# Add environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=product_prj.settings
ENV DJANGO_ALLOWED_HOSTS=*

# Expose port
EXPOSE 8002

# Start command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002", "--noreload"]
