#!/usr/bin/env python3
"""
Test pour vérifier la génération des prompts selon la langue
"""

import sys
sys.path.append('..')
from core.query_chromadb import load_style_guides

def test_prompt_generation():
    print("🧪 Test de génération des prompts par langue")
    print("=" * 60)
    
    # Charger les style guides
    style_guides, style_data = load_style_guides()
    
    # Simuler une question et un contexte
    question = "What are the benefits of protein?"
    context = "Sample context about protein benefits..."
    
    # Test pour chaque langue
    for language in ['fr', 'en']:
        print(f"\n📝 LANGUE: {language.upper()}")
        print("-" * 30)
        
        style_guide = style_guides.get(language, style_guides.get("fr", ""))
        not_found_msg = style_data.get(language, {}).get('not_found_message', 
                                                        style_data.get('fr', {}).get('not_found_message', 
                                                        "Information not found in current content."))
        
        # Générer le prompt selon la langue
        if language == "fr":
            prompt = f"""Tu es Ben, un nutritionniste expert et coach en santé. 

{style_guide}

RÈGLES IMPORTANTES:
1. Tu dois répondre UNIQUEMENT à partir des informations présentes dans le contexte ci-dessous. N'utilise PAS ta connaissance générale.
2. N'établis JAMAIS de diagnostics médicaux.
3. Ne recommande JAMAIS de médicaments, suppléments spécifiques ou traitements sans consulter un professionnel de santé.
4. Pour toute question médicale, blessure ou condition de santé, redirige vers un professionnel qualifié.
5. APPLIQUE TON STYLE: Utilise les formules caractéristiques, la structure narrative, et le ton décrit ci-dessus.

Si l'information n'est pas dans le contexte, réponds: "{not_found_msg}"

Contexte extrait de tes documents:
{context}

Question: {question}

Réponds uniquement avec les informations du contexte ci-dessus, en appliquant ton style personnel et accessible."""
        else:  # en
            prompt = f"""You are Ben, a nutrition expert and health coach.

{style_guide}

IMPORTANT RULES:
1. You must respond ONLY based on the information present in the context below. Do NOT use your general knowledge.
2. NEVER establish medical diagnoses.
3. NEVER recommend specific medications, supplements, or treatments without consulting a healthcare professional.
4. For any medical question, injury, or health condition, redirect to a qualified professional.
5. APPLY YOUR STYLE: Use the characteristic phrases, narrative structure, and tone described above.

If the information is not in the context, respond: "{not_found_msg}"

Context extracted from your documents:
{context}

Question: {question}

Respond only with information from the context above, applying your personal and accessible style."""
        
        # Afficher un extrait du prompt généré
        print(f"Début du prompt:")
        print(prompt[:200] + "...")
        
        # Vérifier des mots-clés spécifiques à chaque langue
        if language == "fr":
            keywords = ["Tu es Ben", "nutritionniste", "RÈGLES IMPORTANTES", "Réponds uniquement"]
        else:
            keywords = ["You are Ben", "nutrition expert", "IMPORTANT RULES", "Respond only"]
        
        found_keywords = [kw for kw in keywords if kw in prompt]
        print(f"Mots-clés trouvés: {len(found_keywords)}/{len(keywords)}")
        
        if len(found_keywords) == len(keywords):
            print("✅ Prompt correctement généré pour cette langue")
        else:
            print("❌ Problème dans la génération du prompt")
            print(f"Manquants: {set(keywords) - set(found_keywords)}")

if __name__ == "__main__":
    test_prompt_generation()
    print("\n🎯 Test terminé!")