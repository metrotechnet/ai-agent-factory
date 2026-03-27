import os
import json
import re
import random
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import requests
import google.auth.transport.requests
import google.oauth2.id_token

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / '.env')

# Initialize ChromaDB client (local storage)
chroma_client = None
collection = None

# Initialize Vercel AI Gateway client (OpenAI-compatible)
# See https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-chat-completions
from openai import OpenAI
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
        with open(PROJECT_ROOT / 'api/config' / 'system_prompts.json', 'r', encoding='utf-8') as f:
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
        kb_path = PROJECT_ROOT / "api/config"
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

def format_context(documents, metadatas_list):
    # Build context from results with harmonized metadata (JSON structure)
    context = []
    for i, doc in enumerate(documents):
        metadata = metadatas_list[i] if i < len(metadatas_list) else {}
        # Build structure: {id, text, metadata}
        doc_id = metadata.get('name') 
        # Try to get the main text: prefer 'text' in doc, fallback to 'resume' or 'summary' in metadata
        doc_text = doc if isinstance(doc, str) else doc.get('text') if isinstance(doc, dict) else None
        if not doc_text:
            doc_text = metadata.get('resume') or metadata.get('summary') or ""
        # Compose the structure
        entry = {
            "id": doc_id,
            "text": doc_text,
            "metadata": metadata
        }
        context.append(f"```\n{json.dumps(entry, ensure_ascii=False, indent=2)}\n```")
    return context

def query_chromadb(project_name, collection_name=None, data=None):
    try:
        chromadb_url = os.getenv("CHROMADB_CENTRAL_URL")

        if not chromadb_url:
            raise ValueError("Missing CHROMADB_CENTRAL_URL")

        # =========================
        # 🔐 GET IAM TOKEN
        # =========================
        auth_req = google.auth.transport.requests.Request()

        id_token = google.oauth2.id_token.fetch_id_token(
            auth_req,
            chromadb_url
        )

        headers = {
            "Authorization": f"Bearer {id_token}",
            "Content-Type": "application/json"
        }

        # =========================
        # 📦 PAYLOAD
        # =========================
        payload = {
            "project_name": project_name,
            "collection_name": collection_name,
            "nodes": ["domain", "cctt"],
            "edges": ["eligible_for_funding"],
            "query": data
        }

        url = f"{chromadb_url}/query"
        # url = f"{chromadb_url}/smart_query"

        # =========================
        # 🚀 REQUEST
        # =========================
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        resp.raise_for_status()

        return resp.json()

    except requests.exceptions.HTTPError as e:
        return {
            "error": "HTTP error",
            "status_code": resp.status_code if 'resp' in locals() else None,
            "details": str(e)
        }

    except Exception as e:
        return {
            "error": "Failed to query central ChromaDB",
            "details": str(e)
        }
    


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

