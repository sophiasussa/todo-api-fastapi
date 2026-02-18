# Use a lightweight official Python image to reduce the final image size
FROM python:3.11-slim

# Set the working directory inside the container
# All application files will live under this path
WORKDIR /app

# Copy dependency definitions first to leverage Docker layer caching
# This avoids reinstalling dependencies when only source code changes
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces image size by not storing pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY . .

# Start the FastAPI application using Uvicorn
# The server listens on all interfaces to allow external access
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
