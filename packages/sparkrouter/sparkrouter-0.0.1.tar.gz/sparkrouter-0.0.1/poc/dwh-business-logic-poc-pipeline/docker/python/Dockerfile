FROM python:3.11-slim

# Install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Add trusted hosts for pip to bypass SSL verification issues
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Set Python path
ENV PYTHONPATH=/app/src

# Set entrypoint
COPY docker/python/python-submit.sh /app/python-submit.sh
RUN chmod +x /app/python-submit.sh

ENTRYPOINT ["/app/python-submit.sh"]