"""
Quick script to create all database tables
Run this once to set up your database with all models including new ones:
- ScoringWeights
- AIAuditLog
- FairnessMetric

Usage:
    cd backend
    python create_tables.py
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import Base, engine
from app import models  # Import all models

def create_all_tables():
    """Create all database tables"""
    print("Creating database tables...")
    print("This includes:")
    print("  - Existing tables (users, jobs, applicants, etc.)")
    print("  - New tables (scoring_weights, ai_audit_logs, fairness_metrics)")
    print()
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] All tables created successfully!")
        print()
        print("You can now use the application with all new features:")
        print("  - Adaptive Learning Scoring System")
        print("  - AI Audit Logging")
        print("  - Fairness Metrics Tracking")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_all_tables()
    sys.exit(0 if success else 1)

