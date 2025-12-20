import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams, useParams } from 'react-router-dom';
import { applicantsApi } from '../api/applicants';
import { applicationsApi } from '../api/applications';
import { jobsApi } from '../api/jobs';
import { rankingApi } from '../api/ranking';
import { Upload, TrendingUp, FileText, Sparkles, Download, Award, MessageSquare, CheckCircle, XCircle, UserCheck } from 'lucide-react';
import toast from 'react-hot-toast';
import UploadModal from '../components/UploadModal';
import ApplicantDetail from '../components/ApplicantDetail';
import './Applicants.css';

const Applicants = () => {
  const { id } = useParams(); // Get job ID from route parameter (/recruiter/jobs/:id/applicants)
  const [searchParams] = useSearchParams();
  const jobIdFromQuery = searchParams.get('job_id'); // Get from query parameter (?job_id=...)
  const jobId = id || jobIdFromQuery; // Use route param first, then query param
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [showRanking, setShowRanking] = useState(false);
  const queryClient = useQueryClient();

  // Get applications which include applicant data
  const { data: applications = [], isLoading: appsLoading } = useQuery({
    queryKey: ['applications', jobId],
    queryFn: () => applicationsApi.getAll().then(res => res.data || res),
  });

  // Also get applicants directly (for backward compatibility with upload CV feature)
  const { data: directApplicants = [], isLoading: applicantsLoading } = useQuery({
    queryKey: ['applicants', jobId],
    queryFn: () => applicantsApi.getAll(jobId).then(res => res.data || res),
  });

  // Filter applications by job if jobId is provided
  const filteredApplications = jobId 
    ? applications.filter(app => app.job_id === parseInt(jobId))
    : applications;

  // Extract applicants from applications (these have AI summaries and interview questions)
  const applicantsFromApplications = filteredApplications
    .filter(app => app.applicant) // Only those with parsed resume data
    .map(app => ({
      ...app.applicant,
      application_id: app.id,
      application_status: app.status,
      job: app.job,
      has_resume: true
    }));

  // Also include applications without resume data (just user info)
  const applicationsWithoutResume = filteredApplications
    .filter(app => !app.applicant && app.user)
    .map(app => ({
      id: `user_${app.user_id}`, // Unique ID for users without applicant record
      first_name: app.user.first_name || 'Unknown',
      last_name: app.user.last_name || '',
      email: app.user.email,
      phone: app.user.phone || null,
      skills: [],
      experience_years: 0,
      education: [],
      work_experience: [],
      overall_score: 0,
      match_score: 0,
      skill_score: 0,
      experience_score: 0,
      education_score: 0,
      ai_summary: null,
      ai_feedback: null,
      interview_questions: [],
      application_id: app.id,
      application_status: app.status,
      job: app.job,
      has_resume: false,
      user_id: app.user_id
    }));

  // Combine applicants from applications and direct applicants (avoid duplicates)
  const applicantIds = new Set(applicantsFromApplications.map(a => a.id));
  const uniqueDirectApplicants = directApplicants.filter(a => !applicantIds.has(a.id));
  const applicants = [...applicantsFromApplications, ...applicationsWithoutResume, ...uniqueDirectApplicants];

  const isLoading = appsLoading || applicantsLoading;

  const { data: jobs = [] } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.getAll().then(res => res.data),
  });

  const { data: rankedCandidates = [] } = useQuery({
    queryKey: ['rankedCandidates', jobId],
    queryFn: () => rankingApi.getRankedCandidates(jobId).then(res => res.data),
    enabled: showRanking && !!jobId,
  });

  const scoreMutation = useMutation({
    mutationFn: (id) => applicantsApi.score(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['applicants']);
      toast.success('Applicant scored successfully');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to score applicant');
    },
  });

  const summaryMutation = useMutation({
    mutationFn: (id) => applicantsApi.generateSummary(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['applicants']);
      queryClient.invalidateQueries(['applications']); // Also invalidate applications
      toast.success('AI summary generated successfully');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to generate summary');
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ applicationId, status, notes }) => applicationsApi.update(applicationId, { status, notes }),
    onSuccess: () => {
      queryClient.invalidateQueries(['applications']);
      queryClient.invalidateQueries(['applicants']);
      toast.success('Application status updated successfully');
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

  const handleScore = (applicantId) => {
    // Only allow scoring for applicants with resume data (integer IDs)
    if (typeof applicantId !== 'number') {
      toast.error('Cannot score applicant without resume data');
      return;
    }
    scoreMutation.mutate(applicantId);
  };

  const handleGenerateSummary = (applicantId) => {
    // Only allow summary generation for applicants with resume data (integer IDs)
    if (typeof applicantId !== 'number') {
      toast.error('Cannot generate summary for applicant without resume data');
      return;
    }
    summaryMutation.mutate(applicantId);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { label: 'Pending', class: 'badge-info' },
      reviewing: { label: 'Reviewing', class: 'badge-warning' },
      shortlisted: { label: 'Shortlisted', class: 'badge-success' },
      rejected: { label: 'Rejected', class: 'badge-danger' },
      hired: { label: 'Hired', class: 'badge-success' },
    };
    const config = statusConfig[status] || statusConfig.pending;
    return <span className={`badge ${config.class}`}>{config.label}</span>;
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading"></div>
        <p>Loading applicants...</p>
      </div>
    );
  }

  return (
    <div className="applicants-page">
      <div className="page-header">
        <div>
          <h1>Applicants</h1>
          <p>Review and manage candidate applications</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsUploadModalOpen(true)}>
          <Upload size={20} />
          Upload CV
        </button>
      </div>

      {jobId && (
        <div className="filter-info">
          <span>Filtered by job: {jobs.find(j => j.id === parseInt(jobId))?.title || 'Unknown'}</span>
          <div>
            <button
              className="btn btn-outline btn-sm"
              onClick={() => setShowRanking(!showRanking)}
            >
              <Award size={16} />
              {showRanking ? 'Hide' : 'Show'} Ranking
            </button>
            <a href="/applicants" style={{ marginLeft: '1rem' }}>Clear filter</a>
          </div>
        </div>
      )}

      {showRanking && jobId && rankedCandidates.length > 0 && (
        <div className="ranking-section">
          <h2>
            <Award size={24} />
            Ranked Candidates
          </h2>
          <div className="ranked-list">
            {rankedCandidates.map((candidate, idx) => (
              <div key={candidate.applicant_id} className="ranked-item">
                <div className="rank-number">#{candidate.rank}</div>
                <div className="rank-info">
                  <h4>{candidate.name}</h4>
                  <p>{candidate.email}</p>
                  <div className="rank-scores">
                    <span>Match: {candidate.match_score.toFixed(1)}%</span>
                    <span>Overall: {candidate.overall_score.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="rank-actions">
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => {
                      const applicant = applicants.find(a => a.id === candidate.applicant_id);
                      if (applicant) setSelectedApplicant(applicant);
                    }}
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="applicants-list">
        {applicants.map((applicant) => (
          <div key={applicant.id} className="applicant-card">
            <div className="applicant-header">
              <div>
                <h3>{applicant.first_name} {applicant.last_name}</h3>
                <p className="applicant-email">{applicant.email}</p>
                {applicant.job && (
                  <p className="applicant-job">Applied for: {applicant.job.title}</p>
                )}
              </div>
              {getStatusBadge(applicant.application_status || applicant.status)}
            </div>

            {applicant.overall_score > 0 && applicant.has_resume !== false && (
              <div className="score-section">
                <div className="score-display">
                  <TrendingUp size={20} />
                  <span className="score-value">{(applicant.overall_score || 0).toFixed(1)}%</span>
                  <span className="score-label">Match Score</span>
                </div>
                <div className="score-breakdown">
                  <div className="score-item">
                    <span>Skills</span>
                    <span>{(applicant.skill_score || 0).toFixed(1)}%</span>
                  </div>
                  <div className="score-item">
                    <span>Experience</span>
                    <span>{(applicant.experience_score || 0).toFixed(1)}%</span>
                  </div>
                  <div className="score-item">
                    <span>Match</span>
                    <span>{(applicant.match_score || 0).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            )}

            {applicant.skills && applicant.skills.length > 0 && (
              <div className="skills-section">
                {applicant.skills.slice(0, 5).map((skill, idx) => (
                  <span key={idx} className="skill-tag">{skill}</span>
                ))}
                {applicant.skills.length > 5 && (
                  <span className="skill-tag">+{applicant.skills.length - 5} more</span>
                )}
              </div>
            )}

                {/* Show AI Summary Preview */}
                {applicant.ai_summary && applicant.ai_summary !== "Unable to generate AI summary at this time." && (
                  <div className="ai-summary-preview">
                    <div className="ai-badge">
                      <Sparkles size={14} />
                      <span>AI Summary</span>
                    </div>
                    <p className="summary-text">{applicant.ai_summary.substring(0, 150)}...</p>
                  </div>
                )}

            {/* Show Interview Questions Count */}
            {applicant.interview_questions && applicant.interview_questions.length > 0 && (
              <div className="interview-questions-badge">
                <MessageSquare size={14} />
                <span>{applicant.interview_questions.length} Interview Questions Generated</span>
              </div>
            )}

            {/* Show notice if no resume uploaded */}
            {applicant.has_resume === false && (
              <div className="no-resume-notice">
                <FileText size={14} />
                <span>No resume uploaded - Basic application only</span>
              </div>
            )}

            <div className="applicant-actions">
              {/* Status Update Buttons (Recruiter Actions) */}
              {applicant.application_id && (
                <div className="status-actions">
                  {applicant.application_status !== 'shortlisted' && applicant.application_status !== 'hired' && (
                    <button
                      className="btn btn-success btn-sm"
                      onClick={() => handleStatusUpdate(applicant.application_id, 'shortlisted')}
                      disabled={updateStatusMutation.isLoading}
                      title="Shortlist this candidate"
                    >
                      <UserCheck size={16} />
                      Shortlist
                    </button>
                  )}
                  {applicant.application_status !== 'rejected' && (
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => {
                        if (window.confirm('Are you sure you want to reject this application?')) {
                          handleStatusUpdate(applicant.application_id, 'rejected');
                        }
                      }}
                      disabled={updateStatusMutation.isLoading}
                      title="Reject this application"
                    >
                      <XCircle size={16} />
                      Reject
                    </button>
                  )}
                  {applicant.application_status === 'shortlisted' && (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => handleStatusUpdate(applicant.application_id, 'hired')}
                      disabled={updateStatusMutation.isLoading}
                      title="Mark as hired"
                    >
                      <CheckCircle size={16} />
                      Mark Hired
                    </button>
                  )}
                </div>
              )}
              
              {/* Only show score/summary buttons for applicants with resume data (integer IDs) */}
              {applicant.has_resume !== false && typeof applicant.id === 'number' && (
                <>
                  {applicant.overall_score === 0 && (
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleScore(applicant.id)}
                      disabled={scoreMutation.isLoading}
                    >
                      <TrendingUp size={16} />
                      Calculate Score
                    </button>
                  )}
                  {!applicant.ai_summary && (
                    <button
                      className="btn btn-outline"
                      onClick={() => handleGenerateSummary(applicant.id)}
                      disabled={summaryMutation.isLoading}
                    >
                      <Sparkles size={16} />
                      Generate AI Summary
                    </button>
                  )}
                </>
              )}
              <button
                className="btn btn-outline"
                onClick={() => setSelectedApplicant(applicant)}
              >
                <FileText size={16} />
                View Details
              </button>
              {applicant.resume_file_path && typeof applicant.id === 'number' && (
                <button
                  className="btn btn-outline"
                  onClick={() => {
                    applicantsApi.downloadResume(applicant.id)
                      .then(res => {
                        const url = window.URL.createObjectURL(new Blob([res.data]));
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', `${applicant.first_name}_${applicant.last_name}_resume.${applicant.resume_file_type || 'pdf'}`);
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                      })
                      .catch(() => toast.error('Failed to download resume'));
                  }}
                >
                  <Download size={16} />
                  Download Resume
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {applicants.length === 0 && (
        <div className="empty-state">
          <FileText size={64} />
          <h3>No applicants yet</h3>
          <p>Upload a CV to get started</p>
          <button className="btn btn-primary" onClick={() => setIsUploadModalOpen(true)}>
            Upload CV
          </button>
        </div>
      )}

      {isUploadModalOpen && (
        <UploadModal
          jobs={jobs}
          onClose={() => setIsUploadModalOpen(false)}
        />
      )}

      {selectedApplicant && (
        <ApplicantDetail
          applicant={selectedApplicant}
          onClose={() => setSelectedApplicant(null)}
        />
      )}
    </div>
  );
};

export default Applicants;

