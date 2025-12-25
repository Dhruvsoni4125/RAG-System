# 📃 Gemini RAG System (Streamlit App)

A **Retrieval-Augmented Generation (RAG)** application built with **Streamlit** and **Google Gemini API**.  
It allows users to upload documents and ask questions that are answered **strictly from the uploaded content**.

---

## 🚀 Features

- Upload documents: **TXT, MD, PDF, DOCX**
- Extracts and processes document text
- Context-aware Q&A using **Gemini 2.5 Flash Lite**
- Strict RAG behavior (no hallucination)
- Simple and clean Streamlit UI

---

## 🧠 How It Works

1. Upload a document  
2. Text is extracted from the file  
3. Ask a question  
4. Gemini answers **only from the document**  
5. If not found → fixed fallback response  

---

## 🛠️ Tech Stack

- Python  
- Streamlit  
- Google Gemini API  
- pypdf  
- python-docx  

---

## 📂 Project Structure

```
.
├── app.py
├── requirements.txt
├── README.md
```

---

## 📦 Requirements

```
streamlit
google-genai
pypdf
python-docx
hugchat
```

---

## 🔐 Environment Variable

### Windows (PowerShell)
```
setx API_KEY "your_api_key_here"
```

### macOS / Linux
```
export API_KEY="your_api_key_here"
```

---

## ▶️ Run the App

```
streamlit run app.py
```

---

## 📄 Supported Files

- .txt  
- .md  
- .pdf  
- .docx  

---

## ❗ RAG Rule

If the answer is not in the document, the system responds:

> I cannot find the answer in the provided document.

---

## 📌 Use Cases

- Document Question Answering  
- Study & Research  
- Policy / Contract Review  
- RAG Demo Projects  

---

## 👤 Author

**Dhruv Soni**
