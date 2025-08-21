from langchain_openai import ChatOpenAI
from sentence_transformers import SentenceTransformer

def analyze_document(file_path, model_name="gpt-4"):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # Step 1: Create embeddings
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    _ = embedder.encode([text])  # You can save/use embeddings further

    # Step 2: Summarize with LangChain LLM
    llm = ChatOpenAI(model=model_name)
    prompt = f"Analyze this document and summarize in 5 bullet points:\n\n{text[:2000]}"
    result = llm.invoke(prompt)

    return result.content
