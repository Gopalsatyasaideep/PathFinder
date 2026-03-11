import { Navigate } from 'react-router-dom';

/**
 * ProtectedRoute Component
 * Prevents access to protected pages without authentication
 */
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
