import { Outlet } from 'react-router-dom';
import Navbar from './components/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

/**
 * Main App Component
 * Wraps all pages with Navbar and provides layout structure
 */
function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main>
          <Outlet />
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
