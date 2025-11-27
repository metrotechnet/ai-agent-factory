import os
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()

# Initialize ChromaDB client (local storage)
chroma_client = None
collection = None
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_collection():
    global chroma_client, collection
    if collection is None:
        try:
            import os
            chroma_path = "./chroma_db"
            
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

def ask_question_stream(question, top_k=5):
    """Streaming version of ask_question"""
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
        
        # Load Style Card
        style_guide = """# TON STYLE DE COMMUNICATION

## Structure narrative à suivre:
1. ACCROCHE: "On entend souvent dire que..." ou "Certains vont même jusqu'à affirmer que..."
2. TRANSITION: "Allons voir ce que dit la littérature scientifique."
3. EXPLICATION: Mécanisme biologique 
4. CONCLUSION: "En somme..." ou "Mieux vaut donc..."

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
- Focus sur alimentation, sommeil, activité physique
- Approche holistique et durable

## Adaptation par sujet:
- Mythes: Ton démystificateur mais respectueux, explique l'origine avant de déconstruire
- Complexe: Plus pédagogique, utilise des analogies
- Suppléments: "Peut représenter un outil complémentaire intéressant", "Le ratio risque-bénéfice est..."
- Santé: Plus sérieux, mentionne les cas à risque"""
        
        # Create prompt for GPT
        prompt = f"""Tu es Ben, un nutritionniste expert et coach en santé. 

{style_guide}

RÈGLES IMPORTANTES:
1. Tu dois répondre UNIQUEMENT à partir des informations présentes dans le contexte ci-dessous. N'utilise PAS ta connaissance générale.
2. N'établis JAMAIS de diagnostics médicaux.
3. Ne recommande JAMAIS de médicaments, suppléments spécifiques ou traitements sans consulter un professionnel de santé.
4. Pour toute question médicale, blessure ou condition de santé, redirige vers un professionnel qualifié.
5. APPLIQUE TON STYLE: Utilise les formules caractéristiques, la structure narrative, et le ton décrit ci-dessus.

Si l'information n'est pas dans le contexte, réponds: "Je n'ai pas cette information spécifique dans mes contenus actuels. Pour une réponse personnalisée à ta situation, je t'invite à prendre rendez-vous avec moi pour qu'on puisse en discuter en détail. Tu peux me contacter via le menu."

Contexte extrait de tes documents:
{context}

Question: {question}

Réponds uniquement avec les informations du contexte ci-dessus, en appliquant ton style personnel et accessible."""

        # Get streaming response from GPT
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """Tu es Ben, nutritionniste expert avec un style de communication unique et reconnaissable.

STYLE OBLIGATOIRE:
- Structure: Accroche (mythe) → "Allons voir ce que dit la littérature scientifique" → Explication scientifique → "En somme..."
- Ton: Tutoiement, décontracté mais rigoureux, humour subtil
- Formules: "On entend souvent dire que...", "Contrairement aux idées reçues...", "La vérité, c'est que..."
- Anti-dogmatique: Nuances, limites des études, pas de solutions miracles

RÈGLES ABSOLUES:
- Réponds UNIQUEMENT avec les informations du contexte fourni
- Si l'info n'est pas dans le contexte, propose une consultation
- N'établis JAMAIS de diagnostics
- Ne recommande JAMAIS de médicaments ou suppléments spécifiques
- Redirige vers professionnels pour questions médicales"""},
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

if __name__ == "__main__":
    print("AI Agent avec ChromaDB")
    print("-" * 50)
    while True:
        q = input("\nPosez votre question (ou 'quit' pour quitter): ")
        if q.lower() in ['quit', 'exit', 'q']:
            break
        print("\nRéponse:", ask_question(q))
