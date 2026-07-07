import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.rag_pipeline import RAGPipeline
from src.pdf_reader import PDFReadError
from src.job_matcher import JobMatcher

app = FastAPI(title="Resume AI Assistant API")

# Allow the static frontend (served from a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RESUME_DIR = "data/resumes"
UPLOADED_RESUME_PATH = os.path.join(RESUME_DIR, "uploaded_resume.pdf")

# Holds the pipeline built from the most recently uploaded resume.
pipeline: RAGPipeline | None = None


class Question(BaseModel):
    question: str


class JobDescription(BaseModel):
    job_description: str


@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
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

    return {"message": f"Resume '{file.filename}' uploaded and indexed successfully."}


@app.post("/ask")
async def ask_question(payload: Question):
    if pipeline is None:
        raise HTTPException(status_code=400, detail="Please upload a resume first.")

    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer = pipeline.answer(payload.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"answer": answer}


@app.post("/match/upload")
async def upload_resumes_for_matching(files: list[UploadFile] = File(...)):
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
        "filenames": saved_filenames
    }


@app.post("/match")
async def match_job(payload: JobDescription):
    if not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    os.makedirs(RESUME_DIR, exist_ok=True)

    matcher = JobMatcher(RESUME_DIR)
    if not matcher.retrievers:
        raise HTTPException(status_code=400, detail="No resumes found. Please upload at least one resume.")

    best_file = max(
        matcher.retrievers,
        key=lambda f: matcher.retrievers[f].similarity_score(payload.job_description)
    )

    return {
        "filename": best_file,
        "resume_text": matcher.retrievers[best_file].resume_text
    }


# Serve the static frontend (index.html, style.css, script.js) from the same
# origin as the API. Mounted last so the API routes above take precedence.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
