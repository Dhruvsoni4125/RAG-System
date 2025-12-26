import streamlit as st
import os
import re
from io import BytesIO
import google.generativeai as genai

# Optional file readers
try:
    from pypdf import PdfReader
except:
    PdfReader = None

try:
    from docx import Document
except:
    Document = None


# ---------- TEXT CLEAN ----------
def clean_text(text: str) -> str:
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------- FILE READER ----------
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


# ---------- CONFIG ----------
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    st.error("API_KEY not found. Add it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-pro"   # ✅ ONLY WORKING MODEL FOR YOUR KEY


# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="RAG System", layout="wide")
st.title("📄 RAG System (Gemini)")

st.markdown(
    "Upload a document and ask questions.\n\n"
    "**Answers are generated ONLY from the document.**"
)


# ---------- SESSION STATE ----------
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""


# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader(
    "Upload a document (.txt, .md, .pdf, .docx)",
    type=["txt", "md", "pdf", "docx"]
)

if uploaded_file:
    raw_text = read_document(uploaded_file)
    cleaned_text = clean_text(raw_text)

    if not cleaned_text:
        st.error("Could not read document.")
        st.stop()

    st.session_state.doc_text = cleaned_text
    st.success("Document loaded successfully!")

    with st.expander("Preview document"):
        st.text(cleaned_text[:2000])


if not st.session_state.doc_text:
    st.info("Please upload a document to continue.")
    st.stop()


# ---------- QUESTION ----------
question = st.text_area(
    "Ask a question based on the document:",
    height=100
)


# ---------- RAG GENERATION ----------
if st.button("Get Answer", type="primary"):
    if not question.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Generating answer..."):
            model = genai.GenerativeModel(MODEL_NAME)

            # 🔒 HARD LIMIT CONTEXT (PREVENTS ERRORS)
            context = st.session_state.doc_text[:3000]

            prompt = (
                "You are a strict RAG system.\n"
                "Answer ONLY using the document below.\n"
                "If the answer is not present, reply exactly:\n"
                "'I cannot find the answer in the provided document.'\n\n"
                f"DOCUMENT:\n{context}\n\n"
                f"QUESTION:\n{question}"
            )

            response = model.generate_content(prompt)
            st.session_state.answer = response.text


# ---------- OUTPUT ----------
if st.session_state.answer:
    st.markdown("### Answer")
    st.write(st.session_state.answer)
