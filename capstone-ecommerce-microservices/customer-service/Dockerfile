FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY ./customer_prj /app/

# Add environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=customer_prj.settings
ENV DJANGO_ALLOWED_HOSTS=*

EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001", "--noreload"]