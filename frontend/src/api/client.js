import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - dynamically add token to each request
client.interceptors.request.use(
  (config) => {
    // Get token from localStorage on each request to ensure it's up to date
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Debug logging for job creation
    if (config.url?.includes('/jobs') && config.method === 'post') {
      console.log('Creating job - Request config:', {
        url: config.url,
        method: config.method,
        data: config.data,
        headers: {
          ...config.headers,
          Authorization: config.headers.Authorization ? 'Bearer ***' : 'Missing'
        }
      });
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const status = error.response.status;
      const data = error.response.data;
      
      // Handle 401 Unauthorized - token might be invalid
      if (status === 401) {
        localStorage.removeItem('token');
        delete client.defaults.headers.common['Authorization'];
        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
      
      // Handle 403 Forbidden - user doesn't have permission
      if (status === 403) {
        const message = data?.detail || data?.message || 'You do not have permission to perform this action';
        return Promise.reject(new Error(message));
      }
      
      // Other errors
      const message = data?.detail || data?.message || `Error ${status}: An error occurred`;
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // Request made but no response
      return Promise.reject(new Error('No response from server. Please check your connection.'));
    } else {
      // Error in request setup
      return Promise.reject(error);
    }
  }
);

export default client;

