# Azure Ubuntu VM Deployment Guide

This guide covers deploying the LLM POC Business Data Query System on an Ubuntu virtual machine in Microsoft Azure using Docker Compose for containerized deployment.

## Prerequisites

- Azure subscription with VM creation permissions
- SSH key pair for secure access
- Azure OpenAI service configured
- Firecrawl API key (optional, for web search functionality)

## Azure VM Setup

### 1. Create Ubuntu VM

```bash
# Using Azure CLI
az vm create \
  --resource-group myResourceGroup \
  --name llm-poc-vm \
  --image Ubuntu2004 \
  --size Standard_B2s \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --public-ip-sku Standard \
  --storage-sku Premium_LRS
```

**Recommended VM Sizes:**
- **Development/Testing**: Standard_B2s (2 vCPUs, 4 GB RAM)
- **Production**: Standard_D4s_v3+ (4+ vCPUs, 16+ GB RAM) - More CPUs = more Gunicorn workers

### 2. Configure Network Security Group

Allow inbound traffic on required ports:

```bash
# Allow SSH (22)
az vm open-port --port 22 --resource-group myResourceGroup --name llm-poc-vm --priority 1000

# Allow HTTP (80) - for production with reverse proxy
az vm open-port --port 80 --resource-group myResourceGroup --name llm-poc-vm --priority 1010

# Allow HTTPS (443) - for production with SSL
az vm open-port --port 443 --resource-group myResourceGroup --name llm-poc-vm --priority 1020

# Allow Flask app (5000) - for development/testing only
az vm open-port --port 5000 --resource-group myResourceGroup --name llm-poc-vm --priority 1030

# Allow Django API (8000) - for development/testing only
az vm open-port --port 8000 --resource-group myResourceGroup --name llm-poc-vm --priority 1040
```

## System Preparation

### 1. Connect to VM

```bash
ssh azureuser@<VM_PUBLIC_IP>
```

### 2. Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git build-essential
```

### 3. Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker azureuser

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for docker group changes to take effect
# Or run: newgrp docker
```

### 4. Verify Installation

```bash
docker --version
docker-compose --version
```

## Docker Compose Deployment

### 1. Clone Repository

```bash
cd /home/azureuser
git clone <YOUR_REPOSITORY_URL> llm-poc
cd llm-poc
```

### 2. Configure Environment Files

```bash
# Create Django API environment file
cat > django_api/.env << EOF
# Database Configuration
POSTGRES_DB=llm_poc_django
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here

# Django Settings
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,nginx,django-api
SECRET_KEY=your_django_secret_key_here
EOF

# Create Flask LLM environment file
cat > flask_llm/.env << EOF
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Database Configuration
DB_HOST=postgres-flask
DB_NAME=llm_poc_flask
DB_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here

# API Configuration
DJANGO_API_URL=http://django-api:8000
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Flask Settings
FLASK_ENV=production
SECRET_KEY=your_flask_secret_key_here
EOF
```

### 3. Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d --build

# View logs to ensure everything started correctly
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Initialize Databases

```bash
# Wait for services to be healthy, then initialize data
sleep 30

# Run Django migrations
docker-compose exec django-api python manage.py migrate

# Populate Django with sample data
docker-compose exec django-api python populate_data.py

# Run Flask migrations
docker-compose exec flask-app flask db upgrade

# Create Flask users (optional)
docker-compose exec flask-app python create_user.py
```

## Dynamic Worker Scaling

The deployment uses **dynamic Gunicorn workers** based on CPU count using the formula `(2 × CPU cores) + 1`.

### Worker Scaling by VM Size

| VM Size | vCPUs | Gunicorn Workers | Memory Usage |
|---------|-------|------------------|--------------|
| Standard_B2s | 2 | 5 workers | ~4 GB RAM |
| Standard_D4s_v3 | 4 | 9 workers | ~16 GB RAM |
| Standard_D8s_v3 | 8 | 17 workers | ~32 GB RAM |
| Standard_D16s_v3 | 16 | 33 workers | ~64 GB RAM |

