import os
import json
import re
import random
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / '.env')

# Initialize ChromaDB client (local storage)
chroma_client = None
collection = None

# Initialize Vercel AI Gateway client (OpenAI-compatible)
# See https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-chat-completions
client = OpenAI(
    api_key=os.getenv("AI_GATEWAY_API_KEY"),
    base_url="https://ai-gateway.vercel.sh/v1"
)



def load_style_guides():
    """Load style guides from JSON file"""
    try:
        with open(PROJECT_ROOT / 'config' / 'style_guides.json', 'r', encoding='utf-8') as f:
            style_data = json.load(f)
        
        # Format the style guides for use in prompts
        formatted_guides = {}
        for lang, data in style_data.items():
            guide = f"# {data['title']}\n\n"
            guide += f"\n## {data['characteristic_expressions']['title']}\n"
            for phrase in data['characteristic_expressions']['phrases']:
                guide += f"- \"{phrase}\"\n"
            guide += f"\n## {data['tone_and_voice']['title']}\n"
            for char in data['tone_and_voice']['characteristics']:
                guide += f"- {char}\n"
            guide += f"\n## {data['key_messages']['title']}\n"
            for msg in data['key_messages']['messages']:
                guide += f"- \"{msg}\"\n"
            formatted_guides[lang] = guide
        
        return formatted_guides, style_data
    except Exception as e:
        return {}, {}

