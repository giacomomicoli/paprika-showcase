"""
PDF Generation Utility Module

Utility for creating PDF documents from storyboard images.
"""
import os
from typing import List
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from app.config import settings


class PDFGenerator:
    """Utility for generating PDF documents from images."""
    
    @staticmethod
    def create_storyboard_pdf(
        image_paths: List[str], 
        session_id: str,
        filename: str = "storyboard.pdf"
    ) -> str:
        """
        Create a PDF document with all storyboard frames.
        
        Args:
            image_paths: List of paths to image files
            session_id: Unique session identifier
            filename: Name of the PDF file
        
        Returns:
            Path to the generated PDF file
        """
        session_dir = os.path.join(settings.OUTPUT_DIR, session_id)
        pdf_path = os.path.join(session_dir, filename)
        
        # Create PDF canvas
        c = canvas.Canvas(pdf_path, pagesize=A4)
        page_width, page_height = A4
        
        # Margins and layout settings
        margin = 0.5 * inch
        max_img_width = page_width - (2 * margin)
        max_img_height = page_height - (2 * margin)
        
        for idx, img_path in enumerate(image_paths):
            if idx > 0:
                c.showPage()  # Start new page for each frame after the first
            
            # Open image to get dimensions
            with Image.open(img_path) as img:
                img_width, img_height = img.size
                
                # Calculate scaling to fit page while maintaining aspect ratio
                width_ratio = max_img_width / img_width
                height_ratio = max_img_height / img_height
                scale = min(width_ratio, height_ratio)
                
                scaled_width = img_width * scale
                scaled_height = img_height * scale
                
                # Center image on page
                x = (page_width - scaled_width) / 2
                y = (page_height - scaled_height) / 2
                
                # Draw image
                c.drawImage(
                    img_path,
                    x, y,
                    width=scaled_width,
                    height=scaled_height,
                    preserveAspectRatio=True
                )
                
                # Add frame number at bottom
                frame_number = idx + 1
                c.setFont("Helvetica", 10)
                c.drawCentredString(
                    page_width / 2,
                    margin / 2,
                    f"Frame {frame_number}"
                )
        
        c.save()
        return pdf_path
