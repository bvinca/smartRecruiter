"""
Enhanced Resume Parser following RESUME_PARSING_PLAN.md
- Uses PyMuPDF for PDF parsing
- Uses spaCy for entity detection
- Enhanced text normalization
- Integrates with SkillExtractor and Summarizer
"""
import re
import io
from typing import Dict, List, Any, Optional
import PyPDF2  # Fallback for PDF
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from docx import Document

# Try to import spaCy (may fail on Python 3.14+ due to Pydantic V1 incompatibility)
SPACY_AVAILABLE = False
nlp = None
try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except (OSError, Exception) as e:
        # Model not downloaded or other error, will use fallback
        print(f"spaCy model not available: {e}")
        nlp = None
        SPACY_AVAILABLE = False
except (ImportError, Exception) as e:
    # spaCy not installed or incompatible (e.g., Python 3.14+ with Pydantic V1)
    print(f"spaCy not available (will use regex fallbacks): {e}")
    SPACY_AVAILABLE = False
    nlp = None

from app.services.skill_extractor import SkillExtractor
from app.services.summarizer import Summarizer


class ResumeParser:
    """Enhanced resume parser with NLP entity detection and AI summarization"""
    
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        try:
            self.summarizer = Summarizer()
        except ValueError:
            # OpenAI not configured, will skip AI features
            self.summarizer = None
    
    def parse_file(self, file_content: bytes, filename: str, use_ai: bool = True) -> Dict[str, Any]:
        """
        Parse resume file and extract structured information
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            use_ai: Whether to use AI summarization (requires OpenAI API key)
        
        Returns:
            Dictionary with parsed resume data
        """
        file_ext = filename.split('.')[-1].lower()
        
        # Step 1: Extract text
        if file_ext == 'pdf':
            text = self._extract_from_pdf(file_content)
        elif file_ext in ['doc', 'docx']:
            text = self._extract_from_docx(file_content)
        elif file_ext == 'txt':
            text = file_content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Step 2: Normalize text
        normalized_text = self._normalize_text(text)
        
        # Step 3: Parse with NLP and extract entities
        parsed_data = self._parse_text(normalized_text, text)
        
        # Step 4: Extract skills using enhanced skill extractor
        parsed_data['skills'] = self.skill_extractor.extract_skills(normalized_text)
        parsed_data['technical_skills'] = self.skill_extractor.extract_technical_skills(normalized_text)
        parsed_data['soft_skills'] = self.skill_extractor.extract_soft_skills(normalized_text)
        
        # Step 5: AI Semantic Enhancement (if available)
        if use_ai and self.summarizer:
            try:
                parsed_data['ai_summary'] = self.summarizer.summarize_candidate(parsed_data)
            except Exception as e:
                print(f"Error generating AI summary: {e}")
                parsed_data['ai_summary'] = None
        
        return parsed_data
    
    def _extract_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF using PyMuPDF (preferred) or PyPDF2 (fallback)"""
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(stream=file_content, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                return text
            except Exception as e:
                print(f"PyMuPDF extraction failed, using fallback: {e}")
        
        # Fallback to PyPDF2
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        doc_file = io.BytesIO(file_content)
        doc = Document(doc_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize extracted text:
        - Remove excessive newlines
        - Remove special symbols
        - Clean up whitespace
        """
        # Remove excessive newlines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove special symbols but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\-\'\(\)\/]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up line breaks
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    def _parse_text(self, normalized_text: str, original_text: str) -> Dict[str, Any]:
        """
        Parse resume text using NLP entity detection and regex patterns
        """
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, original_text)
        email = emails[0] if emails else None
        
        # Extract phone (multiple patterns)
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',
        ]
        phone = None
        for pattern in phone_patterns:
            matches = re.findall(pattern, original_text)
            if matches:
                phone = matches[0]
                break
        
        # Extract name using spaCy if available
        first_name, last_name = self._extract_name(normalized_text, original_text)
        
        # Extract experience years
        experience_years = self._extract_experience_years(normalized_text)
        
        # Extract education
        education = self._extract_education(normalized_text, original_text)
        
        # Extract work experience
        work_experience = self._extract_work_experience(normalized_text, original_text)
        
        # Extract entities using spaCy if available
        entities = {}
        if SPACY_AVAILABLE and nlp:
            entities = self._extract_entities_with_spacy(original_text)
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "experience_years": experience_years,
            "education": education,
            "work_experience": work_experience,
            "resume_text": normalized_text,
            "entities": entities  # NLP entities from spaCy
        }
    
    def _extract_name(self, normalized_text: str, original_text: str) -> tuple:
        """Extract name using spaCy (if available) or fallback to first line"""
        if SPACY_AVAILABLE and nlp:
            try:
                doc = nlp(original_text[:500])  # Process first 500 chars for name
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        name_parts = ent.text.split()
                        if len(name_parts) >= 2:
                            return name_parts[0], " ".join(name_parts[1:])
                        elif len(name_parts) == 1:
                            return name_parts[0], ""
            except Exception as e:
                print(f"Error extracting name with spaCy: {e}")
        
        # Fallback: use first line
        lines = original_text.split('\n')
        name = lines[0].strip() if lines else ""
        name_parts = name.split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        return first_name, last_name
    
    def _extract_entities_with_spacy(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using spaCy NLP"""
        if not SPACY_AVAILABLE or not nlp:
            return {}
        
        try:
            doc = nlp(text[:5000])  # Process first 5000 chars
            entities = {
                "PERSON": [],
                "ORG": [],
                "GPE": [],  # Geopolitical entities (locations)
                "DATE": [],
                "EDUCATION": [],
            }
            
            for ent in doc.ents:
                if ent.label_ in entities:
                    if ent.text not in entities[ent.label_]:
                        entities[ent.label_].append(ent.text)
            
            # Custom extraction for education keywords
            education_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'degree', 'university', 'college']
            for sent in doc.sents:
                sent_lower = sent.text.lower()
                if any(keyword in sent_lower for keyword in education_keywords):
                    entities["EDUCATION"].append(sent.text.strip())
            
            return entities
        except Exception as e:
            print(f"Error extracting entities with spaCy: {e}")
            return {}
    
    def _extract_experience_years(self, text: str) -> float:
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?|yoe|years?\s+of\s+experience)',
            r'(?:experience|exp)[:\s]+(\d+)\+?',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional|work|industry)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    return float(matches[0])
                except:
                    continue
        
        # Estimate from work experience entries
        work_exp = self._extract_work_experience(text, text)
        if work_exp:
            return len(work_exp) * 1.5
        
        return 0.0
    
    def _extract_education(self, normalized_text: str, original_text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        education = []
        education_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'degree', 'university', 'college', 'b.s.', 'm.s.', 'b.a.', 'm.a.']
        
        lines = original_text.split('\n')
        current_edu = {}
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                # Try to extract degree and institution
                parts = re.split(r'[-–—]|,\s*', line)
                if len(parts) >= 2:
                    current_edu = {
                        "degree": parts[0].strip(),
                        "institution": parts[1].strip(),
                        "year": self._extract_year(line)
                    }
                    education.append(current_edu)
                elif len(parts) == 1:
                    # Single part, might be just degree or institution
                    current_edu = {
                        "degree": line.strip(),
                        "institution": "",
                        "year": self._extract_year(line)
                    }
                    education.append(current_edu)
        
        return education[:3]  # Return top 3
    
    def _extract_work_experience(self, normalized_text: str, original_text: str) -> List[Dict[str, Any]]:
        """Extract work experience"""
        experience = []
        lines = original_text.split('\n')
        
        current_exp = {}
        for i, line in enumerate(lines):
            # Look for job titles and companies
            if ' - ' in line or ' at ' in line.lower() or ' | ' in line:
                parts = re.split(r'\s+-\s+|\s+at\s+|\s+\|\s+', line, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    current_exp = {
                        "title": parts[0].strip(),
                        "company": parts[1].strip() if len(parts) > 1 else "",
                        "duration": self._extract_duration(line),
                        "description": ""
                    }
                    # Get next few lines as description
                    if i + 1 < len(lines):
                        desc_lines = []
                        for j in range(i + 1, min(i + 4, len(lines))):
                            if lines[j].strip() and not re.match(r'^\d{4}', lines[j].strip()):
                                desc_lines.append(lines[j].strip())
                        current_exp["description"] = " ".join(desc_lines)
                    experience.append(current_exp)
        
        return experience[:5]  # Return top 5
    
    def _extract_year(self, text: str) -> Optional[str]:
        """Extract year from text"""
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        return year_match.group() if year_match else None
    
    def _extract_duration(self, text: str) -> Optional[str]:
        """Extract duration from text"""
        duration_patterns = [
            r'(\d{4})\s*-\s*(\d{4}|present|current)',
            r'(\w+\s+\d{4})\s*-\s*(\w+\s+\d{4}|present|current)',
            r'(\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{4}|present|current)',
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return None
