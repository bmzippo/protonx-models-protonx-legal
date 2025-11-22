"""OCR model for extracting text from images."""

import io
from typing import Dict, Any, Optional
from PIL import Image
from loguru import logger

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not available")

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available")


class OCRProcessor:
    """OCR processor for extracting text from images."""
    
    def __init__(self, engine: str = "easyocr", languages: list = None):
        """
        Initialize the OCR processor.
        
        Args:
            engine: OCR engine to use ('easyocr' or 'tesseract')
            languages: List of language codes to support (default: ['vi', 'en'])
        """
        self.engine = engine.lower()
        self.languages = languages or ['vi', 'en']
        self.reader = None
        self._initialized = False
        
    def initialize(self):
        """Initialize the OCR engine."""
        if self._initialized:
            return
            
        try:
            if self.engine == "easyocr":
                if not EASYOCR_AVAILABLE:
                    raise RuntimeError("EasyOCR is not installed")
                logger.info(f"Initializing EasyOCR with languages: {self.languages}")
                self.reader = easyocr.Reader(self.languages, gpu=False)
                logger.info("EasyOCR initialized successfully")
            elif self.engine == "tesseract":
                if not PYTESSERACT_AVAILABLE:
                    raise RuntimeError("pytesseract is not installed")
                logger.info("Using Tesseract OCR")
                # Test if tesseract is available
                try:
                    pytesseract.get_tesseract_version()
                    logger.info("Tesseract OCR initialized successfully")
                except Exception as e:
                    logger.error(f"Tesseract not found: {e}")
                    raise RuntimeError(f"Tesseract executable not found. Please install tesseract-ocr. Original error: {e}")
            else:
                raise ValueError(f"Unknown OCR engine: {self.engine}")
                
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize OCR engine: {str(e)}")
            raise
    
    def process_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text from an image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary containing extracted text and confidence scores
        """
        if not self._initialized:
            self.initialize()
        
        try:
            if self.engine == "easyocr":
                return self._process_with_easyocr(image)
            elif self.engine == "tesseract":
                return self._process_with_tesseract(image)
            else:
                raise ValueError(f"Unknown OCR engine: {self.engine}")
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise
    
    def _process_with_easyocr(self, image: Image.Image) -> Dict[str, Any]:
        """Process image with EasyOCR."""
        # Convert PIL Image to numpy array
        import numpy as np
        img_array = np.array(image)
        
        # Perform OCR
        results = self.reader.readtext(img_array)
        
        # Extract text and confidence scores
        texts = []
        confidences = []
        full_text = []
        
        for (bbox, text, confidence) in results:
            texts.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": bbox
            })
            confidences.append(float(confidence))
            full_text.append(text)
        
        # Calculate average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "text": " ".join(full_text),
            "lines": texts,
            "average_confidence": avg_confidence,
            "engine": "easyocr"
        }
    
    def _process_with_tesseract(self, image: Image.Image) -> Dict[str, Any]:
        """Process image with Tesseract."""
        # Get language string for tesseract (e.g., 'vie+eng')
        lang_map = {'vi': 'vie', 'en': 'eng'}
        lang_string = '+'.join([lang_map.get(lang, lang) for lang in self.languages])
        
        # Extract text
        text = pytesseract.image_to_string(image, lang=lang_string)
        
        # Get detailed information with confidence
        data = pytesseract.image_to_data(image, lang=lang_string, output_type=pytesseract.Output.DICT)
        
        # Extract lines with confidence scores
        lines = []
        confidences = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:  # Filter out low confidence
                lines.append({
                    "text": data['text'][i],
                    "confidence": float(data['conf'][i]) / 100.0,  # Convert to 0-1 range
                    "bbox": [
                        data['left'][i],
                        data['top'][i],
                        data['left'][i] + data['width'][i],
                        data['top'][i] + data['height'][i]
                    ]
                })
                confidences.append(float(data['conf'][i]) / 100.0)
        
        # Calculate average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "text": text.strip(),
            "lines": lines,
            "average_confidence": avg_confidence,
            "engine": "tesseract"
        }


# Global OCR processor instance
_ocr_processor = None


def get_ocr_processor(engine: str = "easyocr", languages: list = None) -> OCRProcessor:
    """
    Get or create the global OCR processor instance.
    
    Args:
        engine: OCR engine to use ('easyocr' or 'tesseract')
        languages: List of language codes to support
        
    Returns:
        OCRProcessor instance
    """
    global _ocr_processor
    languages = languages or ['vi', 'en']
    
    # Check if we need to create a new processor or if the existing one matches
    if _ocr_processor is None or _ocr_processor.engine != engine or _ocr_processor.languages != languages:
        _ocr_processor = OCRProcessor(engine=engine, languages=languages)
        _ocr_processor.initialize()
    return _ocr_processor
