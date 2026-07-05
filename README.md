# Resume Q&A Bot — Small RAG System

A conversational AI system that answers questions about a resume using Retrieval-Augmented Generation (RAG).

---

## What It Does

The user loads a resume (PDF), then asks questions about it in a chat loop. The system:

1. Reads and extracts text from the resume.
2. Converts the resume and the question into embeddings (numerical vectors).
3. Checks if the question is relevant to the resume using cosine similarity.
4. If relevant, sends the resume and the question to a Large Language Model (LLM) running through Ollama.
5. Generates an answer based only on the resume.
6. If not relevant, returns a message indicating the question is out of scope.

---

## Project Structure

small-rag-system/
├── data/
│   └── resumes/
│       └── resume_1.pdf
├── src/
│   ├── pdf_reader.py
│   ├── embeddings.py
│   ├── retriever.py
│   ├── generator.py          # Generates answers using Ollama + Qwen3
│   ├── rag_pipeline.py
│   ├── chat_loop.py
│   └── job_matcher.py
├── main.py
├── requirements.txt
└── README.md

---

## How to Run

1. Clone the repository

```bash
git clone https://github.com/your-username/small-rag-system.git
cd small-rag-system
```

2. Create a virtual environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Mac/Linux

```bash
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Install Ollama

Download and install Ollama.

5. Download the language model

```bash
ollama pull qwen3:8b
```

6. Add your resume

Place the resume PDF inside:

```
data/resumes/resume_1.pdf
```

7. Run

```bash
python main.py
```

Choose:

- Option 1 → Resume Q&A Bot
- Option 2 → Job Matcher

---

# Technical Decisions

## Embeddings — sentence-transformers/all-MiniLM-L6-v2

The embedding model is loaded using AutoTokenizer and AutoModel from the Transformers library.

The model converts text into a 384-dimensional embedding vector.

Reasons for choosing this model:

- Lightweight (~22M parameters)
- Fast on CPU
- Good semantic similarity performance
- Widely used for Retrieval-Augmented Generation systems

Mean Pooling is manually applied to obtain one embedding representing the entire text.

Padding tokens are ignored using the attention mask.

---

## Relevance Check — Cosine Similarity

The resume embedding and the question embedding are compared using cosine similarity.

If the similarity score is below **0.2**, the system considers the question unrelated to the resume.

This prevents unnecessary calls to the language model and reduces hallucinations.

---

## Generator — Ollama + Qwen3:8B

The project uses **Ollama** as a local model server.

The Large Language Model used is:

```
Qwen3:8B
```

The Generator sends the prompt to Ollama using the Python Ollama package.

Reasons for choosing Qwen3:

- Excellent instruction following
- Strong question-answering performance
- Better reasoning compared to smaller models
- Runs locally through Ollama without requiring cloud APIs

---

## Error Handling

Each module defines its own exception class.

- PDFReadError
- EmbeddingError
- RetrieverError
- GeneratorError

This improves debugging and keeps responsibilities separated.

---

## Known Limitations

- The system embeds the entire resume as a single vector.
  This is suitable for short resumes but may reduce retrieval accuracy for larger documents.

- Scanned PDFs are not supported because OCR is not implemented.

- The project currently works with one indexed resume for question answering.

---

# Bonus — Job Matcher

Instead of answering questions about one resume, the Job Matcher compares a job description against multiple resumes.

Each resume is converted into an embedding.

The job description is also converted into an embedding.

Cosine similarity is then used to identify the most relevant resume.

---

## Dependencies

- transformers
- torch
- numpy
- pdfplumber
- sentence-transformers
- ollama
- faiss-cpu (future scalability)