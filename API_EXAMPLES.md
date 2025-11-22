# API Usage Examples

This document provides practical examples of using the ProtonX Legal Text Classification API.

## Table of Contents
- [Getting Started](#getting-started)
- [Single Text Classification](#single-text-classification)
- [Batch Classification](#batch-classification)
- [OCR Image Upload](#ocr-image-upload)
- [OCR with Classification](#ocr-with-classification)
- [Health Checks](#health-checks)
- [Python Client Examples](#python-client-examples)
- [JavaScript/Node.js Examples](#javascriptnodejs-examples)
- [cURL Examples](#curl-examples)

## Getting Started

Make sure the API is running:
```bash
# Local development
./run.sh

# Or with Docker
docker-compose up
```

The API will be available at `http://localhost:8000`

## Single Text Classification

### Request

```http
POST /predict
Content-Type: application/json

{
  "text": "Điều 1. Phạm vi điều chỉnh của Luật này là quy định về quyền và nghĩa vụ của công dân"
}
```

### Response

```json
{
  "predicted_class": 0,
  "confidence": 0.9523,
  "all_scores": [0.9523, 0.0321, 0.0156],
  "predicted_label": "Luật",
  "all_labels": {
    "Luật": 0.9523,
    "Hợp đồng": 0.0321,
    "Quyết định": 0.0156
  }
}
```

## Batch Classification

### Request

```http
POST /predict/batch
Content-Type: application/json

{
  "texts": [
    "Điều 1. Phạm vi điều chỉnh...",
    "Hợp đồng mua bán giữa bên A và bên B...",
    "Quyết định số 123/QĐ-TTg về việc..."
  ]
}
```

### Response

```json
{
  "predictions": [
    {
      "predicted_class": 0,
      "confidence": 0.9523,
      "all_scores": [0.9523, 0.0321, 0.0156],
      "predicted_label": "Luật",
      "all_labels": {
        "Luật": 0.9523,
        "Hợp đồng": 0.0321,
        "Quyết định": 0.0156
      }
    },
    {
      "predicted_class": 1,
      "confidence": 0.8912,
      "all_scores": [0.0534, 0.8912, 0.0554],
      "predicted_label": "Hợp đồng",
      "all_labels": {
        "Luật": 0.0534,
        "Hợp đồng": 0.8912,
        "Quyết định": 0.0554
      }
    },
    {
      "predicted_class": 2,
      "confidence": 0.9234,
      "all_scores": [0.0423, 0.0343, 0.9234],
      "predicted_label": "Quyết định",
      "all_labels": {
        "Luật": 0.0423,
        "Hợp đồng": 0.0343,
        "Quyết định": 0.9234
      }
    }
  ]
}
```

## OCR Image Upload

### Request

Upload an image file to extract text using OCR.

```http
POST /ocr/upload
Content-Type: multipart/form-data

file: [image file]
```

### Response

```json
{
  "text": "Điều 1. Phạm vi điều chỉnh của Luật này là quy định về quyền và nghĩa vụ của công dân trong hoạt động kinh doanh.",
  "lines": [
    {
      "text": "Điều 1. Phạm vi điều chỉnh",
      "confidence": 0.95,
      "bbox": [10, 20, 300, 45]
    },
    {
      "text": "của Luật này là quy định",
      "confidence": 0.93,
      "bbox": [10, 50, 280, 75]
    }
  ],
  "average_confidence": 0.94,
  "engine": "easyocr"
}
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/ocr/upload" \
  -F "file=@/path/to/your/image.jpg"
```

## OCR with Classification

Upload an image, extract text, and classify the extracted text in one request.

### Request

```http
POST /ocr/upload-and-classify
Content-Type: multipart/form-data

file: [image file]
```

### Response

```json
{
  "ocr_result": {
    "text": "Điều 1. Phạm vi điều chỉnh của Luật này là quy định về quyền và nghĩa vụ của công dân.",
    "lines": [
      {
        "text": "Điều 1. Phạm vi điều chỉnh",
        "confidence": 0.95,
        "bbox": [10, 20, 300, 45]
      }
    ],
    "average_confidence": 0.94,
    "engine": "easyocr"
  },
  "classification": {
    "predicted_class": 0,
    "confidence": 0.9523,
    "all_scores": [0.9523, 0.0321, 0.0156],
    "predicted_label": "Luật",
    "all_labels": {
      "Luật": 0.9523,
      "Hợp đồng": 0.0321,
      "Quyết định": 0.0156
    }
  }
}
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/ocr/upload-and-classify" \
  -F "file=@/path/to/your/legal-document.jpg"
```

### Python Example

```python
import requests

# Upload and OCR
with open('/path/to/image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/ocr/upload', files=files)
    ocr_result = response.json()
    print(f"Extracted text: {ocr_result['text']}")
    print(f"Confidence: {ocr_result['average_confidence']:.2%}")

# Upload, OCR, and classify
with open('/path/to/image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/ocr/upload-and-classify', files=files)
    result = response.json()
    print(f"Extracted text: {result['ocr_result']['text']}")
    if result['classification']:
        print(f"Classification: {result['classification']['predicted_label']}")
        print(f"Confidence: {result['classification']['confidence']:.2%}")
```

## Health Checks

### Health Endpoint

```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### Model Info Endpoint

```http
GET /model-info
```

Response:
```json
{
  "model_name": "protonx-models/protonx-legal-tc",
  "device": "cpu",
  "model_loaded": true,
  "labels": {
    "0": "Luật",
    "1": "Hợp đồng",
    "2": "Quyết định"
  },
  "num_labels": 3
}
```

## Python Client Examples

### Simple Example

```python
import requests
import json

API_URL = "http://localhost:8000"

# Single prediction
def predict_single(text):
    response = requests.post(
        f"{API_URL}/predict",
        json={"text": text}
    )
    return response.json()

# Example usage
text = "Điều 1. Phạm vi điều chỉnh của Luật này..."
result = predict_single(text)
print(json.dumps(result, indent=2, ensure_ascii=False))
```

### Class-based Client

```python
import requests
from typing import List, Dict, Any

class LegalTextClassifier:
    """Client for ProtonX Legal Text Classification API."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.session = requests.Session()
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Classify a single text."""
        response = self.session.post(
            f"{self.api_url}/predict",
            json={"text": text}
        )
        response.raise_for_status()
        return response.json()
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Classify multiple texts."""
        response = self.session.post(
            f"{self.api_url}/predict/batch",
            json={"texts": texts}
        )
        response.raise_for_status()
        return response.json()["predictions"]
    
    def health(self) -> Dict[str, Any]:
        """Check API health."""
        response = self.session.get(f"{self.api_url}/health")
        response.raise_for_status()
        return response.json()
    
    def model_info(self) -> Dict[str, Any]:
        """Get model information."""
        response = self.session.get(f"{self.api_url}/model-info")
        response.raise_for_status()
        return response.json()

# Usage
client = LegalTextClassifier()

# Check health
print("Health:", client.health())

# Single prediction
text = "Điều 1. Phạm vi điều chỉnh..."
result = client.predict(text)
print(f"Predicted: {result['predicted_label']} (confidence: {result['confidence']:.2%})")

# Batch prediction
texts = [
    "Điều 1. Phạm vi điều chỉnh...",
    "Hợp đồng mua bán...",
    "Quyết định số..."
]
results = client.predict_batch(texts)
for text, result in zip(texts, results):
    print(f"{text[:30]}... -> {result['predicted_label']}")
```

### Async Client

```python
import asyncio
import aiohttp
from typing import List, Dict, Any

class AsyncLegalTextClassifier:
    """Async client for ProtonX Legal Text Classification API."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
    
    async def predict(self, text: str) -> Dict[str, Any]:
        """Classify a single text."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/predict",
                json={"text": text}
            ) as response:
                return await response.json()
    
    async def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Classify multiple texts."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/predict/batch",
                json={"texts": texts}
            ) as response:
                result = await response.json()
                return result["predictions"]

# Usage
async def main():
    client = AsyncLegalTextClassifier()
    
    # Parallel predictions
    texts = [
        "Điều 1. Phạm vi điều chỉnh...",
        "Hợp đồng mua bán...",
        "Quyết định số..."
    ]
    
    tasks = [client.predict(text) for text in texts]
    results = await asyncio.gather(*tasks)
    
    for text, result in zip(texts, results):
        print(f"{result['predicted_label']}: {result['confidence']:.2%}")

# Run
asyncio.run(main())
```

## JavaScript/Node.js Examples

### Using Fetch API

```javascript
// Single prediction
async function predictSingle(text) {
    const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
    });
    return await response.json();
}

// Usage
const text = "Điều 1. Phạm vi điều chỉnh của Luật này...";
predictSingle(text).then(result => {
    console.log('Predicted:', result.predicted_label);
    console.log('Confidence:', result.confidence);
});
```

### Using Axios

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000';

// Single prediction
async function predict(text) {
    try {
        const response = await axios.post(`${API_URL}/predict`, { text });
        return response.data;
    } catch (error) {
        console.error('Error:', error.message);
        throw error;
    }
}

// Batch prediction
async function predictBatch(texts) {
    try {
        const response = await axios.post(`${API_URL}/predict/batch`, { texts });
        return response.data.predictions;
    } catch (error) {
        console.error('Error:', error.message);
        throw error;
    }
}

// Usage
(async () => {
    const text = "Điều 1. Phạm vi điều chỉnh...";
    const result = await predict(text);
    console.log('Result:', result);
    
    const texts = [
        "Điều 1. Phạm vi điều chỉnh...",
        "Hợp đồng mua bán...",
        "Quyết định số..."
    ];
    const results = await predictBatch(texts);
    console.log('Batch results:', results);
})();
```

## cURL Examples

### Single Prediction

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Điều 1. Phạm vi điều chỉnh của Luật này là quy định về quyền và nghĩa vụ của công dân"
  }'
```

### Batch Prediction

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Điều 1. Phạm vi điều chỉnh...",
      "Hợp đồng mua bán...",
      "Quyết định số..."
    ]
  }'
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

### Model Info

```bash
curl "http://localhost:8000/model-info"
```

### Pretty Print JSON Response

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Điều 1. Phạm vi điều chỉnh..."}' \
  | python -m json.tool
```

## Error Handling

### Invalid Input

Request:
```json
{
  "text": ""
}
```

Response (422):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

### Server Error

Response (500):
```json
{
  "detail": "Prediction failed: <error message>"
}
```

### Service Unavailable

Response (503):
```json
{
  "detail": "Service unhealthy: Model not loaded"
}
```

## Best Practices

1. **Reuse connections**: Use session objects to reuse HTTP connections
2. **Handle errors**: Always handle HTTP errors and timeouts
3. **Batch when possible**: Use batch endpoint for multiple texts to improve throughput
4. **Set timeouts**: Set appropriate request timeouts based on text length
5. **Monitor health**: Regularly check the health endpoint
6. **Cache results**: Cache predictions for frequently classified texts

## Rate Limiting

If rate limiting is implemented, you may receive:

Response (429):
```json
{
  "detail": "Too many requests"
}
```

Handle with exponential backoff:

```python
import time
from requests.exceptions import RequestException

def predict_with_retry(text, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={"text": text}
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retry {attempt + 1} after {wait_time}s")
                time.sleep(wait_time)
            else:
                raise
```

## OpenAPI/Swagger Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI spec: `http://localhost:8000/openapi.json`
