"""Test script for OCR functionality."""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from loguru import logger

# Create a test image
def create_test_image():
    """Create a simple test image with text."""
    import tempfile
    import os
    
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
    
    # Draw text
    text = "Dieu 1. Pham vi dieu chinh cua Luat nay"
    d.text((10, 80), text, fill='black', font=font)
    
    # Save the image
    image_path = test_dir / "test_legal_document.jpg"
    img.save(image_path)
    print(f"✓ Test image created at {image_path}")
    return image_path


def test_ocr_imports():
    """Test that OCR modules can be imported."""
    try:
        from src.ocr_model import OCRProcessor, get_ocr_processor
        print("✓ OCR modules can be imported")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_ocr_processor_initialization():
    """Test OCR processor initialization."""
    try:
        from src.ocr_model import OCRProcessor
        
        # Test EasyOCR initialization
        print("\nTesting EasyOCR initialization...")
        processor = OCRProcessor(engine="easyocr", languages=['en'])
        processor.initialize()
        print("✓ EasyOCR processor initialized successfully")
        return True
    except Exception as e:
        print(f"✗ OCR processor initialization error: {e}")
        return False


def test_ocr_processing():
    """Test OCR processing on a test image."""
    try:
        from src.ocr_model import OCRProcessor
        
        # Create test image
        print("\nTesting OCR processing...")
        image_path = create_test_image()
        
        # Open image
        image = Image.open(image_path)
        
        # Process with EasyOCR
        print("Processing image with EasyOCR...")
        processor = OCRProcessor(engine="easyocr", languages=['en'])
        processor.initialize()
        result = processor.process_image(image)
        
        print(f"✓ OCR processing successful")
        print(f"  - Extracted text: {result['text'][:100]}...")
        print(f"  - Average confidence: {result['average_confidence']:.2%}")
        print(f"  - Number of lines: {len(result['lines'])}")
        print(f"  - Engine: {result['engine']}")
        
        # Verify result structure
        assert 'text' in result
        assert 'lines' in result
        assert 'average_confidence' in result
        assert 'engine' in result
        assert result['engine'] == 'easyocr'
        
        return True
    except Exception as e:
        print(f"✗ OCR processing error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes are defined correctly."""
    try:
        from src.api import app
        
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        expected_routes = ["/ocr/upload", "/ocr/upload-and-classify"]
        
        for expected in expected_routes:
            if expected not in routes:
                print(f"✗ Missing route: {expected}")
                return False
        
        print("✓ All OCR API routes are defined")
        for route in app.routes:
            if hasattr(route, 'path') and '/ocr/' in route.path and hasattr(route, 'methods'):
                print(f"  - {list(route.methods)[0]:6s} {route.path}")
        return True
    except Exception as e:
        print(f"✗ API routes error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing OCR Functionality")
    print("=" * 60)
    print()
    
    tests = [
        ("OCR Module Imports", test_ocr_imports),
        ("API Routes", test_api_routes),
        ("OCR Processor Initialization", test_ocr_processor_initialization),
        ("OCR Processing", test_ocr_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All OCR tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
