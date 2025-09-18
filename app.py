import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()

# Use top-level imports (not relative) so uvicorn app:app works from project root
import mcp
import ingest
import rag
from models import LoadModelRequest, UploadResponse, QueryRequest, QueryResponse

app = FastAPI(title="Generative AI for Demystifying Legal Documents")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/load-model")
async def load_model(payload: LoadModelRequest):
    try:
        # call top-level mcp API
        mcp.load_hf_model(payload.domain)
        return {"message": f"Model loaded for {payload.domain}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...), domain: str = Form("general")):
    try:
        content = await file.read()
        doc_id, cnt = ingest.ingest_file(content, file.filename, domain)
        return {"doc_id": doc_id, "message": f"Upload successful for {domain}, chunks={cnt}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest):
    try:
        answer = rag.answer_query(payload.domain or "general", payload.question, payload.doc_id)
        return JSONResponse(content=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))