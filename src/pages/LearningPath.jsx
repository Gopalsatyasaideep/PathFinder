import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import {
  Target,
  BookOpen,
  Trophy,
  Lightbulb,
  CheckCircle2,
  Clock,
  Rocket,
  Save,
  Trash2,
  Plus,
  ChevronRight,
  Sparkles,
  History
} from 'lucide-react';


/**
 * Interactive Learning Path Page - "Think Tech" Redesign
 * Fullscreen app-like layout with split panes
 */
const LearningPath = () => {
  const navigate = useNavigate();
  // --- State Management (Unchanged) ---
  const [currentSkills, setCurrentSkills] = useState('');
  const [targetRole, setTargetRole] = useState('');
  const [learningGoal, setLearningGoal] = useState('');
  const [timeCommitment, setTimeCommitment] = useState('5-10');

  const [learningPath, setLearningPath] = useState(null);
  const [savedPaths, setSavedPaths] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(true);

  // --- Logic (Unchanged) ---
  useEffect(() => {
    loadSavedPaths();
  }, []);

  const loadSavedPaths = async () => {
    try {
      const response = await apiService.getSavedLearningPaths();
      if (response && response.paths) {
        setSavedPaths(response.paths);
      }
    } catch (err) {
      console.error('Error loading saved paths:', err);
    }
  };

  const generateLearningPath = async (e) => {
    e.preventDefault();
    if (!targetRole.trim() || !learningGoal.trim()) {
      setError('Please fill in your target role and learning goal');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setShowForm(false);

      const response = await apiService.generatePersonalizedLearningPath({
        current_skills: currentSkills,
        target_role: targetRole,
        learning_goal: learningGoal,
        time_commitment: timeCommitment
      });

      const pathData = response.learning_path || response.path || response;
      setLearningPath(pathData);

      await apiService.saveLearningPath({
        target_role: targetRole,
        learning_goal: learningGoal,
        current_skills: currentSkills,
        time_commitment: timeCommitment,
        path: pathData
      });

      loadSavedPaths();

      // Navigate to animated results page
      navigate('/learning-path/results', {
        state: {
          learningPath: Array.isArray(pathData) ? pathData : [],
          targetRole,
          learningGoal,
          currentSkills,
          timeCommitment,
        },
      });
    } catch (err) {
      console.error('Error generating learning path:', err);
      setError(err.response?.data?.message || 'Failed to generate learning path. Please try again.');
      setShowForm(true);
    } finally {
      setLoading(false);
    }
  };

  const loadSavedPath = (path) => {
    // Navigate directly to animated results page with saved path data
    navigate('/learning-path/results', {
      state: {
        learningPath: Array.isArray(path.path) ? path.path : [],
        targetRole: path.target_role,
        learningGoal: path.learning_goal,
        currentSkills: path.current_skills || '',
        timeCommitment: path.time_commitment || '5-10',
      },
    });
  };

  const startNewPath = () => {
    setLearningPath(null);
    setShowForm(true);
    setCurrentSkills('');
    setTargetRole('');
    setLearningGoal('');
    setTimeCommitment('5-10');
    setError(null);
  };

  const deletePath = async (e, pathId) => {
    e.stopPropagation(); // Prevent triggering the click on parent
    if (!window.confirm('Delete this learning path?')) return;

    try {
      await apiService.deleteLearningPath(pathId);
      loadSavedPaths();
      if (learningPath) {
        // If we deleted the currently viewed path, go back to form
        const currentPathId = savedPaths.find(p => p.target_role === targetRole && p.learning_goal === learningGoal)?._id;
        if (currentPathId === pathId) startNewPath();
      }
    } catch (err) {
      console.error('Error deleting path:', err);
    }
  };

  // --- Render Components ---

  const BackgroundBlobs = () => (
    <>
      <div className="absolute top-[-10%] left-[-5%] w-[600px] h-[600px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob pointer-events-none"></div>
      <div className="absolute top-[20%] right-[-10%] w-[500px] h-[500px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-[-20%] left-[20%] w-[400px] h-[400px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-4000 pointer-events-none"></div>
    </>
  );

  return (
    <div className="h-screen w-full bg-white relative overflow-hidden flex font-sans text-gray-800 selection:bg-purple-100">
      <BackgroundBlobs />

      {/* --- Sidebar (Saved Paths) --- */}
      <aside className="w-80 flex-none bg-white/60 backdrop-blur-md border-r border-gray-100 flex flex-col z-20 hidden md:flex">
        {/* Sidebar Header */}
        <div className="p-6 border-b border-gray-50 flex items-center justify-between">
          <div className="flex items-center gap-2 text-gray-800">
            <History size={18} className="text-purple-600" />
            <span className="font-semibold text-sm tracking-tight">History</span>
          </div>
          <button
            onClick={startNewPath}
            className="p-2 bg-purple-50 hover:bg-purple-100 text-purple-600 rounded-lg transition-colors"
            title="Create New Path"
          >
            <Plus size={16} />
          </button>
        </div>

        {/* Saved Paths List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2 custom-scrollbar">
          {savedPaths.length === 0 ? (
            <div className="text-center py-10 px-4">
              <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-3">
                <Save size={20} className="text-gray-300" />
              </div>
              <p className="text-xs text-gray-400">No saved paths yet.</p>
            </div>
          ) : (
            savedPaths.map((path) => (
              <div
                key={path._id}
                onClick={() => loadSavedPath(path)}
                className={`group relative p-4 rounded-xl border transition-all cursor-pointer ${targetRole === path.target_role && !showForm
                    ? 'bg-white border-purple-200 shadow-md shadow-purple-50'
                    : 'bg-transparent border-transparent hover:bg-white hover:border-gray-100'
                  }`}
              >
                <div className="pr-6">
                  <h4 className={`text-sm font-medium truncate mb-1 ${targetRole === path.target_role && !showForm ? 'text-purple-700' : 'text-gray-700'
                    }`}>
                    {path.target_role}
                  </h4>
                  <p className="text-[11px] text-gray-400 truncate">
                    {path.learning_goal}
                  </p>
                </div>

                {/* Delete Action */}
                <button
                  onClick={(e) => deletePath(e, path._id)}
                  className="absolute right-3 top-4 p-1.5 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded opacity-0 group-hover:opacity-100 transition-all"
                  title="Delete"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* --- Main Content Area --- */}
      <main className="flex-1 flex flex-col relative z-10 overflow-hidden bg-transparent">

        {/* Mobile Header (Only visible on small screens) */}
        <div className="md:hidden p-4 border-b border-gray-100 flex justify-between items-center bg-white/80 backdrop-blur">
          <span className="font-bold text-gray-900">Learning Path</span>
          <button onClick={startNewPath} className="text-purple-600 font-medium text-sm">New</button>
        </div>

        {/* Scrollable Content Container */}
        <div className="flex-1 overflow-y-auto scroll-smooth">
          <div className="max-w-4xl mx-auto px-6 py-12 md:py-16 min-h-full">

            {/* 1. Header Section */}
            {showForm && (
              <div className="text-center mb-12 animate-fade-in-down">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 border border-purple-100 text-purple-600 text-xs font-bold uppercase tracking-wider mb-6">
                  <Sparkles size={12} />
                  AI Powered Roadmap
                </div>
                <h1 className="text-4xl md:text-5xl font-light text-gray-900 mb-6 tracking-tight">
                  Design your <span className="font-medium">career path</span>
                </h1>
                <p className="text-gray-500 max-w-lg mx-auto leading-relaxed">
                  Tell us your ambitions. Our AI analyzes market demands to create a tailored step-by-step curriculum just for you.
                </p>
              </div>
            )}

            {/* 2. Loading State */}
            {loading && !showForm && (
              <div className="flex flex-col items-center justify-center h-[60vh] animate-fade-in">
                <div className="relative">
                  <div className="w-20 h-20 border-4 border-purple-100 rounded-full"></div>
                  <div className="absolute top-0 left-0 w-20 h-20 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
                </div>
                <h3 className="mt-8 text-xl font-light text-gray-900">Generating Curriculum...</h3>
                <p className="text-gray-400 text-sm mt-2">Analyzing skill gaps and market trends</p>
              </div>
            )}

            {/* 3. Input Form */}
            {showForm && (
              <div className="max-w-2xl mx-auto bg-white/80 backdrop-blur-sm border border-white shadow-xl shadow-purple-100/50 rounded-2xl p-8 md:p-10 animate-fade-in-up">
                <form onSubmit={generateLearningPath} className="space-y-8">

                  {/* Role Input */}
                  <div className="space-y-2">
                    <label className="text-sm font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                      <Target size={16} className="text-purple-500" />
                      Target Role
                    </label>
                    <input
                      type="text"
                      value={targetRole}
                      onChange={(e) => setTargetRole(e.target.value)}
                      placeholder="e.g. Senior Product Designer"
                      className="w-full px-0 py-3 bg-transparent border-b-2 border-gray-100 focus:border-purple-500 outline-none text-lg text-gray-800 placeholder-gray-300 transition-colors"
                      required
                    />
                  </div>

                  {/* Goal Input */}
                  <div className="space-y-2">
                    <label className="text-sm font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                      <Rocket size={16} className="text-purple-500" />
                      Specific Goal
                    </label>
                    <textarea
                      value={learningGoal}
                      onChange={(e) => setLearningGoal(e.target.value)}
                      placeholder="e.g. Transition from marketing to UX design within 6 months..."
                      rows="3"
                      className="w-full px-4 py-3 bg-gray-50/50 rounded-xl border border-transparent focus:bg-white focus:border-purple-200 focus:ring-4 focus:ring-purple-50/50 outline-none text-base text-gray-700 resize-none transition-all"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Skills Input */}
                    <div className="space-y-2">
                      <label className="text-sm font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                        <CheckCircle2 size={16} className="text-purple-500" />
                        Current Skills <span className="text-gray-300 font-normal lowercase">(optional)</span>
                      </label>
                      <input
                        type="text"
                        value={currentSkills}
                        onChange={(e) => setCurrentSkills(e.target.value)}
                        placeholder="e.g. Photoshop, Basic HTML"
                        className="w-full px-4 py-3 bg-gray-50/50 rounded-xl border border-transparent focus:bg-white focus:border-purple-200 outline-none text-sm text-gray-700 transition-all"
                      />
                    </div>

                    {/* Time Input */}
                    <div className="space-y-2">
                      <label className="text-sm font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                        <Clock size={16} className="text-purple-500" />
                        Availability
                      </label>
                      <div className="relative">
                        <select
                          value={timeCommitment}
                          onChange={(e) => setTimeCommitment(e.target.value)}
                          className="w-full px-4 py-3 bg-gray-50/50 rounded-xl border border-transparent focus:bg-white focus:border-purple-200 outline-none text-sm text-gray-700 appearance-none transition-all cursor-pointer"
                        >
                          <option value="1-5">1-5 hours / week</option>
                          <option value="5-10">5-10 hours / week</option>
                          <option value="10-20">10-20 hours / week</option>
                          <option value="20+">20+ hours / week</option>
                        </select>
                        <div className="absolute right-4 top-3.5 text-gray-400 pointer-events-none">
                          <ChevronRight size={16} className="rotate-90" />
                        </div>
                      </div>
                    </div>
                  </div>

                  {error && (
                    <div className="p-4 bg-red-50 text-red-600 text-sm rounded-lg flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full"></div>
                      {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-4 bg-gray-900 text-white font-medium rounded-xl hover:bg-black transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 group"
                  >
                    Generate Roadmap
                    <Sparkles size={18} className="text-purple-400 group-hover:text-white transition-colors" />
                  </button>
                </form>
              </div>
            )}

            {/* Results: Now handled by /learning-path/results page */}

          </div>
        </div>
      </main>
    </div>
  );
};

export default LearningPath;