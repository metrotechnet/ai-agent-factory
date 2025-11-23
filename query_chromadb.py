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
            # Check if chroma_db directory exists
            chroma_path = "./chroma_db"
            print(f"Checking if {chroma_path} exists: {os.path.exists(chroma_path)}")
            if os.path.exists(chroma_path):
                print(f"Contents of {chroma_path}: {os.listdir(chroma_path)}")
            
            print(f"Attempting to connect to ChromaDB at {chroma_path}")
            chroma_client = chromadb.PersistentClient(path=chroma_path)
            print(f"ChromaDB client created successfully")
            
            # List available collections
            collections = chroma_client.list_collections()
            print(f"Available collections: {[c.name for c in collections]}")
            
            if not collections:
                print("No collections found! ChromaDB database may be empty.")
                return None
            
            collection = chroma_client.get_collection(name="transcripts")
            print(f"Collection 'transcripts' loaded with {collection.count()} documents")
        except Exception as e:
            print(f"Error: Could not connect to ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return None
    return collection

def ask_question(question, top_k=5):
    col = get_collection()
    
    if col is None:
        return "Error: ChromaDB collection is not available. Please run 'python index_chromadb.py' first to index your documents."
    
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
            return "No relevant information found. Please make sure you have indexed some transcripts."
        
        # Build context from results
        contexts = []
        for i, doc in enumerate(results['documents'][0]):
            source = results['metadatas'][0][i].get('source', 'Unknown')
            contexts.append(f"[{source}]: {doc}")
        
        context = "\n\n".join(contexts)
        
        # Create prompt for GPT
        prompt = f"""Tu es Ben, un nutritionniste expert et coach en santé. Réponds de façon personnelle, chaleureuse et accessible, comme si tu parlais à un ami.

Utilise un ton conversationnel et des exemples concrets. Évite le jargon complexe et explique simplement.

Contexte extrait de tes documents:
{context}

Question: {question}

Réponds en te basant sur le contexte fourni, mais avec ton style personnel et approchable. Si l'info n'est pas dans le contexte, dis-le simplement et offre des conseils généraux si pertinent."""

        # Get response from GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es Ben, nutritionniste expert. Tu réponds avec ton expertise de façon amicale, personnelle et accessible. Tu utilises 'je' et parles comme dans tes capsules et conférences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error processing your question: {str(e)}"

if __name__ == "__main__":
    print("AI Agent avec ChromaDB")
    print("-" * 50)
    while True:
        q = input("\nPosez votre question (ou 'quit' pour quitter): ")
        if q.lower() in ['quit', 'exit', 'q']:
            break
        print("\nRéponse:", ask_question(q))
