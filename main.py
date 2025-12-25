import streamlit as st
import os
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


# ---------------- FILE READER ----------------
def read_document_content(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    try:
        if ext in [".txt", ".md"]:
            return uploaded_file.getvalue().decode("utf-8")

        elif ext == ".pdf":
            if not PdfReader:
                return "Error: pypdf not installed"
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        elif ext == ".docx":
            if not Document:
                return "Error: python-docx not installed"
            doc = Document(BytesIO(uploaded_file.getvalue()))
            return "\n".join(p.text for p in doc.paragraphs)

        else:
            return "Error: Unsupported file type"

    except Exception as e:
        return f"Error reading file: {e}"


# ---------------- CONFIG ----------------
API_KEY = os.getenv("API_KEY")   # Streamlit Secrets
MODEL_NAME = "gemini-1.5-flash-latest"

if not API_KEY:
    st.error("API_KEY not found. Add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)


# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Gemini RAG", layout="wide")
st.title("📄 RAG System – Document-based Q&A")

st.markdown(
    "Upload a document and ask questions. "
    "**The model answers ONLY from the document.**"
)


# ---------------- SESSION STATE ----------------
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""


# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload a document (.txt, .md, .pdf, .docx)",
    type=["txt", "md", "pdf", "docx"]
)

if uploaded_file:
    content = read_document_content(uploaded_file)

    if content.startswith("Error"):
        st.error(content)
        st.stop()

    st.session_state.doc_text = content
    st.success("Document loaded successfully!")

    with st.expander("Preview document"):
        st.text(content[:2000])


if not st.session_state.doc_text.strip():
    st.info("Please upload a document to continue.")
    st.stop()


# ---------------- QUESTION INPUT ----------------
question = st.text_area(
    "Ask a question based on the document:",
    height=100
)


# ---------------- RAG LOGIC ----------------
if st.button("Get Answer", type="primary"):
    if not question.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Generating answer..."):
            model = genai.GenerativeModel(MODEL_NAME)

            # 🔒 LIMIT CONTEXT SIZE (CRITICAL FIX)
            document_context = st.session_state.doc_text[:12000]

            prompt = f"""
You are a strict RAG system.

Answer ONLY using the document below.
If the answer is not present, reply exactly:
"I cannot find the answer in the provided document."

DOCUMENT:
{document_context}

QUESTION:
{question}
"""

            response = model.generate_content(prompt)
            st.session_state.answer = response.text


# ---------------- OUTPUT ----------------
if st.session_state.answer:
    st.markdown("### Answer")
    st.write(st.session_state.answer)
