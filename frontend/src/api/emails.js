import client from './client';

export const emailsApi = {
  /**
   * Generate an AI email for an applicant
   * @param {number} applicantId - ID of the applicant
   * @param {string} messageType - Type of email (acknowledgment, feedback, rejection, interview_invitation)
   * @param {string} [tone] - Optional tone override
   * @param {object} [additionalContext] - Optional additional context
   * @returns {Promise} Generated email response
   */
  generateForApplicant: async (applicantId, messageType, tone = null, additionalContext = null) => {
    const response = await client.post(`/emails/applicants/${applicantId}/generate`, {
      message_type: messageType,
      tone: tone,
      additional_context: additionalContext
    });
    return response.data;
  },

  /**
   * Generate an AI email for an application
   * @param {number} applicationId - ID of the application
   * @param {string} messageType - Type of email
   * @param {string} [tone] - Optional tone override
   * @param {object} [additionalContext] - Optional additional context
   * @returns {Promise} Generated email response
   */
  generateForApplication: async (applicationId, messageType, tone = null, additionalContext = null) => {
    const response = await client.post(`/emails/applications/${applicationId}/generate`, {
      message_type: messageType,
      tone: tone,
      additional_context: additionalContext
    });
    return response.data;
  },

  /**
   * Get email history for an applicant
   * @param {number} applicantId - ID of the applicant
   * @returns {Promise} List of email history
   */
  getApplicantHistory: async (applicantId) => {
    const response = await client.get(`/emails/applicants/${applicantId}/history`);
    return response.data;
  },

  /**
   * Get email history for a job
   * @param {number} jobId - ID of the job
   * @returns {Promise} List of email history
   */
  getJobHistory: async (jobId) => {
    const response = await client.get(`/emails/jobs/${jobId}/history`);
    return response.data;
  },

  /**
   * Send a previously generated email
   * @param {number} emailId - ID of the email log entry
   * @param {string} [subject] - Optional custom subject line
   * @returns {Promise} Send result
   */
  sendEmail: async (emailId, subject = null) => {
    const response = await client.post(`/emails/${emailId}/send`, {
      subject: subject
    });
    return response.data;
  }
};

