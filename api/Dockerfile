# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pip dependencies early to leverage caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your application code
COPY . .

ARG BRIA_API_TOKEN
ARG STORAGE_SERVICE_ACCOUNT_KEY_PATH
ARG VERTEXAI_SERVICE_ACCOUNT_KEY_PATH
ARG MONGO_URI
ARG MONGO_DB_NAME

ENV BRIA_API_TOKEN=$BRIA_API_TOKEN
ENV STORAGE_SERVICE_ACCOUNT_KEY_PATH=$STORAGE_SERVICE_ACCOUNT_KEY_PATH
ENV VERTEXAI_SERVICE_ACCOUNT_KEY_PATH=$VERTEXAI_SERVICE_ACCOUNT_KEY_PATH
ENV MONGO_URI=$MONGO_URI
ENV MONGO_DB_NAME=$MONGO_DB_NAME

# Expose port and run FastAPI app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]