import client from './client';

export const interviewsApi = {
  create: (data) => client.post('/interviews', data),
  
  getAll: (applicationId) => {
    const params = applicationId ? `?application_id=${applicationId}` : '';
    return client.get(`/interviews${params}`);
  },
  
  getOne: (id) => client.get(`/interviews/${id}`),
  
  update: (id, data) => client.put(`/interviews/${id}`, data),
  
  delete: (id) => client.delete(`/interviews/${id}`),
};

