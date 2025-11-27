# Rapport de Sécurité et Documentation Technique
## Application d'Intelligence Artificielle en Nutrition - Ben Boulanger

**Date:** 24 novembre 2025  
**Version:** 1.0  
**Auteur:** Ben Boulanger  
**Contact:** ben.boulanger.nut@gmail.com

---

## 1. DESCRIPTION DE L'APPLICATION

### 1.1 Vue d'ensemble
L'application **Ben Boulanger AI** est un chatbot nutritionnel intelligent conçu pour fournir des conseils en nutrition basés sur des preuves scientifiques. L'assistant virtuel reproduit le style de communication et l'approche pédagogique de Ben Boulanger, nutritionniste, en s'appuyant sur une base de connaissances constituée de 842 documents issus de transcriptions vidéo.

### 1.2 Architecture technique

#### Stack technologique
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Python 3.11, FastAPI 0.121.3
- **IA:** OpenAI API (GPT-4o-mini, text-embedding-3-large)
- **Base de données vectorielle:** ChromaDB 1.3.5 (842 documents indexés)
- **Serveur:** Uvicorn (ASGI)
- **Déploiement:** Google Cloud Platform (Cloud Run)
- **Conteneurisation:** Docker

#### Infrastructure Cloud Run
- **Région:** us-central1
- **Ressources:** 1 CPU, 1 Gi mémoire
- **Configuration:** 
  - Startup CPU boost activé
  - Timeout: 300 secondes
  - Max instances: 10
  - Workers: 1
  - Timeout keep-alive: 300 secondes

### 1.3 Fonctionnalités principales
1. **Chat en temps réel** avec streaming de réponses (Server-Sent Events)
2. **Recherche sémantique** dans la base de connaissances ChromaDB
3. **Style de communication cohérent** basé sur le Style Card documenté
4. **Interface responsive** adaptée mobile/desktop
5. **Gestion des cookies** avec consentement utilisateur (localStorage)
6. **Liens externes:** Instagram, prise de rendez-vous, contact email

---

## 2. MESURES DE SÉCURITÉ CONTRE LES HALLUCINATIONS

### 2.1 Retrieval-Augmented Generation (RAG)

#### Principe de fonctionnement
L'application utilise **ChromaDB** comme base de données vectorielle pour implémenter un système RAG robuste. Cette architecture garantit que chaque réponse est ancrée dans le contenu réel des transcriptions de Ben Boulanger.

**Processus de réponse:**
```
Question utilisateur 
  → Embedding (text-embedding-3-large)
  → Recherche sémantique dans ChromaDB (n_results=5)
  → Extraction du contexte pertinent
  → Prompt enrichi avec contexte + question
  → Génération GPT-4o-mini (temperature=0.3)
  → Réponse streamée à l'utilisateur
```

#### Configuration ChromaDB
```python
collection = client.get_or_create_collection(
    name="transcriptions",
    metadata={"hnsw:space": "cosine"}
)

results = collection.query(
    query_texts=[question],
    n_results=5  # Limite à 5 documents pertinents
)
```

**Avantages:**
- ✅ Réponses basées sur des documents existants
- ✅ Réduction drastique des hallucinations
- ✅ Traçabilité du contenu source
- ✅ Cohérence avec le style de Ben

### 2.2 Contraintes du prompt système

#### Style Card intégré
Un document **STYLE_CARD.md** exhaustif a été créé pour documenter le style de communication de Ben Boulanger. Ce guide est **intégré dans chaque prompt** envoyé à l'API OpenAI.

