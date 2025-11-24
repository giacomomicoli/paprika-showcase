# Multi-stage build: Use full Python image for building, slim for runtime
FROM python:3.10 as builder

WORKDIR /app

# Install dependencies in builder stage with cache
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Runtime stage: Use slim image
FROM python:3.10-slim

WORKDIR /app

# Copy pre-built dependencies from builder
COPY --from=builder /root/.local /root/.local

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
