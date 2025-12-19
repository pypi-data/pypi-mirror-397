# Stage 1: Build React frontend
FROM node:18 AS frontend-build
WORKDIR /app
# Copy and install frontend dependencies
COPY client/package.json client/package-lock.json ./client/
RUN npm --prefix client ci
# Build the React app (production build)
COPY client/ ./client/
RUN npm --prefix client run build

# Stage 2: Build Python backend with FastAPI
FROM python:3.11-slim AS backend
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY src/ ./src/
COPY run_demo.py run_full_demo.py ./

# Copy built frontend static files into backend (for serving via FastAPI or static server)
# Note: Ensure your FastAPI app is configured to serve static files from ./client/dist if needed
COPY --from=frontend-build /app/client/dist ./client/dist

# Set Python path
ENV PYTHONPATH=/app

# Expose port for FastAPI
EXPOSE 8000

# Command to start the FastAPI server using Uvicorn
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
