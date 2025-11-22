"""Test script to validate project structure without requiring model download."""

import sys
from pathlib import Path

def test_project_structure():
    """Test that all required files exist."""
    required_files = [
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yml",
        "README.md",
        ".env.example",
        ".gitignore",
        "run.sh",
        "example_client.py",
        "src/__init__.py",
        "src/config.py",
        "src/model.py",
        "src/api.py",
        "src/main.py",
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    print("✓ All required files exist")
    return True


def test_imports():
    """Test that all modules can be imported."""
    try:
        from src.config import settings
        from src.model import LegalTextClassifier
        from src.api import app
        from src import main
        
        print("✓ All modules can be imported")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_configuration():
    """Test configuration settings."""
    try:
        from src.config import settings
        
        assert settings.model_name == "protonx-models/protonx-legal-tc"
        assert settings.api_port == 8000
        assert settings.device == "cpu"
        
        print("✓ Configuration is correct")
        print(f"  - Model: {settings.model_name}")
        print(f"  - API Port: {settings.api_port}")
        print(f"  - Device: {settings.device}")
        return True
    except AssertionError as e:
        print(f"✗ Configuration error: {e}")
        return False


def test_api_routes():
    """Test that API routes are defined."""
    try:
        from src.api import app
        
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        expected_routes = ["/", "/health", "/predict", "/predict/batch", "/model-info"]
        
        for expected in expected_routes:
            if expected not in routes:
                print(f"✗ Missing route: {expected}")
                return False
        
        print("✓ All API routes are defined")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  - {list(route.methods)[0]:6s} {route.path}")
        return True
    except Exception as e:
        print(f"✗ API routes error: {e}")
        return False


def test_model_class():
    """Test that model class is properly defined."""
    try:
        from src.model import LegalTextClassifier
        
        # Check if class has required methods
        required_methods = ['load_model', 'predict', 'predict_batch']
        for method in required_methods:
            if not hasattr(LegalTextClassifier, method):
                print(f"✗ Missing method: {method}")
                return False
        
        print("✓ Model class is properly defined")
        print(f"  - Methods: {', '.join(required_methods)}")
        return True
    except Exception as e:
        print(f"✗ Model class error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing ProtonX Legal OCR Service Project Structure")
    print("=" * 60)
    print()
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("API Routes", test_api_routes),
        ("Model Class", test_model_class),
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
        print("\n✓ All tests passed! The project structure is ready.")
        print("\nNote: Model download requires internet access to HuggingFace.")
        print("In a production environment with internet access, the service")
        print("will automatically download and cache the model on first use.")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