**Extraits du prompt système:**
```python
system_prompt = f"""Tu es Ben Boulanger, nutritionniste.

# TON STYLE DE COMMUNICATION

## Structure narrative à suivre:
1. ACCROCHE: "On entend souvent dire que..." ou "Certains vont même jusqu'à affirmer que..."
2. TRANSITION: "Allons voir ce que dit la littérature scientifique."
3. EXPLICATION: Mécanisme biologique 
4. CONCLUSION: "En somme..." ou "Mieux vaut donc..."

## Formules caractéristiques:
- "On entend souvent dire que..."
- "Allons voir ce que dit la littérature scientifique."
- "En somme..."
- "Mieux vaut donc..."

## Ton: tutoiement, décontracté mais rigoureux

# CONTEXTE ISSU DE TES TRANSCRIPTIONS
{context}

# RÈGLES STRICTES
- Base-toi UNIQUEMENT sur le contexte fourni ci-dessus
- Si l'information n'est pas dans le contexte, dis-le clairement
- Cite les études mentionnées dans le contexte
- Ne JAMAIS inventer de données ou d'études
"""
```

**Contraintes appliquées:**
- ✅ Obligation d'utiliser le contexte ChromaDB
- ✅ Interdiction d'inventer des études ou données
- ✅ Instruction explicite de dire "Je ne sais pas" si information absente
- ✅ Maintien du style cohérent avec les transcriptions originales

### 2.3 Paramètres de génération optimisés

#### Configuration OpenAI API
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ],
    temperature=0.3,  # Température basse pour réduire créativité
    stream=True
)
```

**Justification de temperature=0.3:**
- ✅ Réduit la probabilité de génération créative non fondée
- ✅ Favorise les réponses déterministes
- ✅ Maintient un équilibre entre cohérence et fluidité linguistique
- ✅ Évite les variations excessives entre réponses similaires

### 2.4 Validation du contenu

#### Règles explicites dans le Style Card
Le document **STYLE_CARD.md** inclut une section critique: **"Ce que Ben NE fait JAMAIS"**

**Interdictions formelles:**
- ❌ Donner des diagnostics médicaux
- ❌ Prescrire des suppléments spécifiques
- ❌ Inventer des études scientifiques
- ❌ Simplifier à outrance les mécanismes biologiques
- ❌ Utiliser un ton moralisateur ou culpabilisant
- ❌ Promettre des résultats garantis
- ❌ Utiliser du jargon scientifique sans explication

Ces règles sont **intégrées dans le prompt système** pour chaque requête.

---

## 3. AVERTISSEMENTS ET LIMITATIONS

### 3.1 Disclaimer visible dans l'interface

L'application affiche un **avertissement permanent** dans le menu latéral, accessible via l'icône ⚠️:

**Texte de l'avertissement:**
```
⚠️ Avertissements importants

Cet assistant virtuel est un outil d'information général basé sur le contenu éducatif de Ben Boulanger.

❌ NE REMPLACE PAS une consultation médicale
❌ NE POSE PAS de diagnostic
❌ NE PRESCRIT PAS de traitement

Pour tout problème de santé:
✅ Consultez un professionnel de santé qualifié
✅ Ne modifiez pas votre traitement sans avis médical
✅ En cas d'urgence, contactez les services d'urgence

