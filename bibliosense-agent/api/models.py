"""
Data Models - Pydantic models for API requests
"""
from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    question: str
    agent: str = "agent"
    language: str = "fr"
    timezone: str = "UTC"
    locale: str = "fr-FR"
    session_id: Optional[str] = None
    bibliotheque: str = "all"  # Library filter: 'all', 'quebec', or 'montreal'


class TranslateRequest(BaseModel):
    text: str
    target_language: str = "en"
    source_language: str = "auto"
