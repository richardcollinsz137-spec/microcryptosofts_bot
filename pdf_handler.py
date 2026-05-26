import io
import os
import logging
import pdfplumber
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

# Fallback path adjustment for Render binary routing
if os.path.exists("/opt/render/project/src/bin/tesseract"):
    pytesseract.pytesseract.tesseract_cmd = "/opt/render/project/src/bin/tesseract"

def extract_text_from_pdf(file_path: str) -> str:
    """
    Tries a standard programmatic text extraction. If the resulting text
    is missing or too short, it assumes a scanned document and runs OCR.
    """
    extracted_text = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_text.append(page_text)
                    
        full_text = "\n".join(extracted_text).strip()
        
        # Quality Gate Check: If less than 15 characters, it's likely a scanned image
        if len(full_text) > 15:
            logger.info("Successfully extracted native digital text layer.")
            return full_text
            
        logger.info("Digital text layers low/empty. Cascading to OCR fallback...")
        return run_ocr_fallback(file_path)

    except Exception as e:
        logger.error(f"Error executing structural PDF parsing: {str(e)}", exc_info=True)
        raise RuntimeError("Failed to decode PDF structural data.")

def run_ocr_fallback(file_path: str) -> str:
    """Converts PDF pages to high-resolution memory buffers and runs optical character recognition."""
    ocr_results = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                logger.info(f"Processing OCR engine for page {page_index}...")
                
                # Render the vector PDF map to a sharp 200 DPI bitmap
                image_object = page.to_image(resolution=200)
                image_buffer = io.BytesIO()
                image_object.save(image_buffer, format="PNG")
                image_buffer.seek(0)
                
                # Pass off bytes to pytesseract
                pil_image = Image.open(image_buffer)
                page_text = pytesseract.image_to_string(pil_image)
                
                if page_text.strip():
                    ocr_results.append(page_text)
                    
        return "\n".join(ocr_results).strip()
    except Exception as e:
        logger.error(f"OCR Core Processing failure: {str(e)}")
        raise RuntimeError("OCR subsystem failed. Tesseract binary may be missing from environment paths.")
