"""
AI Fairness Auditor - Bias Detection
Detects potential bias or imbalance in AI-based recruitment decisions
"""
from typing import Dict, List, Any, Optional
import sys
import os

# Try to import pandas (optional dependency)
PANDAS_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    print("pandas not available. Install with: pip install pandas")
    pd = None

# Try to import numpy (should be available)
try:
    import numpy as np
except ImportError:
    print("numpy not available. Install with: pip install numpy")
    np = None

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


class FairnessChecker:
    """
    Audits fairness by analyzing aggregate scoring data
    Detects bias by comparing average scores across candidate groups
    """
    
    def audit_fairness(
        self,
        candidate_data: List[Dict[str, Any]],
        group_key: str = "group",
        score_key: str = "overall_score",
        threshold: float = 10.0
    ) -> Dict[str, Any]:
        """
        Audit fairness across candidate groups
        
        Args:
            candidate_data: List of candidate dictionaries with scores and group info
            group_key: Key in candidate dict that identifies the group
            score_key: Key in candidate dict that contains the score
            threshold: Maximum acceptable score difference between groups (default 10%)
            
        Returns:
            Dictionary with fairness analysis:
            {
                "bias_detected": bool,
                "bias_magnitude": float,
                "group_analysis": Dict[str, float],
                "recommendations": List[str],
                "statistical_significance": float
            }
        """
        if not candidate_data or len(candidate_data) < 2:
            return {
                "bias_detected": False,
                "bias_magnitude": 0.0,
                "group_analysis": {},
                "recommendations": ["Insufficient data for fairness analysis"],
                "statistical_significance": 0.0,
                "message": "Need at least 2 candidates to perform fairness audit"
            }
        
        if not PANDAS_AVAILABLE:
            return {
                "bias_detected": False,
                "bias_magnitude": 0.0,
                "group_analysis": {},
                "recommendations": ["pandas library required for fairness analysis. Install with: pip install pandas"],
                "statistical_significance": 0.0,
                "message": "pandas not available for fairness analysis"
            }
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(candidate_data)
            
            # Check if required columns exist
            if group_key not in df.columns or score_key not in df.columns:
                return {
                    "bias_detected": False,
                    "bias_magnitude": 0.0,
                    "group_analysis": {},
                    "recommendations": ["Missing required data columns"],
                    "statistical_significance": 0.0,
                    "message": f"Missing columns: {group_key} or {score_key}"
                }
            
            # Calculate group statistics
            group_stats = df.groupby(group_key)[score_key].agg(['mean', 'std', 'count'])
            
            # Calculate bias magnitude (difference between highest and lowest group means)
            group_means = group_stats['mean']
            bias_magnitude = float(group_means.max() - group_means.min())
            
            # Check if bias exceeds threshold
            bias_detected = bias_magnitude > threshold
            
            # Calculate statistical significance (simple t-test approximation)
            if len(group_means) >= 2:
                # Get two groups with max difference
                max_group = group_means.idxmax()
                min_group = group_means.idxmin()
                
                max_scores = df[df[group_key] == max_group][score_key].values
                min_scores = df[df[group_key] == min_group][score_key].values
                
                # Simple statistical test
                if len(max_scores) > 1 and len(min_scores) > 1:
                    try:
                        from scipy import stats
                        t_stat, p_value = stats.ttest_ind(max_scores, min_scores)
                        statistical_significance = float(1 - p_value)  # Convert to confidence
                    except ImportError:
                        # scipy not available, use simple difference as proxy
                        if np is not None:
                            mean_diff = float(np.mean(max_scores) - np.mean(min_scores))
                            statistical_significance = min(0.95, abs(mean_diff) / 100.0)  # Simple proxy
                        else:
                            statistical_significance = 0.5  # Default if numpy not available
                    except:
                        statistical_significance = 0.5  # Default if test fails
                else:
                    statistical_significance = 0.5
            else:
                statistical_significance = 0.5
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                bias_detected, bias_magnitude, group_stats, threshold
            )
            
            # Format group analysis
            group_analysis = {}
            for group in group_stats.index:
                std_val = group_stats.loc[group, 'std']
                std_dev = 0.0
                if pd is not None and not pd.isna(std_val):
                    std_dev = float(std_val)
                elif std_val is not None and not (isinstance(std_val, float) and (std_val != std_val)):  # Check for NaN manually
                    std_dev = float(std_val)
                
                group_analysis[group] = {
                    "mean_score": float(group_stats.loc[group, 'mean']),
                    "std_dev": std_dev,
                    "count": int(group_stats.loc[group, 'count'])
                }
            
            return {
                "bias_detected": bias_detected,
                "bias_magnitude": round(bias_magnitude, 2),
                "group_analysis": group_analysis,
                "recommendations": recommendations,
                "statistical_significance": round(statistical_significance, 3),
                "threshold_used": threshold,
                "message": self._generate_message(bias_detected, bias_magnitude, threshold)
            }
            
        except Exception as e:
            import traceback
            print(f"FairnessChecker: Error during audit: {e}")
            print(f"FairnessChecker: Traceback: {traceback.format_exc()}")
            
            return {
                "bias_detected": False,
                "bias_magnitude": 0.0,
                "group_analysis": {},
                "recommendations": [f"Error during analysis: {str(e)}"],
                "statistical_significance": 0.0,
                "error": str(e)
            }
    
    def _generate_recommendations(
        self,
        bias_detected: bool,
        bias_magnitude: float,
        group_stats: Any,  # pd.DataFrame when pandas is available
        threshold: float
    ) -> List[str]:
        """Generate recommendations based on fairness analysis"""
        recommendations = []
        
        if bias_detected:
            recommendations.append(
                f"⚠️ Potential bias detected: {bias_magnitude:.2f}% difference between groups "
                f"(threshold: {threshold}%)"
            )
            recommendations.append(
                "Review scoring criteria for potential bias in skill weightings or evaluation methods"
            )
            recommendations.append(
                "Consider anonymizing candidate data during initial screening"
            )
            recommendations.append(
                "Review job description for biased language that may attract certain groups"
            )
        else:
            recommendations.append(
                f"✅ No significant bias detected. Score difference ({bias_magnitude:.2f}%) "
                f"is within acceptable threshold ({threshold}%)"
            )
        
        # Additional recommendations based on group statistics
        if len(group_stats) > 1:
            max_group = group_stats['mean'].idxmax()
            min_group = group_stats['mean'].idxmin()
            recommendations.append(
                f"Highest scoring group: {max_group} (avg: {group_stats.loc[max_group, 'mean']:.1f}%)"
            )
            recommendations.append(
                f"Lowest scoring group: {min_group} (avg: {group_stats.loc[min_group, 'mean']:.1f}%)"
            )
        
        return recommendations
    
    def _generate_message(self, bias_detected: bool, bias_magnitude: float, threshold: float) -> str:
        """Generate human-readable message"""
        if bias_detected:
            return (
                f"⚠️ Potential bias detected: {bias_magnitude:.2f}% difference across groups. "
                f"This exceeds the threshold of {threshold}%. "
                f"Review scoring criteria and job requirements for potential bias."
            )
        else:
            return (
                f"✅ No significant bias detected. "
                f"Score difference ({bias_magnitude:.2f}%) is within acceptable threshold ({threshold}%)."
            )

