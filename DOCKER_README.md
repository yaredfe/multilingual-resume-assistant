# Docker Deployment Guide

## Overview
This guide explains how to dockerize and deploy the Multilingual Resume Screener & Interview Assistant.

## Prerequisites
- Docker installed on your system
- Docker Compose (optional, for easier deployment)

## Quick Start

### 1. Build the Docker Image
```bash
# Option 1: Use the build script
./docker-build.sh

# Option 2: Manual build
docker build -t multilingual-resume-screener:latest .
```

### 2. Run with Docker Compose (Recommended)
```bash
docker-compose up -d
```

### 3. Run with Docker Run
```bash
docker run -d \
  --name resume-screener-app \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/static:/app/static \
  --restart unless-stopped \
  multilingual-resume-screener:latest
```

### 4. Access the Application
- **Main Application**: http://localhost:8000
- **Recruiter Dashboard**: http://localhost:8000/recruiter
- **Employee Dashboard**: http://localhost:8000/employee
- **API Documentation**: http://localhost:8000/docs

## What Happens After Dockerization

### ✅ Benefits
1. **Portability**: Run anywhere with Docker
2. **Consistency**: Same environment everywhere
3. **Easy Deployment**: Deploy to cloud platforms
4. **Version Control**: Track application changes
5. **Isolation**: No conflicts with system dependencies

### 🔄 Local Development
- **Data Persistence**: Your local `data/` folder is mounted, so all resumes and matches persist
- **Model Access**: Local `models/` folder is mounted for faster startup
- **Easy Updates**: Change code locally, rebuild image, restart container

### 📁 File Access
- **Local Files**: All your local files remain accessible
- **Data Directory**: `./data/` is mounted to container
- **Models Directory**: `./models/` is mounted to container
- **Static Files**: `./static/` is mounted to container

## Management Commands

### View Logs
```bash
# Docker Compose
docker-compose logs -f

# Docker Run
docker logs -f resume-screener-app
```

### Stop Application
```bash
# Docker Compose
docker-compose down

# Docker Run
docker stop resume-screener-app
```

### Restart Application
```bash
# Docker Compose
docker-compose restart

# Docker Run
docker restart resume-screener-app
```

### Update Application
```bash
# 1. Stop current container
docker-compose down

# 2. Rebuild image
docker build -t multilingual-resume-screener:latest .

# 3. Start new container
docker-compose up -d
```

## Production Deployment

### Environment Variables
```bash
# Create .env file
CHROMA_DB_PATH=/app/data/chroma_db
HOST=0.0.0.0
PORT=8000
```

### Resource Limits
The Docker Compose file includes:
- Memory limit: 4GB
- Memory reservation: 2GB
- Health checks every 30 seconds

### Security Considerations
- Run container as non-root user (configured in Dockerfile)
- Use secrets management for sensitive data
- Enable HTTPS in production
- Configure proper firewall rules

## Cloud Deployment

### AWS ECS
```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker tag multilingual-resume-screener:latest your-account.dkr.ecr.us-east-1.amazonaws.com/resume-screener:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/resume-screener:latest
```

### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/your-project/resume-screener
gcloud run deploy resume-screener --image gcr.io/your-project/resume-screener --platform managed
```

### Azure Container Instances
```bash
# Build and push to ACR
az acr build --registry your-registry --image resume-screener .
az container create --resource-group your-rg --name resume-screener --image your-registry.azurecr.io/resume-screener:latest --ports 8000
```

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs resume-screener-app

# Check if port is in use
netstat -tulpn | grep 8000

# Check Docker daemon
docker info
```

### Memory Issues
```bash
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
```

### Data Persistence Issues
```bash
# Check volume mounts
docker inspect resume-screener-app | grep -A 10 "Mounts"

# Verify data directory permissions
ls -la data/
```

## Development Workflow

### 1. Local Development
```bash
# Make changes to your code
# Test locally with python run.py
```

### 2. Docker Testing
```bash
# Build new image
docker build -t multilingual-resume-screener:dev .

# Test in container
docker run -p 8000:8000 -v $(pwd)/data:/app/data multilingual-resume-screener:dev
```

### 3. Production Deployment
```bash
# Build production image
docker build -t multilingual-resume-screener:latest .

# Deploy
docker-compose up -d
```

## Backup and Recovery

### Backup Data
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup from running container
docker exec resume-screener-app tar -czf /tmp/backup.tar.gz /app/data
docker cp resume-screener-app:/tmp/backup.tar.gz ./backup.tar.gz
```

### Restore Data
```bash
# Extract backup
tar -xzf backup-20231201.tar.gz

# Restart container with restored data
docker-compose down
docker-compose up -d
```

## Monitoring

### Health Check
The application includes a health check endpoint:
```bash
curl http://localhost:8000/api/health
```

### Metrics
Consider adding monitoring with:
- Prometheus for metrics
- Grafana for visualization
- ELK stack for logs

## Support

For issues or questions:
1. Check the logs: `docker logs resume-screener-app`
2. Verify data directory permissions
3. Check Docker daemon status
4. Review this documentation

---

**Your application is now fully containerized and ready for deployment! 🚀** 