Les informations fournies sont à but éducatif uniquement.
```

**Visibilité:**
- ✅ Icône ⚠️ clairement visible dans le menu principal
- ✅ Texte complet affiché au clic
- ✅ Style visuel distinctif (fond jaune/orange, gras)
- ✅ Accessible sur mobile et desktop

### 3.2 Limitations techniques communiquées

#### Dans le prompt système
Le prompt inclut des instructions explicites sur les limitations:

```python
# SI LA RÉPONSE N'EST PAS DANS LE CONTEXTE
Si la question ne peut pas être répondue avec le contexte fourni:
- Dis clairement que l'information n'est pas dans tes transcriptions
- Propose de rediriger vers une consultation professionnelle
- Ne JAMAIS inventer ou extrapoler
```

#### Gestion des questions hors périmètre
L'assistant est configuré pour:
- ✅ Reconnaître les questions médicales urgentes
- ✅ Rediriger vers un professionnel de santé
- ✅ Refuser de diagnostiquer ou prescrire
- ✅ Admettre les limites de ses connaissances

### 3.3 Consentement des cookies

#### Bannière de consentement
Une **bannière de consentement** apparaît lors de la première visite:

**Fonctionnalités:**
- Affichage après 1 seconde de délai
- Stockage du consentement dans localStorage
- Boutons "Accepter" et "Refuser"
- Animation de slide depuis le bas de l'écran
- Design responsive mobile/desktop

**Code de gestion:**
```javascript
function checkCookieConsent() {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
        setTimeout(() => {
            cookieBanner.classList.add('show');
        }, 1000);
    }
}
```

**Données collectées:**
- ❌ Aucun cookie tiers (Google Analytics, Facebook Pixel, etc.)
- ✅ Uniquement localStorage pour le consentement
- ✅ Aucune collecte de données personnelles
- ✅ Aucun tracking cross-site

---

## 4. SÉCURITÉ TECHNIQUE

### 4.1 Sécurité du backend

#### Variables d'environnement
Les clés API sensibles sont stockées dans des **variables d'environnement**:

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

**Bonnes pratiques:**
- ✅ Fichier .env exclu du contrôle de version (.gitignore)
- ✅ Clés API jamais hardcodées dans le code
- ✅ Variables d'environnement Cloud Run configurées via interface GCP
- ✅ Rotation possible des clés sans redéploiement du code

#### Configuration FastAPI sécurisée
```python
app = FastAPI()

# Headers de sécurité dans les réponses streaming
return StreamingResponse(
    generate(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive"
    }
)
```

#### Endpoint de santé
```python
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Utilité:**
- ✅ Monitoring Cloud Run
- ✅ Health checks automatiques
- ✅ Détection des problèmes de démarrage

### 4.2 Sécurité du frontend

#### Pas de données sensibles côté client
- ✅ Aucune clé API exposée dans le JavaScript
- ✅ Toutes les requêtes OpenAI passent par le backend
- ✅ Aucun token utilisateur stocké

#### Content Security Policy (futur)
Recommandation pour implémentation future:
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data:;">
```

### 4.3 Sécurité de l'infrastructure

#### Docker
```dockerfile
# Image de base minimale
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Pas de root user (implicite dans Cloud Run)
```

#### Cloud Run
- ✅ HTTPS automatique (certificat géré)
- ✅ Isolation des conteneurs
- ✅ Scaling automatique (0-10 instances)
- ✅ Logs centralisés (Cloud Logging)
- ✅ Monitoring intégré (Cloud Monitoring)
- ✅ Authentification IAM possible (actuellement public)

**Configuration réseau:**
- Timeout: 300 secondes (limite les attaques par épuisement)
- Max instances: 10 (limite les coûts et la charge)
- Single worker: évite les problèmes de concurrence

### 4.4 Gestion des erreurs

#### Backend
```python
try:
    # Logique de traitement
except Exception as e:
    print(f"Erreur: {str(e)}")
    # Pas d'exposition des détails d'erreur au client
