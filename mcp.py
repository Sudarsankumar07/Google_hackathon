import os
import json
from typing import Dict, List, Any

CACHE_DIR = os.getenv("CACHE_DIR", "./models")
DOMAIN_MODELS = json.loads(os.getenv("DOMAIN_MODELS", '{"general":"sentence-transformers/all-MiniLM-L6-v2"}'))

# Try to use external fastmcp if available
try:
    from fastmcp import FastMCP  # type: ignore
    FASTMCP_AVAILABLE = True
except Exception:
    FASTMCP_AVAILABLE = False

if FASTMCP_AVAILABLE:
    # Initialize FastMCP (best-effort arguments)
    _fastmcp = FastMCP(cache_dir=CACHE_DIR, domain_models=DOMAIN_MODELS)

    def _ensure_encode(obj):
        # If object already has encode, return as-is; otherwise wrap common embedding APIs.
        if hasattr(obj, "encode"):
            return obj
        class _Wrapper:
            def __init__(self, m):
                self._m = m
            def encode(self, texts, **kwargs):
                # try common names
                if hasattr(self._m, "encode"):
                    return self._m.encode(texts, **kwargs)
                if hasattr(self._m, "embed"):
                    return self._m.embed(texts)
                if hasattr(self._m, "get_embedding"):
                    return [self._m.get_embedding(t) for t in texts]
                raise AttributeError("Underlying fastmcp model has no known encode/embed method")
        return _Wrapper(obj)

    def load_hf_model(domain: str):
        """
        Use fastmcp to load a model for the domain and return an object with encode(texts).
        """
        domain = domain or "general"
        model_obj = _fastmcp.load(domain)  # best-effort: FastMCP.load
        return _ensure_encode(model_obj)

    def get_model_for_domain(domain: str):
        domain = domain or "general"
        try:
            model_obj = _fastmcp.get(domain)
        except Exception:
            model_obj = _fastmcp.load(domain)
        return _ensure_encode(model_obj)

    def encode_texts(domain: str, texts: List[str], **kwargs) -> List[List[float]]:
        model = get_model_for_domain(domain)
        emb = model.encode(texts, **kwargs)
        # normalize return type to list[list[float]]
        try:
            return emb.tolist()
        except Exception:
            return list(emb)
else:
    # Fallback: sentence-transformers local loader
    from sentence_transformers import SentenceTransformer
    loaded_models: Dict[str, SentenceTransformer] = {}

    def get_model_name_for_domain(domain: str) -> str:
        return DOMAIN_MODELS.get(domain, os.getenv("DEFAULT_HF_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))

    def load_hf_model(domain: str):
        """
        Load and cache a SentenceTransformer for the domain (fallback).
        """
        domain = domain or "general"
        if domain in loaded_models:
            return loaded_models[domain]
        model_name = get_model_name_for_domain(domain)
        os.makedirs(CACHE_DIR, exist_ok=True)
        model = SentenceTransformer(model_name, cache_folder=CACHE_DIR)
        loaded_models[domain] = model
        return model

    def get_model_for_domain(domain: str):
        if domain in loaded_models:
            return loaded_models[domain]
        return load_hf_model(domain)

    def encode_texts(domain: str, texts: List[str], show_progress_bar: bool = False, **kwargs) -> List[List[float]]:
        model = get_model_for_domain(domain)
        emb = model.encode(texts, show_progress_bar=show_progress_bar, **kwargs)
        try:
            return emb.tolist()
        except Exception:
            return list(emb)
