import client from './client';

export const authApi = {
  register: (data) => client.post('/auth/register', data),
  login: (email, password) => {
    const formData = new FormData();
    formData.append('username', email); // OAuth2PasswordRequestForm uses 'username'
    formData.append('password', password);
    return client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getCurrentUser: () => client.get('/auth/me'),
  logout: () => client.post('/auth/logout'),
};

