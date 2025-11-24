# Paprika Showcase

Docker setup for a Python 3.10 application with Caddy reverse proxy.

## Setup

1. Add `paprika.local` to your `/etc/hosts` file:

   ```
   127.0.0.1 paprika.local
   ```

2. Build and run the containers:

   ```bash
   docker-compose up -d
   ```

3. Visit http://paprika.local in your browser

## Stop the application

```bash
docker-compose down
```
