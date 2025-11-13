FROM python:3.11-slim-bookworm

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py ./

# Create config directory with proper permissions
RUN mkdir -p /root/.hue && chmod 700 /root/.hue

# Expose default daemon port
EXPOSE 8080

# Run daemon with 0.0.0.0 to accept connections from any interface
CMD ["python3", "daemon.py", "--host", "0.0.0.0", "--port", "8080"]
