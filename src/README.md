# Resume Q&A Bot — Small RAG System

A conversational AI system that answers questions about a resume using Retrieval-Augmented Generation (RAG).

---

## What It Does

The user loads a resume (PDF), then asks questions about it in a chat loop. The system:
1. Reads and extracts text from the resume
2. Converts the resume and the question into embeddings (numerical vectors)
3. Checks if the question is relevant to the resume using cosine similarity
4. If relevant, passes the resume + question to a language model to generate an answer
5. If not relevant, returns a message indicating the question is out of scope

---

## Project Structure

small-rag-system/
├── data/
│   └── resumes/
│       └── resume_1.pdf        # Resume file
├── src/
│   ├── pdf_reader.py           # Extracts text from PDF
│   ├── embeddings.py           # Converts text to vectors using transformers
│   ├── retriever.py            # Computes similarity between question and resume
│   ├── generator.py            # Generates answer using flan-t5-large
│   ├── rag_pipeline.py         # Connects all components
│   ├── chat_loop.py            # Interactive chat loop
│   └── job_matcher.py          # Bonus: matches job description to best resume
├── main.py                     # Entry point
├── requirements.txt
└── README.md

---

## How to Run

1. Clone the repository
git clone https://github.com/your-username/small-rag-system.git
cd small-rag-system

2. Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Add your resume
Place your resume PDF in data/resumes/ and name it resume_1.pdf

5. Run
python main.py
Choose option 1 for the Q&A bot or option 2 for the job matcher.

---

## Technical Decisions

Embeddings — sentence-transformers/all-MiniLM-L6-v2
Used via AutoTokenizer and AutoModel from the transformers library directly.
This model converts text into a 384-dimensional vector.
It was chosen because it is lightweight (22M parameters), fast on CPU, and produces accurate semantic similarity scores.
Mean pooling is applied manually to convert token-level embeddings into a single sentence-level vector.
The attention_mask ensures padding tokens are excluded from the average.

Relevance Check — Cosine Similarity
Before sending a question to the language model, the system computes the cosine similarity between the question embedding and the resume embedding.
If the score is below 0.2, the question is considered off-topic and the model is not called.
This prevents the system from generating hallucinated answers for unrelated questions.

Generator — google/flan-t5-large
Used via AutoTokenizer and AutoModelForSeq2SeqLM from the transformers library.
Flan-T5 is a text-to-text model by Google, fine-tuned on instruction-following tasks including Q&A.
The large variant (780M parameters) was chosen over base for better answer quality.
It runs fully on CPU with no GPU or API key required.

Error Handling
Each module defines a custom exception class:
- PDFReadError: file not found, empty PDF, or unreadable content
- EmbeddingError: empty input text
- RetrieverError: empty resume or index not built before querying
- GeneratorError: empty resume or question passed to the model

Known Limitations
- flan-t5-large occasionally misses information when the question phrasing differs from the resume wording. This is a known limitation of small language models running on CPU.
- The system embeds the full resume as a single vector. This works well for short resumes but may reduce accuracy for longer documents.
- Scanned PDF files (image-based) are not supported as they require OCR.

---

## Bonus — Job Matcher

Instead of asking questions about one resume, this feature lets you describe a job and the system automatically picks the most relevant resume from a folder of resumes.

How to Run:
python main.py
Choose option 2, then type what you are looking for:
- i want a person with python and data science skills
- i need someone with economics background

How It Works:
Every resume in the data/resumes/ folder gets converted into a vector (embedding). When you describe a job, your description also gets converted into a vector. The system then measures how close your description is to each resume and returns the closest one.

---

## Dependencies

transformers   — Load and run embedding and generation models
torch          — Required backend for transformers
pdfplumber     — Extract text from PDF files
numpy          — Vector operations
sentence-transformers — Required by the embedding model
faiss-cpu      — Available for future vector search scaling