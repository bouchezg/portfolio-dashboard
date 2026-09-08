FROM python:3.11-slim

WORKDIR /app

# Install Node for frontend build
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Frontend
COPY frontend ./frontend
RUN cd frontend && npm install && npm run build

# Copy backend code
COPY backend ./backend

# Expose port
EXPOSE 3000

# Run migrations and start backend
CMD ["sh", "-c", "cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 3000"]
