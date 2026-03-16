import os
import json
import re
import random
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.config import Settings
import google.generativeai as genai

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / '.env')

# Initialize ChromaDB client (local storage)
chroma_client = None
collection = None
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))



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
    Load prompts from JSON file in the knowledge base folder (single-agent setup)
    
    Args:
        kb_name: Ignored for single-agent setup
    """
    try:
        kb_path = PROJECT_ROOT / "knowledge-base" / "agent"
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

def get_collection(kb_name=None):
    """
    Get or create ChromaDB collection for the specified knowledge base
    
    Args:
        kb_name: Name of the knowledge base (default: from "agent" env var)
    """
    global chroma_client, collection
    
    if kb_name is None:
        kb_name = "agent"
    
    print(f"[get_collection] Called with kb_name: {kb_name}", flush=True)
    print(f"[get_collection] Collection already loaded: {collection is not None}", flush=True)
    
    if collection is None:
        try:
            kb_path = PROJECT_ROOT / "knowledge-base" / kb_name
            chroma_path = str(kb_path / "chroma_db")
            
            print(f"[get_collection] KB path: {kb_path}", flush=True)
            print(f"[get_collection] Chroma path: {chroma_path}", flush=True)
            print(f"[get_collection] Path exists: {os.path.exists(chroma_path)}", flush=True)
            
            if not os.path.exists(chroma_path):
                print(f"[get_collection] ERROR: ChromaDB path does not exist!", flush=True)
                return None
            
            # Create ChromaDB client with optimized settings for Cloud Run
            print(f"[get_collection] Initializing ChromaDB client...", flush=True)
            chroma_client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False
                )
            )
            print(f"[get_collection] ChromaDB client initialized", flush=True)
            
            # Get collection (will create if doesn't exist)
            try:
                print(f"[get_collection] Getting collection 'gdrive_documents'...", flush=True)
                collection = chroma_client.get_collection(name="gdrive_documents")
                print(f"[get_collection] Collection loaded successfully", flush=True)
                print(f"[get_collection] Collection document count: {collection.count()}", flush=True)
            except Exception as e:
                print(f"[get_collection] Collection not found, creating new one. Error: {e}", flush=True)
                collection = chroma_client.create_collection(
                    name="gdrive_documents"
                )
                print(f"[get_collection] New collection created", flush=True)
                
        except Exception as e:
            print(f"[get_collection] ERROR during initialization: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            return None
    else:
        print(f"[get_collection] Returning cached collection (count: {collection.count()})", flush=True)
    
    return collection

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
    """Extract links from contexts and metadata.
    
    Priority:
    1. Check metadatas for 'links' field (new ChromaDB format)
    2. Extract from matched chunks text (fallback)
    3. Look up chunk_0 of source documents (last resort)
    """
    links = set()
    
    # Priority 1: Check metadatas for direct link references (new format)
    if metadatas:
        for meta in metadatas:
            if isinstance(meta, dict) and 'links' in meta and meta['links']:
                # Links are stored as comma-separated string
                link_list = meta['links'].split(',')
                for link in link_list:
                    link = link.strip()
                    if link:
                        links.add(f"PMID: {link}")
    
    # If we found links in metadata, return them immediately
    if links:
        return list(links)
    
    # Priority 2: Fallback - check the matched chunks text themselves
    for doc in contexts:
        links.update(extract_pmids_from_text(doc))
    
    # Priority 3: If still no links and metadatas available, look up chunk_0
    if not links and metadatas:
        col = get_collection(kb_name=agent)
        if col:
            sources = set()
            for meta in metadatas:
                if isinstance(meta, dict) and 'source' in meta:
                    sources.add(meta['source'])
            chunk0_ids = [src + '_chunk0' for src in sources]
            if chunk0_ids:
                try:
                    results = col.get(ids=chunk0_ids, include=['documents'])
                    for doc in results.get('documents', []):
                        if doc:
                            links.update(extract_pmids_from_text(doc))
                except Exception as e:
                    print(f'Error fetching chunk_0 for links: {e}')
    
    return list(links)

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
    Reformule la question en tenant compte du contexte conversationnel.
    Utile pour des questions comme "du même auteur", "un autre livre similaire", etc.
    
    Args:
        question: Question actuelle de l'utilisateur
        conversation_history: Historique des messages
        language: Langue de la conversation
        
    Returns:
        Question reformulée de manière standalone
    """
    # Si pas d'historique ou historique trop court, retourner la question telle quelle
    if not conversation_history or len(conversation_history) < 2:
        return question
    
    # Construire le contexte des derniers échanges (exclure le message actuel)
    recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history[:-1]
    context = ""
    for msg in recent_messages:
        role_label = "Utilisateur" if msg['role'] == 'user' else "Assistant"
        context += f"{role_label}: {msg['content'][:200]}...\n\n"
    
    # Prompt de reformulation
    if language == 'fr':
        reformulation_prompt = f"""Contexte de la conversation précédente:
{context}

Question actuelle de l'utilisateur: "{question}"

Si cette question fait référence au contexte précédent (par exemple: "du même auteur", "similaire", "autres livres", "encore", etc.), reformule-la de manière standalone en incluant toutes les informations nécessaires (nom d'auteur, genre, etc.).

Si la question est déjà standalone et claire, retourne-la telle quelle.

Retourne UNIQUEMENT la question reformulée, sans explication."""
    else:
        reformulation_prompt = f"""Previous conversation context:
{context}

Current user question: "{question}"

If this question references the previous context (e.g., "by the same author", "similar", "other books", "more", etc.), reformulate it as a standalone question including all necessary information (author name, genre, etc.).

If the question is already standalone and clear, return it as is.

Return ONLY the reformulated question, without explanation."""
    
    try:
        # Utiliser GPT pour la reformulation (rapide avec gpt-4o-mini)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": reformulation_prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        reformulated = response.choices[0].message.content.strip()
        
        # Log pour débug
        if reformulated.lower() != question.lower():
            print(f"[Reformulation] Original: '{question}'")
            print(f"[Reformulation] Reformulée: '{reformulated}'")
        
        return reformulated
        
    except Exception as e:
        print(f"[Reformulation] Error: {e}, using original question")
        return question

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
    
    # Add note about previously recommended books
    if previously_recommended:
        history_text += f"\n\nLIVRES DÉJÀ RECOMMANDÉS (à éviter pour varier les recommandations):\n"
        for title in previously_recommended:
            history_text += f"- {title}\n"

    col = get_collection()
    if col is None:
        yield "Error: ChromaDB collection is not available. Please run 'python index_chromadb.py' first to index your documents."
        return

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
        search_question = reformulate_question_with_context(question, conversation_history, language)
        print(f"[ask_question_stream] Search question after reformulation: '{search_question}'", flush=True)

        # Get embedding for the reformulated question
        query_emb = client.embeddings.create(
            model="text-embedding-3-large", 
            input=search_question
        ).data[0].embedding

        # Build where filter for library selection
        where_filter = None
        if bibliotheque and bibliotheque != "all":
            where_filter = {"bibliotheque": bibliotheque}

        # We only need top 150 for diversity filtering before shuffling and taking top 50
        top_relevant = 150  # Garde les 150 meilleurs pour augmenter la diversité
        # Query ChromaDB with optional library filter
        query_params = {
            "query_embeddings": [query_emb],
            "n_results": top_relevant,
            "include": ['documents', 'metadatas']
        }
        if where_filter:
            query_params["where"] = where_filter
        
        results = col.query(**query_params)

        if not results['documents'] or not results['documents'][0]:
            yield "No relevant information found. Please make sure you have indexed some transcripts."
            return

        # Option 1: Garder les N meilleurs, puis mélanger seulement ceux-là
        documents = results['documents'][0][:top_relevant]
        metadatas_list = results.get('metadatas', [[]])[0][:top_relevant]

        # Extraire les auteurs déjà recommandés de l'historique
        previously_recommended_authors = set()
        if conversation_history:
            for msg in conversation_history:
                if msg['role'] == 'assistant':
                    # Extraire les auteurs avec regex: *par Auteur*
                    authors = re.findall(r'\*par\s+([^*]+)\*', msg['content'])
                    previously_recommended_authors.update(authors)
        
        # Filtrer pour limiter le nombre de livres par auteur (max 2)
        author_count = {}
        filtered_results = []
        for doc, meta in zip(documents, metadatas_list):
            author = meta.get('auteur') or meta.get('author') or 'Unknown'
            
            # Pénaliser les auteurs déjà recommandés dans l'historique
            if author in previously_recommended_authors:
                # Garder seulement si on a très peu de résultats
                if len(filtered_results) < 20:
                    continue
            
            # Limiter à 2 livres par auteur pour plus de diversité
            if author_count.get(author, 0) < 2:
                filtered_results.append((doc, meta))
                author_count[author] = author_count.get(author, 0) + 1
        
        # Si on a trop filtré, garder quand même des résultats
        if len(filtered_results) < 20:
            filtered_results = list(zip(documents, metadatas_list))[:50]
        
        # Mélanger pour varier les recommandations
        random.shuffle(filtered_results)
        
        # Prendre les 50 premiers après shuffle
        filtered_results = filtered_results[:50]
        documents, metadatas_list = zip(*filtered_results) if filtered_results else ([], [])
        documents = list(documents)
        metadatas_list = list(metadatas_list)

        #Print title of first 10 books for debugging
        print(f"[Query] Top {len(documents)} results (after filtering & shuffle):", flush=True)
        print(f"[Query] Previously recommended authors: {previously_recommended_authors}", flush=True)
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

        # Extraire les liens du contexte (with source metadata lookup)
        # Only extract links for substantial questions (not for generic/short questions)
        links = []
        if is_substantial_question(question):
            links = get_links_from_contexts(contexts, metadatas=metadatas_list, agent=agent)
        
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

        # Get streaming response from configured LLM
        model_name = model_config.get('name', 'gpt-4o-mini')
        model_supplier = model_config.get('supplier', 'openai')
        
        if model_supplier == 'openai':
            # OpenAI streaming
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
                        
        elif model_supplier == 'gemini':
            # Gemini streaming
            model = genai.GenerativeModel(model_name, generation_config={
                "temperature": 1.0
            })
            
            response = model.generate_content(prompt, stream=True)
            
            first_chunk = True
            for chunk in response:
                text = getattr(chunk, "text", None)
                if text:
                    if first_chunk:
                        text = text.lstrip()
                        first_chunk = False
                    if text:
                        yield text
        else:
            yield f"Error: Model supplier '{model_supplier}' not supported. Use 'openai' or 'gemini'."
            return

    except Exception as e:
        yield f"Error processing your question: {str(e)}"

