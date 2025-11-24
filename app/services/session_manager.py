"""
Session Management Utilities

Handles session lifecycle for Google ADK agents.
"""
import uuid
import asyncio
from typing import Optional
from google.adk.sessions import InMemorySessionService
from app.config import settings


class SessionManager:
    """Manages session creation and cleanup for agents."""
    
    def __init__(self, session_service: InMemorySessionService, app_name: str):
        """
        Initialize session manager.
        
        Args:
            session_service: The ADK session service instance
            app_name: The application name for session management
        """
        self.session_service = session_service
        self.app_name = app_name
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())
    
    async def create_session(
        self, 
        session_id: str, 
        user_id: str = None
    ) -> None:
        """
        Create a new session.
        
        Args:
            session_id: The unique session identifier
            user_id: The user identifier. Defaults to configured default.
        """
        if user_id is None:
            user_id = settings.DEFAULT_USER_ID
        
        await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
    
    async def delete_session(
        self, 
        session_id: str, 
        user_id: str = None
    ) -> None:
        """
        Delete a session.
        
        Args:
            session_id: The unique session identifier
            user_id: The user identifier. Defaults to configured default.
        """
        if user_id is None:
            user_id = settings.DEFAULT_USER_ID
        
        try:
            await self.session_service.delete_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
        except Exception:
            # Silently ignore cleanup errors
            pass
