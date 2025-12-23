"""
Image Generation Service Module

Business logic for sequential image generation from storyboard frames.
"""
import os
import json
from typing import List, Tuple, Generator, Dict, Any
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
    
    def generate_sequential_images_stream(
        self, 
        frames: List[FrameData]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generate images sequentially with progress events.
        
        Args:
            frames: List of FrameData with descriptions
        
        Yields:
            Dict events with frame progress information
        
        Raises:
            ValueError: If image generation fails
        """
        previous_image_path = None
        
        for frame in frames:
            # Emit frame start event
            yield {
                'type': 'frame_start',
                'frame_number': frame.frame_number
            }
            
            try:
                if previous_image_path is None:
                    image_bytes = self.agent.generate_first_image(frame.description)
                else:
                    image_bytes = self.agent.generate_next_image(
                        description=frame.description,
                        previous_image_path=previous_image_path
                    )
                
                # Save current image to temp file for next iteration reference
                previous_image_path = os.path.join(
                    self.temp_dir,
                    f"temp_frame_{frame.frame_number}.png"
                )
                with open(previous_image_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Emit frame complete event
                yield {
                    'type': 'frame_complete',
                    'frame_number': frame.frame_number,
                    'image_bytes': image_bytes
                }
                
            except (IOError, OSError, FileNotFoundError, ValueError) as e:
                self._cleanup_temp_files()
                raise ValueError(
                    f"Failed to generate image for frame {frame.frame_number}: {str(e)}"
                )
        
        # Clean up temp files after successful generation
        self._cleanup_temp_files()
    
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
    
    def edit_frame(
        self, 
        session_id: str, 
        frame_number: int, 
        edit_instructions: str,
        storyboard_context: str
    ) -> str:
        """
        Edit a specific frame in a storyboard session.
        
        Args:
            session_id: The session ID containing the frame
            frame_number: The frame number to edit (1-based)
            edit_instructions: User's instructions for modifying the frame
            storyboard_context: The overall storyboard description for context
        
        Returns:
            Path to the edited frame image
        
        Raises:
            FileNotFoundError: If the frame doesn't exist
            ValueError: If editing fails
        """
        # Build the path to the current frame
        session_dir = os.path.join(settings.OUTPUT_DIR, session_id)
        current_frame_path = os.path.join(
            session_dir, 
            f"frame_{frame_number:03d}.png"
        )
        
        if not os.path.isfile(current_frame_path):
            raise FileNotFoundError(f"Frame {frame_number} not found in session {session_id}")
        
        try:
            # Generate edited frame using the agent
            edited_image_bytes = self.agent.edit_frame(
                current_image_path=current_frame_path,
                edit_instructions=edit_instructions,
                storyboard_context=storyboard_context
            )
            
            # Overwrite the original frame with the edited version
            with open(current_frame_path, 'wb') as f:
                f.write(edited_image_bytes)
            
            return current_frame_path
            
        except (IOError, OSError, ValueError) as e:
            raise ValueError(f"Failed to edit frame {frame_number}: {str(e)}")
    
    def get_session_frame_paths(self, session_id: str) -> List[str]:
        """
        Get all frame image paths for a session in order.
        
        Args:
            session_id: The session ID to get frames for
        
        Returns:
            List of frame image paths sorted by frame number
        """
        session_dir = os.path.join(settings.OUTPUT_DIR, session_id)
        
        if not os.path.isdir(session_dir):
            return []
        
        frame_files = [
            f for f in os.listdir(session_dir) 
            if f.startswith('frame_') and f.endswith('.png')
        ]
        frame_files.sort()
        
        return [os.path.join(session_dir, f) for f in frame_files]
    
    def save_frame_descriptions(self, frames: List[FrameData], session_id: str) -> None:
        """
        Save frame descriptions to a metadata file.
        
        Args:
            frames: List of FrameData with descriptions
            session_id: Unique session identifier
        """
        session_dir = os.path.join(settings.OUTPUT_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        metadata = {
            'frames': [
                {
                    'frame_number': frame.frame_number,
                    'description': frame.description
                }
                for frame in frames
            ]
        }
        
        metadata_path = os.path.join(session_dir, 'metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def load_frame_descriptions(self, session_id: str) -> List[str]:
        """
        Load frame descriptions from metadata file.
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            List of frame descriptions in order, or empty list if not found
        """
        session_dir = os.path.join(settings.OUTPUT_DIR, session_id)
        metadata_path = os.path.join(session_dir, 'metadata.json')
        
        if not os.path.isfile(metadata_path):
            return []
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Sort by frame_number and extract descriptions
            frames = sorted(metadata['frames'], key=lambda x: x['frame_number'])
            return [frame['description'] for frame in frames]
        except (json.JSONDecodeError, KeyError, IOError):
            return []
    
    def delete_pdf(self, session_id: str) -> bool:
        """
        Delete the PDF file for a session if it exists.
        
        Args:
            session_id: The session ID containing the PDF
        
        Returns:
            True if PDF was deleted, False if it didn't exist
        """
        session_dir = os.path.join(settings.OUTPUT_DIR, session_id)
        pdf_path = os.path.join(session_dir, "storyboard.pdf")
        
        if os.path.isfile(pdf_path):
            try:
                os.remove(pdf_path)
                return True
            except (OSError, PermissionError):
                return False
        return False
        
        return saved_paths
