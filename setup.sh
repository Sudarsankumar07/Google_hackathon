#!/bin/bash
set -e
echo "Installing backend Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Initializing frontend (optional Tailwind tooling)..."
cd frontend || exit
if [ -f package.json ]; then
  npm install || echo "npm install failed or not needed"
fi
cd ..

echo "Pre-downloading default HF model to reduce cold-start..."
python - <<PY
from sentence_transformers import SentenceTransformer
import os
model = os.getenv("DEFAULT_HF_MODEL","sentence-transformers/all-MiniLM-L6-v2")
cache = os.getenv("CACHE_DIR","./models")
SentenceTransformer(model, cache_folder=cache)
print("Model cached:", model)
PY

echo "Setup complete."
echo "You can start the backend (from project root) with:"
echo "  uvicorn app:app --reload --host 0.0.0.0 --port \${PORT:-8000}"
echo "Or run the helper script: ./start_backend.sh (or .\\start_backend.ps1 on Windows)"
