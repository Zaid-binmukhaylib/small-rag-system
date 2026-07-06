import os
from src.pdf_reader import extract_data_from_pdf, PDFReadError
from src.embeddings import TransformerEmbedder
from src.retriever import Retriever


class JobMatcher:
    def __init__(self, resumes_folder: str):
        self.embedder = TransformerEmbedder()
        self.retrievers = {}

        for file in os.listdir(resumes_folder):
            if file.endswith(".pdf"):
                path = os.path.join(resumes_folder, file)
                try:
                    retriever = Retriever(self.embedder)
                    retriever.index(extract_data_from_pdf(path))
                    self.retrievers[file] = retriever
                except PDFReadError:
                    pass

    def find_best_match(self, job_description: str) -> str:
        if not self.retrievers:
            return "No resumes loaded."

        best_file = max(
            self.retrievers,
            key=lambda f: self.retrievers[f].similarity_score(job_description)
        )

        return f"Best match: {best_file}\n\n{self.retrievers[best_file].resume_text}"


def job_match_loop(resumes_folder: str):
    matcher = JobMatcher(resumes_folder)
    print("✅ Ready! Describe the job. Type 'exit' to quit.\n")

    while True:
        try:
            job = input("Job Description: ").strip()
            if not job:
                continue
            if job.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            print(f"\n{matcher.find_best_match(job)}\n")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break