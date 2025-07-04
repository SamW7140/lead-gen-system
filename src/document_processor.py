# Document processing module for lead generation system
# Handles text extraction from PDFs and OCR for images

import os
import logging
from typing import Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: str) -> Optional[str]:
    # Extract text content from a file (PDF or image)
    # Args: file_path (str) - Path to the file to process
    # Returns: Optional[str] - Extracted text content or None if extraction fails
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    file_extension = Path(file_path).suffix.lower()
    logger.info(f"Processing file: {file_path} (type: {file_extension})")
    
    try:
        if file_extension == '.pdf':
            return _extract_text_from_pdf(file_path)
        elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return _extract_text_from_image(file_path)
        else:
            logger.error(f"Unsupported file type: {file_extension}")
            return None
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return None

def _extract_text_from_pdf(file_path: str) -> Optional[str]:
    # Extract text from a PDF file using multiple methods
    # Args: file_path (str) - Path to the PDF file
    # Returns: Optional[str] - Extracted text content
    text_content = ""
    
    # Try pdfplumber first (more reliable for complex PDFs)
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
        
        if text_content.strip():
            logger.info(f"Successfully extracted text from PDF using pdfplumber: {len(text_content)} characters")
            return text_content.strip()
    except ImportError:
        logger.warning("pdfplumber not available, falling back to PyPDF2")
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}, falling back to PyPDF2")
    
    # Fallback to PyPDF2
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
        
        if text_content.strip():
            logger.info(f"Successfully extracted text from PDF using PyPDF2: {len(text_content)} characters")
            return text_content.strip()
        else:
            logger.warning(f"No text extracted from PDF {file_path} - may be scanned/image-based")
            return None
    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {e}")
        return None

def _extract_text_from_image(file_path: str) -> Optional[str]:
    # Extract text from an image file using OCR
    # Args: file_path (str) - Path to the image file
    # Returns: Optional[str] - Extracted text content
    try:
        from PIL import Image
        import pytesseract
        
        # Open and process the image
        image = Image.open(file_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extract text using pytesseract
        text_content = pytesseract.image_to_string(image)
        
        if text_content.strip():
            logger.info(f"Successfully extracted text from image using OCR: {len(text_content)} characters")
            return text_content.strip()
        else:
            logger.warning(f"No text found in image {file_path}")
            return None
            
    except ImportError as e:
        logger.error(f"Required library not available for OCR: {e}")
        logger.error("Please install: pip install pytesseract pillow")
        logger.error("And install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        return None
    except Exception as e:
        logger.error(f"OCR extraction failed for {file_path}: {e}")
        return None

def get_processable_files(directory: str) -> list[str]:
    # Get list of all processable files in a directory
    # Args: directory (str) - Directory path to scan
    # Returns: list[str] - List of file paths that can be processed
    if not os.path.exists(directory):
        logger.error(f"Directory not found: {directory}")
        return []
    
    supported_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    processable_files = []
    
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            file_extension = Path(file_path).suffix.lower()
            if file_extension in supported_extensions:
                processable_files.append(file_path)
    
    logger.info(f"Found {len(processable_files)} processable files in {directory}")
    return sorted(processable_files) 