def analyze_query_llm(query: str, history_text: str):

    # print(f"[analyze_query_llm] Analyzing query: '{query}' ", flush=True)
    # print(f"[analyze_query_llm] History text: {history_text}", flush=True)
    prompt = f"""
    Tu es un expert en innovation et financement R&D au Québec.

    Analyse la question utilisateur et déteermine si le domaine et le contexte du projet sont bien définis
    Voici la question de l'utilisateur et l'historique de la conversation:
    QUESTION:
    \"\"\"{query}\"\"\"
    HISTORIQUE DE LA CONVERSATION:
    \"\"\"{history_text}\"\"\"\"

    Fournis une analyse structurée de la question en retournant un JSON avec les champs suivants:
    - domaines: liste (ex: IA, santé, chimie, foresterie)
    - clarity_score: entre 0 et 1
    - contexte: une reformulation de la question qui intègre le contexte de l'historique pour mieux comprendre les besoins de l'utilisateur
    - reply_question: une question courte que tu poserais à l'utilisateur pour clarifier le domaine et le contexte si il manque des informations.

    Règles:
    - Évite de demander la même question ou la même information plusieurs fois en te fiant à l'HISTORIQUE DE LA CONVERSATION
    - Si des informations sont manquantes, pose une question de clarification courte et précise (reply_question) pour obtenir les informations manquantes.


    Réponds uniquement en JSON valide, sans explication."""

    prompts_data = load_prompts()
    reformulation_model = prompts_data.get("model_name", "openai/gpt-4o-mini")

    response = client.chat.completions.create(
        model=reformulation_model,
        messages=[
            {"role": "system", "content": "Tu réponds uniquement en JSON valide."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )


    content = response.choices[0].message.content.strip()

    # Remove Markdown code block if present
    if content.startswith('```'):
        content = re.sub(r'^```[a-zA-Z]*\n?', '', content)
        content = re.sub(r'```$', '', content).strip()
    
    try:
        return json.loads(content)
    except Exception:
        return {
            "error": "Invalid JSON from LLM",
            "raw": content
        }
    
def generate_clarification_llm(missing_info):
    questions = {
        "domaine": "Dans quel domaine se situe votre projet (IA, santé, énergie…)?",
        "besoin": "Cherchez-vous du financement, un partenaire ou un développement technique?",
        "stade_projet": "À quel stade est votre projet (idée, prototype, produit)?"
    }


    return [questions[m] for m in missing_info if m in questions]


# Nouvelle version : vérifie si une question similaire a déjà été posée dans l'historique
import difflib
import unicodedata

def normalize_text(text):
    """
    Normalise le texte pour comparaison : minuscule, sans accents, sans ponctuation, espaces réduits.
    """
    if not text:
        return ""
    # Minuscule
    text = text.lower()
    # Supprime les accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    # Supprime la ponctuation
    text = ''.join(c for c in text if c.isalnum() or c.isspace())
    # Réduit les espaces
    text = ' '.join(text.split())
    return text

def is_question_already_asked(reply_question, conversation_history, threshold=0.55):
    """
    Vérifie si la reply_question (ou une question très similaire) a déjà été posée dans l'historique.
    Utilise une similarité de séquence (difflib) sur texte normalisé.
    """
    if not reply_question or not conversation_history:
        return False
    norm_reply = normalize_text(reply_question)
    for msg in conversation_history:
        if msg.get('role') == 'assistant':
            content = msg.get('content', '')
            norm_content = normalize_text(content)
            # Similarité
            ratio = difflib.SequenceMatcher(None, norm_reply, norm_content).ratio()
            # print(f"[is_question_already_asked] Comparing '{norm_reply}' to '{norm_content}' => similarity: {ratio:.2f}", flush=True)
            if ratio >= threshold:
                return True
    return False


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
                {"role": "system", "content": "Tu réponds uniquement en JSON valide."},
                {"role": "user", "content": reformulation_prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )

        content = response.choices[0].message.content.strip()

        # Parse JSON response
        result = json.loads(content)
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
        print(f"[Reformulation] JSON parse error, raw: {content}")
        return content if content else question, "specific"
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
        result  = analyze_query_llm(question,history_text)
        # print(f"[ask_question_stream] Query analysis result: {result}", flush=True)
        if result and result.get("clarity_score") < 0.5 and result.get("reply_question"):
            # Vérifie si la reply_question a déjà été posée dans l'historique
            if not is_question_already_asked(result.get("reply_question"), conversation_history):
                yield result.get("reply_question")
                return
            else:
                print("[ask_question_stream] Clarification déjà posée, on ne la repose pas.")
            


        print(f"[ask_question_stream] Question contexte: {result.get('contexte')}", flush=True)
        print(f"[ask_question_stream] Question domaines: {result.get('domaines')}", flush=True)

        domaines_str = ", ".join(result.get("domaines", [])) if isinstance(result.get("domaines", []), list) else str(result.get("domaines", ""))
        question_data = "domaines: " + domaines_str + "\ncontexte: " + result.get("contexte", "")
        
        # Get embedding for the reformulated question
        query_emb = client.embeddings.create(
            model="text-embedding-3-small",  # 3072 dimensions, supported by OpenAI/Vercel
            input=question_data
        ).data[0].embedding

        # We only need top 150 for diversity filtering before shuffling and taking top 50
        # Query ChromaDB with optional library filter
        nbr_results = 20
        query_params = {
            "query_embedding": query_emb,
            "n_results": nbr_results,
            "include": ['documents', 'metadatas']
        }
           
        # Ensure query_params is JSON serializable
        query_params = json.loads(json.dumps(query_params, default=str))
        cctt_results = query_chromadb("innovia","cctt",query_params)
        
        if not cctt_results['documents'] or not cctt_results['documents'][0]:
            yield "No relevant information found. Please make sure you have indexed some transcripts."
            return
        # print(f"[ask_question_stream] ChromaDB results: {cctt_results['documents'][0]} documents found", flush=True)
        context = "\n\n**CONTEXT_CENTER**:".join(format_context(cctt_results['documents'][0], cctt_results.get('metadatas', [[]])[0]))


        #Get funding info from the same collection
        funding_query_params = {
            "query_embedding": query_emb,
            "n_results": 100,
            "include": ['documents', 'metadatas']
        }
        funding_results = query_chromadb("innovia","funding",funding_query_params)
        # print(f"[ask_question_stream] ChromaDB results: {funding_results['documents'][0]} documents found", flush=True)

        if(funding_results):
            context += "\n\n**CONTEXT_FUNDING**:".join(format_context(funding_results['documents'][0], funding_results.get('metadatas', [[]])[0]))

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

        # À la fin de la réponse, envoyer un flag spécial pour demander au parent d'effacer l'historique utilisateur
        yield "__CLEAR_USER_HISTORY__"

    except Exception as e:
        yield f"Error processing your question: {str(e)}"

