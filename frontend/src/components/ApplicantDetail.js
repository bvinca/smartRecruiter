import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Mail, Phone, Briefcase, GraduationCap, Sparkles, MessageSquare, UserCheck, XCircle, CheckCircle, RefreshCw, FileText, HelpCircle, TrendingUp, ExternalLink } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Cell } from 'recharts';
import { applicationsApi } from '../api/applications';
import { applicantsApi } from '../api/applicants';
import { enhancementApi } from '../api/enhancement';
import { explanationApi } from '../api/explanation';
import { visualizationApi } from '../api/visualization';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './Modal.css';
import './ApplicantDetail.css';

const ApplicantDetail = ({ applicant, onClose }) => {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const isRecruiter = user?.role === 'recruiter';
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [skillGap, setSkillGap] = useState(null);
  const [chartView, setChartView] = useState('bar'); // 'bar' or 'radar'
  // Local state to hold updated applicant data
  const [localApplicant, setLocalApplicant] = useState(applicant);
  
  // Update local applicant when prop changes
  React.useEffect(() => {
    setLocalApplicant(applicant);
  }, [applicant]);

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

  const regenerateQuestionsMutation = useMutation({
    mutationFn: ({ applicantId, feedback, numQuestions }) => 
      applicantsApi.regenerateQuestions(applicantId, feedback, numQuestions),
    onSuccess: (response) => {
      const data = response.data || response;
      if (data.success && data.questions) {
        // Update local applicant state with new questions immediately
        setLocalApplicant(prev => ({
          ...prev,
          interview_questions: data.questions
        }));
        
        // Invalidate queries to refresh parent component data
        queryClient.invalidateQueries(['applications']);
        queryClient.invalidateQueries(['applicants']);
        
        toast.success(data.message || 'Questions regenerated successfully');
        setShowFeedbackForm(false);
        setFeedback('');
      } else {
        toast.error(data.message || 'Failed to regenerate questions');
      }
    },
    onError: (error) => {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to regenerate questions';
      toast.error(errorMsg);
    },
  });

  const analyzeResumeMutation = useMutation({
    mutationFn: () => enhancementApi.analyzeResume(
      localApplicant.resume_text || '',
      localApplicant.job?.description || '',
      localApplicant.job?.requirements || ''
    ),
    onSuccess: (response) => {
      setResumeAnalysis(response.data);
      toast.success('Resume analysis complete!');
    },
    onError: (error) => {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to analyze resume';
      toast.error(errorMsg);
    },
  });

  const explainMutation = useMutation({
    mutationFn: () => explanationApi.explainScoring(
      localApplicant.id,
      localApplicant.job_id
    ),
    onSuccess: (response) => {
      setExplanation(response.data);
      toast.success('Scoring explanation generated!');
    },
    onError: (error) => {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate explanation';
      toast.error(errorMsg);
    },
  });

  const analyzeSkillGapMutation = useMutation({
    mutationFn: () => {
      const jobId = localApplicant.job_id || localApplicant.job?.id;
      if (!jobId) {
        throw new Error('Job ID is required for skill gap analysis');
      }
      return visualizationApi.analyzeSkillGap(jobId, localApplicant.id);
    },
    onSuccess: (response) => {
      setSkillGap(response.data);
      toast.success('Skill gap analysis complete!');
    },
    onError: (error) => {
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to analyze skill gap';
      toast.error(errorMsg);
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
          <h2>{localApplicant.first_name} {localApplicant.last_name}</h2>
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
                <span>{localApplicant.email}</span>
              </div>
              {localApplicant.phone && (
                <div className="info-item">
                  <Phone size={18} />
                  <span>{localApplicant.phone}</span>
                </div>
              )}
            </div>
          </div>

          {localApplicant.job && (
            <div className="detail-section">
              <h3>Job Applied For: {localApplicant.job.title}</h3>
              <p style={{ fontSize: '14px', marginBottom: '8px' }}>{localApplicant.job.description}</p>
              {localApplicant.job.requirements && (
                <div style={{ marginTop: '10px' }}>
                  <strong style={{ fontSize: '13px' }}>Requirements:</strong>
                  <p style={{ fontSize: '14px', marginTop: '4px' }}>{localApplicant.job.requirements}</p>
                </div>
              )}
              {isRecruiter && (
                <a 
                  href={`/recruiter/jobs/${localApplicant.job.id}`}
                  className="btn btn-outline btn-sm"
                  style={{ marginTop: '10px', display: 'inline-flex', alignItems: 'center', gap: '6px', textDecoration: 'none' }}
                >
                  View Job Post
                </a>
              )}
            </div>
          )}

          {localApplicant.overall_score > 0 && (
            <div className="detail-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3>Scoring</h3>
                <button 
                  className="btn btn-sm btn-outline" 
                  onClick={() => explainMutation.mutate()}
                  disabled={explainMutation.isLoading}
                  style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '6px 12px' }}
                >
                  <HelpCircle size={14} />
                  {explainMutation.isLoading ? 'Explaining...' : 'Explain Scores'}
                </button>
              </div>
              <div className="scores-grid">
                <div className="score-card">
                  <span className="score-label">Overall Score</span>
                  <span className="score-number">{localApplicant.overall_score.toFixed(1)}%</span>
                </div>
                <div className="score-card">
                  <span className="score-label">Match Score</span>
                  <span className="score-number">{localApplicant.match_score.toFixed(1)}%</span>
                </div>
                <div className="score-card">
                  <span className="score-label">Skill Score</span>
                  <span className="score-number">{localApplicant.skill_score.toFixed(1)}%</span>
                </div>
                <div className="score-card">
                  <span className="score-label">Experience Score</span>
                  <span className="score-number">{localApplicant.experience_score.toFixed(1)}%</span>
                </div>
              </div>
              {explanation && (
                <div className="score-explanation" style={{ 
                  marginTop: '15px', 
                  padding: '15px', 
                  backgroundColor: '#f8f9fa', 
                  borderRadius: '8px',
                  border: '1px solid #dee2e6'
                }}>
                  <h4 style={{ marginTop: 0, marginBottom: '10px' }}>Score Explanation</h4>
                  <div className="explanation-breakdown">
                    {explanation.skills_explanation && (
                      <div style={{ marginBottom: '12px' }}>
                        <strong>Skills Score ({explanation.score_breakdown?.skills?.score || localApplicant.skill_score?.toFixed(1)}%):</strong>
                        <p style={{ margin: '4px 0', fontSize: '14px' }}>{explanation.skills_explanation}</p>
                      </div>
                    )}
                    {explanation.experience_explanation && (
                      <div style={{ marginBottom: '12px' }}>
                        <strong>Experience Score ({explanation.score_breakdown?.experience?.score || localApplicant.experience_score?.toFixed(1)}%):</strong>
                        <p style={{ margin: '4px 0', fontSize: '14px' }}>{explanation.experience_explanation}</p>
                      </div>
                    )}
                    {explanation.education_explanation && (
                      <div style={{ marginBottom: '12px' }}>
                        <strong>Education Score ({explanation.score_breakdown?.education?.score || localApplicant.education_score?.toFixed(1)}%):</strong>
                        <p style={{ margin: '4px 0', fontSize: '14px' }}>{explanation.education_explanation}</p>
                      </div>
                    )}
                  </div>
                  {explanation.overall_summary && (
                    <div className="overall-summary" style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #dee2e6' }}>
                      <strong>Overall Summary:</strong>
                      <p style={{ margin: '4px 0', fontSize: '14px' }}>{explanation.overall_summary}</p>
                    </div>
                  )}
                  {explanation.strengths && explanation.strengths.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                      <strong>Strengths:</strong>
                      <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '14px' }}>
                        {explanation.strengths.map((strength, idx) => (
                          <li key={idx}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {explanation.weaknesses && explanation.weaknesses.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                      <strong>Areas for Improvement:</strong>
                      <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '14px' }}>
                        {explanation.weaknesses.map((weakness, idx) => (
                          <li key={idx}>{weakness}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {localApplicant.skills && localApplicant.skills.length > 0 && (
            <div className="detail-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3>Skills</h3>
                {(localApplicant.job_id || localApplicant.job?.id) && (
                  <button 
                    className="btn btn-sm btn-outline" 
                    onClick={() => analyzeSkillGapMutation.mutate()}
                    disabled={analyzeSkillGapMutation.isLoading}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '6px 12px' }}
                  >
                    <TrendingUp size={14} />
                    {analyzeSkillGapMutation.isLoading ? 'Analyzing...' : 'Analyze Skill Gap'}
                  </button>
                )}
              </div>
              <div className="skills-list">
                {localApplicant.skills.map((skill, idx) => (
                  <span key={idx} className="skill-badge">{skill}</span>
                ))}
              </div>
              {skillGap && (
                <div className="skill-gap-visualization" style={{ 
                  marginTop: '15px', 
                  padding: '15px', 
                  backgroundColor: '#f0f9ff', 
                  borderRadius: '8px',
                  border: '1px solid #bae6fd'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                    <h4 style={{ margin: 0, color: '#0369a1' }}>Skill Gap Analysis</h4>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        className={`btn btn-sm ${chartView === 'bar' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setChartView('bar')}
                        style={{ fontSize: '11px', padding: '4px 8px' }}
                      >
                        Bar Chart
                      </button>
                      <button
                        className={`btn btn-sm ${chartView === 'radar' ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => setChartView('radar')}
                        style={{ fontSize: '11px', padding: '4px 8px' }}
                      >
                        Radar Chart
                      </button>
                    </div>
                  </div>
                  
                  <div className="overall-alignment" style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#fff', borderRadius: '6px' }}>
                    <p style={{ margin: '4px 0', fontWeight: '600', fontSize: '15px' }}>
                      Overall Alignment: <strong style={{ color: '#0369a1' }}>{skillGap.overall_alignment}%</strong>
                    </p>
                    <p style={{ margin: '4px 0', fontSize: '13px', color: '#666' }}>
                      Matched Skills: {skillGap.matched_skills} / {skillGap.total_job_skills}
                    </p>
                  </div>
                  
                  {skillGap.skill_matches && Object.keys(skillGap.skill_matches).length > 0 && (
                    <div className="skill-matches" style={{ marginBottom: '15px' }}>
                      <h5 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px' }}>Skill Similarity Visualization:</h5>
                      
                      {/* Visual Chart */}
                      <div style={{ marginBottom: '20px', backgroundColor: '#fff', padding: '15px', borderRadius: '6px' }}>
                        {chartView === 'bar' ? (
                          <ResponsiveContainer width="100%" height={Math.max(300, Object.keys(skillGap.skill_matches).length * 40)}>
                            <BarChart
                              data={Object.entries(skillGap.skill_matches)
                                .map(([skill, score]) => ({
                                  skill: skill.length > 15 ? skill.substring(0, 15) + '...' : skill,
                                  'Similarity %': parseFloat(score),
                                  fullSkill: skill
                                }))
                                .sort((a, b) => b['Similarity %'] - a['Similarity %'])}
                              layout="vertical"
                              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis type="number" domain={[0, 100]} />
                              <YAxis 
                                dataKey="skill" 
                                type="category" 
                                width={120}
                                tick={{ fontSize: 12 }}
                              />
                              <Tooltip 
                                formatter={(value, name) => [`${value.toFixed(1)}%`, 'Similarity']}
                                labelFormatter={(label, payload) => payload && payload[0] ? payload[0].payload.fullSkill : label}
                              />
                              <Bar 
                                dataKey="Similarity %" 
                                radius={[0, 4, 4, 0]}
                              >
                                {Object.entries(skillGap.skill_matches)
                                  .sort(([, a], [, b]) => b - a)
                                  .map(([skill, score], index) => {
                                    const color = score >= 70 ? '#10b981' : score >= 30 ? '#f59e0b' : '#ef4444';
                                    return <Cell key={`cell-${index}`} fill={color} />;
                                  })}
                              </Bar>
                            </BarChart>
                          </ResponsiveContainer>
                        ) : (
                          <ResponsiveContainer width="100%" height={400}>
                            <RadarChart
                              data={Object.entries(skillGap.skill_matches).map(([skill, score]) => ({
                                skill: skill.length > 12 ? skill.substring(0, 12) + '...' : skill,
                                similarity: parseFloat(score),
                                fullSkill: skill
                              }))}
                            >
                              <PolarGrid />
                              <PolarAngleAxis 
                                dataKey="skill" 
                                tick={{ fontSize: 11 }}
                              />
                              <PolarRadiusAxis 
                                angle={90} 
                                domain={[0, 100]} 
                                tick={{ fontSize: 10 }}
                              />
                              <Radar
                                name="Similarity"
                                dataKey="similarity"
                                stroke="#3b82f6"
                                fill="#3b82f6"
                                fillOpacity={0.6}
                              />
                              <Tooltip 
                                formatter={(value, name) => [`${value.toFixed(1)}%`, 'Similarity']}
                                labelFormatter={(label, payload) => payload && payload[0] ? payload[0].payload.fullSkill : label}
                              />
                            </RadarChart>
                          </ResponsiveContainer>
                        )}
                      </div>
                      
                      {/* Detailed Table View */}
                      <div style={{ marginTop: '15px' }}>
                        <h6 style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>Detailed Breakdown:</h6>
                        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                          {Object.entries(skillGap.skill_matches)
                            .sort(([, a], [, b]) => b - a)
                            .map(([skill, score]) => (
                              <div key={skill} className="skill-match-item" style={{ marginBottom: '8px', padding: '8px', backgroundColor: '#fff', borderRadius: '4px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                  <span style={{ fontSize: '13px', fontWeight: '500' }}>{skill}</span>
                                  <span style={{ fontSize: '13px', fontWeight: '600', color: score >= 70 ? '#10b981' : score >= 30 ? '#f59e0b' : '#ef4444' }}>
                                    {score}%
                                  </span>
                                </div>
                                <div className="skill-bar" style={{ 
                                  width: '100%', 
                                  height: '6px', 
                                  backgroundColor: '#e5e7eb', 
                                  borderRadius: '3px',
                                  overflow: 'hidden'
                                }}>
                                  <div 
                                    className="skill-fill" 
                                    style={{ 
                                      width: `${score}%`, 
                                      height: '100%',
                                      backgroundColor: score >= 70 ? '#10b981' : score >= 30 ? '#f59e0b' : '#ef4444',
                                      transition: 'width 0.3s ease'
                                    }}
                                  />
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {skillGap.strong_matches && skillGap.strong_matches.length > 0 && (
                    <div style={{ marginBottom: '12px', padding: '10px', backgroundColor: '#d1fae5', borderRadius: '6px' }}>
                      <strong style={{ color: '#065f46', fontSize: '13px' }}>✓ Strong Matches (≥70%):</strong>
                      <div style={{ marginTop: '6px' }}>
                        {skillGap.strong_matches.map((skill, idx) => (
                          <span key={idx} className="skill-badge" style={{ backgroundColor: '#10b981', color: '#fff', marginRight: '6px', marginBottom: '4px' }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {skillGap.weak_matches && skillGap.weak_matches.length > 0 && (
                    <div style={{ marginBottom: '12px', padding: '10px', backgroundColor: '#fef3c7', borderRadius: '6px' }}>
                      <strong style={{ color: '#92400e', fontSize: '13px' }}>⚠ Partial Matches (30-70%):</strong>
                      <div style={{ marginTop: '6px' }}>
                        {skillGap.weak_matches.map((skill, idx) => (
                          <span key={idx} className="skill-badge" style={{ backgroundColor: '#f59e0b', color: '#fff', marginRight: '6px', marginBottom: '4px' }}>
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {skillGap.missing_skills && skillGap.missing_skills.length > 0 && (
                    <div className="missing-skills" style={{ padding: '10px', backgroundColor: '#fee2e2', borderRadius: '6px' }}>
                      <strong style={{ color: '#991b1b', fontSize: '13px' }}>✗ Missing Skills (&lt;30%):</strong>
                      <ul style={{ margin: '6px 0', paddingLeft: '20px', fontSize: '13px' }}>
                        {skillGap.missing_skills.map((skill, idx) => (
                          <li key={idx} style={{ marginBottom: '4px' }}>{skill}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {localApplicant.work_experience && localApplicant.work_experience.length > 0 && (
            <div className="detail-section">
              <h3>
                <Briefcase size={20} />
                Work Experience
              </h3>
              {localApplicant.work_experience.map((exp, idx) => (
                <div key={idx} className="experience-item">
                  <h4>{exp.title}</h4>
                  <p className="company">{exp.company}</p>
                  {exp.duration && <p className="duration">{exp.duration}</p>}
                  {exp.description && <p className="description">{exp.description}</p>}
                </div>
              ))}
            </div>
          )}

          {localApplicant.education && localApplicant.education.length > 0 && (
            <div className="detail-section">
              <h3>
                <GraduationCap size={20} />
                Education
              </h3>
              {localApplicant.education.map((edu, idx) => (
                <div key={idx} className="education-item">
                  <h4>{edu.degree}</h4>
                  <p>{edu.institution}</p>
                  {edu.year && <p className="year">{edu.year}</p>}
                </div>
              ))}
            </div>
          )}

          {localApplicant.ai_summary && localApplicant.ai_summary !== "Unable to generate AI summary at this time." ? (
            <div className="detail-section ai-section">
              <h3>
                <Sparkles size={20} />
                AI Summary
              </h3>
              <p className="ai-text">{localApplicant.ai_summary}</p>
            </div>
          ) : localApplicant.resume_text ? (
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

          {localApplicant.ai_feedback && (
            <div className="detail-section ai-section">
              <h3>AI Feedback</h3>
              <p className="ai-text">{localApplicant.ai_feedback}</p>
            </div>
          )}

          {localApplicant.interview_questions && localApplicant.interview_questions.length > 0 && (
            <div className="detail-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3>
                  <MessageSquare size={20} />
                  Suggested Interview Questions
                </h3>
                {isRecruiter && (
                  <button
                    className="btn btn-sm btn-outline"
                    onClick={() => setShowFeedbackForm(!showFeedbackForm)}
                    style={{ fontSize: '12px', padding: '6px 12px' }}
                  >
                    {showFeedbackForm ? 'Cancel' : 'Provide Feedback'}
                  </button>
                )}
              </div>
              
              {showFeedbackForm && isRecruiter && (
                <div style={{ 
                  marginBottom: '15px', 
                  padding: '15px', 
                  backgroundColor: '#f8f9fa', 
                  borderRadius: '8px',
                  border: '1px solid #dee2e6'
                }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
                    Your Feedback on Current Questions:
                  </label>
                  <textarea
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    placeholder="e.g., 'Make questions more technical', 'Focus on leadership experience', 'Ask about specific projects'..."
                    rows={4}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ced4da',
                      borderRadius: '4px',
                      fontSize: '14px',
                      fontFamily: 'inherit',
                      resize: 'vertical'
                    }}
                  />
                  <div style={{ marginTop: '10px', display: 'flex', gap: '10px' }}>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => {
                        if (!feedback.trim()) {
                          toast.error('Please provide feedback before regenerating');
                          return;
                        }
                        regenerateQuestionsMutation.mutate({
                          applicantId: localApplicant.id,
                          feedback: feedback.trim(),
                          numQuestions: localApplicant.interview_questions.length
                        });
                      }}
                      disabled={regenerateQuestionsMutation.isLoading || !feedback.trim()}
                      style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                    >
                      <RefreshCw size={16} className={regenerateQuestionsMutation.isLoading ? 'spinning' : ''} />
                      {regenerateQuestionsMutation.isLoading ? 'Regenerating...' : 'Regenerate Questions'}
                    </button>
                    <button
                      className="btn btn-outline btn-sm"
                      onClick={() => {
                        setShowFeedbackForm(false);
                        setFeedback('');
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
              
              <ol className="questions-list">
                {localApplicant.interview_questions.map((question, idx) => (
                  <li key={idx} className="question-item">{question}</li>
                ))}
              </ol>
            </div>
          )}

          {localApplicant.resume_text && (
            <div className="detail-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3>Resume Text</h3>
                <button 
                  className="btn btn-sm btn-outline" 
                  onClick={() => analyzeResumeMutation.mutate()}
                  disabled={analyzeResumeMutation.isLoading}
                  style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '6px 12px' }}
                >
                  <FileText size={14} />
                  {analyzeResumeMutation.isLoading ? 'Analyzing...' : 'Analyze Resume'}
                </button>
              </div>
              <div className="resume-text">
                <pre>{localApplicant.resume_text.substring(0, 2000)}...</pre>
              </div>
              {resumeAnalysis && (
                <div className="resume-analysis" style={{ 
                  marginTop: '15px', 
                  padding: '15px', 
                  backgroundColor: '#fef3c7', 
                  borderRadius: '8px',
                  border: '1px solid #fde68a'
                }}>
                  <h4 style={{ marginTop: 0, color: '#92400e' }}>Resume Analysis</h4>
                  {resumeAnalysis.summary_feedback && (
                    <p style={{ marginBottom: '12px', fontSize: '14px', whiteSpace: 'pre-wrap' }}>
                      {resumeAnalysis.summary_feedback}
                    </p>
                  )}
                  
                  {resumeAnalysis.strengths && resumeAnalysis.strengths.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#10b981' }}>Strengths:</strong>
                      <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '14px' }}>
                        {resumeAnalysis.strengths.map((strength, idx) => (
                          <li key={idx}>{strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {resumeAnalysis.weaknesses && resumeAnalysis.weaknesses.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#ef4444' }}>Areas for Improvement:</strong>
                      <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '14px' }}>
                        {resumeAnalysis.weaknesses.map((weakness, idx) => (
                          <li key={idx}>{weakness}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {resumeAnalysis.missing_skills && resumeAnalysis.missing_skills.length > 0 && (
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#f59e0b' }}>Missing Skills:</strong>
                      <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '14px' }}>
                        {resumeAnalysis.missing_skills.map((skill, idx) => (
                          <li key={idx}>{skill}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {resumeAnalysis.keyword_suggestions && resumeAnalysis.keyword_suggestions.length > 0 && (
                    <div>
                      <strong style={{ color: '#3b82f6' }}>Keyword Suggestions:</strong>
                      <div style={{ marginTop: '4px' }}>
                        {resumeAnalysis.keyword_suggestions.map((keyword, idx) => (
                          <span key={idx} className="skill-badge" style={{ backgroundColor: '#dbeafe', color: '#1e40af', marginRight: '6px', marginBottom: '4px' }}>
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="modal-actions">
          {/* Status Update Buttons (Recruiter Actions) */}
          {localApplicant.application_id && (
            <div className="status-actions-modal">
              {localApplicant.application_status !== 'shortlisted' && localApplicant.application_status !== 'hired' && (
                <button
                  className="btn btn-success"
                  onClick={() => handleStatusUpdate(localApplicant.application_id, 'shortlisted')}
                  disabled={updateStatusMutation.isLoading}
                >
                  <UserCheck size={18} />
                  Shortlist
                </button>
              )}
              {localApplicant.application_status !== 'rejected' && (
                <button
                  className="btn btn-danger"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to reject this application?')) {
                      handleStatusUpdate(localApplicant.application_id, 'rejected');
                    }
                  }}
                  disabled={updateStatusMutation.isLoading}
                >
                  <XCircle size={18} />
                  Reject
                </button>
              )}
              {localApplicant.application_status === 'shortlisted' && (
                <button
                  className="btn btn-primary"
                  onClick={() => handleStatusUpdate(localApplicant.application_id, 'hired')}
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