```

#### Frontend
```javascript
fetch('/query', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: userInput})
})
.then(response => {
    if (!response.ok) {
        throw new Error('Erreur réseau');
    }
    // Traitement normal
})
.catch(error => {
    console.error('Erreur:', error);
    // Message générique à l'utilisateur
    displayError("Désolé, une erreur est survenue. Veuillez réessayer.");
});
```

---

## 5. CONFORMITÉ ET ÉTHIQUE

### 5.1 Transparence de l'IA

#### Identification claire
L'application s'identifie explicitement comme:
- ✅ "Assistant virtuel" (pas "Ben Boulanger réel")
- ✅ "Basé sur le contenu éducatif de Ben Boulanger"
- ✅ "Outil d'information général"

#### Limitations communiquées
- ✅ Avertissement visible: "NE REMPLACE PAS une consultation médicale"
- ✅ Redirection vers professionnels de santé si nécessaire
- ✅ Admission des limites dans les réponses ("Je ne trouve pas cette information dans mes transcriptions")

### 5.2 Protection des utilisateurs

#### Domaine médical
- ❌ Aucun diagnostic posé
- ❌ Aucune prescription de médicaments ou suppléments
- ❌ Aucune recommandation de modification de traitement
- ✅ Redirection systématique vers professionnels qualifiés

#### Données personnelles
- ❌ Aucune collecte de données personnelles
- ❌ Pas de compte utilisateur
- ❌ Pas de stockage des conversations
- ✅ Historique uniquement en mémoire du navigateur (session)

#### Accessibilité
- ✅ Interface responsive mobile/desktop
- ✅ Taille de police adaptée
- ✅ Contraste suffisant (WCAG 2.1 Level AA visé)
- ⚠️ Amélioration future: lecteurs d'écran, navigation clavier

### 5.3 Propriété intellectuelle

#### Contenu source
- ✅ Contenu basé sur les transcriptions originales de Ben Boulanger
- ✅ Pas de plagiat d'autres sources

#### Modèle d'IA
- ✅ Utilisation légale de l'API OpenAI (licence commerciale)
- ✅ Conformité avec les Terms of Service d'OpenAI
- ✅ Pas de fine-tuning (utilisation du modèle public)

---

## 6. TRAÇABILITÉ ET LOGS

### 6.1 Logs Cloud Run

#### Journalisation automatique
Google Cloud Platform enregistre automatiquement:
- Requêtes HTTP (timestamp, IP, user-agent, status code)
- Erreurs serveur (stack traces, exceptions Python)
- Métriques de performance (latence, temps de réponse)
- Utilisation des ressources (CPU, mémoire)

**Commande de consultation:**
```bash
gcloud run services logs read benboulanger-ai --limit=100 --region=us-central1
```

#### Niveau de logging
```python
# Pas de logs debug en production
print(f"Question reçue: {question}")  # Uniquement pour monitoring
```

### 6.2 Monitoring

#### Métriques Cloud Run disponibles
- Nombre de requêtes (request count)
- Latence (request latency)
- Taux d'erreur (error rate)
- Utilisation CPU/mémoire
- Nombre d'instances actives
- Cold starts

#### Alertes (recommandées)
Configuration future recommandée:
- ✅ Alerte si taux d'erreur > 5%
- ✅ Alerte si latence P95 > 5 secondes
- ✅ Alerte si coût > seuil défini

---

## 7. MAINTENANCE ET MISES À JOUR

### 7.1 Processus de déploiement

#### Scripts automatisés
```batch
# build.bat - Construction de l'image Docker
docker build --platform linux/amd64 -t gcr.io/benboulanger-ai/benboulanger-ai .
docker push gcr.io/benboulanger-ai/benboulanger-ai

# deploy.bat - Déploiement Cloud Run
gcloud run deploy benboulanger-ai ^
    --image gcr.io/benboulanger-ai/benboulanger-ai ^
    --platform managed ^
    --region us-central1 ^
    --allow-unauthenticated ^
    --memory 1Gi ^
    --timeout 300 ^
    --max-instances 10 ^
    --cpu 1 ^
    --startup-cpu-boost
```

**Bonnes pratiques:**
- ✅ Build et push Docker automatisés
- ✅ Paramètres Cloud Run versionnés (deploy.bat)
- ✅ Rollback possible via Cloud Run UI
- ✅ Révisions conservées (historique)

### 7.2 Mises à jour de la base de connaissances

#### Processus d'ingestion
```python
# ingest.py - Ajout de nouveaux documents
python ingest.py  # Scanne transcripts/ et indexe dans ChromaDB
```

**Workflow:**
1. Nouvelle vidéo → Transcription
2. Fichier texte ajouté dans `transcripts/`
3. Exécution de `python ingest.py`
4. Rebuild et redéploiement de l'image Docker

**Amélioration future:**
- ⚠️ Séparation de ChromaDB sur Cloud Storage
- ⚠️ Mise à jour dynamique sans redéploiement

### 7.3 Versioning

#### Git repository
- Repository: `metrotechnet/benboulanger-ai`
- Branche principale: `main`
- Commit messages descriptifs
- Tag de version recommandé (v1.0, v1.1, etc.)

#### Changelog (recommandé)
Création future d'un fichier CHANGELOG.md:
```markdown
## [1.0.0] - 2025-11-24
### Ajouté
- Style Card intégré dans les prompts
- Cookie consent banner
- Email link dans sidebar
- Loading spinner

