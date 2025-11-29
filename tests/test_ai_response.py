#!/usr/bin/env python3
"""
Test pour simuler une réponse complète sans ChromaDB
"""

import sys
sys.path.append('..')
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def test_language_response():
    print("🧪 Test de réponse IA par langue (simulation)")
    print("=" * 60)
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Test cases
    test_cases = [
        {
            "language": "fr",
            "system_prompt": """Tu es Ben, nutritionniste expert avec un style de communication unique et reconnaissable.

STYLE OBLIGATOIRE:
- Structure: Accroche (mythe) → "Allons voir ce que dit la littérature scientifique" → Explication scientifique → "En somme..."
- Ton: Tutoiement, décontracté mais rigoureux, humour subtil
- Formules: "On entend souvent dire que...", "Contrairement aux idées reçues...", "La vérité, c'est que..."
- Anti-dogmatique: Nuances, limites des études, pas de solutions miracles

RÈGLES ABSOLUES:
- Réponds UNIQUEMENT avec les informations du contexte fourni
- Si l'info n'est pas dans le contexte, propose une consultation
- N'établis JAMAIS de diagnostics
- Ne recommande JAMAIS de médicaments ou suppléments spécifiques
- Redirige vers professionnels pour questions médicales""",
            "user_prompt": "Contexte: Les protéines sont essentielles pour la récupération musculaire.\nQuestion: Quels sont les bienfaits des protéines?\nRéponds en français avec ton style."
        },
        {
            "language": "en", 
            "system_prompt": """You are Ben, a nutrition expert with a unique and recognizable communication style.

MANDATORY STYLE:
- Structure: Hook (myth) → "Let's see what the scientific literature tells us" → Scientific explanation → "In summary..."
- Tone: Casual yet rigorous conversational tone, subtle humor
- Phrases: "People often say that...", "Contrary to popular belief...", "The truth is that..."
- Anti-dogmatic: Nuances, study limitations, no miracle solutions

ABSOLUTE RULES:
- Respond ONLY with information from the provided context
- If info is not in context, suggest a consultation
- NEVER establish diagnoses
- NEVER recommend specific medications or supplements
- Redirect to professionals for medical questions""",
            "user_prompt": "Context: Proteins are essential for muscle recovery.\nQuestion: What are the benefits of proteins?\nRespond in English with your style."
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🔍 Test {i+1}: {test_case['language'].upper()}")
        print("-" * 30)
        
        try:
            # Simuler une réponse courte
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": test_case['system_prompt']},
                    {"role": "user", "content": test_case['user_prompt']}
                ],
                temperature=0.3,
                max_tokens=150  # Limiter pour test rapide
            )
            
            response_text = response.choices[0].message.content
            print(f"Réponse: {response_text}")
            
            # Vérifier si la réponse est dans la bonne langue
            if test_case['language'] == 'fr':
                french_indicators = ['tu ', 'te ', 'ton ', 'tes ', 'vous', 'que ', 'des ', 'les ', 'est ', 'sont']
                found_fr = sum(1 for indicator in french_indicators if indicator in response_text.lower())
                if found_fr >= 3:
                    print("✅ Réponse semble être en français")
                else:
                    print("⚠️ Réponse pourrait ne pas être en français")
            else:
                english_indicators = ['the ', 'and ', 'you ', 'are ', 'that ', 'with ', 'for ', 'this ', 'will ', 'have']
                found_en = sum(1 for indicator in english_indicators if indicator in response_text.lower())
                if found_en >= 3:
                    print("✅ Réponse semble être en anglais")
                else:
                    print("⚠️ Réponse pourrait ne pas être en anglais")
                    
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    print(f"\n🎯 Test terminé!")

if __name__ == "__main__":
    test_language_response()