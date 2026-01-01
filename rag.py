from openai import OpenAI
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma


BASE_URL = "http://127.0.0.1:1234/v1"
API_KEY = "dummy-key"
EMBEDDING_MODEL = "text-embedding-nomic-embed-text-v1.5"
VECTORSTORE_PATH = "vectorstore/chroma_db"  # ✅ MUST MATCH INGEST


class LocalEmbeddings(Embeddings):
    def __init__(self):
        self.client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    
    def embed_query(self, text):
        return self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        ).data[0].embedding
    
    def embed_documents(self, texts):
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        return [d.embedding for d in response.data]


embeddings = LocalEmbeddings()

db = Chroma(
    persist_directory=VECTORSTORE_PATH,
    embedding_function=embeddings
)

llm = ChatOpenAI(
    model="microsoft/phi-4-mini-reasoning",
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0
)

def run_agent(query):
    docs = db.similarity_search(query, k=6)  # 🔼 increase recall

    if not docs:
        return "Sorry, this information is not available."

    context = "\n\n".join(d.page_content for d in docs if d.page_content)

    prompt = f"""
You are an HR assistant for Sunbeam Institute.

Rules:
- Use ONLY the provided context
- Do NOT add outside information
- If courses are mentioned, list them clearly
- If fees are present, mention fees
- Answer in bullet points
- If something is missing, explicitly say it is not available

Context:
{context}

Question:
{query}

Answer (detailed, structured):
"""

    return llm.invoke(prompt).content.strip()

# ---------------- CLI ----------------
if __name__ == "__main__":
    print("Sunbeam RAG (type 'exit' to quit)")
    while True:
        q = input("\nAsk: ")
        if q.lower() in ("exit", "quit"):
            break
        print("\nAnswer:\n", run_agent(q))
        print("-" * 60)
