# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for the container to communicate
EXPOSE 8080

# Set environment variable to tell Flask to run in production mode
ENV FLASK_ENV=production

# Command to run the app with Gunicorn, binding it to port 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
