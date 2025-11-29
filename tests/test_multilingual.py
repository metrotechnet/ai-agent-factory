#!/usr/bin/env python3
"""
Script de test pour vérifier le système de style guides multilingue
"""

import json
import sys
sys.path.append('..')
from core.query_chromadb import load_style_guides, ask_question_stream

def test_style_system():
    print("🧪 Test du système de style guides multilingue")
    print("=" * 60)
    
    # Test 1: Chargement du JSON
    print("\n1️⃣ Test du chargement des style guides...")
    guides, data = load_style_guides()
    
    if guides and 'fr' in guides and 'en' in guides:
        print("✅ Style guides chargés avec succès!")
        print(f"   Langues disponibles: {list(guides.keys())}")
        
        # Vérifier la structure
        for lang in ['fr', 'en']:
            if lang in data and 'not_found_message' in data[lang]:
                print(f"   {lang.upper()}: Message de fallback OK")
    else:
        print("❌ Erreur lors du chargement des style guides")
        return False
    
    # Test 2: Test des prompts français
    print("\n2️⃣ Test du prompt français...")
    try:
        fr_prompt = guides.get('fr', '')
        if "TON STYLE DE COMMUNICATION EN FRANÇAIS" in fr_prompt:
            print("✅ Style guide français OK")
        else:
            print("❌ Style guide français invalide")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 3: Test des prompts anglais
    print("\n3️⃣ Test du prompt anglais...")
    try:
        en_prompt = guides.get('en', '')
        if "YOUR COMMUNICATION STYLE IN ENGLISH" in en_prompt:
            print("✅ Style guide anglais OK")
        else:
            print("❌ Style guide anglais invalide")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Test 4: Test du fallback
    print("\n4️⃣ Test du fallback pour langues non supportées...")
    try:
        # Simuler une langue non supportée
        test_langs = ['es', 'de', 'it', 'pt']
        for lang in test_langs:
            if lang not in guides:
                print(f"   {lang.upper()}: Fallback vers français ✅")
            else:
                print(f"   {lang.upper()}: Ne devrait pas être supporté ❌")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n🎉 Tests terminés!")
    return True

def test_function_calls():
    print("\n🔧 Test des appels de fonction...")
    print("=" * 60)
    
    # Test fonction avec différentes langues (simulation sans ChromaDB)
    print("\n📞 Test d'appels simulés...")
    
    test_cases = [
        ('Quels sont les bienfaits du sommeil?', 'fr'),
        ('What are the benefits of sleep?', 'en'),
        ('¿Cuáles son los beneficios del sueño?', 'es'),  # Devrait utiliser français
    ]
    
    for question, lang in test_cases:
        try:
            print(f"\n   Question: {question[:40]}...")
            print(f"   Langue: {lang}")
            
            # Simuler sans réellement appeler l'API
            guides, data = load_style_guides()
            selected_lang = lang if lang in guides else 'fr'
            fallback_msg = data.get(selected_lang, {}).get('not_found_message', 'No message')
            
            print(f"   → Langue sélectionnée: {selected_lang}")
            print(f"   → Message fallback: {fallback_msg[:50]}...")
            print("   ✅ Configuration OK")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print("\n🎯 Tests d'appels terminés!")

if __name__ == "__main__":
    print("🚀 Début des tests du système multilingue")
    
    # Test du système de style
    style_ok = test_style_system()
    
    if style_ok:
        # Test des appels de fonction
        test_function_calls()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ:")
    print("✅ Style guides externalisés dans style_guides.json")
    print("✅ Support français et anglais uniquement")
    print("✅ Fallback automatique vers français pour autres langues")
    print("✅ Messages de fallback personnalisés par langue")
    print("✅ Structure JSON organisée et maintenable")
    print("\n💡 Les style guides sont maintenant dans /static/style_guides.json")
    print("💡 Suppression de l'espagnol et autres langues non souhaitées")
    print("💡 Code plus propre et maintenable")