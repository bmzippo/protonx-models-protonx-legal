# Deployment Guide

This document provides detailed deployment instructions for the ProtonX Legal Text Classification API.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### System Requirements
- Python 3.11 or higher
- 4GB RAM minimum (8GB+ recommended)
- 2GB disk space for model cache
- Internet access to download models from HuggingFace

### For GPU Support (Optional)
- CUDA-compatible GPU
- NVIDIA drivers installed
- CUDA toolkit 12.x

## Local Development

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd protonx-models-protonx-legal
```

2. **Run the setup script**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Activate the virtual environment**
```bash
source venv/bin/activate
```

4. **Start the service**
```bash
./run.sh
```

The API will be available at `http://localhost:8000`

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env as needed
nano .env

# Start the service
python -m src.main
```

### Testing

```bash
# Test project structure
python test_structure.py

# Test API endpoints (while service is running)
python example_client.py
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Docker CLI

```bash
# Build the image
docker build -t protonx-legal-api .

# Run the container
docker run -d \
  --name protonx-legal-api \
  -p 8000:8000 \
  -e DEVICE=cpu \
  -v model-cache:/app/model_cache \
  protonx-legal-api

# View logs
docker logs -f protonx-legal-api

# Stop the container
docker stop protonx-legal-api
docker rm protonx-legal-api
```

### GPU Support with Docker

```bash
docker run -d \
  --name protonx-legal-api \
  --gpus all \
  -p 8000:8000 \
  -e DEVICE=cuda \
  -v model-cache:/app/model_cache \
  protonx-legal-api
```

## Production Deployment

### Environment Configuration

Create a `.env` file with production settings:

```bash
# Model configuration
MODEL_NAME=protonx-models/protonx-legal-tc
MODEL_CACHE_DIR=/app/model_cache
DEVICE=cpu  # or cuda for GPU

# API configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4  # Adjust based on CPU cores

# Logging
LOG_LEVEL=WARNING  # Use WARNING or ERROR in production
```

### Kubernetes Deployment

Create a deployment manifest (`k8s-deployment.yaml`):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-cache-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: protonx-legal-api
  labels:
    app: protonx-legal-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: protonx-legal-api
  template:
    metadata:
      labels:
        app: protonx-legal-api
    spec:
      containers:
      - name: api
        image: protonx-legal-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEVICE
          value: "cpu"
        - name: MODEL_CACHE_DIR
          value: "/app/model_cache"
        - name: API_WORKERS
          value: "2"
        - name: LOG_LEVEL
          value: "WARNING"
        resources:
          requests:
            memory: "4Gi"
            cpu: "1000m"
          limits:
            memory: "8Gi"
            cpu: "2000m"
        volumeMounts:
        - name: model-cache
          mountPath: /app/model_cache
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: protonx-legal-api-service
spec:
  selector:
    app: protonx-legal-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

Deploy to Kubernetes:

```bash
kubectl apply -f k8s-deployment.yaml
```

### Cloud Deployment

#### AWS Elastic Beanstalk

1. Install EB CLI: `pip install awsebcli`
2. Initialize: `eb init`
3. Create environment: `eb create production`
4. Deploy: `eb deploy`

#### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/protonx-legal-api

# Deploy to Cloud Run
gcloud run deploy protonx-legal-api \
  --image gcr.io/PROJECT_ID/protonx-legal-api \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2
```

#### Azure Container Instances

```bash
# Create resource group
az group create --name protonx-rg --location eastus

# Deploy container
az container create \
  --resource-group protonx-rg \
  --name protonx-legal-api \
  --image protonx-legal-api:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables DEVICE=cpu
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health

# Check model info
curl http://localhost:8000/model-info
```

### Log Monitoring

```bash
# Docker logs
docker logs -f protonx-legal-api

# Kubernetes logs
kubectl logs -f deployment/protonx-legal-api

# View application logs
tail -f logs/app.log
```

### Performance Monitoring

Add monitoring tools:

```python
# Install monitoring dependencies
pip install prometheus-client

# Add to requirements.txt
prometheus-client>=0.19.0
```

### Scaling

#### Horizontal Scaling (Multiple Instances)

```bash
# Docker Compose
docker-compose up --scale api=3

# Kubernetes
kubectl scale deployment/protonx-legal-api --replicas=5
```

#### Vertical Scaling (Resources)

Update resource limits in deployment configuration:
- Increase memory for larger models
- Add GPU support for faster inference
- Increase CPU cores for better throughput

### Updates and Maintenance

```bash
# Pull latest code
git pull origin main

# Rebuild and redeploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or with Kubernetes
kubectl rollout restart deployment/protonx-legal-api
```

### Backup

```bash
# Backup model cache
tar -czf model-cache-backup.tar.gz model_cache/

# Backup configuration
cp .env .env.backup
```

## Troubleshooting

### Model Download Issues

If model download fails:
1. Check internet connectivity
2. Verify HuggingFace is accessible
3. Try manual download: `huggingface-cli download protonx-models/protonx-legal-tc`

### Out of Memory

If running out of memory:
1. Reduce `API_WORKERS` count
2. Increase container memory limits
3. Switch to CPU if GPU memory is insufficient

### Slow Response Times

To improve performance:
1. Use GPU (set `DEVICE=cuda`)
2. Increase worker count
3. Enable model caching
4. Use batch predictions for multiple texts

### Port Conflicts

If port 8000 is in use:
1. Change `API_PORT` in `.env`
2. Update port mapping in docker-compose.yml
3. Update firewall rules if needed

## Security Considerations

### Production Checklist

- [ ] Use HTTPS/TLS encryption
- [ ] Implement authentication (API keys, OAuth)
- [ ] Set up rate limiting
- [ ] Enable CORS with specific origins
- [ ] Use secure environment variables
- [ ] Regular security updates
- [ ] Monitor for suspicious activity
- [ ] Implement request validation
- [ ] Use firewalls and security groups
- [ ] Regular backups

### API Security

Add authentication to FastAPI:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/predict", dependencies=[Depends(verify_api_key)])
async def predict(input_data: TextInput):
    # ... existing code
```

## Support

For issues and questions:
- Model-related: Check [HuggingFace model page](https://huggingface.co/protonx-models/protonx-legal-tc)
- API-related: Open an issue in this repository
