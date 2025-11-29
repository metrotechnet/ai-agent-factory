import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent

load_dotenv()

# Initialize ChromaDB client (local storage)
chroma_client = None
collection = None
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_style_guides():
    """Load style guides from JSON file"""
    try:
        with open(PROJECT_ROOT / 'config' / 'style_guides.json', 'r', encoding='utf-8') as f:
            style_data = json.load(f)
        
        # Format the style guides for use in prompts
        formatted_guides = {}
        for lang, data in style_data.items():
            guide = f"# {data['title']}\n\n"
            guide += f"## {data['narrative_structure']['title']}\n"
            for i, step in enumerate(data['narrative_structure']['steps'], 1):
                guide += f"{i}. {step}\n"
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
                settings=chromadb.Settings(
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

def ask_question_stream(question, language="fr", timezone="UTC", locale="fr-FR", top_k=5):
    """Streaming version of ask_question with language support"""
    col = get_collection()
    
    if col is None:
        yield "Error: ChromaDB collection is not available. Please run 'python index_chromadb.py' first to index your documents."
        return
    
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
        
        # Load Style Card from JSON based on language
        style_guides, style_data = load_style_guides()
        style_guide = style_guides.get(language, style_guides.get("fr", ""))
        
        # Get not found message for the language
        not_found_msg = style_data.get(language, {}).get('not_found_message', 
                                                        style_data.get('fr', {}).get('not_found_message', 
                                                        "Information not found in current content."))
        
        # Load system prompts from JSON
        system_prompts_data = load_system_prompts()
        
        # Create dynamic prompts with context and style guide
        base_prompt_fr = system_prompts_data.get('fr', {}).get('content', '')
        base_prompt_en = system_prompts_data.get('en', {}).get('content', '')
        
        # Build full prompts with style guide and context
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
        
        # Use French as fallback for unsupported languages
        prompt = prompts.get(language, prompts["fr"]) if language in ["fr", "en"] else prompts["fr"]

        # Get streaming response from GPT
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
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

