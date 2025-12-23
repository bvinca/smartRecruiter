"""
Bias Visualizer - Generates heatmap visualizations for fairness analysis
Creates visual representations of score distributions across groups
"""
from typing import Dict, List, Any, Optional
import sys
import os

# Try to import visualization libraries
MATPLOTLIB_AVAILABLE = False
SEABORN_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("matplotlib not available. Install with: pip install matplotlib")
    plt = None

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    print("seaborn not available. Install with: pip install seaborn")
    sns = None

PANDAS_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    print("pandas not available. Install with: pip install pandas")
    pd = None

NUMPY_AVAILABLE = False
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("numpy not available. Install with: pip install numpy")
    np = None


class BiasVisualizer:
    """
    Generates heatmap visualizations for fairness analysis
    Creates visual representations of score distributions across demographic groups
    """
    
    def __init__(self, output_dir: str = "ai/reports"):
        """
        Initialize the visualizer
        
        Args:
            output_dir: Directory to save generated visualizations
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def plot_bias_heatmap(
        self,
        candidate_data: List[Dict[str, Any]],
        group_col: str = "group",
        score_col: str = "overall_score",
        output_filename: str = "fairness_heatmap.png"
    ) -> Dict[str, Any]:
        """
        Generate heatmap visualization of scores by group
        
        Args:
            candidate_data: List of candidate dictionaries with scores and group info
            group_col: Column name for group identifier
            score_col: Column name for score values
            output_filename: Name of output file
            
        Returns:
            Dictionary with visualization info:
            {
                "success": bool,
                "file_path": str,
                "message": str
            }
        """
        if not MATPLOTLIB_AVAILABLE or not PANDAS_AVAILABLE:
            return {
                "success": False,
                "file_path": None,
                "message": "matplotlib and pandas required for visualization. Install with: pip install matplotlib pandas"
            }
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(candidate_data)
            
            if group_col not in df.columns or score_col not in df.columns:
                return {
                    "success": False,
                    "file_path": None,
                    "message": f"Missing required columns: {group_col} or {score_col}"
                }
            
            # Create pivot table for heatmap
            pivot = df.pivot_table(
                values=score_col,
                index=group_col,
                aggfunc=['mean', 'std', 'count']
            )
            
            # Flatten column names
            pivot.columns = ['_'.join(col).strip() for col in pivot.columns.values]
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            if SEABORN_AVAILABLE:
                # Use seaborn for better-looking heatmap
                sns.heatmap(
                    pivot[['mean_' + score_col]].T,
                    annot=True,
                    fmt='.2f',
                    cmap='coolwarm',
                    center=pivot['mean_' + score_col].mean(),
                    cbar_kws={'label': 'Average Score'},
                    linewidths=0.5,
                    linecolor='gray'
                )
            else:
                # Fallback to matplotlib
                plt.imshow(pivot[['mean_' + score_col]].T.values, cmap='coolwarm', aspect='auto')
                plt.colorbar(label='Average Score')
                plt.xticks(range(len(pivot.index)), pivot.index, rotation=45, ha='right')
                plt.yticks([0], ['Mean Score'])
            
            plt.title('AI Fairness Heatmap by Group', fontsize=14, fontweight='bold', pad=20)
            plt.xlabel('Group', fontsize=12)
            plt.ylabel('Score Type', fontsize=12)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.output_dir, output_filename)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "success": True,
                "file_path": output_path,
                "message": f"Heatmap saved to {output_path}"
            }
            
        except Exception as e:
            import traceback
            print(f"BiasVisualizer: Error generating heatmap: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "file_path": None,
                "message": f"Error generating heatmap: {str(e)}"
            }
    
    def plot_score_distribution(
        self,
        candidate_data: List[Dict[str, Any]],
        group_col: str = "group",
        score_col: str = "overall_score",
        output_filename: str = "score_distribution.png"
    ) -> Dict[str, Any]:
        """
        Generate box plot showing score distribution by group
        
        Args:
            candidate_data: List of candidate dictionaries
            group_col: Column name for group identifier
            score_col: Column name for score values
            output_filename: Name of output file
            
        Returns:
            Dictionary with visualization info
        """
        if not MATPLOTLIB_AVAILABLE or not PANDAS_AVAILABLE:
            return {
                "success": False,
                "file_path": None,
                "message": "matplotlib and pandas required for visualization"
            }
        
        try:
            df = pd.DataFrame(candidate_data)
            
            if group_col not in df.columns or score_col not in df.columns:
                return {
                    "success": False,
                    "file_path": None,
                    "message": f"Missing required columns: {group_col} or {score_col}"
                }
            
            # Create figure
            plt.figure(figsize=(12, 6))
            
            if SEABORN_AVAILABLE:
                # Use seaborn for better box plots
                sns.boxplot(data=df, x=group_col, y=score_col, palette='Set2')
                sns.stripplot(data=df, x=group_col, y=score_col, color='black', alpha=0.3, size=3)
            else:
                # Fallback to matplotlib
                groups = df[group_col].unique()
                data_by_group = [df[df[group_col] == group][score_col].values for group in groups]
                plt.boxplot(data_by_group, labels=groups)
            
            plt.title('Score Distribution by Group', fontsize=14, fontweight='bold', pad=20)
            plt.xlabel('Group', fontsize=12)
            plt.ylabel('Score', fontsize=12)
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            
            # Save figure
            output_path = os.path.join(self.output_dir, output_filename)
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "success": True,
                "file_path": output_path,
                "message": f"Distribution plot saved to {output_path}"
            }
            
        except Exception as e:
            import traceback
            print(f"BiasVisualizer: Error generating distribution plot: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "file_path": None,
                "message": f"Error generating plot: {str(e)}"
            }
    
    def generate_comprehensive_report(
        self,
        candidate_data: List[Dict[str, Any]],
        group_col: str = "group",
        score_col: str = "overall_score",
        output_prefix: str = "fairness_report"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive fairness visualization report
        
        Creates multiple visualizations:
        1. Heatmap of mean scores by group
        2. Score distribution box plots
        3. Summary statistics
        
        Args:
            candidate_data: List of candidate dictionaries
            group_col: Column name for group identifier
            score_col: Column name for score values
            output_prefix: Prefix for output files
            
        Returns:
            Dictionary with report info
        """
        results = {
            "heatmap": self.plot_bias_heatmap(
                candidate_data, group_col, score_col,
                f"{output_prefix}_heatmap.png"
            ),
            "distribution": self.plot_score_distribution(
                candidate_data, group_col, score_col,
                f"{output_prefix}_distribution.png"
            )
        }
        
        # Calculate summary statistics
        if PANDAS_AVAILABLE:
            try:
                df = pd.DataFrame(candidate_data)
                if group_col in df.columns and score_col in df.columns:
                    summary = df.groupby(group_col)[score_col].agg(['mean', 'std', 'min', 'max', 'count'])
                    results["summary_statistics"] = summary.to_dict('index')
                else:
                    results["summary_statistics"] = {}
            except Exception as e:
                results["summary_statistics"] = {"error": str(e)}
        else:
            results["summary_statistics"] = {}
        
        results["success"] = results["heatmap"]["success"] or results["distribution"]["success"]
        
        return results

