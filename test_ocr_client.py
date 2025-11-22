"""Test client for OCR API endpoints."""

import requests
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import tempfile


def create_test_image():
    """Create a simple test image with text."""
    test_dir = Path(tempfile.gettempdir()) / "test_ocr_images"
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test image with text
    img = Image.new('RGB', (800, 200), color='white')
    d = ImageDraw.Draw(img)
    
    # Try to use default font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except (OSError, IOError):
        font = ImageFont.load_default()
    
    # Draw Vietnamese legal text (using ASCII approximation for test)
    text = "Dieu 1. Pham vi dieu chinh cua Luat nay"
    d.text((10, 80), text, fill='black', font=font)
    
    # Save the image
    image_path = test_dir / "test_legal_document.jpg"
    img.save(image_path)
    print(f"✓ Test image created at {image_path}")
    return image_path


def test_ocr_upload(base_url, image_path):
    """Test OCR upload endpoint."""
    print("\n" + "=" * 60)
    print("Testing /ocr/upload endpoint")
    print("=" * 60)
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/ocr/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ OCR upload successful!")
            print(f"\nExtracted text:")
            print(f"  {result['text']}")
            print(f"\nConfidence: {result['average_confidence']:.2%}")
            print(f"Engine: {result['engine']}")
            print(f"Number of lines detected: {len(result['lines'])}")
            print(f"\nFull response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_ocr_upload_and_classify(base_url, image_path):
    """Test OCR upload and classify endpoint."""
    print("\n" + "=" * 60)
    print("Testing /ocr/upload-and-classify endpoint")
    print("=" * 60)
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/ocr/upload-and-classify", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ OCR upload and classify successful!")
            
            print(f"\nOCR Result:")
            print(f"  Text: {result['ocr_result']['text']}")
            print(f"  Confidence: {result['ocr_result']['average_confidence']:.2%}")
            print(f"  Engine: {result['ocr_result']['engine']}")
            
            if result['classification']:
                print(f"\nClassification Result:")
                print(f"  Predicted class: {result['classification']['predicted_class']}")
                if 'predicted_label' in result['classification']:
                    print(f"  Predicted label: {result['classification']['predicted_label']}")
                print(f"  Confidence: {result['classification']['confidence']:.2%}")
            else:
                print("\nNo classification result (text might be empty or classification failed)")
            
            print(f"\nFull response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("OCR API Client Test")
    print("=" * 60)
    
    # Create test image
    print("\nCreating test image...")
    image_path = create_test_image()
    
    # Test endpoints
    results = []
    results.append(test_ocr_upload(base_url, image_path))
    results.append(test_ocr_upload_and_classify(base_url, image_path))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed.")


if __name__ == "__main__":
    main()
