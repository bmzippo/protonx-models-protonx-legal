# ProtonX Legal Text Classification API

A Python-based REST API service for deploying the ProtonX Legal Text Classification model (`protonx-models/protonx-legal-tc`) from HuggingFace. This service provides endpoints for classifying Vietnamese legal documents using state-of-the-art transformer models.

## Features

- 🚀 FastAPI-based REST API
- 🤖 HuggingFace Transformers integration
- 📦 Docker support for easy deployment
- 🔄 Single and batch prediction endpoints
- 📊 Health monitoring and model info endpoints
- ⚙️ Configurable via environment variables
- 🪵 Structured logging with Loguru

## Project Structure

```
.
├── src/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration management
│   ├── model.py            # Model loading and inference
│   ├── api.py              # FastAPI application
│   └── main.py             # Entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── run.sh                  # Startup script
├── example_client.py       # Example API client
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Requirements

- Python 3.11+
- PyTorch
- Transformers
- FastAPI
- Other dependencies listed in `requirements.txt`

## Installation

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd protonx-models-protonx-legal
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env as needed
```

### Option 2: Docker Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd protonx-models-protonx-legal
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

## Configuration

Configuration can be set via environment variables or a `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `protonx-models/protonx-legal-tc` | HuggingFace model identifier |
| `MODEL_CACHE_DIR` | `./model_cache` | Directory to cache downloaded models |
| `DEVICE` | `cpu` | Device to run inference on (`cpu` or `cuda`) |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `API_WORKERS` | `1` | Number of API workers |
| `LOG_LEVEL` | `INFO` | Logging level |

## Usage

### Starting the Server

#### Local:
```bash
# Using the run script
chmod +x run.sh
./run.sh

# Or directly with Python
python -m src.main
```

#### Docker:
```bash
docker-compose up
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Root Endpoint
```bash
GET /
```
Returns basic API information.

#### Health Check
```bash
GET /health
```
Returns the health status of the service.

#### Model Information
```bash
GET /model-info
```
Returns information about the loaded model.

#### Single Text Classification
```bash
POST /predict
Content-Type: application/json

{
  "text": "Your Vietnamese legal text here"
}
```

Response:
```json
{
  "predicted_class": 0,
  "confidence": 0.95,
  "all_scores": [0.95, 0.03, 0.02],
  "predicted_label": "LABEL_0",
  "all_labels": {
    "LABEL_0": 0.95,
    "LABEL_1": 0.03,
    "LABEL_2": 0.02
  }
}
```

#### Batch Text Classification
```bash
POST /predict/batch
Content-Type: application/json

{
  "texts": [
    "First legal text",
    "Second legal text"
  ]
}
```

Response:
```json
{
  "predictions": [
    {
      "predicted_class": 0,
      "confidence": 0.95,
      "all_scores": [0.95, 0.03, 0.02],
      "predicted_label": "LABEL_0",
      "all_labels": {...}
    },
    ...
  ]
}
```

### Example Client

An example Python client is provided in `example_client.py`:

```bash
# Make sure the server is running first
python example_client.py
```

### Using curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Điều 1. Phạm vi điều chỉnh của Luật này..."}'
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style

```bash
# Format code
black src/

# Lint code
flake8 src/
```

## Deployment

### Production Considerations

1. **Resource Requirements**: The model requires adequate RAM and CPU. For better performance, use a GPU by setting `DEVICE=cuda`.

2. **Workers**: Increase `API_WORKERS` for better concurrency, but be mindful of memory usage.

3. **Caching**: The model is downloaded on first use and cached in `MODEL_CACHE_DIR`. Ensure this directory persists across restarts.

4. **Security**: 
   - Use HTTPS in production
   - Implement authentication/authorization
   - Set up rate limiting
   - Use environment-specific configurations

### Docker Deployment

```bash
# Build image
docker build -t protonx-legal-api .

# Run container
docker run -p 8000:8000 \
  -e DEVICE=cpu \
  -v model-cache:/app/model_cache \
  protonx-legal-api
```

### Kubernetes Deployment

Example deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: protonx-legal-api
spec:
  replicas: 2
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
        volumeMounts:
        - name: model-cache
          mountPath: /app/model_cache
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
```

## Troubleshooting

### Model Download Issues

If the model fails to download:
1. Check your internet connection
2. Verify HuggingFace is accessible
3. Try downloading manually: `huggingface-cli download protonx-models/protonx-legal-tc`

### Memory Issues

If you encounter out-of-memory errors:
1. Reduce batch size in batch predictions
2. Use CPU instead of GPU if GPU memory is limited
3. Increase system memory allocation

### Port Already in Use

If port 8000 is already in use:
1. Change `API_PORT` in `.env`
2. Or stop the process using port 8000: `lsof -ti:8000 | xargs kill -9`

## License

This project is provided as-is for deployment of the ProtonX Legal model.

## Model Information

Model: [protonx-models/protonx-legal-tc](https://huggingface.co/protonx-models/protonx-legal-tc)

For more information about the model, visit the HuggingFace model page.

## Support

For issues and questions:
- Model-related: Check the HuggingFace model page
- API-related: Open an issue in this repository
