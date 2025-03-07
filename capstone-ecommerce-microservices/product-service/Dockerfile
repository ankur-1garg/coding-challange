FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY product_prj/ .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=product_prj.settings
ENV DJANGO_ALLOWED_HOSTS=*

EXPOSE 8002

# Run migrations and start server
CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8002 --noreload
