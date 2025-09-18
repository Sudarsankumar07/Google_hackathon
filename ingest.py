import os
import uuid
import json
from chromadb import Client
from chromadb.config import Settings
from typing import Tuple
from utils import extract_text_from_pdf, extract_text_from_docx, chunk_text
import mcp  # use top-level mcp module

VECTOR_DB_DIR = os.path.abspath(os.getenv("VECTOR_DB_DIR", "./vector_db"))
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# Simple chroma client using in-process persistence
chroma_client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=VECTOR_DB_DIR))

def ingest_file(file_bytes: bytes, filename: str, domain: str) -> Tuple[str, int]:
    """
    Returns (doc_id, num_chunks)
    """
    # extract text
    text = ""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif lower.endswith(".docx") or lower.endswith(".doc"):
        text = extract_text_from_docx(file_bytes)
    else:
        # assume plain text
        try:
            text = file_bytes.decode("utf-8")
        except:
            text = ""
    chunks = chunk_text(text)
    doc_id = str(uuid.uuid4())
    # compute embeddings via mcp.encode_texts (fastmcp will be used when available)
    embeddings = mcp.encode_texts(domain, chunks, show_progress_bar=False)
    # create a collection for this domain if not exists
    collection_name = f"{domain}_collection"
    try:
        collection = chroma_client.get_collection(collection_name)
    except Exception:
        collection = chroma_client.create_collection(collection_name)
    # store each chunk with metadata including doc_id and chunk index
    ids = [f"{doc_id}__{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": doc_id, "domain": domain, "chunk_index": i} for i in range(len(chunks))]
    collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
    chroma_client.persist()
    return doc_id, len(chunks)
    chroma_client.persist()
    return doc_id, len(chunks)
