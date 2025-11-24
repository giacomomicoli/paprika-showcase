"""
Storyboard Models Module

Pydantic models for storyboard API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class StoryboardRequest(BaseModel):
    """Request model for storyboard generation."""
    user_description: str = Field(
        ..., 
        min_length=1, 
        description="Description for storyboard generation"
    )


class StoryboardResponse(BaseModel):
    """Response model for storyboard generation."""
    status: str
    description: str
    timestamp: str


class StoryboardGenerationResponse(BaseModel):
    """Response model for complete storyboard generation with images."""
    success: bool = Field(
        ...,
        description="Whether the storyboard generation was successful"
    )
    message: str = Field(
        ...,
        description="Status message"
    )
    storyboard_path: Optional[str] = Field(
        None,
        description="Path to the generated PDF storyboard"
    )
    total_frames: Optional[int] = Field(
        None,
        description="Total number of frames generated"
    )


class FrameData(BaseModel):
    """Individual frame in a storyboard."""
    description: str = Field(
        ..., 
        min_length=1, 
        description="Description of what happens in this frame"
    )
    frame_number: int = Field(
        ..., 
        ge=1, 
        description="Frame number starting from 1"
    )


class StoryboardOutput(BaseModel):
    """Output schema for the storyboard agent."""
    total_frames: int = Field(
        ..., 
        ge=1, 
        le=10, 
        description="Total number of frames (max 10)"
    )
    frames: List[FrameData] = Field(
        ..., 
        description="List of frame descriptions"
    )
