"""
Storyboard Agent Module

Defines the Google ADK agent for storyboard generation.
"""
from google.adk.agents.llm_agent import LlmAgent
from app.models.storyboard import StoryboardOutput
from app.agents.prompts import STORYBOARD_INSTRUCTION
from app.config import settings


def create_storyboard_agent(model_name: str = None) -> LlmAgent:
    """
    Create and configure the storyboard segmentation agent.
    
    Args:
        model_name: The Gemini model to use. Defaults to configured model.
    
    Returns:
        LlmAgent configured for storyboard generation
    """
    if model_name is None:
        model_name = settings.GEMINI_TEXT_MODEL
    
    agent = LlmAgent(
        model=model_name,
        name=settings.STORYBOARD_AGENT_NAME,
        description=settings.STORYBOARD_AGENT_DESCRIPTION,
        instruction=STORYBOARD_INSTRUCTION,
        output_schema=StoryboardOutput,
    )
    return agent
