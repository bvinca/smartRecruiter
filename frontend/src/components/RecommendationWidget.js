import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Sparkles, Briefcase, Users, TrendingUp, ExternalLink } from 'lucide-react';
import { recommendationsApi } from '../api/recommendations';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './RecommendationWidget.css';

const RecommendationWidget = ({ type, applicantId, jobId, onSelect }) => {
  const { user } = useAuth();
  const [selectedType, setSelectedType] = useState(type || 'jobs');

  // Fetch job recommendations for applicant
  const { data: jobRecommendations = [], isLoading: jobsLoading } = useQuery({
    queryKey: ['job-recommendations', applicantId],
    queryFn: () => recommendationsApi.getJobRecommendations(applicantId),
    enabled: selectedType === 'jobs' && !!applicantId && user?.role === 'applicant',
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to load job recommendations');
    }
  });

  // Fetch candidate recommendations for job
  const { data: candidateRecommendations = [], isLoading: candidatesLoading } = useQuery({
    queryKey: ['candidate-recommendations', jobId],
    queryFn: () => recommendationsApi.getCandidateRecommendations(jobId),
    enabled: selectedType === 'candidates' && !!jobId && user?.role === 'recruiter',
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to load candidate recommendations');
    }
  });

  const isLoading = jobsLoading || candidatesLoading;

  if (user?.role === 'applicant' && selectedType === 'jobs') {
    return (
      <div className="recommendation-widget">
        <div className="widget-header">
          <Sparkles size={20} />
          <h3>Recommended Jobs for You</h3>
        </div>
        
        {isLoading ? (
          <div className="loading-state">Loading recommendations...</div>
        ) : jobRecommendations.length === 0 ? (
          <div className="empty-state">
            <p>No job recommendations available. Complete your profile to get personalized recommendations.</p>
          </div>
        ) : (
          <div className="recommendations-list">
            {jobRecommendations.map((job) => (
              <div key={job.id} className="recommendation-item" onClick={() => onSelect && onSelect(job)}>
                <div className="recommendation-header">
                  <Briefcase size={18} />
                  <h4>{job.title}</h4>
                  <span className="match-badge">{job.match_percentage?.toFixed(0) || 0}% match</span>
                </div>
                <p className="recommendation-description">
                  {job.description?.substring(0, 150)}...
                </p>
                <div className="recommendation-footer">
                  <span className="location">{job.location || 'Remote'}</span>
                  {job.salary_range && <span className="salary">{job.salary_range}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  if (user?.role === 'recruiter' && selectedType === 'candidates') {
    return (
      <div className="recommendation-widget">
        <div className="widget-header">
          <Users size={20} />
          <h3>Recommended Candidates</h3>
        </div>
        
        {isLoading ? (
          <div className="loading-state">Loading recommendations...</div>
        ) : candidateRecommendations.length === 0 ? (
          <div className="empty-state">
            <p>No candidate recommendations available for this job.</p>
          </div>
        ) : (
          <div className="recommendations-list">
            {candidateRecommendations.map((candidate) => (
              <div key={candidate.id} className="recommendation-item" onClick={() => onSelect && onSelect(candidate)}>
                <div className="recommendation-header">
                  <Users size={18} />
                  <h4>{candidate.first_name} {candidate.last_name}</h4>
                  <span className="match-badge">{candidate.match_percentage?.toFixed(0) || 0}% match</span>
                </div>
                <div className="recommendation-details">
                  <p className="email">{candidate.email}</p>
                  {candidate.skills && candidate.skills.length > 0 && (
                    <div className="skills">
                      {candidate.skills.slice(0, 5).map((skill, idx) => (
                        <span key={idx} className="skill-tag">{skill}</span>
                      ))}
                    </div>
                  )}
                  <div className="candidate-stats">
                    <span>Experience: {candidate.experience_years || 0} years</span>
                    <span>Score: {candidate.overall_score?.toFixed(1) || 'N/A'}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return null;
};

export default RecommendationWidget;

