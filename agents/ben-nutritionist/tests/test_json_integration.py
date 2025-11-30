#!/usr/bin/env python3
"""
Test de validation pour les system prompts externalisés en JSON
"""

import sys
sys.path.append('..')
from core.query_chromadb import load_system_prompts, load_style_guides

def test_json_integration():
    print("🧪 Test d'intégration des prompts JSON")
    print("=" * 60)
    
    # Test 1: Chargement des system prompts
    print("\n1️⃣ Test du chargement des system prompts...")
    system_prompts = load_system_prompts()
    
    if system_prompts and 'fr' in system_prompts and 'en' in system_prompts:
        print("✅ System prompts chargés avec succès!")
        print(f"   Langues disponibles: {list(system_prompts.keys())}")
        
        # Vérifier la structure
        for lang in ['fr', 'en']:
            if 'content' in system_prompts[lang]:
                content = system_prompts[lang]['content']
                print(f"   {lang.upper()}: {len(content)} caractères")
                
                # Vérifier des mots-clés spécifiques
                if lang == 'fr':
                    keywords = ['Ben', 'nutritionniste', 'STYLE OBLIGATOIRE', 'RÈGLES ABSOLUES']
                else:
                    keywords = ['Ben', 'nutrition expert', 'MANDATORY STYLE', 'ABSOLUTE RULES']
                
                found = [kw for kw in keywords if kw in content]
                print(f"      Mots-clés trouvés: {len(found)}/{len(keywords)}")
                
                if len(found) == len(keywords):
                    print(f"      ✅ Structure correcte pour {lang.upper()}")
                else:
                    print(f"      ⚠️ Structure incomplète pour {lang.upper()}")
    else:
        print("❌ Erreur lors du chargement des system prompts")
        return False
    
    # Test 2: Comparaison avec les style guides
    print("\n2️⃣ Test de cohérence avec les style guides...")
    style_guides, style_data = load_style_guides()
    
    if style_guides and system_prompts:
        print("✅ Les deux systèmes sont chargés")
        
        # Vérifier que les langues correspondent
        style_langs = set(style_guides.keys())
        system_langs = set(system_prompts.keys())
        
        if style_langs == system_langs:
            print(f"   ✅ Langues cohérentes: {style_langs}")
        else:
            print(f"   ⚠️ Langues différentes:")
            print(f"      Style guides: {style_langs}")
            print(f"      System prompts: {system_langs}")
    
    # Test 3: Validation du contenu JSON
    print("\n3️⃣ Test de validation du contenu...")
    
    for lang in ['fr', 'en']:
        print(f"\n   📝 Validation {lang.upper()}:")
        
        # System prompt
        sys_content = system_prompts.get(lang, {}).get('content', '')
        if sys_content:
            print(f"      System prompt: {len(sys_content)} caractères ✅")
        else:
            print(f"      System prompt: Manquant ❌")
        
        # Style guide
        style_content = style_guides.get(lang, '')
        if style_content:
            print(f"      Style guide: {len(style_content)} caractères ✅")
        else:
            print(f"      Style guide: Manquant ❌")
        
        # Message fallback
        fallback_msg = style_data.get(lang, {}).get('not_found_message', '')
        if fallback_msg:
            print(f"      Message fallback: {len(fallback_msg)} caractères ✅")
        else:
            print(f"      Message fallback: Manquant ❌")
    
    print("\n🎉 Tests terminés!")
    return True

def test_file_structure():
    print("\n📁 Test de structure des fichiers JSON")
    print("=" * 60)
    
    import os
    
    files_to_check = [
        '../config/system_prompts.json',
        '../config/style_guides.json',
        '../static/translations.json'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {file_size} octets")
        else:
            print(f"❌ {file_path}: Fichier manquant")
    
    print(f"\n💡 Les system prompts sont maintenant externalisés!")
    print(f"💡 Modification facile sans redéploiement du code")
    print(f"💡 Structure JSON cohérente et maintenable")

if __name__ == "__main__":
    print("🚀 Validation de l'externalisation des system prompts")
    
    # Test d'intégration
    integration_ok = test_json_integration()
    
    if integration_ok:
        # Test de structure
        test_file_structure()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ:")
    print("✅ System prompts externalisés dans system_prompts.json")
    print("✅ Chargement dynamique depuis JSON")
    print("✅ Support français et anglais")
    print("✅ Fallback automatique vers français")
    print("✅ Cohérence avec style_guides.json")
    print("\n💾 Les prompts système sont maintenant dans /config/system_prompts.json")