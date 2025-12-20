import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import ApplicantLayout from './components/ApplicantLayout';
import RecruiterLayout from './components/RecruiterLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import Jobs from './pages/Jobs';
import Applicants from './pages/Applicants';
import Analytics from './pages/Analytics';
import ApplicantDashboard from './pages/ApplicantDashboard';
import ApplicantProfile from './pages/ApplicantProfile';
import ApplicantApplications from './pages/ApplicantApplications';
import JobDetail from './pages/JobDetail';
import ApplicantJobs from './pages/ApplicantJobs';
import RecruiterDashboard from './pages/RecruiterDashboard';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Redirect component based on user role
const RoleRedirect = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (user?.role === 'recruiter') {
    return <Navigate to="/recruiter/dashboard" replace />;
  } else if (user?.role === 'applicant') {
    return <Navigate to="/applicant/dashboard" replace />;
  }

  return <Navigate to="/login" replace />;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Root redirect */}
      <Route path="/" element={<RoleRedirect />} />

      {/* Recruiter routes */}
      <Route
        path="/recruiter/dashboard"
        element={
          <ProtectedRoute requireRole="recruiter">
            <RecruiterLayout>
              <RecruiterDashboard />
            </RecruiterLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/jobs"
        element={
          <ProtectedRoute requireRole="recruiter">
            <RecruiterLayout>
              <Jobs />
            </RecruiterLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/jobs/:id/applicants"
        element={
          <ProtectedRoute requireRole="recruiter">
            <RecruiterLayout>
              <Applicants />
            </RecruiterLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/applicants"
        element={
          <ProtectedRoute requireRole="recruiter">
            <RecruiterLayout>
              <Applicants />
            </RecruiterLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/recruiter/analytics"
        element={
          <ProtectedRoute requireRole="recruiter">
            <RecruiterLayout>
              <Analytics />
            </RecruiterLayout>
          </ProtectedRoute>
        }
      />

      {/* Applicant routes */}
      <Route
        path="/applicant/dashboard"
        element={
          <ProtectedRoute requireRole="applicant">
            <ApplicantLayout>
              <ApplicantDashboard />
            </ApplicantLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/applicant/jobs"
        element={
          <ProtectedRoute requireRole="applicant">
            <ApplicantLayout>
              <ApplicantJobs />
            </ApplicantLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/applicant/jobs/:id"
        element={
          <ProtectedRoute requireRole="applicant">
            <ApplicantLayout>
              <JobDetail />
            </ApplicantLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/applicant/applications"
        element={
          <ProtectedRoute requireRole="applicant">
            <ApplicantLayout>
              <ApplicantApplications />
            </ApplicantLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/applicant/profile"
        element={
          <ProtectedRoute requireRole="applicant">
            <ApplicantLayout>
              <ApplicantProfile />
            </ApplicantLayout>
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <AppRoutes />
        </Router>
        <Toaster position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
