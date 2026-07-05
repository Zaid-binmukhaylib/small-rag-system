from src.chat_loop import chat
from src.job_matcher import job_match_loop
import os

if __name__ == "__main__":
    print("1. Resume Q&A Bot")
    print("2. Job Matcher ")
    choice = input("Choose (1 or 2): ").strip()

    if choice == "1":
        print("\nAvailable resumes:")
        resumes = os.listdir("data/resumes")
        for i, file in enumerate(resumes, 1):
            print(f"{i}. {file}")
        resume_choice = input("Choose resume number: ").strip()
        selected = resumes[int(resume_choice) - 1]
        chat(f"data/resumes/{selected}")

    elif choice == "2":
        job_match_loop("data/resumes")

    else:
        print("Invalid choice.")