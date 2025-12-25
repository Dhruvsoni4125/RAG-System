import streamlit as st
import os
from typing import Optional
from io import BytesIO
from google import genai
from google.genai.errors import APIError
from hugchat.hugchat import Model

try:
    from pypdf import PdfReader
except:
    PdfReader = None

try:
    from docx import Document
except:
    Document = None


# Extract text content from TXT, MD, PDF, DOCX
def read_document_content(uploaded_file):
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    try:
        # TXT + MD
        if file_extension in ['.txt', '.md']:
            return uploaded_file.getvalue().decode("utf-8")

        # PDF
        elif file_extension == '.pdf':
            if not PdfReader:
                return "Error: Cannot read PDF. Please install pypdf."
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        # DOCX
        elif file_extension == '.docx':
            if not Document:
                return "Error: Cannot read DOCX. Please install python-docx."
            doc = Document(BytesIO(uploaded_file.getvalue()))
            text = "\n".join([p.text for p in doc.paragraphs])
            return text

        else:
            return "Error: Unsupported file type. Only .txt, .md, .pdf, .docx are supported."

    except Exception as e:
        return f"Error reading file content: {e}"


# CONFIG
API_KEY = os.getenv("API_KEY")
MODEL_NAME = "gemini-2.5-flash-lite"


# Gemini API wrapper
class GeminiAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def generate_content(self, model: str, contents: list, system_instruction: str) -> str:
        try:
            client = genai.Client(api_key=self.api_key)
            config = genai.types.GenerateContentConfig(system_instruction=system_instruction)

            response = client.models.generate_content(
                model=model, contents=contents, config=config
            )

            return response.text

        except APIError as e:
            return f"Error during API call: {e}"

        except Exception as e:
            return f"Error during API call: {e}"


# Streamlit UI
st.set_page_config(page_title="Gemini RAG", layout="wide")
st.title("📃 RAG SYSTEM: Contextual Q&A with Gemini")

st.markdown("""
This application demonstrates a **Retrieval-Augmented Generation (RAG)** system.

Supported file types:
- .docx  
- .pdf  
- .md  
- .txt
""")

# Session state
if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""

if "rag_response" not in st.session_state:
    st.session_state.rag_response = {}

if "user_prompt_input" not in st.session_state:
    st.session_state.user_prompt_input = ""


# 1) File Upload Section
uploaded_file = st.file_uploader(
    "1. Upload data source (TXT, MD, PDF or DOCX)",
    type=["txt", "md", "pdf", "docx"],
    help="Upload the document Gemini must reference"
)

if uploaded_file is not None:
    file_contents = read_document_content(uploaded_file)

    if file_contents.startswith("Error:"):
        st.error(file_contents)
        st.session_state.uploaded_text = ""
        st.stop()
    else:
        st.session_state.uploaded_text = file_contents
        st.success(f"File **{uploaded_file.name}** loaded! ({len(file_contents)} characters)")

        with st.expander("Review Extracted Document"):
            preview = file_contents[:2000]
            if len(file_contents) > 2000:
                preview += "\n[... truncated ...]"
            st.text(preview)


# Stop if no document uploaded
if not st.session_state.uploaded_text:
    st.info("Upload a supported file to enable Q&A.")
    st.stop()


# 2) Prompt Input
st.subheader("2. Ask a Question from the Document")
st.text_area(
    "Enter your question:",
    placeholder="Example: What is the purpose of the first paragraph?",
    height=100,
    key="user_prompt_input"
)


# RAG Query Function
gemini_api = GeminiAPI(api_key=API_KEY)

def run_rag_query():
    current_prompt = st.session_state.get("user_prompt_input", "").strip()

    if not current_prompt:
        st.error("Please enter a question.")
        return

    system_instruction = (
        "You are a strict RAG system. You can ONLY answer using the provided document."
        "If the answer is not available, respond exactly with: "
        "'I cannot find the answer in the provided document.'"
    )

    content_payload = [
        {"parts": [{"text": st.session_state.uploaded_text}]},
        {"parts": [{"text": current_prompt}]}
    ]

    with st.spinner("Generating answer..."):
        response_text = gemini_api.generate_content(
            model=MODEL_NAME,
            contents=content_payload,
            system_instruction=system_instruction
        )

    st.session_state.rag_response = {
        "prompt": current_prompt,
        "answer": response_text
    }


# Button
st.button("3. Get Grounded Answer", on_click=run_rag_query, type="primary")


# 4) Display Output
st.subheader("RAG Response")

if st.session_state.get("rag_response") and st.session_state["rag_response"].get("answer"):
    st.markdown("---")
    st.markdown(f"**Question:** {st.session_state['rag_response']['prompt']}")
    st.markdown(st.session_state["rag_response"]["answer"])
    st.markdown("---")
else:
    st.info("Your answer will appear here.")


st.caption("RAG Demo Completed")
