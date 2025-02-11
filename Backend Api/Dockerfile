# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies as root (temporary) to build image layers
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user.
RUN adduser --disabled-password --gecos "" myappuser \
    && chown -R myappuser /app

# Switch to non-root user.
USER myappuser

# Make port 7860 available to the world outside this container
EXPOSE 7860

# Use Gunicorn to run the app
CMD ["gunicorn", "--workers=1", "--bind", "0.0.0.0:7860", "app:app"]
