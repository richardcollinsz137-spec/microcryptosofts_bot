import io
import logging
import pdfplumber
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Attempts clean digital extraction. 
    If structural text length is less than 10 characters, it flags the PDF as scanned
    and triggers the Tesseract OCR fallback engine.
    """
    extracted_text = []
    
    try:
        # Step 1: Attempt standard programmatic text parsing
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_text.append(page_text)
        
        full_text = "\n".join(extracted_text).strip()
        
        # Step 2: Quality Gate Trigger for Scanned / Image-Based PDFs
        if len(full_text) > 10:
            return full_text
            
        logger.info("Digital text layer insufficient. Triggering OCR engine...")
        return run_ocr_fallback(file_path)

    except Exception as e:
        logger.error(f"Error inside text extraction module: {str(e)}", exc_info=True)
        raise RuntimeError("Failed to correctly process the PDF structure.")

def run_ocr_fallback(file_path: str) -> str:
    """Converts layout objects to image buffers and feeds them to Tesseract OCR."""
    ocr_text = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                logger.info(f"Performing optical character recognition on page {i}...")
                # Render the vector PDF layout stream to a 200 DPI bitmap image 
                img_obj = page.to_image(resolution=200)
                
                # Convert the internal frame pointer back into an active memory bytes buffer
                img_bytes = io.BytesIO()
                img_obj.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                
                # Hand off image stream to PyTesseract
                pil_img = Image.open(img_bytes)
                page_ocr = pytesseract.image_to_string(pil_img)
                
                if page_ocr.strip():
                    ocr_text.append(page_ocr)
                    
        return "\n".join(ocr_text).strip()
    except Exception as e:
        logger.error(f"OCR Pipeline Exception: {str(e)}")
        raise RuntimeError("OCR processing failed. The system binary may be unconfigured.")
