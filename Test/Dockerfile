# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Use Gunicorn to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"] 