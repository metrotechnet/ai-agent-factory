"""
Text-to-Speech (TTS) API Routes

This module defines endpoints for converting text to speech using the OpenAI TTS API in the Nutria Agent backend.
"""
from fastapi import APIRouter, Body, Request
from fastapi.responses import Response, JSONResponse
import openai
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)



@router.post("/api/tts")
@limiter.limit("10/hour")  # Max 10 TTS requests per hour per IP (TTS is expensive)
async def text_to_speech(
    request: Request,
    text: str = Body(..., embed=True),
    language: str = Body("fr", embed=True)
):
    """
    Convert text to speech using the OpenAI TTS API.

    Args:
        request (Request): FastAPI request object.
        text (str): The text to convert to speech.
        language (str): Target language for voice selection (default: 'fr').

    Returns:
        Response: Audio/mpeg stream or error message.
    """
    try:
        client_openai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Choose voice based on language
        voice = "nova" if language in ["fr", "es", "it", "pt", "ro"] else "alloy"
        response = client_openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text[:4096],  # TTS API limit
            response_format="mp3"
        )
        # Read full audio content
        audio_bytes = b""
        for chunk in response.iter_bytes(chunk_size=4096):
            audio_bytes += chunk
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Length": str(len(audio_bytes)),
                "Content-Disposition": "inline"
            }
        )
    except Exception as e:
        print(f"TTS error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
