import os
import json
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
            # guide += f"## {data['narrative_structure']['title']}\n"
            # for i, step in enumerate(data['narrative_structure']['steps'], 1):
            #     guide += f"{i}. {step}\n"
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
        print(f"Error loading style guides: {e}")
        return {}, {}

def load_system_prompts():
    """Load system prompts from JSON file"""
    try:
        with open(PROJECT_ROOT / 'config' / 'system_prompts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading system prompts: {e}")
        return {}

def get_collection():
    global chroma_client, collection
    if collection is None:
        try:
            import os
            chroma_path = str(PROJECT_ROOT / "chroma_db")
            
            # Create ChromaDB client with optimized settings for Cloud Run
            chroma_client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False
                )
            )
            
            # Get collection (will create if doesn't exist)
            try:
                collection = chroma_client.get_collection(name="transcripts")
                print(f"Collection 'transcripts' loaded with {collection.count()} documents")
            except:
                print("Creating new transcripts collection...")
                collection = chroma_client.create_collection(name="transcripts")
                print("Empty collection created")
                
        except Exception as e:
            print(f"ChromaDB error: {e}")
            return None
    return collection

def ask_question_stream(question, language="fr", timezone="UTC", locale="fr-FR", top_k=5, conversation_history=None):
    """Streaming version of ask_question with language support and conversation history"""
    col = get_collection()
    
    if col is None:
        yield "Error: ChromaDB collection is not available. Please run 'python index_chromadb.py' first to index your documents."
        return
    
    # Use conversation_history if provided, otherwise empty list
    if conversation_history is None:
        conversation_history = []
    
    try:
        # Get embedding for the question
        query_emb = client.embeddings.create(
            model="text-embedding-3-large", 
            input=question
        ).data[0].embedding
        
        # Query ChromaDB
        results = col.query(
            query_embeddings=[query_emb],
            n_results=top_k
        )
        
        if not results['documents'] or not results['documents'][0]:
            yield "No relevant information found. Please make sure you have indexed some transcripts."
            return
        
        # Build context from results
        contexts = []
        for i, doc in enumerate(results['documents'][0]):
            contexts.append(doc)
        context = "\n\n".join(contexts)
        
 
        # Build conversation history string for context
        history_text = ""
        if conversation_history and len(conversation_history) > 1:  # More than just current question
            history_text = "\n\nHISTORIQUE DE LA CONVERSATION:\n"
            # Include last 6 messages (3 exchanges) for context
            recent_history = conversation_history[-7:-1] if len(conversation_history) > 1 else []
            for msg in recent_history:
                role_label = "Utilisateur" if msg['role'] == 'user' else "Assistant"
                history_text += f"{role_label}: {msg['content']}\n"
        
        # Build full prompts with style guide, context, and conversation history
        prompts = {
            "fr": f"""Tu es Ben, nutritionniste expert avec un style de communication unique et reconnaissable.

                # TON STYLE DE COMMUNICATION EN FRANÇAIS

                ## Expressions caractéristiques à utiliser:
                - "Contrairement aux idées reçues..."
                - "Il est vrai que... Mais..."
                - "Sur le plan [aspect], des études montrent que..."
                - "La vérité, c'est que..."
                - "Entre nous, si [situation absurde]..."
                - "C'est justement parce que..."

                ## Ton et voix:
                - Tutoiement systématique, ton conversationnel et décontracté
                - Scientifiquement rigoureux
                - Démystificateur avec humour et pédagogie
                - Humble et nuancé sur les limites des études
                - Vocabulaire scientifique expliqué simplement
                - Anti-dogmatique, évite les absolus et solutions miracles

                ## Messages clés à transmettre:
                - "Ce n'est pas une pilule magique"
                - "Il n'y a pas de solution universelle"
                - "Le risque dépend avant tout de la dose"
                - "Nous ne sommes pas tous égaux face au poids"
                - "Focus sur alimentation, sommeil, activité physique"
                - "Approche holistique et durable"

                CONTEXTE DISPONIBLE:
                {context}
                {history_text}

                QUESTION DE L'UTILISATEUR: {question}

                RÈGLES ABSOLUES:
                - Réponds UNIQUEMENT avec les informations du contexte fourni
                - Si l'info n'est pas dans le contexte, propose une consultation
                - N'établis JAMAIS de diagnostics
                - Ne recommande JAMAIS de médicaments ou suppléments spécifiques
                - Redirige vers professionnels pour questions médicales

                INSTRUCTIONS SPÉCIALES:
                - utilise des formulations différentes pour chaque réponse
                - Applique rigoureusement ta structure narrative et tes expressions caractéristiques
                - Utilise l'historique de conversation pour maintenir la cohérence et faire référence aux échanges précédents si pertinent""",

            "en": f"""You are Ben, a nutrition expert with a unique and recognizable communication style.

                # YOUR COMMUNICATION STYLE IN ENGLISH

                ## Characteristic expressions to use:
                - "Contrary to popular belief..."
                - "It's true that... But..."
                - "On the [aspect] front, studies show that..."
                - "The truth is that..."
                - "Between you and me, if [absurd situation]..."
                - "It's precisely because..."

                ## Tone and voice:
                - Casual yet rigorous conversational tone
                - Scientifically rigorous
                - Myth-buster with humor and pedagogy
                - Humble and nuanced about study limitations
                - Scientific vocabulary explained simply
                - Anti-dogmatic, avoids absolutes and miracle solutions

                ## Key messages to convey:
                - "It's not a magic pill"
                - "There's no universal solution"
                - "Risk depends primarily on dosage"
                - "We're not all equal when it comes to weight"
                - "Focus on nutrition, sleep, physical activity"
                - "Holistic and sustainable approach"

                AVAILABLE CONTEXT:
                {context}
                {history_text.replace('HISTORIQUE DE LA CONVERSATION:', 'CONVERSATION HISTORY:').replace('Utilisateur:', 'User:').replace('Assistant:', 'Assistant:')}

                USER QUESTION: {question}

                ABSOLUTE RULES:
                - Respond ONLY with information from the provided context
                - If info is not in context, suggest a consultation
                - NEVER establish diagnoses
                - NEVER recommend specific medications or supplements
                - Redirect to professionals for medical questions

                SPECIAL INSTRUCTIONS:
                - Strictly apply your narrative structure and characteristic expressions
                - Use different formulations for each response
                - Use conversation history to maintain coherence and reference previous exchanges if relevant"""
        }
        
        # Use French as fallback for unsupported languages
        prompt = prompts.get(language, prompts["fr"]) if language in ["fr", "en"] else prompts["fr"]

        # Get streaming response from GPT
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            stream=True
        )
        
        first_chunk = True
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                # Strip leading whitespace from first chunk only
                if first_chunk:
                    content = content.lstrip()
                    first_chunk = False
                if content:  # Only yield if not empty after stripping
                    yield content
        
    except Exception as e:
        yield f"Error processing your question: {str(e)}"


