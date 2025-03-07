FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY order_prj/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY order_prj/ .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=order_prj.settings
ENV DJANGO_ALLOWED_HOSTS=*

EXPOSE 8003

# Run migrations and start server
CMD python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8003 --noreload