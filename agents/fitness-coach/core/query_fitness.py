"""
Fitness Coach Core Logic
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

class FitnessDatabase:
    """Simple in-memory fitness knowledge base"""
    
    def __init__(self):
        self.workout_plans = {
            "beginner": [
                "3 sets of 10 push-ups",
                "3 sets of 15 squats", 
                "3 sets of 30-second plank",
                "20-minute walk"
            ],
            "intermediate": [
                "4 sets of 15 push-ups",
                "4 sets of 20 squats",
                "4 sets of 45-second plank",
                "3 sets of 10 lunges each leg",
                "30-minute jog"
            ],
            "advanced": [
                "5 sets of 20 push-ups",
                "5 sets of 25 squats",
                "5 sets of 60-second plank",
                "4 sets of 15 lunges each leg",
                "4 sets of 10 burpees",
                "45-minute intense cardio"
            ]
        }
        
        self.nutrition_tips = [
            "Eat protein within 30 minutes after workout",
            "Stay hydrated - drink water before, during, and after exercise",
            "Include complex carbohydrates for sustained energy",
            "Don't skip meals on workout days",
            "Consider a light snack 1-2 hours before exercise"
        ]
        
    def get_workout_plan(self, level: str) -> List[str]:
        return self.workout_plans.get(level.lower(), self.workout_plans["beginner"])
    
    def get_fitness_tips(self) -> List[str]:
        return self.nutrition_tips

# Global fitness database
fitness_db = FitnessDatabase()

async def ask_fitness_question_stream(question: str, language: str = "en") -> AsyncIterator[str]:
    """Process fitness questions and provide streaming responses"""
    
    try:
        # Analyze question for fitness level and type
        fitness_level = "beginner"
        if "advanced" in question.lower() or "expert" in question.lower():
            fitness_level = "advanced"
        elif "intermediate" in question.lower():
            fitness_level = "intermediate"
        
        # Get relevant workout plan
        workout_plan = fitness_db.get_workout_plan(fitness_level)
        tips = fitness_db.get_fitness_tips()
        
        # Build context
        context = f"""
        Workout Plan ({fitness_level}):
        {chr(10).join(f"- {exercise}" for exercise in workout_plan)}
        
        Fitness Tips:
        {chr(10).join(f"- {tip}" for tip in tips)}
        """
        
        # Create fitness coach prompt
        system_prompt = f"""You are a professional fitness coach with expertise in:
        - Workout planning and exercise techniques
        - Nutrition for athletic performance
        - Injury prevention and recovery
        - Motivation and goal setting
        
        STYLE:
        - Enthusiastic and motivating
        - Focus on proper form and safety
        - Provide actionable advice
        - Encourage progressive improvement
        
        Available context:
        {context}
        
        User question: {question}
        
        Provide helpful, motivating fitness advice in {language}."""
        
        # Get streaming response from GPT
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.7,
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
        yield f"Error processing fitness question: {str(e)}"