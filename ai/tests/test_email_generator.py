"""
Unit tests for AI Email Generator
"""
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ai.llm.email_generator import EmailGenerator


def test_email_generation():
    """Test basic email generation"""
    generator = EmailGenerator()
    
    # Test acknowledgment email
    email = generator.generate_email(
        candidate_name="Alice Brown",
        job_title="Python Developer",
        message_type="acknowledgment",
        score_data=None
    )
    
    assert email is not None
    assert len(email) > 0
    assert "Alice" in email or "alice" in email.lower()
    assert "Python Developer" in email or "python" in email.lower()
    print("✓ Acknowledgment email generated successfully")
    
    # Test feedback email with scores
    email = generator.generate_email(
        candidate_name="Bob Smith",
        job_title="Full-Stack Engineer",
        message_type="feedback",
        score_data={"overall_score": 78.5, "skill_score": 85.0}
    )
    
    assert email is not None
    assert len(email) > 0
    assert "Bob" in email or "bob" in email.lower()
    print("✓ Feedback email generated successfully")
    
    # Test rejection email
    email = generator.generate_email(
        candidate_name="Charlie Davis",
        job_title="Senior Developer",
        message_type="rejection",
        score_data={"overall_score": 45.0}
    )
    
    assert email is not None
    assert len(email) > 0
    print("✓ Rejection email generated successfully")
    
    # Test interview invitation
    email = generator.generate_email(
        candidate_name="Diana Wilson",
        job_title="Data Scientist",
        message_type="interview_invitation",
        score_data={"overall_score": 92.0}
    )
    
    assert email is not None
    assert len(email) > 0
    print("✓ Interview invitation email generated successfully")
    
    print("\n✅ All email generation tests passed!")


if __name__ == "__main__":
    test_email_generation()

