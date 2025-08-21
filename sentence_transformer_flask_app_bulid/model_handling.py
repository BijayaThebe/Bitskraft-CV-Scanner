# model_handling.py
import io
import fitz
from docx import Document
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from typing import List, Dict, Tuple

class UniversalResumeAnalyzer:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_text_from_pdf(self, content: bytes) -> str:
        try:
            pdf_stream = io.BytesIO(content)
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            return " ".join([page.get_text("text") for page in doc])
        except:
            return ""

    def extract_text_from_docx(self, content: bytes) -> str:
        try:
            doc = Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        except:
            return ""

    def extract_text(self, file_bytes: bytes, file_type: str) -> str:
        if file_type == "application/pdf":
            return self.extract_text_from_pdf(file_bytes)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self.extract_text_from_docx(file_bytes)
        else:
            return ""

    def preprocess_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-]', '', text)
        return text.lower().strip()

    def extract_keywords(self, job_desc: str, top_n: int = 30) -> List[str]:
        words = re.findall(r'\b[A-Z][a-z]{2,}\b', job_desc)
        tools = re.findall(
            r'(?i)\b(?:Python|Java|JavaScript|TypeScript|Go|C\+\+|C#|Ruby|Kotlin|Swift|Rust|'
            r'Docker|Kubernetes|Terraform|Ansible|Jenkins|GitHub Actions|GitLab CI|'
            r'AWS|Azure|GCP|Google Cloud|'
            r'React|Angular|Vue|Node\.js|Spring|Django|Flask|'
            r'PostgreSQL|MySQL|MongoDB|Redis|'
            r'Agile|Scrum|CI/CD|Microservices|REST|GraphQL)\b', job_desc)
        
        return list(set(words + [t.title() for t in tools]))[:top_n]

    def get_embedding(self, text: str) -> np.ndarray:
        return self.model.encode(text)

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            return 0.0
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return cosine_similarity([emb1], [emb2])[0][0]

    def analyze_resume(self, resume_text: str, job_description: str) -> Dict:
        clean_resume = self.preprocess_text(resume_text)
        clean_job = self.preprocess_text(job_description)

        semantic_sim = self.compute_similarity(clean_resume, clean_job)
        semantic_score = semantic_sim * 100

        keywords = self.extract_keywords(job_description)
        matched = [kw for kw in keywords if kw.lower() in resume_text.lower()]
        keyword_score = (len(matched) / len(keywords)) * 100 if keywords else 50

        final_score = 0.60 * semantic_score + 0.40 * keyword_score
        final_score = round(min(final_score, 100), 3)

        return {
            "overall_match_score": round(final_score, 3),
            "keywords_matched": matched,
            "semantic_relevance": round(semantic_score, 3),
            "summary": "Strong match" if final_score > 80 else "Moderate match" if final_score > 60 else "Low match"
        }
        

    def batch_analyze(self, files: List[Tuple[bytes, str]], job_description: str) -> List[Dict]:
        results = []
        for content, file_type in files:
            text = self.extract_text(content, file_type)
            if not text.strip():
                result = {"Error": "Failed to extract text"}
            else:
                analysis = self.analyze_resume(text, job_description)

                result = {
                    "Overall Match Score": f"{analysis['overall_match_score']:.3f}",  # formatted as 3 decimal digits
                    "Keywords Matched": ", ".join(analysis["keywords_matched"]),
                    "Semantic Relevance": f"{analysis['semantic_relevance']:.3f}",
                    "Summary": analysis["summary"]
                }


            results.append(result)
        return results