def load_system_prompts():
    """Load system prompts from JSON file"""
    try:
        with open(PROJECT_ROOT / 'config' / 'system_prompts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {}

def load_prompts(kb_name=None):
    """
    Load prompts from JSON file in the config folder (single-agent setup)
    
    Args:
        kb_name: Ignored for single-agent setup
    """
    try:
        kb_path = PROJECT_ROOT / "config"
        prompts_path = kb_path / 'prompts.json'
            
        with open(prompts_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {}

def build_prompt_from_template(language, context, question, history_text="", agent=None):
    """Build a complete prompt from the JSON template. Returns (prompt, model_config)"""
    prompts_data = load_prompts(kb_name=agent)
    lang_data = prompts_data.get(language, prompts_data.get("fr", {}))
    
    # Extract model configuration
    model_config = {
        "name": prompts_data.get("model_name", "openai/gpt-4o-mini")
    }
    
    if not lang_data:
        return None, model_config
    
    # Build communication style content
    comm_style = lang_data.get('communication_style', {})
    tone = comm_style.get('tone_and_voice', {})
    recurring = comm_style.get('recurring_messages', {})
    
    tone_content = f"## {tone.get('title', '')}\n"
    for char in tone.get('characteristics', []):
        tone_content += f"- {char}\n"
    
    recurring_content = f"\n## {recurring.get('title', '')}\n"
    for msg in recurring.get('messages', []):
        recurring_content += f"- « {msg} »\n"
    
    communication_style_content = tone_content + recurring_content
    
    # Build absolute rules content
    rules = lang_data.get('absolute_rules', {})
    rules_content = ""
    for rule in rules.get('rules', []):
        rules_content += f"- {rule}\n"
    
    # Build behavioral constraints content
    constraints = lang_data.get('behavioral_constraints', {})
    constraints_content = ""
    for constraint in constraints.get('constraints', []):
        constraints_content += f"- {constraint}\n"
    
    # Build output format content
    output_format = lang_data.get('output_format', {})
    output_format_content = ""
    for format_rule in output_format.get('format_rules', []):
        output_format_content += f"- {format_rule}\n"
    
    # Build the final prompt using the template
    template = lang_data.get('template', '')
    prompt = template.format(
        system_role=lang_data.get('system_role', ''),
        important_notice=lang_data.get('important_notice', ''),
        communication_style_title=comm_style.get('title', ''),
        communication_style_content=communication_style_content,
        absolute_rules_title=rules.get('title', ''),
        absolute_rules_content=rules_content,
        behavioral_constraints_title=constraints.get('title', ''),
        behavioral_constraints_content=constraints_content,
        output_format_title=output_format.get('title', ''),
        output_format_content=output_format_content,
        context=context,
        history=history_text,
        question=question
    )
    
    return prompt, model_config


def query_chromadb(data=None):

    try:
        chromadb_url = os.getenv("CHROMADB_CENTRAL_URL")
        url = f"{chromadb_url}/bibliosense/query"
        resp = requests.post(url, json=data, timeout=30)
        return resp.json()
    except Exception as e:
        return {"error": f"Failed to query central ChromaDB: {str(e)}"}
    


def is_substantial_question(question):
    """
    Vérifie si la question est suffisamment substantielle pour mériter des liens.
    Retourne False pour les questions trop courtes ou génériques.
    """
    if not question or len(question.strip()) < 10:
        return False
    
    # Compter les mots significatifs (au moins 3 caractères)
    words = [w for w in question.split() if len(w) >= 3]
    if len(words) < 3:
        return False
    
    # Liste de phrases génériques qui ne méritent pas de liens
    generic_phrases = [
        'pose une question',
        'aide moi',
        'bonjour',
        'salut',
        'merci',
        'hello',
        'hi',
        'help',
        'ask a question',
        'ask question',
    ]
    
    question_lower = question.lower().strip()
    for phrase in generic_phrases:
        if question_lower == phrase or question_lower == phrase + '?':
            return False
    
    return True

def extract_pmids_from_text(text):
    """Extrait toutes les références PMID d'un texte."""
    return re.findall(r'PMID:\s*\d+', text)


def detect_vague_question(question, language="fr"):
    """
    Détecte si une question est trop vague et nécessite des clarifications.
    
    Args:
        question: Question de l'utilisateur
        language: Langue de la question
        
    Returns:
        tuple (is_vague: bool, clarification_message: str or None)
    """
    question_lower = question.lower().strip()
    
    # Questions très courtes (moins de 3 mots non-vides)
    words = [w for w in question_lower.split() if len(w) > 2]
    if len(words) < 3:
        # Vérifier si c'est juste des termes génériques
        generic_terms_fr = ['livre', 'livres', 'roman', 'romans', 'auteur', 'auteurs', 'lecture', 'lire']
        generic_terms_en = ['book', 'books', 'novel', 'novels', 'author', 'authors', 'read', 'reading']
        generic_terms = generic_terms_fr if language == 'fr' else generic_terms_en
        
        if any(term in question_lower for term in generic_terms) and len(words) <= 2:
            if language == 'fr':
                return True, "Pouvez-vous préciser ce que vous recherchez? Par exemple:\n- Un genre spécifique (roman policier, science-fiction, romance, etc.)?\n- Un auteur en particulier?\n- Un thème ou sujet qui vous intéresse?\n- Un type de lecture (facile, complexe, court, série, etc.)?"
            else:
                return True, "Could you be more specific about what you're looking for? For example:\n- A specific genre (mystery, sci-fi, romance, etc.)?\n- A particular author?\n- A theme or topic of interest?\n- A type of reading (easy, complex, short, series, etc.)?"
    
    # Termes très vagues sans qualificatifs
    vague_patterns_fr = [
        (r'^(un|une|des)\s+(bon|bonne|bons|bonnes)\s+(livre|livres|roman|romans)[\s?!.]*$', 
         "Qu'est-ce qui rend un livre 'bon' pour vous? Pourriez-vous préciser:\n- Le genre que vous préférez?\n- Les thèmes qui vous intéressent?\n- Le style d'écriture que vous aimez?\n- Des auteurs que vous avez appréciés?"),
        (r'^(quelque chose|qqch)\s+(d[\'e])?intéressant', 
         "Qu'est-ce qui vous intéresse en particulier? Un genre, un auteur, un thème spécifique?"),
        (r'^(un|une)\s+(livre|roman)\s*[\s?!.]*$',
         "Quel type de livre recherchez-vous? (genre, auteur, thème, style...)"),
        (r'^\s*(livre|livres|roman|romans)\s*[\s?!.]*$',
         "Pouvez-vous préciser quel type de livre vous intéresse? (genre, auteur, thème...)"),
    ]
    
    vague_patterns_en = [
        (r'^(a|an|some)\s+good\s+(book|books|novel|novels)[\s?!.]*$',
         "What makes a book 'good' for you? Could you specify:\n- Your preferred genre?\n- Topics of interest?\n- Writing style you enjoy?\n- Authors you've liked?"),
        (r'^something\s+interesting',
         "What interests you in particular? A genre, author, or specific theme?"),
        (r'^(a|an)\s+(book|novel)\s*[\s?!.]*$',
         "What type of book are you looking for? (genre, author, theme, style...)"),
        (r'^\s*(book|books|novel|novels)\s*[\s?!.]*$',
         "Could you specify what type of book interests you? (genre, author, theme...)"),
    ]
    
    patterns = vague_patterns_fr if language == 'fr' else vague_patterns_en
    
    for pattern, message in patterns:
        if re.match(pattern, question_lower):
            return True, message
    
    return False, None


def reformulate_question_with_context(question, conversation_history, language="fr"):
    """
    Reformule la question en tenant compte du contexte conversationnel et
    qualifie la question comme 'general' ou 'specific'.
    
    Args:
        question: Question actuelle de l'utilisateur
        conversation_history: Historique des messages
        language: Langue de la conversation
        
    Returns:
        tuple (reformulated_question: str, question_type: str)
            question_type is 'general' (e.g. genre, broad theme) or 'specific' (e.g. specific author, title)
    """
    # Construire le contexte des derniers échanges (exclure le message actuel)
    context = ""
    if conversation_history and len(conversation_history) >= 2:
        recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history[:-1]
        for msg in recent_messages:
            role_label = "Utilisateur" if msg['role'] == 'user' else "Assistant"
            context += f"{role_label}: {msg['content'][:200]}...\n\n"
    
    # Prompt de reformulation + qualification
    if language == 'fr':
        reformulation_prompt = f"""{"Contexte de la conversation précédente:" + chr(10) + context + chr(10) if context else ""}Question actuelle de l'utilisateur: "{question}"

Effectue deux tâches:
1. REFORMULATION: Si la question fait référence au contexte précédent (ex: "du même auteur", "similaire", "autres livres"), reformule-la de manière standalone. Sinon, retourne-la telle quelle.
2. QUALIFICATION: Qualifie la question comme "general" ou "specific".
   - "general": demande large (un genre, un thème, un type de livre, ex: "roman policier", "science-fiction", "livre pour enfants")
   - "specific": demande précise (un auteur spécifique, un titre, un sujet pointu, ex: "livres de Victor Hugo", "Le Petit Prince")

Réponds UNIQUEMENT en JSON, sans explication:
{{"question": "la question reformulée", "type": "general ou specific"}}"""
    else:
        reformulation_prompt = f"""{"Previous conversation context:" + chr(10) + context + chr(10) if context else ""}Current user question: "{question}"

Perform two tasks:
1. REFORMULATION: If the question references previous context (e.g., "by the same author", "similar", "other books"), reformulate it as standalone. Otherwise, return it as is.
2. QUALIFICATION: Qualify the question as "general" or "specific".
   - "general": broad request (a genre, theme, type of book, e.g., "mystery novels", "sci-fi", "children's books")
   - "specific": precise request (a specific author, title, narrow topic, e.g., "books by Victor Hugo", "The Little Prince")

Respond ONLY in JSON, no explanation:
{{"question": "the reformulated question", "type": "general or specific"}}"""
    
    try:
        # Utiliser Vercel AI Gateway pour la reformulation
        prompts_data = load_prompts()
        reformulation_model = prompts_data.get("model_name", "openai/gpt-4o-mini")
        response = client.chat.completions.create(
            model=reformulation_model,
            messages=[
                {"role": "user", "content": reformulation_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Parse JSON response
        result = json.loads(raw)
        reformulated = result.get("question", question).strip()
        question_type = result.get("type", "specific").strip().lower()
        
        # Validate question_type
        if question_type not in ("general", "specific"):
            question_type = "specific"
        
        # Log pour débug
        print(f"[Reformulation] Original: '{question}'")
        if reformulated.lower() != question.lower():
            print(f"[Reformulation] Reformulée: '{reformulated}'")
        print(f"[Reformulation] Type: {question_type}")
        
        return reformulated, question_type
        
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract the text anyway
        print(f"[Reformulation] JSON parse error, raw: {raw}")
        return raw if raw else question, "specific"
    except Exception as e:
        print(f"[Reformulation] Error: {e}, using original question")
        return question, "specific"

def ask_question_stream(question, language="fr", timezone="UTC", locale="fr-FR", top_k=100, conversation_history=None, session=None, question_id=None, agent=None, bibliotheque="all", distance_threshold=None):
    """Streaming version of ask_question with language support and conversation history
    
    Args:
        distance_threshold: Optional float. If provided, only return results with distance < threshold.
                          Lower distance = higher similarity. Typical values: 0.3-0.5
    """
    # Use conversation_history if provided, otherwise empty list
    if conversation_history is None:
        conversation_history = []

    # Build history_text for prompt template
    history_text = ""
    # Extract previously recommended books from history to avoid repetition
    previously_recommended = set()
    
    if conversation_history and len(conversation_history) > 1:
        history_text = "\n\nHISTORIQUE DE LA CONVERSATION:\n"
        recent_history = conversation_history[-7:-1] if len(conversation_history) > 1 else []
        for msg in recent_history:
            role_label = "Utilisateur" if msg['role'] == 'user' else "Assistant"
            history_text += f"{role_label}: {msg['content']}\n"
            
            # Extract book titles from assistant responses (look for ### **Title** pattern)
            if msg['role'] == 'assistant':
                titles = re.findall(r'###\s*\*\*(.+?)\*\*', msg['content'])
                previously_recommended.update(titles)
    


    try:
        # Détecter si la question est trop vague et nécessite clarification
        is_vague, clarification_msg = detect_vague_question(question, language)
        if is_vague and not conversation_history:
            # Seulement demander clarification si pas d'historique (première question)
            # Si historique existe, la reformulation pourrait aider
            print(f"[Vague Question Detected] Question: '{question}'")
            yield clarification_msg
            return
        
        # Reformuler la question en tenant compte du contexte si nécessaire
        # Cela permet de gérer des questions comme "du même auteur", "similaire", etc.
        search_question, question_type = reformulate_question_with_context(question, conversation_history, language)
        print(f"[ask_question_stream] Search question after reformulation: '{search_question}' (type: {question_type})", flush=True)

        # Get embedding for the reformulated question
        query_emb = client.embeddings.create(
            model="openai/text-embedding-3-large", 
            input=search_question
        ).data[0].embedding

        # Build where filter for library selection
        where_filter = None
        if bibliotheque and bibliotheque != "all":
            where_filter = {"bibliotheque": bibliotheque}

        # We only need top 150 for diversity filtering before shuffling and taking top 50
        # Query ChromaDB with optional library filter
        nbr_results = 500
        query_params = {
            "query_embedding": query_emb,
            "n_results": nbr_results,
            "include": ['documents', 'metadatas']
        }
        if where_filter:
            query_params["where"] = where_filter
            
        # Ensure query_params is JSON serializable
        query_params = json.loads(json.dumps(query_params, default=str))
        results = query_chromadb(query_params)
        print(f"ChromaDB results: {results}")  # Debug log for ChromaDB results
        
        if not results['documents'] or not results['documents'][0]:
            yield "No relevant information found. Please make sure you have indexed some transcripts."
            return
        
        documents = results['documents'][0]
        metadatas_list = results.get('metadatas', [[]])[0]

        # Filtrer pour limiter le nombre de livres par auteur (max 2)
        filtered_results = []
        for doc, meta in zip(documents, metadatas_list):
            title = meta.get('titre') or meta.get('title') or ''
            # Inclure les livres non recommandés dans l'historique
            if title and title not in previously_recommended:
                filtered_results.append((doc, meta))

        
        # Si on a trop filtré, garder quand même des résultats
        if len(filtered_results) < 20:
            filtered_results = list(zip(documents, metadatas_list))[:50]
        
        # Shuffle les résultats si la question est générale pour plus de diversité
        if question_type == 'general':
            random.shuffle(filtered_results)
            print(f"[Query] Shuffled results (general question)", flush=True)

        # Prendre les 50 premiers
        filtered_results = filtered_results[:50]
        documents, metadatas_list = zip(*filtered_results) if filtered_results else ([], [])
        documents = list(documents)
        metadatas_list = list(metadatas_list)

        #Print title of first 10 books for debugging
        print(f"[Query] Top {len(documents)} results (after filtering & shuffle):", flush=True)
        for i, meta in enumerate(metadatas_list[:10]):
            title = meta.get('titre') or meta.get('title') or 'Unknown Title'
            auteur = meta.get('auteur') or meta.get('author') or 'Unknown Author'
            print(f"  {i+1}. {title} by {auteur}", flush=True)                                                         

        # Build context from results with metadata
        contexts = []
        for i, doc in enumerate(documents):
            # Include metadata with each document
            metadata = metadatas_list[i] if i < len(metadatas_list) else {}
            context_entry = f"Document {i+1}:\n{doc}"
            
            # Add relevant metadata fields
            if metadata:
                metadata_str = "\nMétadonnées:"
                for key, value in metadata.items():
                    if key in ['image', 'couverture', 'cover', 'image_url', 'cover_url', 'titre', 'title', 
                               'auteur', 'author', 'lien', 'resume', 'summary', 'categorie', 'category',
                               'editeur', 'publisher', 'parution', 'publication', 'pages', 'langue', 'language', 'bibliotheque']:
                        metadata_str += f"\n- {key}: {value}"
                context_entry += metadata_str
            
            contexts.append(context_entry)
        context = "\n\n".join(contexts)


        # Build prompt using template from JSON
        prompt, model_config = build_prompt_from_template(language, context, question, history_text, agent=agent)
        
        if not prompt:
            yield "Error: Unable to load prompt template."
            return

        # Get streaming response from Vercel AI Gateway
        model_name = model_config.get('name', 'openai/gpt-4o-mini')
        
        stream = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,
            stream=True
        )

        first_chunk = True
        answer = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                # Strip leading whitespace from first chunk only
                if first_chunk:
                    content = content.lstrip()
                    first_chunk = False
                if content:
                    answer += content
                    yield content

    except Exception as e:
        yield f"Error processing your question: {str(e)}"

