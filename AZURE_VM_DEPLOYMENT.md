# Azure Ubuntu VM Deployment Guide

This guide covers deploying the LLM POC Business Data Query System on an Ubuntu virtual machine in Microsoft Azure.

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
- **Production**: Standard_D4s_v3 (4 vCPUs, 16 GB RAM)

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

### 3. Install Python 3.13

```bash
# Add deadsnakes PPA for latest Python versions
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.13 and development tools
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3-pip
sudo apt install -y sqlite3 libsqlite3-dev

# Set Python 3.13 as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1
```

### 4. Install Process Manager

```bash
# Install supervisor for process management
sudo apt install -y supervisor

# Or install PM2 (Node.js process manager)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
```

## Application Deployment

### 1. Clone Repository

```bash
cd /home/azureuser
git clone <YOUR_REPOSITORY_URL> llm-poc
cd llm-poc
```

### 2. Set Up Django API

```bash
cd django_api

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and populate data
python manage.py migrate
python populate_data.py

# Test Django API
python manage.py runserver 0.0.0.0:8000 &
```

### 3. Set Up Flask LLM App

```bash
cd ../flask_llm

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
DJANGO_API_URL=http://localhost:8000
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
EOF

# Initialize database
flask db upgrade

# Create initial user (optional)
python create_user.py

# Test Flask app
python app.py &
```

## Production Configuration

### 1. Using Supervisor (Recommended)

Create supervisor configuration files:

```bash
# Django API supervisor config
sudo tee /etc/supervisor/conf.d/django-api.conf << EOF
[program:django-api]
command=/home/azureuser/llm-poc/django_api/venv/bin/python manage.py runserver 0.0.0.0:8000
directory=/home/azureuser/llm-poc/django_api
user=azureuser
autostart=true
autorestart=true
stderr_logfile=/var/log/django-api.err.log
stdout_logfile=/var/log/django-api.out.log
environment=PATH="/home/azureuser/llm-poc/django_api/venv/bin"
EOF

# Flask LLM app supervisor config
sudo tee /etc/supervisor/conf.d/flask-llm.conf << EOF
[program:flask-llm]
command=/home/azureuser/llm-poc/flask_llm/venv/bin/python app.py
directory=/home/azureuser/llm-poc/flask_llm
user=azureuser
autostart=true
autorestart=true
stderr_logfile=/var/log/flask-llm.err.log
stdout_logfile=/var/log/flask-llm.out.log
environment=PATH="/home/azureuser/llm-poc/flask_llm/venv/bin"
EOF

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### 2. Using PM2 (Alternative)

```bash
# Start Django API with PM2
cd /home/azureuser/llm-poc/django_api
pm2 start --name "django-api" --interpreter python3 -- manage.py runserver 0.0.0.0:8000

# Start Flask app with PM2
cd ../flask_llm
pm2 start --name "flask-llm" app.py --interpreter python3

# Save PM2 configuration
pm2 save
pm2 startup
```

### 3. Nginx Reverse Proxy (Production)

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/llm-poc << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or VM IP

    # Flask LLM App (main interface)
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Django API (internal)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/llm-poc /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
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

## Testing Deployment

### 1. Verify Services

```bash
# Check if both services are running
curl http://localhost:8000/admin/  # Django admin (should redirect to login)
curl http://localhost:5000/health  # Flask health check

# Test from external access (replace with your VM's public IP)
curl http://YOUR_VM_PUBLIC_IP:5000/health
```

### 2. Test Query Functionality

```bash
# Test a sample query
curl -X POST http://YOUR_VM_PUBLIC_IP:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What contracts are currently active?"}'
```

## Troubleshooting

### Common Issues

1. **Port Access Issues**: Ensure NSG rules allow traffic on required ports
2. **Python Version**: Verify Python 3.13 is installed and virtual environments use correct version
3. **Database Permissions**: Ensure azureuser has write access to SQLite database files
4. **Environment Variables**: Check `.env` file exists and has correct Azure OpenAI credentials

### Log Locations

```bash
# Supervisor logs
tail -f /var/log/django-api.out.log
tail -f /var/log/flask-llm.out.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
```

## Performance Optimization

### For Production Workloads

1. **Upgrade VM Size**: Use Standard_D4s_v3 or larger
2. **Database Migration**: Move from SQLite to PostgreSQL
3. **Caching**: Implement Redis for query caching
4. **Load Balancing**: Use Azure Load Balancer for multiple instances
5. **Application Insights**: Enable Azure monitoring

### Resource Monitoring

```bash
# Install htop for resource monitoring
sudo apt install -y htop

# Monitor processes
htop

# Monitor disk usage
df -h

# Monitor memory usage
free -h
```

## Alternative: Using Docker on Azure VM

For a more containerized approach, you can also deploy using the existing Docker configuration:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker azureuser

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone <YOUR_REPOSITORY_URL> llm-poc
cd llm-poc

# Configure environment files
cp django_api/.env.sample django_api/.env
cp flask_llm/.env.sample flask_llm/.env
# Edit the .env files with your credentials

# Deploy with Docker Compose
docker-compose up -d --build
```

This provides both native deployment and containerized options for your Azure Ubuntu VM deployment.
