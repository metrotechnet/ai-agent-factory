import os
import json
import re
import random
from pathlib import Path
from dotenv import load_dotenv
import requests
from openai import OpenAI
from api.refusal_engine import validate_user_query

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
    Load prompts from JSON file in the knowledge base folder (single-agent setup)
    
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
        "supplier": prompts_data.get("model_supplier", "openai"),
        "name": prompts_data.get("model_name", "gpt-4o-mini")
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
        context=context,
        history=history_text,
        question=question
    )
    
    return prompt, model_config

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
            "query": data
        }

        url = f"{chromadb_url}/query"

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

def get_links_from_contexts(contexts, metadatas=None, agent=None):
    """Extract PMID references from chunk metadata's 'references' field."""
    links = set()

    if metadatas:
        for meta in metadatas:
            if not isinstance(meta, dict):
                continue
            refs_str = meta.get("references", "")
            if refs_str:
                try:
                    refs = json.loads(refs_str)
                    for pmid in refs.get("pmids", []):
                        links.add(f"PMID: {pmid}")
                except (json.JSONDecodeError, TypeError):
                    pass

    return list(links)


def ask_question_stream(question, language="fr", timezone="UTC", locale="fr-FR", top_k=5, conversation_history=None, session=None, question_id=None, agent=None):
    """Streaming version of ask_question with language support and conversation history"""
    # Use conversation_history if provided, otherwise empty list
    if conversation_history is None:
        conversation_history = []

    # Build history_text for refusal_engine
    history_text = ""
    if conversation_history and len(conversation_history) > 1:
        history_text = "\n\nHISTORIQUE DE LA CONVERSATION:\n"
        recent_history = conversation_history[-7:-1] if len(conversation_history) > 1 else []
        for msg in recent_history:
            role_label = "Utilisateur" if msg['role'] == 'user' else "Assistant"
            history_text += f"{role_label}: {msg['content']}\n"

    # context is not available yet (need ChromaDB), so pass empty string for now
    refusal_result = validate_user_query(question, llm_call_fn=None, language=language)
    if refusal_result and refusal_result.get("decision") == "refuse":
        # Store empty links list in session for refusal
        if session is not None and question_id is not None:
            if 'links' not in session:
                session['links'] = {}
            session['links'][question_id] = []
        yield "__REFUSAL__"
        yield refusal_result["answer"]
        return


    try:
        # Get embedding for the question
        query_emb = client.embeddings.create(
            model="text-embedding-3-large", 
            input=question
        ).data[0].embedding

        # Query ChromaDB
        query_params = {
            "query_embedding": query_emb,
            "n_results": top_k,
            "include": ['documents', 'metadatas']
        }
            
        # Ensure query_params is JSON serializable
        query_params = json.loads(json.dumps(query_params, default=str))
        results = query_chromadb(project_name="nutria", collection_name="gdrive_documents", data=query_params)

        if not results['documents'] or not results['documents'][0]:
            yield "No relevant information found. Please make sure you have indexed some transcripts."
            return

        # Build context from results
        contexts = []
        for i, doc in enumerate(results['documents'][0]):
            contexts.append(doc)
        context = "\n\n".join(contexts)

        # Extraire les liens du contexte (with source metadata lookup)
        # Only extract links for substantial questions (not for generic/short questions)
        links = []
        if is_substantial_question(question):
            metadatas = results.get('metadatas', [[]])[0]
            links = get_links_from_contexts(contexts, metadatas=metadatas, agent=agent)
        
        # Save links in session if provided
        if session is not None and question_id is not None:
            if 'links' not in session:
                session['links'] = {}
            session['links'][question_id] = links

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
