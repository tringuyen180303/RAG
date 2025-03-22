# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the current directory contents into the container
COPY ./app  .

COPY ./requirements.txt .

COPY .env /app/.env 
# Install any needed packages specified in requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# Expose port 80 for the FastAPI app
EXPOSE 30000

# Run FastAPI app using Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "30000"]
