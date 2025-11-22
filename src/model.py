"""Model loading and inference logic."""

import os
from typing import Dict, Any, List
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from loguru import logger

from .config import settings


class LegalTextClassifier:
    """Legal text classification model wrapper."""
    
    def __init__(self):
        """Initialize the model and tokenizer."""
        self.model = None
        self.tokenizer = None
        self.device = None
        self.model_loaded = False
        
    def load_model(self):
        """Load the model and tokenizer from HuggingFace."""
        try:
            logger.info(f"Loading model: {settings.model_name}")
            logger.info(f"Device: {settings.device}")
            
            # Set cache directory
            os.environ["TRANSFORMERS_CACHE"] = settings.model_cache_dir
            
            # Determine device
            if settings.device == "cuda" and torch.cuda.is_available():
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")
            
            logger.info(f"Using device: {self.device}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.model_name,
                cache_dir=settings.model_cache_dir
            )
            
            self.model = AutoModelForSequenceClassification.from_pretrained(
                settings.model_name,
                cache_dir=settings.model_cache_dir
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            self.model_loaded = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Perform inference on input text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary containing predictions and scores
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Perform inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            # Get predicted class and confidence
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
            
            # Get all class probabilities
            all_scores = probabilities[0].cpu().numpy().tolist()
            
            # Get label mapping if available
            id2label = self.model.config.id2label if hasattr(self.model.config, 'id2label') else None
            
            result = {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "all_scores": all_scores
            }
            
            if id2label:
                result["predicted_label"] = id2label.get(predicted_class, f"LABEL_{predicted_class}")
                result["all_labels"] = {id2label.get(i, f"LABEL_{i}"): score for i, score in enumerate(all_scores)}
            
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Perform inference on a batch of texts.
        
        Args:
            texts: List of input texts to classify
            
        Returns:
            List of dictionaries containing predictions and scores
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Tokenize inputs
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Perform inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
            
            # Process results
            results = []
            id2label = self.model.config.id2label if hasattr(self.model.config, 'id2label') else None
            
            for i in range(len(texts)):
                predicted_class = torch.argmax(probabilities[i], dim=-1).item()
                confidence = probabilities[i][predicted_class].item()
                all_scores = probabilities[i].cpu().numpy().tolist()
                
                result = {
                    "predicted_class": predicted_class,
                    "confidence": confidence,
                    "all_scores": all_scores
                }
                
                if id2label:
                    result["predicted_label"] = id2label.get(predicted_class, f"LABEL_{predicted_class}")
                    result["all_labels"] = {id2label.get(j, f"LABEL_{j}"): score for j, score in enumerate(all_scores)}
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during batch prediction: {str(e)}")
            raise


# Global model instance
model_instance = None


def get_model() -> LegalTextClassifier:
    """Get or create the global model instance."""
    global model_instance
    if model_instance is None:
        model_instance = LegalTextClassifier()
        model_instance.load_model()
    return model_instance
