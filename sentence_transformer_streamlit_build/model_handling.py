import io
import fitz  # PyMuPDF
from docx import Document
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
from typing import List, Dict, Tuple


class UniversalResumeAnalyzer:
    def __init__(self):
        """
        Initialize the universal resume analyzer.
        No fixed skills — all logic derived from job description.
        """
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_text_from_pdf(self, content: bytes) -> str:
        try:
            pdf_stream = io.BytesIO(content)
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            text = " ".join([page.get_text("text") for page in doc])
            doc.close()
            return text
        except Exception as e:
            print(f"PDF extraction failed: {e}")
            return ""

    def extract_text_from_docx(self, content: bytes) -> str:
        try:
            doc = Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"DOCX extraction failed: {e}")
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

    def extract_keywords(self, job_desc: str, top_n: int = 20) -> List[str]:
        """
        Simple keyword extraction: extract important nouns and skills.
        (Can be enhanced with NLP later)
        """
        # Simple: get capitalized words, words after "in", "with", "using", etc.
        words = re.findall(r'\b[A-Z][a-z]{2,}\b', job_desc)  # Proper nouns
        tools = re.findall(r'(?i)\b(?:Python|Java|Selenium|Docker|Kubernetes|CI/CD|Jenkins|Git|SQL|Postman|REST|API|Agile|Scrum|AWS|Azure|GCP|Linux|MySQL|MongoDB|React|Node|TensorFlow|PyTorch)\b', job_desc)
        
        combined = list(set(words + [t.title() for t in tools]))
        return combined[:top_n]

    def get_embedding(self, text: str) -> np.ndarray:
        return self.model.encode(text)

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not text1.strip() or not text2.strip():
            return 0.0
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return cosine_similarity([emb1], [emb2])[0][0]

    def analyze_resume(self, resume_text: str, job_description: str) -> Dict:
        """
        Analyze resume against job description using semantic + keyword matching.
        """
        clean_resume = self.preprocess_text(resume_text)
        clean_job = self.preprocess_text(job_description)

        # 1. Semantic Match (60% weight)
        semantic_sim = self.compute_similarity(clean_resume, clean_job)
        semantic_score = semantic_sim * 100

        # 2. Keyword Match (40% weight)
        keywords = self.extract_keywords(job_description, top_n=30)
        matched = [kw for kw in keywords if kw.lower() in resume_text.lower()]
        keyword_score = (len(matched) / len(keywords)) * 100 if keywords else 0

        # Final weighted score
        final_score = 0.60 * semantic_score + 0.40 * keyword_score
        final_score = round(min(final_score, 100), 1)

        return {
            "overall_match_score": final_score,
            "keywords_matched": matched,
            "keywords_total": keywords,
            "semantic_relevance": round(semantic_score, 1),
            "summary": (
                        "Outstanding Match" if final_score > 80 else
                        "Strong Match" if final_score > 65 else
                        "Moderate Match" if final_score > 50 else
                        "Needs Improvement" if final_score > 35 else
                        "Unsatisfactory"
                    )
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
                    "Overall Match Score": analysis["overall_match_score"],
                    "Keywords Matched": ", ".join(analysis["keywords_matched"]),
                    "Semantic Relevance": analysis["semantic_relevance"],
                    "Summary": analysis["summary"]
                }
            results.append(result)
        return results