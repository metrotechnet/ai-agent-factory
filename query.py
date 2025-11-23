import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from config import PINECONE_API_KEY, PINECONE_ENV, INDEX_NAME

load_dotenv()

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "YOUR_API_KEY")

def ask_question(question, top_k=3):
    # embed query
    query_emb = client.embeddings.create(model="text-embedding-3-large", input=question).data[0].embedding
    results = index.query(vector=query_emb, top_k=top_k, include_metadata=True)
    
    context = "\n".join([match["metadata"]["source"] + ": " + match["id"] for match in results["matches"]])
    prompt = f"Answer the question using ONLY the following context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    while True:
        q = input("Ask your AI agent: ")
        print(ask_question(q))
