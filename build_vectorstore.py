import os
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


# give the path of all files 

PROJECT_ROOT = os.getcwd()
DATA_PATH = os.path.join(PROJECT_ROOT, "data")
VECTORSTORE_PATH = os.path.join(PROJECT_ROOT, "vectorstore", "chroma_db")

os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(os.path.dirname(VECTORSTORE_PATH), exist_ok=True)


# if path is present then it remove 1st and gives new

if os.path.exists(VECTORSTORE_PATH):
    print(" Removing old vectorstore...")
    shutil.rmtree(VECTORSTORE_PATH)


# Used embedding model 


embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# To load text files

documents = []
total_chars = 0

print("\n Loading data files...\n")

for file in os.listdir(DATA_PATH):
    if not file.endswith(".txt"):
        continue

    file_path = os.path.join(DATA_PATH, file)
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if len(text) < 5:
        continue  # used to ignore tiny junk files

    total_chars += len(text)

    documents.append(
        Document(
            page_content=text,
            metadata={
                "source": file,
                "type": "sunbeam_data"
            }
        )
    )

    print(f" Loaded {file} ({len(text)} chars)")

if not documents:
    raise RuntimeError(" No valid .txt files found in data folder")


# Chunking 

print("\nChunking configuration")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

print("Chunk size:", CHUNK_SIZE)
print("Chunk overlap:", CHUNK_OVERLAP)
print("Total characters:", total_chars)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " ", ""]
)

chunks = splitter.split_documents(documents)


# Vectorestore path 

vectorstore = Chroma(
    persist_directory=VECTORSTORE_PATH,
    embedding_function=embeddings
)

vectorstore.add_documents(chunks)

# Veryfiy 

print("\nVectorstore build complete")
print("Original documents:", len(documents))
print("Total chunks:", len(chunks))
print("Average chunk size:",
      sum(len(c.page_content) for c in chunks) // len(chunks))

print("\nReady for RAG queries")
