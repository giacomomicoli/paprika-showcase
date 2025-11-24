# Paprika Showcase

A simple Python 3.10 Flask application with Docker and Caddy reverse proxy setup.

## Features

- Python 3.10 Flask application
- Docker containerization
- Caddy reverse proxy for custom domain routing
- Health check endpoints

## Prerequisites

- Docker
- Docker Compose
- Add `paprika.local` to your hosts file

## Setup

### 1. Configure Local Domain

Add the following line to your `/etc/hosts` file (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
127.0.0.1 paprika.local
```

### 2. Build and Run

```bash
docker-compose up --build
```

This will:
- Build the Python application container
- Start the Caddy reverse proxy
- Expose the application on `paprika.local`

### 3. Access the Application

Once running, visit:
- http://paprika.local - Main application
- http://paprika.local/health - Health check endpoint

## Architecture

```
paprika.local (Caddy) → app:8000 (Python Flask + Gunicorn)
```

### Services

1. **app**: Python 3.10 Flask application running with Gunicorn
   - Internal port: 8000
   - Health check enabled

2. **caddy**: Caddy web server acting as reverse proxy
   - Ports: 80 (HTTP), 443 (HTTPS)
   - Routes `paprika.local` to the app service

## Development

### Application Structure

```
.
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration for the app
├── docker-compose.yml # Multi-container setup
├── Caddyfile         # Caddy reverse proxy configuration
└── README.md         # This file
```

### Stopping the Application

```bash
docker-compose down
```

To remove volumes as well:

```bash
docker-compose down -v
```

## API Endpoints

### GET /
Returns a welcome message with application status.

**Response:**
```json
{
  "message": "Welcome to Paprika Showcase!",
  "status": "running",
  "python_version": "3.10"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## License

This is a showcase project.
