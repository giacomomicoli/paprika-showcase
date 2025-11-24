"""
Image Generation Service Module

Business logic for sequential image generation from storyboard frames.
"""
import os
from typing import List, Tuple
from app.agents.image_generation_agent import ImageGenerationAgent
from app.models.storyboard import FrameData
from app.config import settings


class ImageGenerationService:
    """Service for handling sequential image generation operations."""
    
    def __init__(self):
        """Initialize the image generation service."""
        self.agent = ImageGenerationAgent()
        self._ensure_output_directory()
        self._ensure_temp_directory()
    
    def _ensure_output_directory(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    def _ensure_temp_directory(self):
        """Create temporary directory for intermediate images."""
        self.temp_dir = os.path.join(settings.OUTPUT_DIR, '.temp')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def generate_sequential_images(self, frames: List[FrameData]) -> List[Tuple[int, bytes]]:
        """
        Generate images sequentially, using each previous image as reference.
        
        Args:
            frames: List of FrameData with descriptions
        
        Returns:
            List of tuples containing (frame_number, image_bytes)
        
        Raises:
            ValueError: If image generation fails
        """
        generated_images = []
        previous_image_path = None
        
        for frame in frames:
            try:
                if previous_image_path is None:
                    # First frame: generate from description only
                    image_bytes = self.agent.generate_first_image(frame.description)
                else:
                    # Subsequent frames: use previous image as reference
                    image_bytes = self.agent.generate_next_image(
                        description=frame.description,
                        previous_image_path=previous_image_path
                    )
                
                generated_images.append((frame.frame_number, image_bytes))
                
                # Save current image to temp file for next iteration reference
                previous_image_path = os.path.join(
                    self.temp_dir,
                    f"temp_frame_{frame.frame_number}.png"
                )
                with open(previous_image_path, 'wb') as f:
                    f.write(image_bytes)
                
            except (IOError, OSError, FileNotFoundError, ValueError) as e:
                # Clean up temp files on error
                self._cleanup_temp_files()
                raise ValueError(
                    f"Failed to generate image for frame {frame.frame_number}: {str(e)}"
                )
        
        # Clean up temp files after successful generation
        self._cleanup_temp_files()
        
        return generated_images
    
    def _cleanup_temp_files(self):
        """Remove temporary files created during generation."""
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except (OSError, PermissionError):
                    pass  # Ignore cleanup errors
    
    def save_images(self, images: List[Tuple[int, bytes]], session_id: str) -> List[str]:
        """
        Save generated images to disk.
        
        Args:
            images: List of tuples containing (frame_number, image_bytes)
            session_id: Unique session identifier for organizing files
        
        Returns:
            List of file paths where images were saved
        """
        session_dir = os.path.join(settings.OUTPUT_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        saved_paths = []
        for frame_number, image_bytes in images:
            file_path = os.path.join(
                session_dir, 
                f"frame_{frame_number:03d}.png"
            )
            
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            saved_paths.append(file_path)
        
        return saved_paths
