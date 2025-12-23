"""
Multi-Language Resume Parsing
Extends resume parsing to support multilingual CVs
"""
from typing import Dict, Any, Optional
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Try to import language detection
LANGDETECT_AVAILABLE = False
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0  # For consistent results
    LANGDETECT_AVAILABLE = True
except ImportError:
    print("langdetect not available. Install with: pip install langdetect")

# Try to import translation
GOOGLETRANS_AVAILABLE = False
try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    print("googletrans not available. Install with: pip install googletrans==4.0.0rc1")

from .parser import ResumeParser


class MultilingualResumeParser(ResumeParser):
    """
    Extended resume parser with multilingual support
    Detects language and normalizes to English for consistency
    """
    
    def __init__(self):
        """Initialize multilingual parser"""
        super().__init__()
        self.translator = None
        
        if GOOGLETRANS_AVAILABLE:
            try:
                self.translator = Translator()
                print("MultilingualResumeParser: Translation available")
            except Exception as e:
                print(f"MultilingualResumeParser: Failed to initialize translator: {e}")
    
    def parse_file(
        self,
        file_content: bytes,
        filename: str,
        use_ai: bool = False,
        detect_language: bool = True,
        translate_to_english: bool = True
    ) -> Dict[str, Any]:
        """
        Parse resume file with multilingual support
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            use_ai: Whether to use AI summarization
            detect_language: Whether to detect document language
            translate_to_english: Whether to translate to English for processing
            
        Returns:
            Dictionary with parsed resume data, including language info
        """
        # First, extract text using parent class
        parsed_data = super().parse_file(file_content, filename, use_ai)
        
        # Detect language
        detected_language = "en"  # Default to English
        if detect_language and LANGDETECT_AVAILABLE:
            try:
                resume_text = parsed_data.get("resume_text", "")
                if resume_text:
                    detected_language = detect(resume_text)
                    print(f"MultilingualResumeParser: Detected language: {detected_language}")
            except Exception as e:
                print(f"MultilingualResumeParser: Language detection failed: {e}")
                detected_language = "en"
        
        parsed_data["detected_language"] = detected_language
        
        # Translate to English if needed
        if translate_to_english and detected_language != "en" and self.translator:
            try:
                print(f"MultilingualResumeParser: Translating from {detected_language} to English...")
                resume_text = parsed_data.get("resume_text", "")
                
                if resume_text:
                    # Translate resume text
                    translated = self.translator.translate(resume_text, src=detected_language, dest='en')
                    parsed_data["resume_text_original"] = resume_text
                    parsed_data["resume_text"] = translated.text
                    
                    # Translate extracted fields
                    if parsed_data.get("first_name"):
                        translated_name = self.translator.translate(
                            parsed_data["first_name"], src=detected_language, dest='en'
                        )
                        parsed_data["first_name_original"] = parsed_data["first_name"]
                        parsed_data["first_name"] = translated_name.text
                    
                    print("MultilingualResumeParser: Translation completed")
            except Exception as e:
                print(f"MultilingualResumeParser: Translation failed: {e}")
                # Keep original text if translation fails
                parsed_data["translation_error"] = str(e)
        
        return parsed_data
    
    def parse_text_multilingual(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse text with language detection
        
        Args:
            text: Resume text
            language: Optional language code (if None, will be detected)
            
        Returns:
            Parsed data with language information
        """
        if not language and LANGDETECT_AVAILABLE:
            try:
                language = detect(text)
            except:
                language = "en"
        
        # Use parent parser
        parsed_data = self._parse_text(text, text)
        parsed_data["detected_language"] = language or "en"
        
        return parsed_data

