"""
AI Fairness Auditor Endpoints
Detect bias in recruitment decisions
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import sys
import os

# Add ai directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.database import get_db
from app import models, schemas
from app.dependencies import require_recruiter
from ai.evaluation.fairness_checker import FairnessChecker
from ai.evaluation.bias_visualizer import BiasVisualizer

router = APIRouter(prefix="/fairness", tags=["fairness"])

# Lazy-load fairness checker
_fairness_checker = None

def get_fairness_checker():
    """Get or create FairnessChecker (lazy initialization)"""
    global _fairness_checker
    if _fairness_checker is None:
        _fairness_checker = FairnessChecker()
    return _fairness_checker


@router.post("/audit", response_model=schemas.FairnessAuditResponse)
def audit_fairness(
    request: schemas.FairnessAuditRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """
    Audit fairness for a job posting
    Analyzes scoring data across candidate groups to detect bias
    Only recruiters can access this
    """
    fairness_checker = get_fairness_checker()
    
    # Get applicants for the job
    if request.job_id:
        # Verify job belongs to recruiter
        job = db.query(models.Job).filter(
            models.Job.id == request.job_id,
            models.Job.recruiter_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get all applicants for this job
        applicants = db.query(models.Applicant).filter(
            models.Applicant.job_id == request.job_id
        ).all()
        
        if len(applicants) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 applicants to perform fairness audit"
            )
        
        # Prepare candidate data for analysis
        # Group by education type (STEM vs non-STEM) as example
        candidate_data = []
        for applicant in applicants:
            # Determine group based on education
            group = "unknown"
            if applicant.education:
                education_text = " ".join([
                    edu.get("degree", "") + " " + edu.get("institution", "")
                    for edu in applicant.education
                ]).lower()
                
                stem_keywords = ['computer', 'engineering', 'science', 'technology', 'math', 'statistics']
                if any(keyword in education_text for keyword in stem_keywords):
                    group = "stem"
                else:
                    group = "non_stem"
            else:
                group = "no_education"
            
            candidate_data.append({
                "group": group,
                "overall_score": applicant.overall_score or 0.0,
                "skill_score": applicant.skill_score or 0.0,
                "experience_score": applicant.experience_score or 0.0,
                "experience_years": applicant.experience_years or 0.0
            })
    else:
        # Audit all applicants (for admin/global analysis)
        applicants = db.query(models.Applicant).all()
        
        if len(applicants) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 applicants to perform fairness audit"
            )
        
        candidate_data = []
        for applicant in applicants:
            group = "unknown"
            if applicant.education:
                education_text = " ".join([
                    edu.get("degree", "") + " " + edu.get("institution", "")
                    for edu in applicant.education
                ]).lower()
                
                stem_keywords = ['computer', 'engineering', 'science', 'technology', 'math', 'statistics']
                if any(keyword in education_text for keyword in stem_keywords):
                    group = "stem"
                else:
                    group = "non_stem"
            else:
                group = "no_education"
            
            candidate_data.append({
                "group": group,
                "overall_score": applicant.overall_score or 0.0,
                "skill_score": applicant.skill_score or 0.0,
                "experience_score": applicant.experience_score or 0.0,
                "experience_years": applicant.experience_years or 0.0
            })
    
    try:
        # Use comprehensive fairness audit with MSD and DIR
        result = fairness_checker.comprehensive_fairness_audit(
            candidate_data=candidate_data,
            group_key=request.group_key or "group",
            score_key=request.score_key or "overall_score",
            threshold=request.threshold or 10.0,
            pass_threshold=70.0
        )
        
        # Log fairness metrics to database for trend tracking
        try:
            from app.models import FairnessMetric
            fairness_metric = FairnessMetric(
                job_id=request.job_id,
                mean_score_difference=result.get("mean_score_difference", 0.0),
                disparate_impact_ratio=result.get("disparate_impact_ratio", 1.0),
                bias_magnitude=result.get("bias_magnitude", 0.0),
                bias_detected=result.get("bias_detected", False),
                group_analysis=result.get("group_analysis", {}),
                candidate_count=len(candidate_data),
                threshold_used=request.threshold or 10.0
            )
            db.add(fairness_metric)
            db.commit()
        except Exception as e:
            print(f"Error logging fairness metrics: {e}")
            # Don't fail the request if logging fails
        
        return result
    except Exception as e:
        import traceback
        print(f"Error auditing fairness: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error auditing fairness: {str(e)}"
        )


@router.post("/visualize")
def generate_fairness_visualization(
    request: schemas.FairnessAuditRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """
    Generate fairness visualization heatmap and distribution plots
    Only recruiters can access this
    """
    from ai.evaluation.bias_visualizer import BiasVisualizer
    
    visualizer = BiasVisualizer()
    fairness_checker = get_fairness_checker()
    
    # Get candidate data (same logic as audit endpoint)
    if request.job_id:
        job = db.query(models.Job).filter(
            models.Job.id == request.job_id,
            models.Job.recruiter_id == current_user.id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        applicants = db.query(models.Applicant).filter(
            models.Applicant.job_id == request.job_id
        ).all()
        
        if len(applicants) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 applicants to generate visualization"
            )
        
        candidate_data = []
        for applicant in applicants:
            group = "unknown"
            if applicant.education:
                education_text = " ".join([
                    edu.get("degree", "") + " " + edu.get("institution", "")
                    for edu in applicant.education
                ]).lower()
                
                stem_keywords = ['computer', 'engineering', 'science', 'technology', 'math', 'statistics']
                if any(keyword in education_text for keyword in stem_keywords):
                    group = "stem"
                else:
                    group = "non_stem"
            else:
                group = "no_education"
            
            candidate_data.append({
                "group": group,
                "overall_score": applicant.overall_score or 0.0,
                "skill_score": applicant.skill_score or 0.0,
                "experience_score": applicant.experience_score or 0.0
            })
    else:
        applicants = db.query(models.Applicant).all()
        
        if len(applicants) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 applicants to generate visualization"
            )
        
        candidate_data = []
        for applicant in applicants:
            group = "unknown"
            if applicant.education:
                education_text = " ".join([
                    edu.get("degree", "") + " " + edu.get("institution", "")
                    for edu in applicant.education
                ]).lower()
                
                stem_keywords = ['computer', 'engineering', 'science', 'technology', 'math', 'statistics']
                if any(keyword in education_text for keyword in stem_keywords):
                    group = "stem"
                else:
                    group = "non_stem"
            else:
                group = "no_education"
            
            candidate_data.append({
                "group": group,
                "overall_score": applicant.overall_score or 0.0,
                "skill_score": applicant.skill_score or 0.0,
                "experience_score": applicant.experience_score or 0.0
            })
    
    try:
        # Generate comprehensive report
        output_prefix = f"fairness_job_{request.job_id}" if request.job_id else "fairness_global"
        report = visualizer.generate_comprehensive_report(
            candidate_data=candidate_data,
            group_col=request.group_key or "group",
            score_col=request.score_key or "overall_score",
            output_prefix=output_prefix
        )
        
        return {
            "success": report.get("success", False),
            "heatmap_path": report.get("heatmap", {}).get("file_path"),
            "distribution_path": report.get("distribution", {}).get("file_path"),
            "summary_statistics": report.get("summary_statistics", {}),
            "message": "Visualization generated successfully"
        }
    except Exception as e:
        import traceback
        print(f"Error generating visualization: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualization: {str(e)}"
        )


@router.get("/trends/{job_id}", response_model=dict)
def get_fairness_trends(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_recruiter)
):
    """
    Get historical fairness trends for a job
    Shows bias reduction over time
    Only recruiters can access this
    """
    # Verify job belongs to recruiter
    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.recruiter_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get historical fairness metrics
    from app.models import FairnessMetric
    metrics = db.query(FairnessMetric).filter(
        FairnessMetric.job_id == job_id
    ).order_by(FairnessMetric.created_at.asc()).all()
    
    if len(metrics) < 2:
        raise HTTPException(
            status_code=400,
            detail="Need at least 2 fairness audits to show trends"
        )
    
    # Prepare data for visualization
    metrics_data = [
        {
            "created_at": metric.created_at.isoformat() if metric.created_at else None,
            "mean_score_difference": float(metric.mean_score_difference),
            "disparate_impact_ratio": float(metric.disparate_impact_ratio),
            "bias_magnitude": float(metric.bias_magnitude),
            "bias_detected": metric.bias_detected
        }
        for metric in metrics
    ]
    
    # Generate trends visualization
    try:
        from ai.visualization.fairness_trends_visualizer import FairnessTrendsVisualizer
        
        visualizer = FairnessTrendsVisualizer()
        
        # Generate trends plot
        trends_result = visualizer.plot_fairness_trends(
            metrics_data=metrics_data,
            output_filename=f"fairness_trends_job_{job_id}.png"
        )
        
        # Generate bias reduction plot
        bias_result = visualizer.plot_bias_reduction(
            metrics_data=metrics_data,
            output_filename=f"bias_reduction_job_{job_id}.png"
        )
        
        return {
            "success": True,
            "job_id": job_id,
            "metrics_count": len(metrics),
            "trends_plot": trends_result.get("file_path"),
            "bias_reduction_plot": bias_result.get("file_path"),
            "trend_statistics": trends_result.get("trend_statistics", {}),
            "bias_reduction": bias_result.get("reduction_percentage"),
            "metrics": metrics_data
        }
    except Exception as e:
        import traceback
        print(f"Error generating trends: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating trends: {str(e)}"
        )