### Configuration Files

The system uses `gunicorn.conf.py` files in both Django and Flask directories that automatically calculate worker count:

```python
import multiprocessing
workers = (2 * multiprocessing.cpu_count()) + 1
```

### Viewing Current Worker Count

```bash
# Check actual worker count being used
docker-compose exec django-api ps aux | grep gunicorn
docker-compose exec flask-app ps aux | grep gunicorn

# Or check the logs during startup
docker-compose logs django-api | grep "workers"
docker-compose logs flask-app | grep "workers"
```

## Production Configuration

### SSL and Reverse Proxy (Optional)

The Docker Compose setup includes Nginx as a reverse proxy. For production with SSL:

```bash
# The nginx service is already configured in docker-compose.yml
# Ensure SSL certificates are placed in ./nginx/ssl/ directory

# For Let's Encrypt certificates:
sudo apt install -y certbot

# Generate certificates (replace your-domain.com)
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to nginx/ssl directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/ssl/
sudo chown azureuser:azureuser ./nginx/ssl/*

# Restart nginx service
docker-compose restart nginx
```

## Security Configuration

### 1. Firewall Setup

```bash
# Install and configure UFW
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'  # If using Nginx
sudo ufw allow 5000/tcp      # For direct Flask access (dev only)
```

### 2. SSL Certificate (Production)

```bash
# Install Certbot for Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Environment Security

```bash
# Secure environment files
chmod 600 /home/azureuser/llm-poc/flask_llm/.env
chown azureuser:azureuser /home/azureuser/llm-poc/flask_llm/.env

# Create backup of databases
mkdir -p /home/azureuser/backups
sqlite3 /home/azureuser/llm-poc/django_api/db.sqlite3 ".backup /home/azureuser/backups/django_backup_$(date +%Y%m%d).db"
sqlite3 /home/azureuser/llm-poc/flask_llm/instance/app.db ".backup /home/azureuser/backups/flask_backup_$(date +%Y%m%d).db"
```

## Monitoring and Maintenance

### 1. Log Management

```bash
# Create log rotation for application logs
sudo tee /etc/logrotate.d/llm-poc << EOF
/var/log/django-api.*.log /var/log/flask-llm.*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

### 2. Health Checks

```bash
# Create health check script
tee /home/azureuser/health_check.sh << EOF
#!/bin/bash
echo "=== Health Check $(date) ==="

# Check Django API
if curl -f http://localhost:8000/admin/ > /dev/null 2>&1; then
    echo "✓ Django API is running"
else
    echo "✗ Django API is down"
fi

# Check Flask LLM App
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✓ Flask LLM App is running"
else
    echo "✗ Flask LLM App is down"
fi

# Check processes
echo "=== Process Status ==="
sudo supervisorctl status
EOF

chmod +x /home/azureuser/health_check.sh
```

### 3. Automated Backups

```bash
# Create backup script
tee /home/azureuser/backup.sh << EOF
#!/bin/bash
BACKUP_DIR="/home/azureuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR

# Backup databases
sqlite3 /home/azureuser/llm-poc/django_api/db.sqlite3 ".backup \$BACKUP_DIR/django_\$DATE.db"
sqlite3 /home/azureuser/llm-poc/flask_llm/instance/app.db ".backup \$BACKUP_DIR/flask_\$DATE.db"

# Keep only last 7 days of backups
find \$BACKUP_DIR -name "*.db" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF

chmod +x /home/azureuser/backup.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/azureuser/backup.sh") | crontab -
```

## Testing Docker Deployment

### 1. Verify All Services

```bash
# Check service status
docker-compose ps

# All services should show "Up" status:
# - postgres-django (healthy)
# - postgres-flask (healthy)
# - django-api (healthy)
# - flask-app (healthy)
# - nginx (up)
```

### 2. Test Health Endpoints

```bash
# Test Django API health (via docker network)
docker-compose exec django-api curl http://localhost:8000/api/health/

# Test Flask app health (via docker network)
docker-compose exec flask-app curl http://localhost:5000/health

# Test external access (replace YOUR_VM_PUBLIC_IP)
curl http://YOUR_VM_PUBLIC_IP/health
curl http://YOUR_VM_PUBLIC_IP:8000/api/health/
```

