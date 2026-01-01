import streamlit as st
import requests
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

#  UI main page 
st.set_page_config(page_title="Sunbeam RAG Chatbot", layout="centered")
st.title("Sunbeam Internship & Course Chatbot")

# System prompt
SYSTEM_PROMPT = """
You are an official academic advisor for Sunbeam Institute of Information Technology.

STRICT RULES:
- Answer ONLY using the provided context
- Do NOT guess or add external knowledge
- If details are missing, clearly say so

WHEN ASKED ABOUT A COURSE / INTERNSHIP:
You MUST include:
• Course name
• Duration
• Complete syllabus/modules (bullet points)
• Eligibility / prerequisites
• Fees (if present in context)
• Location / mode

WHEN ASKED ABOUT THE INSTITUTE (About Sunbeam):
You MUST include:
• Overview
• Locations
• Courses / domains offered
• Training mode

If syllabus is mentioned in multiple places, COMBINE them.

If ANY field is missing, explicitly say:
"Information not available in provided data."

Your answer MUST be detailed and structured.
"""

# Embeddings 
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

VECTORSTORE_PATH = "vectorstore/chroma_db"

vectorstore = Chroma(
    persist_directory=VECTORSTORE_PATH,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

#  call LM Studio 
def query_lmstudio(system_prompt, user_prompt):
    url = "http://127.0.0.1:1234/v1/chat/completions"
    payload = {
        "model": "llama3-docchat-1.0-8b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }
    response = requests.post(url, json=payload)
    return response.json()["choices"][0]["message"]["content"]

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["question"])
    with st.chat_message("assistant"):
        st.write(chat["answer"])

# Take user input
query = st.chat_input("Ask about Sunbeam courses or internships")

if query:
    docs = retriever.invoke(query)

    if not docs:
        answer = "Information not available in provided data."
    else:
        context = "\n\n".join(doc.page_content for doc in docs)

        user_prompt = f"""
Context:
{context}

Question:
{query}

Answer:
"""

        answer = query_lmstudio(SYSTEM_PROMPT, user_prompt)

    st.session_state.chat_history.append({
        "question": query,
        "answer": answer
    })

    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        st.write(answer)
