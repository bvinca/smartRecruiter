import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { FileText, Clock, CheckCircle, XCircle, Eye, TrendingUp } from 'lucide-react';
import { applicationsApi } from '../api/applications';
import './ApplicantApplications.css';

const ApplicantApplications = () => {
  const navigate = useNavigate();

  const { data: applications = [], isLoading } = useQuery({
    queryKey: ['applications'],
    queryFn: () => applicationsApi.getAll().then(res => res.data || res),
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
                <div className="score-display">
                  <TrendingUp size={18} />
                  <span className="score-label">Match Score:</span>
                  <span className="score-value">
                    {app.match_score?.toFixed(1) || app.applicant?.overall_score?.toFixed(1) || '0.0'}%
                  </span>
                </div>
                {app.applicant && (
                  <div className="score-breakdown">
                    <span>Skills: {app.applicant.skill_score?.toFixed(1) || '0.0'}%</span>
                    <span>Experience: {app.applicant.experience_score?.toFixed(1) || '0.0'}%</span>
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

