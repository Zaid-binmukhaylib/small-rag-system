import pdfplumber
import os


class PDFReadError(Exception):
    pass


def extract_data_from_pdf(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise PDFReadError(f"File not found: {file_path}")

    extracted_text = []

    try:
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) == 0:
                raise PDFReadError("The PDF contains no pages.")
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)

    except PDFReadError:
        raise
    except Exception as e:
        raise PDFReadError(f"Unable to read PDF: {e}")

    full_text = "\n".join(extracted_text)

    if not full_text.strip():
        raise PDFReadError("No readable text found in the PDF.")

    return full_text