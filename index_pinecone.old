import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
from config import PINECONE_API_KEY, PINECONE_ENV, INDEX_NAME, TRANSCRIPT_FOLDER

load_dotenv()

# init Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
if INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,  # text-embedding-3-large dim
        metric="cosine"
    )
index = pc.Index(INDEX_NAME)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "YOUR_API_KEY")

def get_embeddings(texts):
    resp = client.embeddings.create(model="text-embedding-3-large", input=texts)
    return [e.embedding for e in resp.data]

if __name__ == "__main__":
    for file in os.listdir(TRANSCRIPT_FOLDER):
        if file.endswith(".txt"):
            file_path = os.path.join(TRANSCRIPT_FOLDER, file)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # simple chunking
            chunks = [text[i:i+500] for i in range(0, len(text), 500)]
            embeddings = get_embeddings(chunks)
            vectors = [(f"{file}_chunk{i}", embeddings[i], {"source": file}) for i in range(len(chunks))]
            index.upsert(vectors)
            print(f"Indexed {file} with {len(chunks)} chunks")
