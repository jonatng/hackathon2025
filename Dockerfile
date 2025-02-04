# Use the official Python image from the Docker Hub
FROM python:3.9-slim
# Set the working directory
WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Make port 8080 available to the world outside this container
EXPOSE 8080
# Run app.py when the container launches
CMD ["python", "app.py"]
# Example of setting an environment variable in Dockerfile
ENV HF_TOKEN=your_hugging_face_token 