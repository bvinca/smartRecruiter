import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { FileText, Clock, CheckCircle, XCircle, Eye, TrendingUp, HelpCircle } from 'lucide-react';
import { applicationsApi } from '../api/applications';
import { explanationApi } from '../api/explanation';
import toast from 'react-hot-toast';
import './ApplicantApplications.css';

const ApplicantApplications = () => {
  const navigate = useNavigate();
  const [explanations, setExplanations] = useState({}); // Store explanations by application ID

  const { data: applications = [], isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationsApi.getAll().then(res => res.data || res),
  });

  const explainMutation = useMutation({
    mutationFn: ({ applicantId, jobId, applicationId }) => explanationApi.explainScoring(applicantId, jobId),
    onSuccess: (response, variables) => {
      setExplanations(prev => ({
        ...prev,
        [variables.applicationId]: response.data
      }));
      toast.success('Scoring explanation generated!');
    },
    onError: (error) => {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate explanation';
      toast.error(errorMsg);
    },
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
      case 'reviewing':
        return <Clock size={20} className="status-icon pending" />;
      case 'shortlisted':
      case 'hired':
        return <CheckCircle size={20} className="status-icon success" />;
      case 'rejected':
        return <XCircle size={20} className="status-icon rejected" />;
      default:
        return <FileText size={20} className="status-icon" />;
    }
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading"></div>
        <p>Loading applications...</p>
      </div>
    );
  }

  return (
    <div className="applicant-applications">
      <div className="page-header">
        <h1>My Applications</h1>
        <p>Track the status of your job applications</p>
      </div>

      <div className="applications-list">
        {applications.map((app) => (
          <div key={app.id} className="application-card">
            <div className="application-header">
              <div className="application-title">
                {getStatusIcon(app.status)}
                <div>
                  <h2>{app.job?.title || 'Unknown Job'}</h2>
                  <p className="application-date">
                    Applied on {new Date(app.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <span className={`status-badge status-${app.status}`}>
                {app.status}
              </span>
            </div>
            {app.job && (
              <div className="application-details">
                <p className="job-location">{app.job.location || 'Remote'}</p>
                <p className="job-description">
                  {app.job.description.substring(0, 200)}...
                </p>
              </div>
            )}
            
            {/* Show Match Score if available */}
            {(app.match_score !== null && app.match_score !== undefined) || (app.applicant?.overall_score) ? (
              <div className="match-score-section">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div className="score-display">
                    <TrendingUp size={18} />
                    <span className="score-label">Match Score:</span>
                    <span className="score-value">
                      {app.match_score?.toFixed(1) || app.applicant?.overall_score?.toFixed(1) || '0.0'}%
                    </span>
                  </div>
                  {app.applicant?.id && (
                    <button 
                      className="btn btn-sm btn-outline" 
                      onClick={() => explainMutation.mutate({
                        applicantId: app.applicant.id,
                        jobId: app.job_id,
                        applicationId: app.id
                      })}
                      disabled={explainMutation.isLoading}
                      style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '6px 12px' }}
                    >
                      <HelpCircle size={14} />
                      {explainMutation.isLoading ? 'Explaining...' : 'Explain Scores'}
                    </button>
                  )}
                </div>
                {app.applicant && (
                  <div className="score-breakdown">
                    <span>Skills: {app.applicant.skill_score?.toFixed(1) || '0.0'}%</span>
                    <span>Experience: {app.applicant.experience_score?.toFixed(1) || '0.0'}%</span>
                    {app.applicant.education_score !== null && app.applicant.education_score !== undefined && (
                      <span>Education: {app.applicant.education_score?.toFixed(1) || '0.0'}%</span>
                    )}
                  </div>
                )}
                {explanations[app.id] && (
                  <div className="score-explanation" style={{ 
                    marginTop: '15px', 
                    padding: '15px', 
                    backgroundColor: '#f8f9fa', 
                    borderRadius: '8px',
                    border: '1px solid #dee2e6'
                  }}>
                    <h5 style={{ marginTop: 0, marginBottom: '10px', fontSize: '14px', fontWeight: '600' }}>Score Explanation</h5>
                    <div className="explanation-breakdown">
                      {explanations[app.id].skills_explanation && (
                        <div style={{ marginBottom: '12px' }}>
                          <strong style={{ fontSize: '13px' }}>Skills Score ({app.applicant?.skill_score?.toFixed(1) || '0.0'}%):</strong>
                          <p style={{ margin: '4px 0', fontSize: '13px' }}>{explanations[app.id].skills_explanation}</p>
                        </div>
                      )}
                      {explanations[app.id].experience_explanation && (
                        <div style={{ marginBottom: '12px' }}>
                          <strong style={{ fontSize: '13px' }}>Experience Score ({app.applicant?.experience_score?.toFixed(1) || '0.0'}%):</strong>
                          <p style={{ margin: '4px 0', fontSize: '13px' }}>{explanations[app.id].experience_explanation}</p>
                        </div>
                      )}
                      {explanations[app.id].education_explanation && (
                        <div style={{ marginBottom: '12px' }}>
                          <strong style={{ fontSize: '13px' }}>Education Score ({app.applicant?.education_score?.toFixed(1) || '0.0'}%):</strong>
                          <p style={{ margin: '4px 0', fontSize: '13px' }}>{explanations[app.id].education_explanation}</p>
                        </div>
                      )}
                    </div>
                    {explanations[app.id].overall_summary && (
                      <div className="overall-summary" style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #dee2e6' }}>
                        <strong style={{ fontSize: '13px' }}>Overall Summary:</strong>
                        <p style={{ margin: '4px 0', fontSize: '13px' }}>{explanations[app.id].overall_summary}</p>
                      </div>
                    )}
                    {explanations[app.id].strengths && explanations[app.id].strengths.length > 0 && (
                      <div style={{ marginTop: '12px' }}>
                        <strong style={{ fontSize: '13px', color: '#10b981' }}>Strengths:</strong>
                        <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '13px' }}>
                          {explanations[app.id].strengths.map((strength, idx) => (
                            <li key={idx}>{strength}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {explanations[app.id].weaknesses && explanations[app.id].weaknesses.length > 0 && (
                      <div style={{ marginTop: '12px' }}>
                        <strong style={{ fontSize: '13px', color: '#ef4444' }}>Areas for Improvement:</strong>
                        <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '13px' }}>
                          {explanations[app.id].weaknesses.map((weakness, idx) => (
                            <li key={idx}>{weakness}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : null}
            
            <div className="application-actions">
              <button
                className="btn btn-secondary"
                onClick={() => navigate(`/applicant/jobs/${app.job_id}`)}
              >
                <Eye size={16} />
                View Job
              </button>
            </div>
          </div>
        ))}

        {applications.length === 0 && (
          <div className="empty-state">
            <FileText size={64} />
            <h3>No applications yet</h3>
            <p>Start applying to jobs to see your applications here</p>
            <button
              className="btn btn-primary"
              onClick={() => navigate('/applicant/jobs')}
            >
              Browse Jobs
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApplicantApplications;

