import React, { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi } from '../api/jobs';
import { useAuth } from '../context/AuthContext';
import { X } from 'lucide-react';
import toast from 'react-hot-toast';
import './Modal.css';

const JobModal = ({ job, onClose }) => {
  const { user, isRecruiter } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    salary_range: '',
    status: 'active',
  });

  const queryClient = useQueryClient();

  useEffect(() => {
    if (job) {
      setFormData({
        title: job.title || '',
        description: job.description || '',
        requirements: job.requirements || '',
        location: job.location || '',
        salary_range: job.salary_range || '',
        status: job.status || 'active',
      });
    }
  }, [job]);

  const mutation = useMutation({
    mutationFn: (data) => {
      if (job) {
        return jobsApi.update(job.id, data);
      }
      return jobsApi.create(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['jobs']);
      queryClient.invalidateQueries(['analytics']); // Refresh analytics when job is created/updated
      toast.success(job ? 'Job updated successfully' : 'Job created successfully');
      onClose();
    },
    onError: (error) => {
      console.error('Job creation error:', error);
      console.error('Error response:', error?.response);
      console.error('Error status:', error?.response?.status);
      console.error('Error data:', error?.response?.data);
      
      let errorMessage = 'Failed to save job';
      
      if (error?.response?.status === 403) {
        errorMessage = 'Access denied. You must be logged in as a recruiter to create jobs.';
      } else if (error?.response?.status === 401) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (error?.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error?.message) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Debug: Check user role and token
    console.log('Submitting job:', formData);
    console.log('Current user:', user);
    console.log('Is recruiter:', isRecruiter);
    console.log('Token:', localStorage.getItem('token') ? 'Present' : 'Missing');
    
    // Verify user is recruiter before submitting
    if (!isRecruiter) {
      toast.error('Only recruiters can create jobs. Please log in as a recruiter.');
      return;
    }
    
    mutation.mutate(formData);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{job ? 'Edit Job' : 'Create New Job'}</h2>
          <button className="btn-icon" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-group">
            <label>Job Title *</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="input"
              required
            />
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="textarea"
              required
              rows="5"
            />
          </div>

          <div className="form-group">
            <label>Requirements</label>
            <textarea
              name="requirements"
              value={formData.requirements}
              onChange={handleChange}
              className="textarea"
              rows="4"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Location</label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                className="input"
                placeholder="e.g., Remote, New York, NY"
              />
            </div>

            <div className="form-group">
              <label>Salary Range</label>
              <input
                type="text"
                name="salary_range"
                value={formData.salary_range}
                onChange={handleChange}
                className="input"
                placeholder="e.g., $80k - $120k"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Status</label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="input"
            >
              <option value="active">Active</option>
              <option value="draft">Draft</option>
              <option value="closed">Closed</option>
            </select>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={mutation.isLoading}>
              {mutation.isLoading ? 'Saving...' : job ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default JobModal;

