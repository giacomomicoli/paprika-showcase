"""
Streaming Storyboard Service Module

Business logic for storyboard generation with progress streaming.
Extends StoryboardService to add real-time SSE progress events.
"""
from typing import Generator, Dict, Any

from app.services.storyboard_service import StoryboardService
from app.services.session_manager import SessionManager
from app.services.image_generation_service import ImageGenerationService
from app.services.pdf_generator import PDFGenerator
from app.config import settings


class StreamingStoryboardService(StoryboardService):
    """
    Service for handling storyboard generation with progress streaming.
    
    Extends StoryboardService to reuse frame generation logic while adding
    SSE-compatible progress events for real-time UI updates.
    """
    
    def __init__(self):
        """Initialize the streaming storyboard service."""
        super().__init__()
        # Override with fresh instances if needed for streaming context
        self.image_service = ImageGenerationService()
        self.pdf_generator = PDFGenerator()
    
    def generate_complete_storyboard_stream(
        self, 
        user_description: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generate complete storyboard with progress events.
        
        Yields events with the following types:
        - step_start: A step has started
        - step_progress: Progress within a step (for frame generation)
        - step_complete: A step has completed
        - complete: Generation is finished with final result
        - error: An error occurred
        """
        try:
            # Step 1: Analyzing description
            yield {
                'type': 'step_start',
                'step': 1,
                'step_name': 'analyzing',
                'message': 'Analyzing your description...'
            }
            
            storyboard_output = self.generate_frames(user_description)
            total_frames = storyboard_output.total_frames
            
            yield {
                'type': 'step_complete',
                'step': 1,
                'step_name': 'analyzing',
                'message': f'Analysis complete. Planning {total_frames} frames.',
                'total_frames': total_frames
            }
            
            # Step 2: Generate images with per-frame progress
            yield {
                'type': 'step_start',
                'step': 2,
                'step_name': 'generating',
                'message': 'Generating frame images...',
                'total_frames': total_frames
            }
            
            # Generate unique session ID for this storyboard
            session_id = self.session_manager.generate_session_id()
            
            # Generate images with progress updates
            generated_images = []
            for frame_event in self.image_service.generate_sequential_images_stream(
                storyboard_output.frames
            ):
                if frame_event['type'] == 'frame_complete':
                    generated_images.append(
                        (frame_event['frame_number'], frame_event['image_bytes'])
                    )
                    yield {
                        'type': 'step_progress',
                        'step': 2,
                        'step_name': 'generating',
                        'current_frame': frame_event['frame_number'],
                        'total_frames': total_frames,
                        'message': f"Generated frame {frame_event['frame_number']}/{total_frames}"
                    }
                elif frame_event['type'] == 'frame_start':
                    yield {
                        'type': 'step_progress',
                        'step': 2,
                        'step_name': 'generating',
                        'current_frame': frame_event['frame_number'],
                        'total_frames': total_frames,
                        'generating': True,
                        'message': f"Generating frame {frame_event['frame_number']}/{total_frames}..."
                    }
            
            yield {
                'type': 'step_complete',
                'step': 2,
                'step_name': 'generating',
                'message': f'Generated all {total_frames} frames.',
                'total_frames': total_frames
            }
            
            # Step 3: Save images and generate PDF
            yield {
                'type': 'step_start',
                'step': 3,
                'step_name': 'creating_pdf',
                'message': 'Creating PDF storyboard...'
            }
            
            # Save images to disk
            image_paths = self.image_service.save_images(generated_images, session_id)
            
            # Save frame descriptions metadata
            self.image_service.save_frame_descriptions(storyboard_output.frames, session_id)
            
            # Generate PDF with descriptions
            frame_descriptions = [frame.description for frame in storyboard_output.frames]
            pdf_path = self.pdf_generator.create_storyboard_pdf(
                image_paths=image_paths,
                session_id=session_id,
                frame_descriptions=frame_descriptions
            )
            
            yield {
                'type': 'step_complete',
                'step': 3,
                'step_name': 'creating_pdf',
                'message': 'PDF created successfully.'
            }
            
            # Final complete event
            yield {
                'type': 'complete',
                'success': True,
                'message': 'Storyboard generated successfully',
                'session_id': session_id,
                'storyboard_path': pdf_path,
                'total_frames': total_frames
            }
            
        except (ValueError, IOError, OSError) as e:
            yield {
                'type': 'error',
                'message': f'Storyboard generation failed: {str(e)}'
            }
