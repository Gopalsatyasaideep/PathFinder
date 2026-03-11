import { createBrowserRouter } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ResumeUpload from './pages/ResumeUpload';
import Dashboard from './pages/Dashboard';
import JobRecommendations from './pages/JobRecommendations';
import LearningPath from './pages/LearningPath';
import LearningPathResults from './pages/LearningPathResults';
import Chatbot from './pages/Chatbot';
import UserHistory from './pages/UserHistory';
import MockInterview from './pages/MockInterview';
import MockInterviewScreen from './pages/MockInterviewScreen';
import MockInterviewResults from './pages/MockInterviewResults';
import MockInterviewHistory from './pages/MockInterviewHistory';
import MockInterviewHistoryDetail from './pages/MockInterviewHistoryDetail';
import App from './App';
import ProtectedRoute from './components/ProtectedRoute';

/**
 * Application Routes
 * Defines all routes for the application
 * Login and Signup are public, others require authentication
 */
export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/signup',
    element: <Signup />,
  },
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: <Landing />,
      },
      {
        path: 'upload',
        element: (
          <ProtectedRoute>
            <ResumeUpload />
          </ProtectedRoute>
        ),
      },
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        ),
      },
      {
        path: 'jobs',
        element: (
          <ProtectedRoute>
            <JobRecommendations />
          </ProtectedRoute>
        ),
      },
      {
        path: 'learning-path',
        element: (
          <ProtectedRoute>
            <LearningPath />
          </ProtectedRoute>
        ),
      },
      {
        path: 'learning-path/results',
        element: (
          <ProtectedRoute>
            <LearningPathResults />
          </ProtectedRoute>
        ),
      },
      {
        path: 'chatbot',
        element: (
          <ProtectedRoute>
            <Chatbot />
          </ProtectedRoute>
        ),
      },
      {
        path: 'history',
        element: (
          <ProtectedRoute>
            <UserHistory />
          </ProtectedRoute>
        ),
      },
      {
        path: 'mock-interview',
        element: (
          <ProtectedRoute>
            <MockInterview />
          </ProtectedRoute>
        ),
      },
      {
        path: 'mock-interview/start',
        element: (
          <ProtectedRoute>
            <MockInterviewScreen />
          </ProtectedRoute>
        ),
      },
      {
        path: 'mock-interview/results',
        element: (
          <ProtectedRoute>
            <MockInterviewResults />
          </ProtectedRoute>
        ),
      },
      {
        path: 'mock-interview/history',
        element: (
          <ProtectedRoute>
            <MockInterviewHistory />
          </ProtectedRoute>
        ),
      },
      {
        path: 'mock-interview/history/:interviewId',
        element: (
          <ProtectedRoute>
            <MockInterviewHistoryDetail />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);
