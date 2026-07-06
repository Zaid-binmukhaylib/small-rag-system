import os

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

# Load environment variables from a local .env file (e.g. GEMINI_API_KEY, API_KEY).
load_dotenv()

# ---------------------------------------------------------------------------
# API key authentication
# ---------------------------------------------------------------------------
# Every endpoint requires the secret API key to be sent in the "X-API-Key"
# header. The expected key is read from the API_KEY environment variable.
API_KEY = os.environ.get("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(provided_key: str = Security(api_key_header)) -> None:
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Server misconfigured: API_KEY is not set.",
        )
    if provided_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )

from src.rag_pipeline import RAGPipeline
from src.pdf_reader import PDFReadError
from src.job_matcher import JobMatcher

# ---------------------------------------------------------------------------
# OpenAPI / Swagger metadata
# ---------------------------------------------------------------------------
tags_metadata = [
    {
        "name": "Resume Q&A",
        "description": "Upload a single resume and ask natural-language questions about it.",
    },
    {
        "name": "Job Matcher",
        "description": "Upload multiple resumes and find the best match for a job description.",
    },
]

app = FastAPI(
    title="Resume AI Assistant API",
    description=(
        "A small Retrieval-Augmented Generation (RAG) system for resumes.\n\n"
        "- **Resume Q&A** — ask questions about an uploaded resume "
        "(embeddings + cosine-similarity relevance check + Qwen3 via Ollama).\n"
        "- **Job Matcher** — match a job description against a pool of resumes.\n\n"
        "Built with FastAPI, sentence-transformers (all-MiniLM-L6-v2), and Ollama (Qwen3)."
    ),
    version="1.0.0",
    contact={"name": "Zaid bin Mukhaylib"},
    openapi_tags=tags_metadata,
)

# Allow the static frontend (served from a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory where uploaded resumes are stored. On hosts with a read-only
# filesystem (e.g. Cloud Run), set RESUME_DIR to a writable path like /tmp/resumes.
RESUME_DIR = os.environ.get("RESUME_DIR", "data/resumes")
UPLOADED_RESUME_PATH = os.path.join(RESUME_DIR, "uploaded_resume.pdf")

# Holds the pipeline built from the most recently uploaded resume.
pipeline: RAGPipeline | None = None


# ---------------------------------------------------------------------------
# Request / Response schemas (shown in Swagger with examples)
# ---------------------------------------------------------------------------
class Question(BaseModel):
    question: str = Field(
        ...,
        description="The question to ask about the uploaded resume.",
        examples=["What programming languages does the candidate know?"],
    )


class JobDescription(BaseModel):
    job_description: str = Field(
        ...,
        description="A description of the job or the skills you are looking for.",
        examples=["Looking for a candidate with strong Python and data science skills"],
    )


class UploadResponse(BaseModel):
    message: str = Field(
        ..., examples=["Resume 'resume.pdf' uploaded and indexed successfully."]
    )


class AnswerResponse(BaseModel):
    answer: str = Field(..., examples=["The candidate knows Python and R."])


class MatchUploadResponse(BaseModel):
    message: str = Field(..., examples=["Uploaded 2 resume(s) for matching."])
    filenames: list[str] = Field(..., examples=[["resume1.pdf", "resume2.pdf"]])


class MatchResponse(BaseModel):
    filename: str = Field(..., examples=["resume1.pdf"])
    resume_text: str = Field(..., examples=["ZAID BIN MUKHAYLIB\nRiyadh, Saudi Arabia ..."])


class ErrorResponse(BaseModel):
    detail: str = Field(..., examples=["Please upload a resume first."])


