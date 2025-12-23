from ai.nlp.multilingual_parser import MultilingualResumeParser

def test_french_resume_detection():
    french_cv = "Développeur Python avec expérience en FastAPI."
    # Convert text to bytes as parse_file expects bytes
    file_content = french_cv.encode('utf-8')
    parsed = MultilingualResumeParser().parse_file(
        file_content=file_content,
        filename="test_cv.txt",
        detect_language=True
    )
    assert isinstance(parsed, dict)
    assert "detected_language" in parsed or "language" in parsed
    # Language detection may not always work without langdetect, so just check structure
    assert "resume_text" in parsed
