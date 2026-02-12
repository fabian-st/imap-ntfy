FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY database.py .
COPY ntfy.py .

# Create directory for SQLite database
RUN mkdir -p /data

# Run the application
CMD ["python", "-u", "main.py"]
