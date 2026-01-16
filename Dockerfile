# Stage 1: Build Frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Python Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for audio processing libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy pocket-tts-main (The library code)
COPY pocket-tts-main/pocket-tts-main /app/pocket-tts-main/pocket-tts-main

# Copy Backend code
COPY backend /app/backend

# Copy built frontend assets to /app/static
COPY --from=frontend-builder /app/frontend/dist /app/static

# Set workdir to backend to facilitate imports
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Command to run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
