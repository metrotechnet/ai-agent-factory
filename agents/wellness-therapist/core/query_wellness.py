"""
Wellness Therapist Core Logic
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncIterator
from openai import OpenAI
import asyncio

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class WellnessDatabase:
    """Simple in-memory wellness and mental health knowledge base"""
    
    def __init__(self):
        self.meditation_techniques = {
            "breathing": [
                "4-7-8 breathing: Inhale for 4, hold for 7, exhale for 8",
                "Box breathing: Inhale 4, hold 4, exhale 4, hold 4",
                "Belly breathing: Deep diaphragmatic breaths"
            ],
            "mindfulness": [
                "Body scan meditation",
                "Walking meditation", 
                "Mindful eating practice",
                "Present moment awareness"
            ],
            "stress_relief": [
                "Progressive muscle relaxation",
                "Visualization meditation",
                "Loving-kindness meditation",
                "Mantra repetition"
            ]
        }
        
        self.wellness_tips = [
            "Practice gratitude daily - write down 3 things you're grateful for",
            "Maintain regular sleep schedule - 7-9 hours per night",
            "Limit screen time before bed",
            "Connect with nature regularly",
            "Practice saying 'no' to protect your energy",
            "Schedule regular breaks during work",
            "Maintain social connections with supportive people"
        ]
        
        self.stress_management = [
            "Identify your stress triggers",
            "Use the STOP technique: Stop, Take a breath, Observe, Proceed mindfully",
            "Break large tasks into smaller, manageable steps",
            "Practice self-compassion when facing challenges",
            "Engage in regular physical activity",
            "Maintain work-life boundaries"
        ]
        
    def get_meditation_techniques(self, category: str = "breathing") -> List[str]:
        return self.meditation_techniques.get(category.lower(), self.meditation_techniques["breathing"])
    
    def get_wellness_tips(self) -> List[str]:
        return self.wellness_tips
        
    def get_stress_management_tips(self) -> List[str]:
        return self.stress_management

# Global wellness database
wellness_db = WellnessDatabase()

async def ask_wellness_question_stream(question: str, language: str = "en") -> AsyncIterator[str]:
    """Process wellness and mental health questions and provide streaming responses"""
    
    try:
        # Analyze question type
        question_lower = question.lower()
        
        meditation_category = "breathing"
        if "mindfulness" in question_lower:
            meditation_category = "mindfulness"
        elif "stress" in question_lower:
            meditation_category = "stress_relief"
            
        # Get relevant information
        meditation_techniques = wellness_db.get_meditation_techniques(meditation_category)
        wellness_tips = wellness_db.get_wellness_tips()
        stress_tips = wellness_db.get_stress_management_tips()
        
        # Build context
        context = f"""
        Meditation Techniques ({meditation_category}):
        {chr(10).join(f"- {technique}" for technique in meditation_techniques)}
        
        Wellness Tips:
        {chr(10).join(f"- {tip}" for tip in wellness_tips)}
        
        Stress Management:
        {chr(10).join(f"- {tip}" for tip in stress_tips)}
        """
        
        # Create wellness therapist prompt
        system_prompt = f"""You are a compassionate wellness therapist and mental health coach with expertise in:
        - Mindfulness and meditation practices
        - Stress management and anxiety reduction
        - Emotional regulation and coping strategies
        - Work-life balance and burnout prevention
        - Self-care and personal wellness
        
        STYLE:
        - Warm, empathetic, and non-judgmental
        - Provide practical, evidence-based advice
        - Encourage self-reflection and mindful awareness
        - Emphasize self-compassion and gradual progress
        - Always recommend professional help for serious mental health concerns
        
        Available context:
        {context}
        
        User question: {question}
        
        Provide caring, supportive wellness guidance in {language}. 
        Remember: If someone expresses thoughts of self-harm, encourage them to seek immediate professional help."""
        
        # Get streaming response from GPT
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.8,
            stream=True
        )
        
        first_chunk = True
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                if first_chunk:
                    content = content.lstrip()
                    first_chunk = False
                if content:
                    yield content
        
    except Exception as e:
        yield f"Error processing wellness question: {str(e)}"