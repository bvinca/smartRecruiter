import client from './client';

export const recommendationsApi = {
  getJobRecommendations: (applicantId, topK = 5) => {
    return client.get(`/recommendations/jobs/${applicantId}?top_k=${topK}`);
  },

  getCandidateRecommendations: (jobId, topK = 5) => {
    return client.get(`/recommendations/candidates/${jobId}?top_k=${topK}`);
  },

  getSimilarCandidates: (applicantId, topK = 5) => {
    return client.get(`/recommendations/similar/${applicantId}?top_k=${topK}`);
  }
};

