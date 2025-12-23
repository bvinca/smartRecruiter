from ai.enhancement.job_description_enhancer import JobDescriptionEnhancer

def test_job_enhancer_bias_reduction():
    text = "Looking for a young, native English speaker Python developer."
    result = JobDescriptionEnhancer().enhance_job_description(
        job_description=text,
        job_title="Python Developer"
    )
    
    assert isinstance(result, dict)
    assert "improved_description" in result
    assert "identified_issues" in result
    assert "bias_detected" in result
    
    # Check that bias-related terms are flagged or removed
    improved_text = result["improved_description"].lower()
    issues_text = " ".join(result["identified_issues"]).lower()
    
    # Either the improved text doesn't contain bias terms, or they're flagged in issues
    assert ("young" not in improved_text or "young" in issues_text)
    assert ("native english" not in improved_text or "native" in issues_text or "english" in issues_text)
