# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy application files
COPY app/ /app/
COPY .env /app/

# Install required Python libraries
RUN pip install --no-cache-dir -r requirements.txt


# Run the application
CMD ["python", "main.py"]

