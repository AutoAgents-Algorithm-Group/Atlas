# Multi-stage Dockerfile for Fullstack FrankStyle Template
FROM node:18-alpine AS frontend

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ ./

# Build frontend application
RUN npm run build

# Backend Python stage
FROM python:3.11-slim AS backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Final production stage
FROM python:3.11-slim AS production

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    curl \
    make \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies from backend stage
COPY --from=backend /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=backend /usr/local/bin/ /usr/local/bin/

# Copy built frontend from frontend stage
COPY --from=frontend /app/frontend/.next ./frontend/.next
COPY --from=frontend /app/frontend/public ./frontend/public
COPY --from=frontend /app/frontend/package*.json ./frontend/
COPY --from=frontend /app/frontend/next.config.ts ./frontend/
COPY --from=frontend /app/frontend/node_modules ./frontend/node_modules

# Copy backend source
COPY backend/ ./backend/

# Copy Makefile
COPY Makefile ./

# Set environment variables
ENV NODE_ENV=production
ENV PYTHONPATH=/app/backend

# Expose ports
EXPOSE 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/health && curl -f http://localhost:3000 || exit 1

# Use make prod-docker as the command (for container internal use)
CMD ["make", "prod"]