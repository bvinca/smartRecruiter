import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Mail, Phone, Briefcase, GraduationCap, Sparkles, MessageSquare, UserCheck, XCircle, CheckCircle } from 'lucide-react';
import { applicationsApi } from '../api/applications';
import toast from 'react-hot-toast';
import './Modal.css';
import './ApplicantDetail.css';

const ApplicantDetail = ({ applicant, onClose }) => {
  const queryClient = useQueryClient();

  const updateStatusMutation = useMutation({
    mutationFn: ({ applicationId, status }) => applicationsApi.update(applicationId, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries(['applications']);
      queryClient.invalidateQueries(['applicants']);
      toast.success('Application status updated successfully');
      onClose(); // Close modal after successful update
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to update application status');
    },
  });

  const handleStatusUpdate = (applicationId, status) => {
    if (!applicationId) {
      toast.error('Application ID not found');
      return;
    }
    updateStatusMutation.mutate({ applicationId, status });
  };
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{applicant.first_name} {applicant.last_name}</h2>
          <button className="btn-icon" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="detail-content">
          <div className="detail-section">
            <h3>Contact Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <Mail size={18} />
                <span>{applicant.email}</span>
              </div>
              {applicant.phone && (
                <div className="info-item">
                  <Phone size={18} />
                  <span>{applicant.phone}</span>
                </div>
              )}
            </div>
          </div>

          {applicant.overall_score > 0 && (
            <div className="detail-section">
              <h3>Scoring</h3>
              <div className="scores-grid">
                <div className="score-card">
                  <span className="score-label">Overall Score</span>
                  <span className="score-number">{applicant.overall_score.toFixed(1)}%</span>
                </div>
                <div className="score-card">
                  <span className="score-label">Match Score</span>
                  <span className="score-number">{applicant.match_score.toFixed(1)}%</span>
                </div>
                <div className="score-card">
                  <span className="score-label">Skill Score</span>
                  <span className="score-number">{applicant.skill_score.toFixed(1)}%</span>
                </div>
                <div className="score-card">
                  <span className="score-label">Experience Score</span>
                  <span className="score-number">{applicant.experience_score.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          )}

          {applicant.skills && applicant.skills.length > 0 && (
            <div className="detail-section">
              <h3>Skills</h3>
              <div className="skills-list">
                {applicant.skills.map((skill, idx) => (
                  <span key={idx} className="skill-badge">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {applicant.work_experience && applicant.work_experience.length > 0 && (
            <div className="detail-section">
              <h3>
                <Briefcase size={20} />
                Work Experience
              </h3>
              {applicant.work_experience.map((exp, idx) => (
                <div key={idx} className="experience-item">
                  <h4>{exp.title}</h4>
                  <p className="company">{exp.company}</p>
                  {exp.duration && <p className="duration">{exp.duration}</p>}
                  {exp.description && <p className="description">{exp.description}</p>}
                </div>
              ))}
            </div>
          )}

          {applicant.education && applicant.education.length > 0 && (
            <div className="detail-section">
              <h3>
                <GraduationCap size={20} />
                Education
              </h3>
              {applicant.education.map((edu, idx) => (
                <div key={idx} className="education-item">
                  <h4>{edu.degree}</h4>
                  <p>{edu.institution}</p>
                  {edu.year && <p className="year">{edu.year}</p>}
                </div>
              ))}
            </div>
          )}

          {applicant.ai_summary && applicant.ai_summary !== "Unable to generate AI summary at this time." ? (
            <div className="detail-section ai-section">
              <h3>
                <Sparkles size={20} />
                AI Summary
              </h3>
              <p className="ai-text">{applicant.ai_summary}</p>
            </div>
          ) : applicant.resume_text ? (
            <div className="detail-section ai-section">
              <h3>
                <Sparkles size={20} />
                AI Summary
              </h3>
              <p className="ai-text ai-unavailable">
                AI summary is currently unavailable. This may be due to API quota limits. 
                The resume has been parsed and stored successfully.
              </p>
            </div>
          ) : null}

          {applicant.ai_feedback && (
            <div className="detail-section ai-section">
              <h3>AI Feedback</h3>
              <p className="ai-text">{applicant.ai_feedback}</p>
            </div>
          )}

          {applicant.interview_questions && applicant.interview_questions.length > 0 && (
            <div className="detail-section">
              <h3>
                <MessageSquare size={20} />
                Suggested Interview Questions
              </h3>
              <ol className="questions-list">
                {applicant.interview_questions.map((question, idx) => (
                  <li key={idx} className="question-item">{question}</li>
                ))}
              </ol>
            </div>
          )}

          {applicant.resume_text && (
            <div className="detail-section">
              <h3>Resume Text</h3>
              <div className="resume-text">
                <pre>{applicant.resume_text.substring(0, 2000)}...</pre>
              </div>
            </div>
          )}
        </div>

        <div className="modal-actions">
          {/* Status Update Buttons (Recruiter Actions) */}
          {applicant.application_id && (
            <div className="status-actions-modal">
              {applicant.application_status !== 'shortlisted' && applicant.application_status !== 'hired' && (
                <button
                  className="btn btn-success"
                  onClick={() => handleStatusUpdate(applicant.application_id, 'shortlisted')}
                  disabled={updateStatusMutation.isLoading}
                >
                  <UserCheck size={18} />
                  Shortlist
                </button>
              )}
              {applicant.application_status !== 'rejected' && (
                <button
                  className="btn btn-danger"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to reject this application?')) {
                      handleStatusUpdate(applicant.application_id, 'rejected');
                    }
                  }}
                  disabled={updateStatusMutation.isLoading}
                >
                  <XCircle size={18} />
                  Reject
                </button>
              )}
              {applicant.application_status === 'shortlisted' && (
                <button
                  className="btn btn-primary"
                  onClick={() => handleStatusUpdate(applicant.application_id, 'hired')}
                  disabled={updateStatusMutation.isLoading}
                >
                  <CheckCircle size={18} />
                  Mark Hired
                </button>
              )}
            </div>
          )}
          <button className="btn btn-outline" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApplicantDetail;

