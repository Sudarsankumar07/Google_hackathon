# Generative AI for Demystifying Legal Documents — README

Overview
This repository implements a prototype: domain-aware retrieval (HF embeddings) + Groq-only generation, with a simple HTML/CSS frontend. Backend is FastAPI with an MCP (multi-checkpoint pipeline) that lazy-loads HF models by domain and caches them. The frontend is static HTML/CSS/JS (Tailwind optional) and calls backend endpoints.

## How to run — Backend and Frontend (quick)

Important note — Common pitfall
- If you run `uvicorn app:app` from a directory that does not contain app.py (for example `venv\Scripts`) Python will not find the module "app" and you will see: "Could not import module 'app'".
- Always run uvicorn from the project root, or use the provided start scripts below which ensure the correct app directory.

Run from project root (recommended)
1. Activate your venv and change to the project root (the folder that contains app.py).
   - Windows PowerShell
     cd "C:\Users\sudarsan kumar\OneDrive\Desktop\Google_hackathon"
     .\.venv\Scripts\Activate.ps1
   - macOS/Linux
     cd /path/to/Google_hackathon
     source .venv/bin/activate

2. Start backend:
   uvicorn app:app --reload --host 0.0.0.0 --port 8000

Or use the helper scripts (they ensure uvicorn looks in the project folder even if you run them from elsewhere):

- Windows PowerShell helper:
  .\start_backend.ps1

- Bash helper:
  ./start_backend.sh

Frontend — simple static serving
Option A — serve with npm http-server (recommended for easy CORS control)
1. (Optional) install http-server globally or run via npx:
  npm install -g http-server
2. Serve the frontend directory on port 3000:
  cd frontend
  http-server -p 3000
  # or npx http-server -p 3000

Open the frontend in your browser:
  http://localhost:3000

Option B — use Python built-in (quick local testing)
  cd frontend
  python -m http.server 3000
Open:
  http://localhost:3000

Connecting frontend <-> backend
- Frontend expects backend at http://localhost:8000 by default.
- If serving frontend from a different host/port, ensure CORS is enabled on backend (app.py includes CORS wildcard by default).
- If using HTTPS in production, update endpoints accordingly.

Important Endpoints (examples)
1) Load a domain model (lazy-load to warm cache)
POST /load-model
Body JSON:
{ "domain": "legal" }
Example:
curl -X POST "http://localhost:8000/load-model" -H "Content-Type: application/json" -d "{\"domain\":\"legal\"}"

2) Upload a document (multipart)
POST /upload
Form fields:
- file (multipart file)
- domain (string)
Example:
curl -X POST "http://localhost:8000/upload" -F "file=@/path/to/doc.pdf" -F "domain=legal"

Response:
{ "doc_id": "<uuid>", "message": "Upload successful for legal" }

3) Query (RAG)
POST /query
Body JSON:
{ "question": "Simplify clause X", "doc_id": "<uuid>", "domain": "legal" }
Example:
curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d "{\"question\":\"What are the termination rights?\",\"doc_id\":\"<uuid>\",\"domain\":\"legal\"}"

Response shape:
{
  "summary": "...",
  "key_points": [...],
  "guidance": "...",
  "citations": [...],
  "disclaimer": "This AI is not a substitute for legal advice; consult a professional."
}

Testing
- Unit tests: pytest (create tests/ for mcp, utils)
- Example: pytest -q

Setup script
If setup.sh is provided:
bash setup.sh
(Windows: run the individual steps manually or from WSL)

Troubleshooting & Notes
- If HF model download fails, ensure internet and huggingface credentials if model requires access.
- Increase CACHE_DIR permissions if model caching errors occur.
- For large PDFs increase chunking size or memory; monitor RAM when loading many HF models.
- Secure GROQ_API_KEY — do not commit .env to git.
- GROQ_API_KEY missing: generation calls will fail. Check .env and restart backend.
- Large model downloads may take time and disk space. Use CACHE_DIR and pre-download if desired.
- If embeddings/Chroma errors occur, ensure vector_db folder exists and has write permission.
- If frontend can't reach backend: check ports, CORS, and firewall. Use browser DevTools network tab to inspect requests and errors.
- For Windows path issues, prefer running commands in PowerShell or WSL.

Troubleshooting: "Could not import module 'app'" and pydantic import errors
- Cause: FastAPI requires Pydantic v1.x while your environment may have Pydantic v2 installed.
- Fix: Recreate the virtual environment and reinstall pinned dependencies.

Windows PowerShell (recommended)
cd "C:\Users\sudarsan kumar\OneDrive\Desktop\Google_hackathon"
# remove old venv or create a fresh one
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# reinstall using the pinned requirements
pip install --upgrade pip
pip install -r requirements.txt

Linux / macOS
cd /path/to/Google_hackathon
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

Then start backend from the project root:
uvicorn app:app --reload --host 0.0.0.0 --port 8000

If you still see import errors, run:
pip list | findstr pydantic
# ensure it reports pydantic 1.10.x

Security & Compliance
- Do not send PII or sensitive client data to third-party LLMs without explicit consent.
- This tool is for prototyping only. Add proper logging, access control, rate limits for production.

Disclaimer
This AI tool provides informational summaries and is not legal advice. Always consult a licensed attorney for legal guidance.

If you want, I can now generate the following starter files next:
- mcp.py (HF model loader)
- app.py (FastAPI endpoints)
- ingest.py (uploading & chunking)
- rag.py (retrieval + Groq prompt wrapper)
- frontend/index.html, styles.css, script.js
Reply with which files to generate now and I will produce concise, ready-to-merge edits.
