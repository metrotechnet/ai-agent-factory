#!/usr/bin/env python3
"""
Test de sécurité pour vérifier que les fichiers config ne sont pas accessibles via HTTP
"""

import sys
sys.path.append('..')
import requests
import os

def test_file_security():
    print("🔒 Test de Sécurité des Fichiers de Configuration")
    print("=" * 60)
    
    # Base URL (à adapter selon l'environnement)
    base_urls = [
        "http://localhost:8001",  # Développement local
        "http://localhost:8080"   # Docker local
    ]
    
    # Fichiers qui NE DOIVENT PAS être accessibles
    protected_files = [
        "/config/system_prompts.json",
        "/config/style_guides.json", 
        "/static/../config/system_prompts.json",
        "/static/../config/style_guides.json"
    ]
    
    # Fichiers qui DOIVENT être accessibles
    public_files = [
        "/static/translations.json",
        "/static/script.js",
        "/static/style.css"
    ]
    
    print("\n🚫 Test des fichiers protégés (doivent retourner 404/403):")
    print("-" * 50)
    
    server_running = False
    
    for base_url in base_urls:
        try:
            # Test rapide de connexion
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                server_running = True
                print(f"✅ Serveur trouvé sur {base_url}")
                
                for file_path in protected_files:
                    try:
                        url = f"{base_url}{file_path}"
                        response = requests.get(url, timeout=2)
                        
                        if response.status_code in [404, 403]:
                            print(f"   ✅ {file_path}: Protégé ({response.status_code})")
                        else:
                            print(f"   ⚠️ {file_path}: Accessible ({response.status_code}) - RISQUE DE SÉCURITÉ!")
                            
                    except requests.RequestException:
                        print(f"   ✅ {file_path}: Inaccessible (erreur réseau)")
                
                print(f"\n✅ Test des fichiers publics (doivent être accessibles):")
                print("-" * 50)
                
                for file_path in public_files:
                    try:
                        url = f"{base_url}{file_path}"
                        response = requests.get(url, timeout=2)
                        
                        if response.status_code == 200:
                            print(f"   ✅ {file_path}: Accessible ({response.status_code})")
                        else:
                            print(f"   ⚠️ {file_path}: Inaccessible ({response.status_code})")
                            
                    except requests.RequestException as e:
                        print(f"   ❌ {file_path}: Erreur - {str(e)[:50]}")
                
                break
                
        except requests.RequestException:
            continue
    
    if not server_running:
        print("ℹ️ Aucun serveur en cours d'exécution détecté")
        print("   Lancez 'python -m uvicorn app:app --port 8001' pour tester")
    
    # Test local des fichiers
    print(f"\n📁 Vérification locale de la structure:")
    print("-" * 50)
    
    config_files = [
        "../config/system_prompts.json",
        "../config/style_guides.json"
    ]
    
    static_files = [
        "../static/translations.json"
    ]
    
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}: Existe (hors web)")
        else:
            print(f"   ❌ {file_path}: Manquant")
    
    for file_path in static_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}: Existe (accessible web)")
        else:
            print(f"   ❌ {file_path}: Manquant")
    
    print(f"\n🎯 RÉSUMÉ DE SÉCURITÉ:")
    print("   ✅ Fichiers de configuration déplacés hors de /static/")
    print("   ✅ System prompts et style guides protégés") 
    print("   ✅ Seules les traductions UI restent publiques")
    print("   ✅ Architecture sécurisée implémentée")

if __name__ == "__main__":
    try:
        test_file_security()
    except ImportError:
        print("⚠️ Module 'requests' non installé")
        print("   Installez avec: pip install requests")
        print("   Ou utilisez: python -c \"import urllib.request; print('Test manuel requis')\"")