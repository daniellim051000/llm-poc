# Production Deployment Guide

## Overview
This guide covers deploying the LLM POC system using Docker containers with PostgreSQL, Gunicorn, and Nginx.

## Architecture
```
Internet → Nginx (Port 80/443) → Django API (Port 8000) → PostgreSQL Django (Port 5432)
                                 → Flask App (Port 5000)  → PostgreSQL Flask (Port 5433)
```

## Prerequisites
- Docker and Docker Compose installed
- Environment files configured
- SSL certificates (optional for HTTPS)

## Setup Steps

### 1. Configure Environment Variables

Copy and customize the environment files:
```bash
# Django API environment
cp django_api/.env.sample django_api/.env
# Edit django_api/.env with your production values

# Flask LLM app environment
cp flask_llm/.env.sample flask_llm/.env
# Edit flask_llm/.env with your production values
```

### 2. Required Environment Variables

**Django API (.env)**:
- `DJANGO_SECRET_KEY`: Strong secret key for Django
- `DEBUG`: Set to `False` for production
- `POSTGRES_PASSWORD`: Secure database password
- `ALLOWED_HOSTS`: Your domain names

**Flask LLM App (.env)**:
- `SECRET_KEY`: Strong secret key for Flask
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `FIRECRAWL_API_KEY`: Your Firecrawl API key
- `DB_PASSWORD`: Same as Django's POSTGRES_PASSWORD

### 3. SSL Configuration (Optional)

For HTTPS support:
```bash
# Generate self-signed certificates for development
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem

# For production, use certificates from your CA
# Place cert.pem and key.pem in nginx/ssl/
```

### 4. Deploy the Stack

```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service-name]
```

### 5. Initialize Databases

```bash
# Run Django migrations
docker-compose exec django-api python manage.py migrate

# Populate Django with sample data
docker-compose exec django-api python populate_data.py

# Run Flask migrations
docker-compose exec flask-app flask db upgrade

# Create Flask users (optional)
docker-compose exec flask-app python create_user.py
```

## Service Details

### PostgreSQL Databases
- **Django Database**:
  - Container: `llm_poc_postgres_django`
  - Database: `llm_poc_django`
  - Port: 5432 (external), 5432 (internal)
  - Data: Persisted in `postgres_django_data` volume
- **Flask Database**:
  - Container: `llm_poc_postgres_flask`
  - Database: `llm_poc_flask`
  - Port: 5433 (external), 5432 (internal)
  - Data: Persisted in `postgres_flask_data` volume

### Django API
- **Container**: `llm_poc_django_api`
- **Port**: 8000 (internal)
- **Workers**: 3 Gunicorn workers
- **Health Check**: `/api/health/`

### Flask LLM App
- **Container**: `llm_poc_flask_app`
- **Port**: 5000 (internal)
- **Workers**: 2 Gunicorn workers
- **Health Check**: `/health`

### Nginx Reverse Proxy
- **Container**: `llm_poc_nginx`
- **Ports**: 80, 443 (external)
- **Routes**:
  - `/api/` → Django API
  - `/` → Flask App

## Monitoring and Maintenance

### Health Checks
```bash
# Check all service health
docker-compose ps

# Test individual endpoints
curl http://localhost/health
curl http://localhost/api/health/
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f nginx
docker-compose logs -f django-api
docker-compose logs -f flask-app
docker-compose logs -f postgres
```

### Database Backup
```bash
# Backup databases
docker-compose exec postgres-django pg_dump -U postgres llm_poc_django > django_backup.sql
docker-compose exec postgres-flask pg_dump -U postgres llm_poc_flask > flask_backup.sql
```

### Updates
```bash
# Update and rebuild services
docker-compose down
docker-compose up -d --build

# Update specific service
docker-compose up -d --build django-api
```

## Troubleshooting

### Common Issues

1. **Service won't start**: Check logs with `docker-compose logs [service]`
2. **Database connection issues**: Verify environment variables and network connectivity
3. **Permission errors**: Ensure proper file permissions for volumes
4. **Port conflicts**: Check if ports 80/443 are available

### Useful Commands
```bash
# Restart specific service
docker-compose restart [service-name]

# Execute commands in container
docker-compose exec [service-name] [command]

# Scale services
docker-compose up -d --scale flask-app=3

# Remove everything (including volumes)
docker-compose down -v
```

## Security Considerations

1. **Change default passwords** in production
2. **Use strong secret keys** for Django and Flask
3. **Configure firewall** to restrict access
4. **Enable SSL/TLS** for production
5. **Regular security updates** for base images
6. **Monitor logs** for suspicious activity
7. **Backup regularly** and test restore procedures

## Performance Tuning

- Adjust Gunicorn worker counts based on CPU cores
- Configure PostgreSQL connection pooling
- Enable Nginx caching for static content
- Set appropriate resource limits in docker-compose.yml
- Monitor resource usage and scale horizontally if needed
