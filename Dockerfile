# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install build dependencies for uWSGI
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies and uWSGI
RUN pip install --no-cache-dir -r requirements.txt uwsgi

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run uWSGI with improved configuration
CMD ["uwsgi", \
    "--http", "0.0.0.0:8080", \
    "--wsgi-file", "app.py", \
    "--callable", "app", \
    "--master", \
    "--enable-threads", \
    "--processes", "2", \
    "--threads", "2", \
    "--buffer-size", "32768", \
    "--log-5xx", \
    "--log-4xx", \
    "--log-slow", \
    "--log-date", \
    "--log-x-forwarded-for"]