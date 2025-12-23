"""
PDF Generation Utility Module

Utility for creating PDF documents from storyboard images.
"""
import os
from typing import List, Optional
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from app.config import settings


class PDFGenerator:
    """Utility for generating PDF documents from images."""
    
    @staticmethod
    def create_storyboard_pdf(
        image_paths: List[str], 
        session_id: str,
        filename: str = "storyboard.pdf",
        frame_descriptions: Optional[List[str]] = None
    ) -> str:
        """
        Create a PDF document with all storyboard frames.
        
        Args:
            image_paths: List of paths to image files
            session_id: Unique session identifier
            filename: Name of the PDF file
            frame_descriptions: Optional list of frame descriptions to include
        
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
        frame_number_height = 0.3 * inch  # Space for frame number at bottom
        description_area_height = 1.5 * inch  # Space reserved for description text below image
        max_img_width = page_width - (2 * margin)
        max_img_height = page_height - (2 * margin) - frame_number_height - description_area_height
        
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
                
                # Position image at top of page
                x = (page_width - scaled_width) / 2
                y = page_height - margin - scaled_height
                
                # Draw image
                c.drawImage(
                    img_path,
                    x, y,
                    width=scaled_width,
                    height=scaled_height,
                    preserveAspectRatio=True
                )
                
                # Add frame description right below the image
                if frame_descriptions and idx < len(frame_descriptions):
                    description = frame_descriptions[idx]
                    
                    # Start description right below the image
                    desc_start_y = y - 0.3 * inch
                    
                    # Add "Description:" label
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(margin, desc_start_y, "Description:")
                    
                    # Add the description text with word wrap
                    c.setFont("Helvetica", 9)
                    text_y = desc_start_y - 0.2 * inch
                    
                    # Simple text wrapping
                    max_chars_per_line = 90
                    words = description.split()
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        if len(test_line) <= max_chars_per_line:
                            current_line = test_line
                        else:
                            if current_line:
                                c.drawString(margin, text_y, current_line)
                                text_y -= 0.15 * inch
                            current_line = word
                    
                    # Draw the last line
                    if current_line:
                        c.drawString(margin, text_y, current_line)
                
                # Add frame number at bottom
                frame_number = idx + 1
                c.setFont("Helvetica-Bold", 12)
                c.drawCentredString(
                    page_width / 2,
                    margin / 2,
                    f"Frame {frame_number}"
                )
        
        c.save()
        return pdf_path
