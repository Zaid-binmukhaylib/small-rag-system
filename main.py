from src.chat_loop import chat
from src.job_matcher import job_match_loop

if __name__ == "__main__":
    print("1. Resume Q&A Bot")
    print("2. Job Matcher (Bonus)")
    choice = input("Choose (1 or 2): ").strip()

    if choice == "1":
        chat("data/resumes/resume_1.pdf")
    elif choice == "2":
        job_match_loop("data/resumes")
    else:
        print("Invalid choice.")