# 📁 Structure du Projet Ben Boulanger AI

## 🏗️ Architecture Organisée

```
benboulanger-ai/
├── 📄 app.py                    # Application FastAPI principale
├── 📄 requirements.txt          # Dépendances Python
├── 📄 Dockerfile              # Configuration Docker
├── 📄 startup.sh               # Script de démarrage
├── 📄 start_server.ps1         # Script de démarrage Windows
│
├── 📂 core/                    # 🧠 Modules principaux
│   ├── __init__.py
│   ├── query_chromadb.py       # Logique IA et RAG
│   └── config.py               # Configuration de base
│
├── 📂 config/                  # 🔒 Configuration (non-public)
│   ├── system_prompts.json     # Prompts système GPT
│   └── style_guides.json       # Guides de style Ben
│
├── 📂 static/                  # 🌐 Fichiers publics web
│   ├── translations.json       # Traductions UI (fr/en)
│   ├── script.js              # JavaScript frontend
│   ├── style.css              # Styles CSS
│   ├── ben.nutritioniste.jpg  # Photo de profil
│   └── favicon.ico            # Icône du site
│
├── 📂 templates/               # 🎨 Templates HTML
│   └── index.html             # Page principale
│
├── 📂 scripts/                 # 🔧 Utilitaires et outils
│   ├── __init__.py
│   ├── ingest.py              # Transcription vidéo
│   ├── extract_docx.py        # Extraction documents Word
│   ├── index_chromadb.py      # Indexation ChromaDB
│   ├── init_chromadb.py       # Initialisation base de données
│   └── create_favicon.py      # Génération favicon
│
├── 📂 tests/                   # 🧪 Tests et validation
│   ├── __init__.py
│   ├── test_multilingual.py   # Tests multilingues
│   ├── test_ai_response.py    # Tests réponses IA
│   ├── test_prompts.py        # Tests génération prompts
│   ├── test_json_integration.py # Tests intégration JSON
│   ├── test_endtoend.py       # Tests end-to-end
│   └── test_security.py       # Tests sécurité
│
├── 📂 chroma_db/              # 💾 Base de données vectorielle
│   └── [données ChromaDB]
│
└── 📂 transcripts_extracted/  # 📝 Transcriptions extraites
    └── [fichiers .txt]
```

## 🎯 Avantages de cette Structure

### ✅ **Organisation Claire**
- **`core/`** : Logique métier et modules essentiels
- **`config/`** : Configuration sensible (non-publique)
- **`scripts/`** : Outils utilitaires et maintenance
- **`tests/`** : Validation complète du système

### ✅ **Sécurité Renforcée**
- Fichiers de configuration hors de `static/`
- Prompts système protégés
- Séparation public/privé claire

### ✅ **Maintenabilité**
- Modules Python organisés en packages
- Imports explicites et cohérents
- Tests regroupés et structurés

### ✅ **Développement**
- Structure professionnelle
- Évolutivité facilitée
- Onboarding simplifié

## 🚀 Utilisation

### Démarrage de l'application
```bash
python app.py
# ou
./start_server.ps1
```

### Exécution des tests
```bash
cd tests/
python test_multilingual.py
python test_security.py
```

### Utilisation des scripts
```bash
cd scripts/
python index_chromadb.py     # Indexer des documents
python init_chromadb.py      # Initialiser la base
```

## 📦 Modules Principaux

- **`core.query_chromadb`** : Système RAG et génération IA
- **`config/`** : Configuration JSON multilingue
- **`static/translations.json`** : Interface utilisateur
- **`tests/`** : Suite de validation complète

Cette structure respecte les bonnes pratiques Python et facilite la maintenance à long terme du projet.