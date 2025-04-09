# Use the slim Python 3.11 image as the base image
FROM python:3.11

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file first for efficient Docker caching
COPY requirements.txt .

# Install the dependencies from requirements.txt with no cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Expose port 8080; production environments typically use this port
EXPOSE 8080

# Run the FastAPI application with uvicorn, listening on all interfaces at port 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
