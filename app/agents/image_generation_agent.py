"""
Image Generation Agent Module

Defines the Google ADK agent for sequential image generation.
"""
import os
from google.genai import Client
from app.config import settings
from app.agents.prompts import (
    IMAGE_GENERATION_SYSTEM_INSTRUCTION,
    FIRST_IMAGE_PROMPT_TEMPLATE,
    SEQUENTIAL_IMAGE_PROMPT_TEMPLATE,
    FRAME_EDIT_PROMPT_TEMPLATE
)
from typing import Optional
import base64


class ImageGenerationAgent:
    """Agent for sequential image generation using Gemini's image model."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the image generation agent.
        
        Args:
            model_name: The Gemini image model to use. Defaults to configured model.
        """
        if model_name is None:
            model_name = settings.GEMINI_IMAGE_MODEL
        
        self.model_name = model_name
        self.client = Client()
    
    def generate_first_image(self, description: str) -> bytes:
        """
        Generate the first image from a description only.
        
        Args:
            description: Text description for the image
        
        Returns:
            Image bytes
        """
        # Construct prompt following Gemini best practices
        prompt = FIRST_IMAGE_PROMPT_TEMPLATE.format(
            system_instruction=IMAGE_GENERATION_SYSTEM_INSTRUCTION,
            description=description
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        
        # Extract image from response
        return self._extract_image_from_response(response)
    
    def generate_next_image(self, description: str, previous_image_path: str) -> bytes:
        """
        Generate an image using both a description and previous image as reference.
        
        Args:
            description: Text description for the new image
            previous_image_path: Path to the previous image file to use as reference
        
        Returns:
            Image bytes
        
        Raises:
            FileNotFoundError: If the previous image file doesn't exist
            ValueError: If the file path is invalid
        """
        # Validate file exists and is readable
        if not os.path.isfile(previous_image_path):
            raise FileNotFoundError(f"Previous image not found: {previous_image_path}")
        
        # Read the image file and encode to base64
        with open(previous_image_path, 'rb') as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Construct prompt following Gemini best practices
        prompt = SEQUENTIAL_IMAGE_PROMPT_TEMPLATE.format(
            system_instruction=IMAGE_GENERATION_SYSTEM_INSTRUCTION,
            description=description
        )
        
        # Create multimodal request with previous image and structured prompt
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                {
                    'parts': [
                        {
                            'inline_data': {
                                'mime_type': 'image/png',
                                'data': image_base64
                            }
                        },
                        {
                            'text': prompt
                        }
                    ]
                }
            ]
        )
        
        return self._extract_image_from_response(response)
    
    def edit_frame(
        self, 
        current_image_path: str, 
        edit_instructions: str,
        storyboard_context: str
    ) -> bytes:
        """
        Edit an existing frame based on user instructions.
        
        Args:
            current_image_path: Path to the current frame image to edit
            edit_instructions: User's instructions on how to modify the frame
            storyboard_context: The overall storyboard description for context
        
        Returns:
            Image bytes of the edited frame
        
        Raises:
            FileNotFoundError: If the current image file doesn't exist
            ValueError: If the file path is invalid
        """
        # Validate file exists and is readable
        if not os.path.isfile(current_image_path):
            raise FileNotFoundError(f"Current image not found: {current_image_path}")
        
        # Read the image file and encode to base64
        with open(current_image_path, 'rb') as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Construct prompt for frame editing
        prompt = FRAME_EDIT_PROMPT_TEMPLATE.format(
            system_instruction=IMAGE_GENERATION_SYSTEM_INSTRUCTION,
            edit_instructions=edit_instructions,
            storyboard_context=storyboard_context
        )
        
        # Create multimodal request with current image and edit instructions
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                {
                    'parts': [
                        {
                            'inline_data': {
                                'mime_type': 'image/png',
                                'data': image_base64
                            }
                        },
                        {
                            'text': prompt
                        }
                    ]
                }
            ]
        )
        
        return self._extract_image_from_response(response)
    
    def _extract_image_from_response(self, response) -> bytes:
        """
        Extract image bytes from Gemini API response.
        
        Args:
            response: The API response object
        
        Returns:
            Image bytes
        """
        # Gemini returns generated images in the response text as base64
        # or in inline_data parts
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content.parts:
                for part in candidate.content.parts:
                    # Check for inline_data (binary image data)
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Data might already be bytes or base64 string
                        data = part.inline_data.data
                        if isinstance(data, bytes):
                            return data
                        elif isinstance(data, str):
                            return base64.b64decode(data)
                    
                    # Check for text content that might contain base64
                    if hasattr(part, 'text') and part.text:
                        # Try to decode if it looks like base64
                        try:
                            # Remove any potential data URL prefix
                            text = part.text.strip()
                            if text.startswith('data:image'):
                                text = text.split(',', 1)[1]
                            return base64.b64decode(text)
                        except (ValueError, TypeError, base64.binascii.Error):
                            pass
        
        raise ValueError(f"No image found in response. Response structure: {response}")
