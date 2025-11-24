"""
Agent Response Parser

Utilities for parsing and validating agent responses.
"""
import json
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class ResponseParser:
    """Parses and validates agent responses."""
    
    @staticmethod
    def parse_json_response(
        response_text: str, 
        model_class: Type[T]
    ) -> T:
        """
        Parse JSON response and validate against Pydantic model.
        
        Args:
            response_text: The raw JSON response text
            model_class: The Pydantic model class to validate against
        
        Returns:
            Validated model instance
        
        Raises:
            ValueError: If JSON is invalid or validation fails
        """
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from agent: {e}")
        
        try:
            return model_class(**response_data)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to parse agent response: {e}")
    
    @staticmethod
    def extract_final_response(events) -> str:
        """
        Extract the final response text from agent events.
        
        Args:
            events: Iterator of agent response events
        
        Returns:
            The final response text
        
        Raises:
            ValueError: If no final response is found
        """
        for event in events:
            if event.is_final_response() and event.content:
                return event.content.parts[0].text.strip()
        
        raise ValueError("Agent did not return a response")
