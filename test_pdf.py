"""
سكربت اختبار سريع للتأكد إن استخراج النص من PDF يشتغل صح.
شغّله بعد ما تحط أي ملف PDF تجريبي بمسار data/resumes/resume_1.pdf
"""

from src.pdf_reader import extract_text_from_pdf, PDFReadError

if __name__ == "__main__":
    try:
        text = extract_text_from_pdf("data/resumes/resume_1.pdf")
        print("✅ نجح الاستخراج! أول 300 حرف:\n")
        print(text[:300])
    except PDFReadError as e:
        print(f"❌ خطأ: {e}")