### 3. Test Query Functionality

```bash
# Test sample query through Nginx proxy
curl -X POST http://YOUR_VM_PUBLIC_IP/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What contracts are currently active?"}'

# Test direct Flask access
curl -X POST http://YOUR_VM_PUBLIC_IP:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the purchase history for Company A?"}'
```

### 4. Verify Dynamic Workers

```bash
# Check worker count matches CPU cores
echo "Expected workers: $((2 * $(nproc) + 1))"

# Verify actual worker processes
docker-compose exec django-api ps aux | grep "gunicorn: worker" | wc -l
docker-compose exec flask-app ps aux | grep "gunicorn: worker" | wc -l
```

## Troubleshooting

### Common Docker Issues

1. **Port Access Issues**: Ensure NSG rules allow traffic on required ports (80, 443, 5000, 8000)
2. **Service Health**: Use `docker-compose ps` to check service health status
3. **Database Connection**: Ensure PostgreSQL containers are healthy before app containers start
4. **Environment Variables**: Check `.env` files exist in both `django_api/` and `flask_llm/` directories
5. **Worker Count**: Verify Gunicorn workers scale with available CPU cores

### Docker Log Management

```bash
# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f django-api
docker-compose logs -f flask-app
docker-compose logs -f nginx

# View recent logs with timestamps
docker-compose logs --tail=100 --timestamps

# Follow logs for troubleshooting
docker-compose logs -f --tail=50
```

### Quick Troubleshooting Commands

```bash
# Restart specific service
docker-compose restart django-api

# Rebuild and restart all services
docker-compose down && docker-compose up -d --build

# Check container resource usage
docker stats

# Access container shell for debugging
docker-compose exec django-api bash
docker-compose exec flask-app bash
```

## Performance Optimization

### For Production Workloads

1. **Upgrade VM Size**: Use Standard_D8s_v3+ for higher worker counts and better performance
2. **Database Optimization**: PostgreSQL containers are already configured - consider Azure Database for PostgreSQL for managed solution
3. **Caching**: Add Redis container to docker-compose.yml for query caching
4. **Load Balancing**: Use Azure Load Balancer with multiple VM instances
5. **Monitoring**: Enable Azure Container Insights and Application Insights
6. **Auto-scaling**: Configure VM Scale Sets based on CPU/memory usage

### Resource Monitoring

```bash
# Monitor Docker container resources
docker stats

# Monitor VM resources
htop  # Install with: sudo apt install htop

# Monitor disk usage
df -h

# Monitor memory usage
free -h

# View container resource limits
docker-compose exec django-api cat /sys/fs/cgroup/memory/memory.limit_in_bytes
docker-compose exec flask-app cat /sys/fs/cgroup/memory/memory.limit_in_bytes
```

### Scaling Considerations

**Worker Scaling Table:**
- 2 vCPU VM = 5 workers each (Django + Flask) = 10 total workers
- 4 vCPU VM = 9 workers each = 18 total workers
- 8 vCPU VM = 17 workers each = 34 total workers
- 16 vCPU VM = 33 workers each = 66 total workers

**Memory Requirements:**
- Each Gunicorn worker: ~100-200 MB RAM
- PostgreSQL containers: ~100 MB each
- Nginx: ~50 MB
- **Minimum**: 4 GB RAM for development
- **Recommended**: 16+ GB RAM for production

## Deployment Summary

This Docker Compose deployment provides:
- ✅ **Containerized services** with health checks
- ✅ **Dynamic worker scaling** based on CPU cores
- ✅ **PostgreSQL databases** with persistent volumes
- ✅ **Nginx reverse proxy** with SSL support
- ✅ **Automated restarts** and dependency management
- ✅ **Comprehensive logging** and monitoring

The system automatically scales Gunicorn workers based on your Azure VM's CPU count, ensuring optimal performance regardless of VM size.