# ---------------------------------------------------------------------------
# Resume Q&A endpoints
# ---------------------------------------------------------------------------
@app.post(
    "/upload",
    tags=["Resume Q&A"],
    summary="Upload a resume",
    response_model=UploadResponse,
    dependencies=[Depends(require_api_key)],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or unreadable PDF"},
        401: {"model": ErrorResponse, "description": "Invalid or missing API key"},
    },
)
async def upload_resume(file: UploadFile = File(..., description="A PDF resume file.")):
    """
    Upload a **PDF resume**, save it on the server, and build the RAG pipeline
    (embeddings + retriever) used by the `/ask` endpoint.

    Uploading a new file replaces the resume currently used for Q&A.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs(RESUME_DIR, exist_ok=True)

    contents = await file.read()
    with open(UPLOADED_RESUME_PATH, "wb") as f:
        f.write(contents)

    global pipeline
    try:
        pipeline = RAGPipeline(UPLOADED_RESUME_PATH)
    except PDFReadError as e:
        pipeline = None
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        pipeline = None
        raise HTTPException(status_code=500, detail=f"Failed to index resume: {e}")

    return {"message": f"Resume '{file.filename}' uploaded and indexed successfully."}


@app.post(
    "/ask",
    tags=["Resume Q&A"],
    summary="Ask a question about the resume",
    response_model=AnswerResponse,
    dependencies=[Depends(require_api_key)],
    responses={
        400: {"model": ErrorResponse, "description": "No resume uploaded or empty question"},
        401: {"model": ErrorResponse, "description": "Invalid or missing API key"},
        500: {"model": ErrorResponse, "description": "Answer generation failed"},
    },
)
async def ask_question(payload: Question):
    """
    Answer a natural-language question about the currently uploaded resume.

    The question is first checked for relevance using cosine similarity; if it is
    out of scope, a fixed message is returned without calling the language model.
    """
    if pipeline is None:
        raise HTTPException(status_code=400, detail="Please upload a resume first.")

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer = pipeline.answer(payload.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"answer": answer}


# ---------------------------------------------------------------------------
# Job Matcher endpoints
# ---------------------------------------------------------------------------
@app.post(
    "/match/upload",
    tags=["Job Matcher"],
    summary="Upload resumes for matching",
    response_model=MatchUploadResponse,
    dependencies=[Depends(require_api_key)],
    responses={
        400: {"model": ErrorResponse, "description": "No valid PDF files uploaded"},
        401: {"model": ErrorResponse, "description": "Invalid or missing API key"},
    },
)
async def upload_resumes_for_matching(
    files: list[UploadFile] = File(..., description="One or more PDF resume files.")
):
    """
    Upload **one or more PDF resumes** and add them to the shared resume pool used
    by the `/match` endpoint. Non-PDF files are silently skipped.
    """
    os.makedirs(RESUME_DIR, exist_ok=True)

    saved_filenames = []
    for file in files:
        if file.content_type != "application/pdf":
            continue

        filename = os.path.basename(file.filename)
        contents = await file.read()

        with open(os.path.join(RESUME_DIR, filename), "wb") as f:
            f.write(contents)

        saved_filenames.append(filename)

    if not saved_filenames:
        raise HTTPException(status_code=400, detail="No valid PDF files were uploaded.")

    return {
        "message": f"Uploaded {len(saved_filenames)} resume(s) for matching.",
        "filenames": saved_filenames,
    }


@app.post(
    "/match",
    tags=["Job Matcher"],
    summary="Find the best-matching resume",
    response_model=MatchResponse,
    dependencies=[Depends(require_api_key)],
    responses={
        400: {"model": ErrorResponse, "description": "Empty description or no resumes"},
        401: {"model": ErrorResponse, "description": "Invalid or missing API key"},
    },
)
async def match_job(payload: JobDescription):
    """
    Compare a **job description** against every resume in the pool and return the
    single best-matching resume, based on embedding cosine similarity.
    """
    if not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    os.makedirs(RESUME_DIR, exist_ok=True)

    matcher = JobMatcher(RESUME_DIR)
    if not matcher.retrievers:
        raise HTTPException(
            status_code=400,
            detail="No resumes found. Please upload at least one resume.",
        )

    best_file = max(
        matcher.retrievers,
        key=lambda f: matcher.retrievers[f].similarity_score(payload.job_description),
    )

    return {
        "filename": best_file,
        "resume_text": matcher.retrievers[best_file].resume_text,
    }
