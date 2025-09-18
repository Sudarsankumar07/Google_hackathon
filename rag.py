import os
import json
import requests
from typing import Dict, Any, List
import mcp  # use top-level mcp module
from chromadb import Client
from chromadb.config import Settings

VECTOR_DB_DIR = os.path.abspath(os.getenv("VECTOR_DB_DIR", "./vector_db"))
chroma_client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=VECTOR_DB_DIR))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ENDPOINT = "https://api.groq.ai/v1"  # example base; adapt if needed

DISCLAIMER = "This AI is not a substitute for legal advice; consult a licensed professional."

def retrieve_top_chunks(domain: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    # embed query using mcp.encode_texts (fastmcp used when available)
    q_embs = mcp.encode_texts(domain, [query])
    if not q_embs:
        return []
    q_emb = q_embs[0]
    collection_name = f"{domain}_collection"
    try:
        collection = chroma_client.get_collection(collection_name)
    except Exception:
        return []
    results = collection.query(query_embeddings=[q_emb], n_results=top_k, include=["metadatas","documents","distances"])
    docs = []
    if results and "documents" in results and len(results["documents"])>0:
        for i in range(len(results["documents"][0])):
            docs.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
    return docs

def call_groq_generate(domain: str, question: str, context_chunks: List[str]) -> Dict[str, Any]:
    """
    Very simple Groq call: send a prompt and return text. The exact payload depends on Groq SDK/API.
    This implementation uses a minimal requests POST; adapt if you use groq SDK.
    """
    api_key = os.getenv("GROQ_API_KEY")
    prompt = f"As a {domain} expert, using the following context:\n\n{''.join(context_chunks)}\n\nAnswer this question concisely and list citations: {question}\n\nProvide: summary, key_points (3), guidance."
    if not api_key:
        return {"text": "GROQ_API_KEY not set. Cannot generate.", "error": True}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "groq-1", 
        "input": prompt,
        "max_tokens": 512
    }
    try:
        resp = requests.post(f"{GROQ_ENDPOINT}/models/groq-1/outputs", headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        body = resp.json()
        # best-effort extraction
        out_text = ""
        if isinstance(body, dict):
            if "output" in body and isinstance(body["output"], list) and len(body["output"])>0:
                out_text = body["output"][0].get("content", "") or str(body["output"][0])
            else:
                out_text = json.dumps(body)
        else:
            out_text = str(body)
        return {"text": out_text, "error": False}
    except Exception as e:
        return {"text": f"Groq request failed: {e}", "error": True}

def answer_query(domain: str, question: str, doc_id: str = None) -> Dict[str, Any]:
    # Retrieve relevant chunks; if doc_id provided, do a domain-scoped filter by matching metadata
    chunks_info = retrieve_top_chunks(domain, question, top_k=4)
    context_texts = [c["text"] for c in chunks_info]
    groq_resp = call_groq_generate(domain, question, context_texts)
    response = {
        "summary": groq_resp.get("text", ""),
        "key_points": [],  # client can parse from summary
        "guidance": "",
        "citations": [m.get("doc_id") for m in [ci["metadata"] for ci in chunks_info] if m],
        "disclaimer": DISCLAIMER
    }
    if groq_resp.get("error"):
        response["error"] = groq_resp.get("text")
    return response
