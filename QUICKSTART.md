# Quick Start Guide

This guide will help you deploy and test the ProtonX Legal Text Classification API quickly.

## Prerequisites

- Docker and Docker Compose installed
- Internet connection (for downloading the model on first run)
- At least 4GB RAM available

## Quick Deployment (Recommended)

### Option 1: Using the Deployment Script

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

Select option 1 to build and start the API.

### Option 2: Using Docker Compose Directly

```bash
# Build and start the service
docker compose up -d

# View logs
docker compose logs -f

# Stop the service
docker compose down
```

### Option 3: Manual Docker Build

```bash
# Build the Docker image
docker build -t protonx-legal-api .

# Run the container
docker run -d \
  --name protonx-legal-api \
  -p 8000:8000 \
  -v model-cache:/app/model_cache \
  protonx-legal-api

# View logs
docker logs -f protonx-legal-api

# Stop the container
docker stop protonx-legal-api
docker rm protonx-legal-api
```

## Accessing the API

Once deployed, the API will be available at:

- **API Base URL**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

### 2. Model Information

```bash
curl http://localhost:8000/model-info
```

### 3. Text Classification

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Điều 1. Phạm vi điều chỉnh. Luật này quy định về các vấn đề liên quan đến pháp luật."
  }'
```

### 4. Batch Classification

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Điều 1. Phạm vi điều chỉnh của Luật này.",
      "Khoản 1. Các quy định về thực hiện."
    ]
  }'
```

### 5. Using the Example Client

```bash
# Make sure the API is running
python example_client.py
```

## Interactive Testing

Open your browser and go to:
- **http://localhost:8000/docs**

This provides an interactive Swagger UI where you can:
1. View all available endpoints
2. Test endpoints directly from the browser
3. See request/response schemas
4. Try different inputs

## Common Issues

### Issue: Port 8000 already in use

**Solution**: Change the port in docker-compose.yml or .env file:
```yaml
ports:
  - "8080:8000"  # Use port 8080 instead
```

### Issue: Model download fails

**Solution**: 
1. Check your internet connection
2. Verify HuggingFace is accessible
3. Try pre-downloading the model:
```bash
./deploy.sh
# Select option 5
```

### Issue: Out of memory

**Solution**: 
1. Ensure Docker has at least 4GB RAM allocated
2. Close other applications
3. Reduce API_WORKERS in .env file

### Issue: Container fails to start

**Solution**: View the logs to see the error:
```bash
docker compose logs -f
```

## Monitoring

### View Logs

```bash
# Docker Compose
docker compose logs -f

# Docker
docker logs -f protonx-legal-api
```

### Check Container Status

```bash
docker compose ps
```

### Stop the Service

```bash
docker compose down
```

## Next Steps

1. Read the full [README.md](README.md) for detailed information
2. Check [API_EXAMPLES.md](API_EXAMPLES.md) for more API usage examples
3. Review [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment options
4. Explore the interactive API documentation at http://localhost:8000/docs

## Support

If you encounter any issues:
1. Check the logs: `docker compose logs -f`
2. Verify Docker is running: `docker ps`
3. Check the health endpoint: `curl http://localhost:8000/health`
4. Review the troubleshooting section in README.md

## Clean Up

To completely remove the deployment:

```bash
# Stop and remove containers
docker compose down

# Remove the Docker image
docker rmi protonx-models-protonx-legal-api

# Remove the model cache volume
docker volume rm protonx-models-protonx-legal_model-cache
```
