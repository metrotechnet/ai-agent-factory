"""
====================================================
 models.py – Pydantic Data Models for Translator Agent API
----------------------------------------------------
 Defines request schemas for API endpoints using Pydantic.
 Used for validation and documentation of incoming requests.
====================================================
"""

from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    """
    Request model for /query endpoint.
    Represents a user question/query to the agent.
    """
    question: str  # The user's question or prompt
    agent: str = "agent"  # Agent identifier (default: 'agent')
    language: str = "fr"  # Language code (default: French)
    timezone: str = "UTC"  # User's timezone
    locale: str = "fr-FR"  # User's locale
    session_id: Optional[str] = None  # Optional session identifier


class TranslateRequest(BaseModel):
    """
    Request model for /api/translate endpoint.
    Represents a translation request (text or audio).
    """
    text: str  # Text to translate
    target_language: str = "en"  # Target language code (default: English)
    source_language: str = "auto"  # Source language code (default: auto-detect)
