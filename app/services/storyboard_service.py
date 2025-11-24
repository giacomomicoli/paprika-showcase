"""
Storyboard Service Module

Business logic for storyboard generation.
"""
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.models.storyboard import StoryboardOutput, StoryboardGenerationResponse
from app.agents import create_storyboard_agent
from app.services.session_manager import SessionManager
from app.services.response_parser import ResponseParser
from app.services.image_generation_service import ImageGenerationService
from app.services.pdf_generator import PDFGenerator
from app.config import settings


class StoryboardService:
    """Service for handling storyboard generation operations."""
    
    def __init__(self):
        """Initialize the storyboard service."""
        self.session_service = InMemorySessionService()
        self.session_manager = SessionManager(
            session_service=self.session_service,
            app_name=settings.STORYBOARD_APP_NAME
        )
        self.response_parser = ResponseParser()
        self.image_service = ImageGenerationService()
        self.pdf_generator = PDFGenerator()
    
    def generate_frames(self, user_description: str) -> StoryboardOutput:
        """
        Generate storyboard frames from a user description.
        
        Args:
            user_description: The text description of the video sequence
        
        Returns:
            StoryboardOutput containing total_frames and list of frames
        
        Raises:
            ValueError: If agent execution fails or returns invalid data
        """
        # Create agent and runner
        agent = create_storyboard_agent()
        runner = Runner(
            agent=agent,
            app_name=settings.STORYBOARD_APP_NAME,
            session_service=self.session_service
        )
        
        # Generate unique session
        session_id = self.session_manager.generate_session_id()
        
        # Create session
        asyncio.run(self.session_manager.create_session(session_id))
        
        # Create user message content
        content = types.Content(
            role='user',
            parts=[types.Part(text=user_description)]
        )
        
        try:
            # Run the agent
            events = runner.run(
                user_id=settings.DEFAULT_USER_ID,
                session_id=session_id,
                new_message=content
            )
            
            # Extract and parse response
            final_response = self.response_parser.extract_final_response(events)
            storyboard = self.response_parser.parse_json_response(
                final_response, 
                StoryboardOutput
            )
            
            return storyboard
        
        finally:
            # Clean up session
            asyncio.run(self.session_manager.delete_session(session_id))
    
    def generate_complete_storyboard(self, user_description: str) -> StoryboardGenerationResponse:
        """
        Generate complete storyboard with sequential images and PDF.
        
        Args:
            user_description: The text description of the video sequence
        
        Returns:
            StoryboardGenerationResponse with success status and PDF path
        """
        try:
            # Step 1: Generate frame descriptions using the first agent
            storyboard_output = self.generate_frames(user_description)
            
            # Step 2: Generate unique session ID for this storyboard
            session_id = self.session_manager.generate_session_id()
            
            # Step 3: Generate images sequentially using the second agent
            generated_images = self.image_service.generate_sequential_images(
                storyboard_output.frames
            )
            
            # Step 4: Save images to disk
            image_paths = self.image_service.save_images(generated_images, session_id)
            
            # Step 5: Generate PDF from images
            pdf_path = self.pdf_generator.create_storyboard_pdf(
                image_paths=image_paths,
                session_id=session_id
            )
            
            return StoryboardGenerationResponse(
                success=True,
                message="Storyboard generated successfully",
                storyboard_path=pdf_path,
                total_frames=storyboard_output.total_frames
            )
        
        except (ValueError, IOError, OSError) as e:
            return StoryboardGenerationResponse(
                success=False,
                message=f"Storyboard generation failed: {str(e)}",
                storyboard_path=None,
                total_frames=None
            )