def ask_question_stream_gemini(question, language="fr", timezone="UTC", locale="fr-FR", top_k=5, model_name="gemini-2.5-flash"):
    """Streaming answer using Gemini, mirroring ask_question_stream flow."""
    col = get_collection()

    if col is None:
        yield "Error: ChromaDB collection is not available. Please run 'python index_chromadb.py' first to index your documents."
        return

    try:
        # Get embedding for the question using OpenAI (keeps Chroma flow unchanged)
        query_emb = client.embeddings.create(
            model="text-embedding-3-large",
            input=question
        ).data[0].embedding

        # Query ChromaDB
        results = col.query(
            query_embeddings=[query_emb],
            n_results=top_k
        )

        if not results['documents'] or not results['documents'][0]:
            yield "No relevant information found. Please make sure you have indexed some transcripts."
            return

        # Build context from results
        contexts = []
        for i, doc in enumerate(results['documents'][0]):
            contexts.append(doc)
        context = "\n\n".join(contexts)

        # Load Style Card and system prompts
        style_guides, style_data = load_style_guides()
        style_guide = style_guides.get(language, style_guides.get("fr", ""))
        not_found_msg = style_data.get(language, {}).get(
            'not_found_message',
            style_data.get('fr', {}).get('not_found_message', "Information not found in current content.")
        )

        system_prompts_data = load_system_prompts()
        base_prompt_fr = system_prompts_data.get('fr', {}).get('content', '')
        base_prompt_en = system_prompts_data.get('en', {}).get('content', '')

        prompts = {
            "fr": f"""{base_prompt_fr}

            {style_guide}

            CONTEXTE DISPONIBLE:
            {context}

            QUESTION DE L'UTILISATEUR: {question}

            INSTRUCTIONS SPÉCIALES:
            - Si l'information n'est pas disponible dans le contexte, réponds: "{not_found_msg}"
            - Applique rigoureusement ta structure narrative et tes expressions caractéristiques
            - Reste dans ton rôle de Ben avec ton style unique et reconnaissable""",

            "en": f"""{base_prompt_en}

            {style_guide}

            AVAILABLE CONTEXT:
            {context}

            USER QUESTION: {question}

            SPECIAL INSTRUCTIONS:
            - If information is not available in the context, respond: "{not_found_msg}"
            - Strictly apply your narrative structure and characteristic expressions
            - Stay in your role as Ben with your unique and recognizable style"""
        }

        prompt = prompts.get(language, prompts["fr"]) if language in ["fr", "en"] else prompts["fr"]

        # Configure model (temperature to mirror OpenAI setup)
        model = genai.GenerativeModel(model_name, generation_config={
            "temperature": 0.3
        })

        # Stream tokens
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

    except Exception as e:
        yield f"Error processing your question (Gemini): {str(e)}"
