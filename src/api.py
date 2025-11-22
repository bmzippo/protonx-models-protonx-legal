"""FastAPI application for the OCR service."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional
from loguru import logger
from PIL import Image, UnidentifiedImageError
import io

from .model import get_model
from .config import settings
from .ocr_model import get_ocr_processor


class TextInput(BaseModel):
    """Input model for single text classification."""
    text: str = Field(..., description="Text to classify", min_length=1)


class BatchTextInput(BaseModel):
    """Input model for batch text classification."""
    texts: List[str] = Field(..., description="List of texts to classify", min_length=1)


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    predicted_class: int
    confidence: float
    all_scores: List[float]
    predicted_label: Optional[str] = None
    all_labels: Optional[dict] = None


class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions."""
    predictions: List[PredictionResponse]


class OCRResponse(BaseModel):
    """Response model for OCR."""
    text: str
    lines: List[dict]
    average_confidence: float
    engine: str


class OCRWithClassificationResponse(BaseModel):
    """Response model for OCR with classification."""
    ocr_result: OCRResponse
    classification: Optional[PredictionResponse] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - load model on startup, cleanup on shutdown."""
    # Startup
    logger.info("Starting up the API server...")
    try:
        # Initialize model
        model = get_model()
        logger.info("Model loaded successfully on startup")
    except Exception as e:
        logger.error(f"Failed to load model on startup: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down the API server...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="ProtonX Legal Text Classification API",
    description="API for legal document text classification using ProtonX models",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ProtonX Legal Text Classification API",
        "version": "0.1.0",
        "model": settings.model_name
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        model = get_model()
        return {
            "status": "healthy",
            "model_loaded": model.model_loaded
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: TextInput):
    """
    Classify a single text.
    
    Args:
        input_data: Input text to classify
        
    Returns:
        Classification results with predicted class and confidence scores
    """
    try:
        model = get_model()
        result = model.predict(input_data.text)
        return result
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(input_data: BatchTextInput):
    """
    Classify multiple texts in a batch.
    
    Args:
        input_data: List of texts to classify
        
    Returns:
        List of classification results
    """
    try:
        model = get_model()
        results = model.predict_batch(input_data.texts)
        return {"predictions": results}
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/model-info")
async def model_info():
    """Get information about the loaded model."""
    try:
        model = get_model()
        
        info = {
            "model_name": settings.model_name,
            "device": str(model.device),
            "model_loaded": model.model_loaded
        }
        
        # Add label information if available
        if model.model and hasattr(model.model.config, 'id2label'):
            info["labels"] = model.model.config.id2label
            info["num_labels"] = len(model.model.config.id2label)
        
        return info
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


async def validate_and_load_image(file: UploadFile) -> Image.Image:
    """
    Validate and load an uploaded image file.
    
    Args:
        file: Uploaded file
        
    Returns:
        PIL Image object
        
    Raises:
        HTTPException: If validation fails
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image data
    image_data = await file.read()
    
    # Check file size
    if len(image_data) > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_upload_size} bytes"
        )
    
    # Open image with PIL
    try:
        image = Image.open(io.BytesIO(image_data))
        return image
    except (UnidentifiedImageError, OSError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")


def get_configured_ocr_processor():
    """
    Get OCR processor with configuration from settings.
    
    Returns:
        OCRProcessor instance configured with settings
    """
    # Parse languages and strip whitespace
    languages = [lang.strip() for lang in settings.ocr_languages.split(',')]
    return get_ocr_processor(engine=settings.ocr_engine, languages=languages)


@app.post("/ocr/upload", response_model=OCRResponse)
async def ocr_upload(file: UploadFile = File(...)):
    """
    Upload an image and extract text using OCR.
    
    Args:
        file: Image file to process (jpg, jpeg, png, etc.)
        
    Returns:
        OCR results with extracted text and confidence scores
    """
    try:
        # Validate and load image
        image = await validate_and_load_image(file)
        
        # Get OCR processor
        ocr_processor = get_configured_ocr_processor()
        
        # Process image
        result = ocr_processor.process_image(image)
        
        logger.info(f"OCR processed successfully. Extracted {len(result['text'])} characters")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/ocr/upload-and-classify", response_model=OCRWithClassificationResponse)
async def ocr_upload_and_classify(file: UploadFile = File(...)):
    """
    Upload an image, extract text using OCR, and classify the extracted text.
    
    Args:
        file: Image file to process (jpg, jpeg, png, etc.)
        
    Returns:
        OCR results and classification of the extracted text
    """
    try:
        # Validate and load image
        image = await validate_and_load_image(file)
        
        # Get OCR processor
        ocr_processor = get_configured_ocr_processor()
        
        # Process image
        ocr_result = ocr_processor.process_image(image)
        
        logger.info(f"OCR processed successfully. Extracted {len(ocr_result['text'])} characters")
        
        # Classify extracted text if there's any
        classification = None
        if ocr_result['text'].strip():
            try:
                model = get_model()
                classification = model.predict(ocr_result['text'])
                logger.info(f"Text classified successfully")
            except Exception as e:
                logger.warning(f"Classification failed: {str(e)}")
                # Continue without classification
        
        return {
            "ocr_result": ocr_result,
            "classification": classification
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
