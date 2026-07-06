FROM python:3.13-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Cloud Run provides the port via the PORT environment variable (default 8080).
ENV PORT=8080

# Start the FastAPI app; shell form so $PORT is expanded at runtime.
CMD uvicorn api:app --host 0.0.0.0 --port $PORT
