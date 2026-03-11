import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { 
  Clock, Calendar, Award, ChevronRight, FileText, 
  TrendingUp, Filter, Sparkles, Plus, CheckCircle2, 
  Hourglass, LayoutList 
} from 'lucide-react';

/**
 * Mock Interview History - "Think Tech" Redesign
 */
const MockInterviewHistory = () => {
  const navigate = useNavigate();
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, completed, pending
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // --- Logic (Preserved) ---

  useEffect(() => {
    fetchInterviews();
  }, [page]);

  const fetchInterviews = async () => {
    try {
      setLoading(true);
      const data = await apiService.getInterviewHistory(page, 10);
      setInterviews(data.interviews);
      setTotalPages(Math.ceil(data.total / data.per_page));
      setError(null);
    } catch (err) {
      console.error('Error fetching interview history:', err);
      setError('Failed to load interview history');
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (performance) => {
    switch (performance?.toLowerCase()) {
      case 'excellent': return 'text-emerald-700 bg-emerald-50 border-emerald-100';
      case 'good': return 'text-blue-700 bg-blue-50 border-blue-100';
      case 'average': return 'text-amber-700 bg-amber-50 border-amber-100';
      case 'needs improvement': return 'text-rose-700 bg-rose-50 border-rose-100';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'completed') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-green-50 text-green-700 border border-green-100">
          <CheckCircle2 size={12} /> Completed
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-yellow-50 text-yellow-700 border border-yellow-100">
        <Hourglass size={12} /> Pending
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric'
    });
  };

  const handleViewDetails = (interviewId) => {
    navigate(`/mock-interview/history/${interviewId}`);
  };

  const handleStartNew = () => {
    navigate('/mock-interview');
  };

  const filteredInterviews = interviews.filter(interview => {
    if (filter === 'all') return true;
    if (filter === 'completed') return interview.status === 'completed';
    if (filter === 'pending') return interview.status === 'generated';
    return true;
  });

  // --- Visual Components ---

  const BackgroundBlobs = () => (
    <>
      <div className="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob pointer-events-none"></div>
      <div className="absolute top-[20%] right-[-10%] w-[400px] h-[400px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] left-[20%] w-[300px] h-[300px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-4000 pointer-events-none"></div>
    </>
  );

  if (loading && interviews.length === 0) {
    return (
      <div className="min-h-screen bg-white relative overflow-hidden flex flex-col items-center justify-center font-sans">
        <BackgroundBlobs />
        <div className="relative z-10 text-center">
          <div className="w-16 h-16 border-4 border-purple-100 border-t-purple-600 rounded-full animate-spin mx-auto mb-6"></div>
          <h2 className="text-2xl font-light text-gray-900 mb-2">Loading History</h2>
          <p className="text-gray-500 text-sm">Retrieving your past sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white relative font-sans text-gray-800 selection:bg-purple-100">
      <BackgroundBlobs />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-12 border-b border-gray-100 pb-8">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 border border-purple-100 rounded-full mb-4">
               <Sparkles size={14} className="text-purple-600 fill-purple-200" />
               <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider">Performance Archive</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-light text-gray-900 mb-2">
              Interview <span className="font-medium">History</span>
            </h1>
            <p className="text-gray-500 max-w-xl text-sm leading-relaxed">
              Track your progress over time. Review past answers, AI feedback, and performance scores to continuously improve.
            </p>
          </div>
          
          <button
            onClick={handleStartNew}
            className="group px-6 py-3 bg-gray-900 text-white rounded-xl text-sm font-medium hover:bg-black hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center gap-2"
          >
            <Plus size={18} />
            Start New Session
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
           <StatCard 
             title="Total Sessions" 
             value={interviews.length} 
             icon={LayoutList} 
             color="indigo" 
           />
           <StatCard 
             title="Completed" 
             value={interviews.filter(i => i.status === 'completed').length} 
             icon={CheckCircle2} 
             color="emerald" 
           />
           <StatCard 
             title="Pending" 
             value={interviews.filter(i => i.status === 'generated').length} 
             icon={Hourglass} 
             color="amber" 
           />
           <StatCard 
             title="Avg Score" 
             value={interviews.filter(i => i.totalScore).length > 0
               ? Math.round(interviews.filter(i => i.totalScore).reduce((sum, i) => sum + i.totalScore, 0) / interviews.filter(i => i.totalScore).length)
               : '-'} 
             icon={Award} 
             color="purple" 
           />
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 mb-8 overflow-x-auto pb-2 no-scrollbar">
           <div className="p-2 bg-gray-50 rounded-lg mr-2 text-gray-400">
              <Filter size={16} />
           </div>
           {['all', 'completed', 'pending'].map((opt) => (
             <button
               key={opt}
               onClick={() => setFilter(opt)}
               className={`px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                 filter === opt 
                   ? 'bg-purple-600 text-white shadow-md shadow-purple-200' 
                   : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
               }`}
             >
               {opt.charAt(0).toUpperCase() + opt.slice(1)}
             </button>
           ))}
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm flex items-center justify-center">
            {error}
          </div>
        )}

        {/* List Content */}
        <div className="space-y-4">
          {filteredInterviews.length === 0 ? (
            <div className="bg-white/50 border border-dashed border-gray-300 rounded-2xl p-16 text-center">
               <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-300">
                  <FileText size={32} />
               </div>
               <h3 className="text-lg font-medium text-gray-900 mb-1">No interviews found</h3>
               <p className="text-gray-500 text-sm mb-6">
                 {filter === 'all' ? "You haven't taken any mock interviews yet." : `No ${filter} interviews found.`}
               </p>
               {filter === 'all' && (
                 <button onClick={handleStartNew} className="text-purple-600 font-medium text-sm hover:underline">
                   Start your first interview
                 </button>
               )}
            </div>
          ) : (
            filteredInterviews.map((interview) => (
              <div 
                key={interview.interview_id}
                onClick={() => handleViewDetails(interview.interview_id)}
                className="group bg-white rounded-2xl p-6 border border-gray-100 hover:border-purple-200 hover:shadow-xl hover:shadow-purple-50/30 transition-all duration-300 cursor-pointer relative overflow-hidden"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                   
                   {/* Left: Info */}
                   <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                         <h3 className="text-lg font-bold text-gray-900 group-hover:text-purple-700 transition-colors">
                           {interview.role}
                         </h3>
                         {getStatusBadge(interview.status)}
                      </div>
                      
                      <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 font-medium">
                         <span className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded border border-gray-100">
                            <FileText size={12} /> {interview.interviewType}
                         </span>
                         <span className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded border border-gray-100">
                            <Calendar size={12} /> {formatDate(interview.created_at)}
                         </span>
                         <span className="flex items-center gap-1.5 bg-gray-50 px-2 py-1 rounded border border-gray-100">
                            <Clock size={12} /> {interview.totalQuestions} Qs
                         </span>
                      </div>
                   </div>

                   {/* Right: Score & Action */}
                   <div className="flex items-center gap-6 justify-between md:justify-end border-t md:border-t-0 border-gray-50 pt-4 md:pt-0">
                      {interview.totalScore !== null && (
                        <div className="text-right">
                           <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider">Score</span>
                           <span className="text-2xl font-light text-gray-900">{interview.totalScore}<span className="text-sm text-gray-400">/100</span></span>
                        </div>
                      )}
                      
                      {interview.performance && (
                         <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase border ${getPerformanceColor(interview.performance)}`}>
                            {interview.performance}
                         </span>
                      )}

                      <div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center text-gray-400 group-hover:bg-purple-600 group-hover:text-white transition-all">
                         <ChevronRight size={16} />
                      </div>
                   </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-10 flex items-center justify-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-gray-500 font-medium">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        )}

      </div>
    </div>
  );
};

// --- Sub-Components ---

const StatCard = ({ title, value, icon: Icon, color }) => {
  const colors = {
    indigo: "text-indigo-600 bg-indigo-50",
    emerald: "text-emerald-600 bg-emerald-50",
    amber: "text-amber-600 bg-amber-50",
    purple: "text-purple-600 bg-purple-50",
  };

  return (
    <div className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4 hover:border-gray-200 hover:shadow-md transition-all">
       <div className={`p-3 rounded-xl ${colors[color]}`}>
          <Icon size={24} />
       </div>
       <div>
          <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-0.5">{title}</p>
          <h3 className="text-2xl font-light text-gray-900">{value}</h3>
       </div>
    </div>
  );
};

export default MockInterviewHistory;