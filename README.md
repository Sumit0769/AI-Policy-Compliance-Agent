# AI Policy & Compliance Agent

An AI-powered compliance system that analyzes AI applications against global regulations such as GDPR and the EU AI Act.

---

##Features

- Legal Document Ingestion (PDF/DOCX)
- Structure-aware Chunking (Articles, Sections)
- Compliance Reasoning Engine
- Vectorless RAG using PageIndex
- Risk Classification (EU AI Act)
- Audit-ready Compliance Reports
- LLM-powered Explanation with Citations

---

## Architecture

User Input  
↓  
FastAPI  
↓  
Compliance Reasoner  
↓  
PageIndex Retrieval (Vectorless RAG)  
↓  
Rule-based + LLM reasoning  
↓  
Report Generator  

---

## 📂 Project Structure

