import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Upload, User, Mail, Building, Sparkles, MessageSquare } from 'lucide-react';
import { profileApi } from '../api/profile';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './ApplicantProfile.css';

const ApplicantProfile = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState(null);

  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => profileApi.get().then(res => res.data || res),
  });

  const { data: resumeData, isLoading: resumeLoading, refetch: refetchResume } = useQuery({
    queryKey: ['resume'],
    queryFn: () => profileApi.getResume().then(res => res.data || res),
    enabled: user?.role === 'applicant',
  });

  const updateMutation = useMutation({
    mutationFn: (data) => profileApi.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['profile']);
      toast.success('Profile updated successfully');
    },
    onError: () => {
      toast.error('Failed to update profile');
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (file) => profileApi.uploadResume(file),
    onSuccess: () => {
      queryClient.invalidateQueries(['resume']);
      refetchResume();
      toast.success('Resume uploaded successfully');
      setSelectedFile(null);
    },
    onError: (error) => {
      console.error('Upload error:', error);
      toast.error(error?.response?.data?.detail || 'Failed to upload resume');
    },
  });

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  const handleUpdate = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
      first_name: formData.get('first_name'),
      last_name: formData.get('last_name'),
    };
    updateMutation.mutate(data);
  };

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="applicant-profile">
      <div className="profile-header">
        <h1>My Profile</h1>
        <p>Manage your personal information and resume</p>
      </div>

      <div className="profile-content">
        <div className="profile-section">
          <h2>Personal Information</h2>
          <form onSubmit={handleUpdate}>
            <div className="form-group">
              <label>
                <Mail size={16} />
                Email
              </label>
              <input type="email" value={profile?.email || user?.email} disabled />
            </div>
            <div className="form-group">
              <label>
                <User size={16} />
                First Name
              </label>
              <input
                type="text"
                name="first_name"
                defaultValue={profile?.first_name || ''}
              />
            </div>
            <div className="form-group">
              <label>
                <User size={16} />
                Last Name
              </label>
              <input
                type="text"
                name="last_name"
                defaultValue={profile?.last_name || ''}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={updateMutation.isLoading}>
              {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>

        <div className="profile-section">
          <h2>Resume</h2>
          <div className="resume-upload">
            <div className="upload-area">
              <Upload size={32} />
              <p>Upload your resume (PDF or DOCX)</p>
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileChange}
                style={{ display: 'none' }}
                id="resume-upload"
              />
              <label htmlFor="resume-upload" className="btn btn-secondary">
                Choose File
              </label>
              {selectedFile && (
                <p className="file-name">{selectedFile.name}</p>
              )}
            </div>
            {selectedFile && (
              <button
                className="btn btn-primary"
                onClick={handleUpload}
                disabled={uploadMutation.isLoading}
              >
                {uploadMutation.isLoading ? 'Uploading...' : 'Upload Resume'}
              </button>
            )}
          </div>

          {/* Display Parsed Resume Data */}
          {resumeLoading ? (
            <div className="loading-state">
              <p>Loading resume data...</p>
            </div>
          ) : resumeData?.extracted_data ? (
            <div className="resume-data">
              <h3>Parsed Resume Information</h3>
              <div className="resume-info-grid">
                {resumeData.extracted_data.skills && resumeData.extracted_data.skills.length > 0 && (
                  <div className="info-item">
                    <h4>Skills</h4>
                    <div className="skills-list">
                      {resumeData.extracted_data.skills.map((skill, idx) => (
                        <span key={idx} className="skill-tag">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}
                
                {resumeData.extracted_data.experience_years > 0 && (
                  <div className="info-item">
                    <h4>Experience</h4>
                    <p>{resumeData.extracted_data.experience_years} years</p>
                  </div>
                )}

                {resumeData.extracted_data.education && resumeData.extracted_data.education.length > 0 && (
                  <div className="info-item">
                    <h4>Education</h4>
                    <ul>
                      {resumeData.extracted_data.education.map((edu, idx) => (
                        <li key={idx}>
                          {edu.degree && `${edu.degree} `}
                          {edu.major && `in ${edu.major} `}
                          {edu.institution && `from ${edu.institution}`}
                          {edu.year && ` (${edu.year})`}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {resumeData.extracted_data.work_experience && resumeData.extracted_data.work_experience.length > 0 && (
                  <div className="info-item">
                    <h4>Work Experience</h4>
                    <ul>
                      {resumeData.extracted_data.work_experience.map((exp, idx) => (
                        <li key={idx}>
                          <strong>{exp.title}</strong>
                          {exp.company && ` at ${exp.company}`}
                          {exp.duration && ` (${exp.duration})`}
                          {exp.description && <p className="exp-description">{exp.description}</p>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {resumeData.extracted_data.ai_summary && resumeData.extracted_data.ai_summary !== "Unable to generate AI summary at this time." ? (
                  <div className="info-item ai-section">
                    <h4>
                      <Sparkles size={18} />
                      AI Summary
                    </h4>
                    <p className="ai-text">{resumeData.extracted_data.ai_summary}</p>
                  </div>
                ) : resumeData.extracted_data.resume_text ? (
                  <div className="info-item ai-section">
                    <h4>
                      <Sparkles size={18} />
                      AI Summary
                    </h4>
                    <p className="ai-text ai-unavailable">
                      AI summary is currently unavailable. This may be due to API quota limits. 
                      The resume has been parsed and stored successfully.
                    </p>
                  </div>
                ) : null}

                {resumeData.extracted_data.interview_questions && resumeData.extracted_data.interview_questions.length > 0 && (
                  <div className="info-item">
                    <h4>
                      <MessageSquare size={18} />
                      Suggested Interview Questions
                    </h4>
                    <ol className="questions-list">
                      {resumeData.extracted_data.interview_questions.map((question, idx) => (
                        <li key={idx}>{question}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="no-resume-data">
              <p>No parsed resume data available. Upload a resume when applying to a job to see parsed information.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApplicantProfile;

