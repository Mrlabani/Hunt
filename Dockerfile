# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 5000 (or any port your app will use)
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=main.py

# Run the command to start your bot
CMD ["python3", "main.py"]