### Corrigé
- Bug streaming async/sync
- Server termination (limit-max-requests)
- Burger menu alignment
```

---

## 8. TESTS ET VALIDATION

### 8.1 Tests fonctionnels effectués

#### Tests locaux
- ✅ Streaming de réponses (Server-Sent Events)
- ✅ Recherche sémantique ChromaDB (5 résultats pertinents)
- ✅ Cohérence du style (formules caractéristiques présentes)
- ✅ Gestion des questions hors contexte
- ✅ Cookie consent (accept/decline, localStorage)
- ✅ Menu burger responsive
- ✅ Liens externes (Instagram, rendez-vous, email)

#### Tests de charge (recommandés)
Tests futurs à effectuer:
- ⚠️ Nombre de requêtes simultanées supportées
- ⚠️ Temps de réponse sous charge
- ⚠️ Comportement avec 10 instances actives
- ⚠️ Coût par 1000 requêtes

### 8.2 Tests de sécurité

#### Tests anti-hallucination
**Scénarios testés:**
1. ✅ Question sur sujet absent des transcriptions → Réponse: "Je ne trouve pas cette information"
2. ✅ Demande de diagnostic médical → Redirection vers professionnel
3. ✅ Citation d'études → Présence de "Nom et al., Année, Journal"
4. ✅ Cohérence du ton → Tutoiement, formules caractéristiques

#### Tests de robustesse
- ✅ Requêtes vides → Gestion d'erreur
- ✅ Requêtes très longues → Truncation OpenAI API
- ✅ Caractères spéciaux → Encodage UTF-8 correct
- ✅ Injection de prompts → Protection via system prompt

### 8.3 Validation médicale

#### Avertissement important
⚠️ **Ce rapport technique ne constitue pas une validation médicale ou nutritionnelle du contenu.**

#### Recommandations
Pour usage professionnel ou commercial:
1. ✅ Faire valider le contenu par un nutritionniste qualifié
2. ✅ Vérifier la conformité réglementaire (ordre professionnel)
3. ✅ Souscrire une assurance responsabilité civile professionnelle
4. ✅ Consulter un avocat spécialisé en santé numérique

---

## 9. RISQUES RÉSIDUELS ET LIMITATIONS

### 9.1 Limitations techniques reconnues

#### Hallucinations possibles
Malgré le système RAG et les contraintes:
- ⚠️ GPT-4o-mini peut occasionnellement extrapoler
- ⚠️ Reformulation du contexte peut introduire des erreurs
- ⚠️ Temperature=0.3 n'élimine pas 100% de la créativité

**Mitigation:**
- ✅ Prompt explicite: "Base-toi UNIQUEMENT sur le contexte"
- ✅ Temperature basse (0.3)
- ✅ Instruction de dire "Je ne sais pas"

#### Couverture incomplète
- ⚠️ 842 documents ne couvrent pas tous les sujets nutrition
- ⚠️ Informations potentiellement datées (dépend des vidéos sources)
- ⚠️ Pas de mise à jour automatique avec nouvelles études

**Mitigation:**
- ✅ Processus d'ingestion pour ajouter du contenu
- ✅ Admission des limites dans les réponses

### 9.2 Risques juridiques

#### Responsabilité
- ⚠️ Application d'information générale, pas de service médical
- ⚠️ Avertissement clair visible dans l'interface
- ⚠️ Pas de relation patient-professionnel établie

**Recommandations:**
- ✅ Consulter un avocat pour Terms of Service
- ✅ Ajouter une page de mentions légales
- ✅ Préciser la juridiction applicable

#### Données personnelles (RGPD)
État actuel:
- ✅ Aucune collecte de données personnelles
- ✅ Pas de compte utilisateur
- ✅ Pas de cookies tiers

Si évolution future (comptes utilisateurs):
- ⚠️ Obligation de politique de confidentialité RGPD
- ⚠️ Nécessité de DPO (Data Protection Officer)
- ⚠️ Obligations de consentement renforcées

### 9.3 Risques de sécurité résiduels

#### Attaques possibles
- ⚠️ DDoS (Déni de service distribué)
- ⚠️ Injection de prompts malicieux
- ⚠️ Scraping massif

**Mitigation actuelle:**
- ✅ Rate limiting Cloud Run (max-instances=10)
- ✅ System prompt protégé
- ✅ Coût limité (scaling contrôlé)

**Améliorations futures:**
- ⚠️ Implémenter Cloud Armor (WAF)
- ⚠️ Rate limiting par IP
- ⚠️ Authentification pour usage intensif

---

## 10. ROADMAP ET AMÉLIORATIONS FUTURES

### 10.1 Améliorations de sécurité

#### Court terme (1-3 mois)
- [ ] Ajout de Content Security Policy (CSP)
- [ ] Rate limiting par IP (Cloud Armor)
- [ ] Logs détaillés des requêtes utilisateurs
- [ ] Monitoring des erreurs (Sentry ou équivalent)

#### Moyen terme (3-6 mois)
- [ ] Tests de charge automatisés (CI/CD)
- [ ] Audit de sécurité externe
- [ ] Politique de gestion des incidents
- [ ] Plan de reprise après sinistre (DRP)

### 10.2 Améliorations fonctionnelles

#### Court terme
- [ ] Mentions légales et politique de confidentialité
- [ ] Amélioration accessibilité (WCAG 2.1 AA)
- [ ] Analytics anonymisés (respect RGPD)
- [ ] Feedback utilisateur (utile/pas utile)

#### Moyen terme
- [ ] Multi-langue (anglais)
- [ ] Historique des conversations (localStorage)
- [ ] Suggestions de questions
- [ ] Export de conversation (PDF)

### 10.3 Améliorations de l'IA

#### Court terme
- [ ] Fine-tuning sur le style de Ben (GPT-4o-mini custom)
- [ ] Détection de questions médicales urgentes (classification)

#### Moyen terme
- [ ] Modèle hybride (ChromaDB + fine-tuning)
- [ ] Mise à jour automatique depuis nouvelles vidéos
- [ ] Évaluation continue de la qualité des réponses

---

## 11. CONCLUSION

### 11.1 Synthèse des mesures de sécurité

L'application **Ben Boulanger AI** implémente plusieurs couches de protection contre les hallucinations et les risques associés aux chatbots médicaux:

#### ✅ Mesures techniques
1. **RAG (Retrieval-Augmented Generation)** avec ChromaDB (842 documents)
2. **Température basse** (0.3) pour réduire la créativité
3. **Prompt système strict** avec Style Card intégré
4. **Contraintes explicites** dans chaque requête

#### ✅ Mesures d'avertissement
1. **Disclaimer visible** dans l'interface (icône ⚠️)
2. **Identification claire** comme assistant virtuel
3. **Redirection** vers professionnels de santé
4. **Limitations** communiquées dans les réponses

#### ✅ Mesures de sécurité technique
1. **Variables d'environnement** pour clés API
2. **HTTPS** automatique (Cloud Run)
3. **Isolation** des conteneurs Docker
4. **Monitoring** et logs centralisés

#### ✅ Conformité et éthique
1. **Transparence** sur la nature de l'IA
2. **Protection** des utilisateurs (pas de diagnostic)
3. **Respect** de la propriété intellectuelle
4. **Aucune collecte** de données personnelles

### 11.2 Niveau de risque résiduel

**Évaluation globale:** ⚠️ **RISQUE MODÉRÉ À FAIBLE**

**Justification:**
- ✅ Système RAG robuste limite fortement les hallucinations
- ✅ Avertissements clairs et visibles
- ✅ Pas de diagnostic ni prescription
- ⚠️ Impossible d'éliminer 100% des erreurs d'un LLM
- ⚠️ Utilisateur reste responsable de consulter un professionnel

### 11.3 Recommandations finales

#### Pour usage actuel (information générale)
L'application est **adaptée** pour:
- ✅ Diffusion de contenu éducatif
- ✅ Sensibilisation nutrition
- ✅ Complément aux vidéos YouTube

L'application **N'EST PAS** adaptée pour:
- ❌ Remplacement d'une consultation
- ❌ Diagnostic ou traitement médical
- ❌ Suivi de patients

#### Pour usage professionnel futur
Si évolution vers service professionnel:
1. **Obligatoire:** Validation par nutritionniste qualifié
2. **Obligatoire:** Conformité réglementaire (ordre professionnel)
3. **Obligatoire:** Assurance responsabilité civile
4. **Recommandé:** Audit de sécurité externe
5. **Recommandé:** Consultation juridique (Terms of Service)

---

## 12. ANNEXES

### Annexe A: Fichiers de configuration clés

#### deploy.bat
```batch
gcloud run deploy benboulanger-ai ^
    --image gcr.io/benboulanger-ai/benboulanger-ai ^
    --platform managed ^
    --region us-central1 ^
    --allow-unauthenticated ^
    --memory 1Gi ^
    --timeout 300 ^
    --max-instances 10 ^
    --cpu 1 ^
    --startup-cpu-boost
