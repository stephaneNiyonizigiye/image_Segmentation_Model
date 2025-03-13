# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5005 for Flask
EXPOSE 5005

# Run the application
CMD ["python", "app.py"]
