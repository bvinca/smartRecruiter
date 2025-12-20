"""
AI Helpers - Common utilities for cleaning, logging, etc.
"""
import re
from typing import List, Dict, Any


class AIHelpers:
    """Common helper functions for AI operations"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\-\'\(\)\/]', ' ', text)
        return text.strip()
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 8000) -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def parse_questions_from_text(text: str) -> List[str]:
        """Parse numbered questions from text"""
        questions = []
        for line in text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                question = re.sub(r'^\d+[\.\)]\s*|^-\s*', '', line)
                if question:
                    questions.append(question)
        return questions
    
    @staticmethod
    def parse_key_value_response(text: str, keys: List[str]) -> Dict[str, Any]:
        """Parse key-value pairs from AI response"""
        result = {}
        current_key = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with a key
            for key in keys:
                if line.upper().startswith(key.upper() + ':'):
                    current_key = key
                    value = line.split(':', 1)[1].strip()
                    result[key] = value
                    break
            else:
                # Continue current section
                if current_key and current_key in result:
                    result[current_key] += " " + line
        
        return result
    
    @staticmethod
    def extract_list_from_text(text: str, separator: str = ',') -> List[str]:
        """Extract comma-separated list from text"""
        items = [item.strip() for item in text.split(separator) if item.strip()]
        return items
    
    @staticmethod
    def validate_score(score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """Validate and clamp score to range"""
        return max(min_val, min(max_val, score))

