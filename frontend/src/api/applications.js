import client from './client';

export const applicationsApi = {
  apply: async (jobId, file) => {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    // Note: Even if no file, we send FormData (empty) - FastAPI handles Optional[UploadFile] = File(None)
    return client.post(`/applications/apply/${jobId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getAll: () => client.get('/applications'),
  
  getOne: (id) => client.get(`/applications/${id}`),
  
  update: (id, data) => client.put(`/applications/${id}`, data),
};

