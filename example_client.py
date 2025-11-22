"""Example client for the ProtonX Legal Text Classification API."""

import requests
import json


def test_api():
    """Test the API with example requests."""
    
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    print("Testing root endpoint...")
    response = requests.get(f"{base_url}/")
    print(f"Response: {response.json()}\n")
    
    # Test health endpoint
    print("Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Response: {response.json()}\n")
    
    # Test model info endpoint
    print("Testing model info endpoint...")
    response = requests.get(f"{base_url}/model-info")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    
    # Test single prediction
    print("Testing single text prediction...")
    test_text = "Điều 1. Phạm vi điều chỉnh của Luật này là quy định về..."
    
    response = requests.post(
        f"{base_url}/predict",
        json={"text": test_text}
    )
    print(f"Input text: {test_text}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    
    # Test batch prediction
    print("Testing batch prediction...")
    test_texts = [
        "Điều 1. Phạm vi điều chỉnh của Luật này...",
        "Hợp đồng mua bán nhà đất giữa hai bên...",
        "Quyết định số 123/QĐ-TTg về việc..."
    ]
    
    response = requests.post(
        f"{base_url}/predict/batch",
        json={"texts": test_texts}
    )
    print(f"Input texts: {test_texts}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


if __name__ == "__main__":
    try:
        test_api()
        print("✓ All tests completed successfully!")
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
