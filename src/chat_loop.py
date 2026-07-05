from src.rag_pipeline import RAGPipeline
from src.pdf_reader import PDFReadError


def chat(resume_path: str):
    print("Loading models, please wait...")

    try:
        pipeline = RAGPipeline(resume_path)
    except PDFReadError as e:
        print(f"Error loading resume: {e}")
        return

    print("✅ Ready! Ask anything about the resume. Type 'exit' to quit.\n")

    while True:
        try:
            question = input("You: ").strip()

            if not question:
                print("Please enter a question.\n")
                continue

            if question.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            answer = pipeline.answer(question)
            print(f"Bot: {answer}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

            