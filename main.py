import streamlit as st
import os
import re
from io import BytesIO
import google.generativeai as genai

# Optional readers
try:
    from pypdf import PdfReader
except:
    PdfReader = None

try:
    from docx import Document
except:
    Document = None


# -------- TEXT CLEAN --------
def clean_text(text):
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------- FILE READER --------
def read_document(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    if ext in [".txt", ".md"]:
        return uploaded_file.getvalue().decode("utf-8")

    if ext == ".pdf" and PdfReader:
        reader = PdfReader(uploaded_file)
        return " ".join(page.extract_text() or "" for page in reader.pages)

    if ext == ".docx" and Document:
        doc = Document(BytesIO(uploaded_file.getvalue()))
        return " ".join(p.text for p in doc.paragraphs)

    return ""


# -------- CONFIG --------
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    st.error("API_KEY missing. Add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-1.0-pro"  # ✅ GUARANTEED AVAILABLE


# -------- UI --------
st.set_page_config(page_title="RAG System", layout="wide")
st.title("📄 RAG System (Gemini – Stable)")

uploaded_file = st.file_uploader(
    "Upload document (.txt, .md, .pdf, .docx)",
    type=["txt", "md", "pdf", "docx"]
)

if not uploaded_file:
    st.info("Upload a document to continue.")
    st.stop()

raw_text = read_document(uploaded_file)
doc_text = clean_text(raw_text)[:3000]   # 🔒 SAFE LIMIT

if not doc_text:
    st.error("Could not read document.")
    st.stop()

question = st.text_area("Ask a question from the document:")

if st.button("Get Answer"):
    if not question.strip():
        st.error("Enter a question.")
    else:
        with st.spinner("Generating answer..."):
            model = genai.GenerativeModel(MODEL_NAME)

            prompt = (
                "Answer ONLY using the document below.\n"
                "If the answer is not present, reply exactly:\n"
                "'I cannot find the answer in the provided document.'\n\n"
                f"DOCUMENT:\n{doc_text}\n\n"
                f"QUESTION:\n{question}"
            )

            response = model.generate_content(prompt)
            st.markdown("### Answer")
            st.write(response.text)