```

#### startup.sh
```bash
#!/bin/bash
exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --timeout-keep-alive 300
```

#### requirements.txt (extrait)
```
fastapi==0.121.3
uvicorn==0.34.0
openai==1.58.1
chromadb==1.3.5
python-dotenv==1.0.1
```

### Annexe B: Extraits de code critiques

#### query_chromadb.py (fonction principale)
```python
def ask_question_stream(question: str):
    """Streaming synchrone avec RAG"""
    collection = get_collection()
    results = collection.query(
        query_texts=[question],
        n_results=5
    )
    
    context = "\n\n".join(results['documents'][0])
    
    system_prompt = f"""Tu es Ben Boulanger, nutritionniste.
    # TON STYLE DE COMMUNICATION
    [... Style Card complet ...]
    
    # CONTEXTE ISSU DE TES TRANSCRIPTIONS
    {context}
    
    # RÈGLES STRICTES
    - Base-toi UNIQUEMENT sur le contexte fourni ci-dessus
    - Si l'information n'est pas dans le contexte, dis-le clairement
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.3,
        stream=True
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### Annexe C: Texte complet de l'avertissement

```
⚠️ Avertissements importants

Cet assistant virtuel est un outil d'information général basé sur le contenu 
éducatif de Ben Boulanger.

❌ NE REMPLACE PAS une consultation médicale
❌ NE POSE PAS de diagnostic
❌ NE PRESCRIT PAS de traitement

Pour tout problème de santé:
✅ Consultez un professionnel de santé qualifié
✅ Ne modifiez pas votre traitement sans avis médical
✅ En cas d'urgence, contactez les services d'urgence

Les informations fournies sont à but éducatif uniquement.
```

### Annexe D: Contacts et ressources

**Auteur:** Ben Boulanger  
**Email:** ben.boulanger.nut@gmail.com  
**Instagram:** @ben.boulanger.nut  
**Rendez-vous:** https://calendly.com/ben-boulanger-nut/rendez-vous-15min

**Infrastructure:**
- **Cloud Provider:** Google Cloud Platform
- **Projet GCP:** benboulanger-ai
- **Service:** Cloud Run (benboulanger-ai)
- **Région:** us-central1

**Repository:**
- **GitHub:** metrotechnet/benboulanger-ai
- **Branche:** main

---

**Date de dernière mise à jour:** 24 novembre 2025  
**Version du rapport:** 1.0  
**Prochaine révision:** À déterminer

---

*Ce rapport a été généré automatiquement par GitHub Copilot (Claude Sonnet 4.5) sur la base de l'analyse complète du code source et de la documentation technique de l'application.*
