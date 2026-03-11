import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import Loading from '../components/Loading';
import Error from '../components/Error';
import { 
  MessageSquare, FileText, Briefcase, Eye, Trash2, 
  Download, Search, Filter, Clock, LayoutGrid, List, 
  X, MoreHorizontal, GraduationCap, BookOpen, FileCheck2,
  Sparkles, Calendar, ChevronRight
} from 'lucide-react';

/**
 * UserHistory Component - "Think Tech" Redesign
 */
const UserHistory = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('chats');
  const [chatHistory, setChatHistory] = useState([]);
  const [resumeHistory, setResumeHistory] = useState([]);
  const [jobHistory, setJobHistory] = useState([]);
  const [learningPathHistory, setLearningPathHistory] = useState([]);
  const [mockInterviewHistory, setMockInterviewHistory] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid'); 

  // --- Logic (Preserved) ---

  useEffect(() => {
    fetchAllHistory();
  }, []);

  const fetchAllHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const [chatsData, resumesData, jobsData, learningData, interviewData, summaryData] = await Promise.all([
        apiService.getChatHistory(),
        apiService.getResumeAnalyses(),
        apiService.getJobRecommendationsHistory(),
        apiService.getSavedLearningPaths(),
        apiService.getInterviewHistory(1, 100).catch(() => ({ interviews: [] })),
        apiService.getUserHistorySummary()
      ]);

      setChatHistory(chatsData.chats || []);
      setResumeHistory(resumesData.analyses || []);
      setJobHistory(jobsData.recommendations || []);
      setLearningPathHistory(learningData.learning_paths || []);
      setMockInterviewHistory(interviewData.interviews || []);
      
      setSummary({
        ...summaryData,
        total_learning_paths: learningData.learning_paths?.length || 0,
        total_mock_interviews: interviewData.interviews?.length || 0
      });
    } catch (err) {
      console.error('Error fetching history:', err);
      setError('Failed to load your history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChat = async (chatId) => {
    if (!confirm('Are you sure you want to delete this chat?')) return;
    try {
      await apiService.deleteChat(chatId);
      setChatHistory(prev => prev.filter(c => c._id !== chatId));
    } catch (err) {
      console.error('Error deleting chat:', err);
      alert('Failed to delete chat. Please try again.');
    }
  };

  const handleDeleteLearningPath = async (pathId) => {
    if (!confirm('Are you sure you want to delete this learning path?')) return;
    try {
      await apiService.deleteLearningPath(pathId);
      setLearningPathHistory(prev => prev.filter(p => p._id !== pathId));
      setSummary(prev => ({
        ...prev,
        total_learning_paths: (prev.total_learning_paths || 1) - 1
      }));
    } catch (err) {
      console.error('Error deleting learning path:', err);
      alert('Failed to delete learning path. Please try again.');
    }
  };

  const handleViewChat = (chatId) => {
    localStorage.setItem('lastActiveChatId', chatId);
    navigate('/chatbot');
  };

  const handleViewMockInterview = (interviewId) => {
    navigate(`/mock-interview/history/${interviewId}`);
  };

  const handleViewResume = (resume) => {
    navigate('/dashboard', { state: { resumeData: resume } });
  };

  const handleViewLearningPath = (learningPath) => {
    navigate('/learning-path', { state: { learningPathData: learningPath } });
  };

  const handleExport = () => {
    const exportData = {
      chats: chatHistory,
      resumes: resumeHistory,
      jobs: jobHistory,
      learningPaths: learningPathHistory,
      summary,
      exportedAt: new Date().toISOString()
    };
    const dataStr = JSON.stringify(exportData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pathfinder-history-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const getFilteredData = () => {
    const lowerQuery = searchQuery.toLowerCase();
    switch (activeTab) {
        case 'chats':
            return chatHistory.filter(c => 
                (c.session_name?.toLowerCase() || '').includes(lowerQuery) ||
                c.messages?.some(m => (m.content?.toLowerCase() || '').includes(lowerQuery))
            );
        case 'resumes':
            return resumeHistory.filter(r => 
                (r.file_name?.toLowerCase() || '').includes(lowerQuery) ||
                (r.resume_data?.name?.toLowerCase() || '').includes(lowerQuery)
            );
        case 'jobs':
            return jobHistory.filter(j => 
                j.jobs?.some(job => 
                    (job.title?.toLowerCase() || '').includes(lowerQuery) ||
                    (job.company?.toLowerCase() || '').includes(lowerQuery)
                )
            );
        case 'learning-paths':
            return learningPathHistory.filter(lp =>
                (lp.topic?.toLowerCase() || '').includes(lowerQuery) ||
                (lp.career_path?.toLowerCase() || '').includes(lowerQuery)
            );
        case 'mock-interviews':
            return mockInterviewHistory.filter(mi =>
                (mi.role?.toLowerCase() || '').includes(lowerQuery) ||
                (mi.interviewType?.toLowerCase() || '').includes(lowerQuery)
            );
        default: return [];
    }
  };

  const filteredData = getFilteredData();

  // --- Visual Components ---

  const BackgroundBlobs = () => (
    <>
      <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob pointer-events-none"></div>
      <div className="absolute top-[20%] left-[-10%] w-[400px] h-[400px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[20%] w-[300px] h-[300px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-4000 pointer-events-none"></div>
    </>
  );

  if (loading) return <Loading message="Loading activity..." />;
  if (error) return <Error message={error} onRetry={fetchAllHistory} />;

  return (
    <div className="min-h-screen bg-white relative overflow-hidden font-sans text-gray-800 selection:bg-purple-100 pb-20">
      <BackgroundBlobs />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 pt-12">
        
        {/* Header */}
        <div className="mb-12">
           <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 border border-purple-100 rounded-full mb-3">
              <Sparkles size={12} className="text-purple-600 fill-purple-200" />
              <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider">My Activity</span>
           </div>
           <h1 className="text-3xl md:text-4xl font-light text-gray-900 mb-2">
             Career <span className="font-medium">Archive</span>
           </h1>
           <p className="text-gray-500 text-sm max-w-2xl">
             Track your progress. Access past chats, resumes, learning paths, and interview results.
           </p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-10">
           <StatCard title="Chats" value={summary.total_chats || 0} icon={MessageSquare} color="indigo" />
           <StatCard title="Resumes" value={summary.total_resume_analyses || 0} icon={FileText} color="emerald" />
           <StatCard title="Jobs Found" value={summary.total_job_recommendations || 0} icon={Briefcase} color="amber" />
           <StatCard title="Learning" value={summary.total_learning_paths || 0} icon={GraduationCap} color="purple" />
           <StatCard title="Interviews" value={summary.total_mock_interviews || 0} icon={FileCheck2} color="blue" />
        </div>

        {/* Controls Toolbar */}
        <div className="bg-white/80 backdrop-blur-md rounded-2xl border border-gray-100 shadow-sm p-2 mb-8 sticky top-20 z-20 flex flex-col md:flex-row gap-4 items-center justify-between">
           
           {/* Tabs */}
           <div className="flex items-center gap-1 overflow-x-auto w-full md:w-auto p-1 no-scrollbar">
              <TabButton active={activeTab === 'chats'} onClick={() => setActiveTab('chats')} label="Chats" />
              <TabButton active={activeTab === 'resumes'} onClick={() => setActiveTab('resumes')} label="Resumes" />
              <TabButton active={activeTab === 'jobs'} onClick={() => setActiveTab('jobs')} label="Jobs" />
              <TabButton active={activeTab === 'learning-paths'} onClick={() => setActiveTab('learning-paths')} label="Learning" />
              <TabButton active={activeTab === 'mock-interviews'} onClick={() => setActiveTab('mock-interviews')} label="Interviews" />
           </div>

           {/* Search & Actions */}
           <div className="flex items-center gap-2 w-full md:w-auto">
              <div className="relative flex-1 md:w-64">
                 <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                 <input 
                   type="text" 
                   placeholder="Search history..." 
                   value={searchQuery}
                   onChange={(e) => setSearchQuery(e.target.value)}
                   className="w-full pl-9 pr-8 py-2 bg-gray-50 border border-gray-200 rounded-lg text-xs focus:outline-none focus:bg-white focus:border-purple-300 transition-all"
                 />
                 {searchQuery && (
                   <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                     <X size={12} />
                   </button>
                 )}
              </div>
              
              <div className="flex bg-gray-100 p-1 rounded-lg">
                 <button onClick={() => setViewMode('grid')} className={`p-1.5 rounded-md transition-all ${viewMode === 'grid' ? 'bg-white shadow-sm text-purple-600' : 'text-gray-400 hover:text-gray-600'}`}>
                    <LayoutGrid size={14} />
                 </button>
                 <button onClick={() => setViewMode('list')} className={`p-1.5 rounded-md transition-all ${viewMode === 'list' ? 'bg-white shadow-sm text-purple-600' : 'text-gray-400 hover:text-gray-600'}`}>
                    <List size={14} />
                 </button>
              </div>

              <button onClick={handleExport} className="p-2 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors border border-transparent hover:border-purple-100" title="Export">
                 <Download size={16} />
              </button>
           </div>
        </div>

        {/* Content Grid */}
        <div className="animate-fade-in-up min-h-[400px]">
           {/* -- CHATS -- */}
           {activeTab === 'chats' && (
             <GridListWrapper viewMode={viewMode} isEmpty={filteredData.length === 0} emptyText="No chat history found.">
               {filteredData.map(chat => (
                 <HistoryCard 
                   key={chat._id}
                   viewMode={viewMode}
                   title={chat.session_name || 'Untitled Session'}
                   subtitle={`${chat.messages?.length || 0} messages`}
                   date={chat.updated_at}
                   icon={MessageSquare}
                   color="indigo"
                   action={() => handleViewChat(chat._id)}
                   onDelete={() => handleDeleteChat(chat._id)}
                 />
               ))}
             </GridListWrapper>
           )}

           {/* -- RESUMES -- */}
           {activeTab === 'resumes' && (
             <GridListWrapper viewMode={viewMode} isEmpty={filteredData.length === 0} emptyText="No resumes found.">
               {filteredData.map(item => (
                 <HistoryCard 
                   key={item._id}
                   viewMode={viewMode}
                   title={item.file_name || 'Resume Analysis'}
                   subtitle={`${item.resume_data?.skills?.length || 0} skills detected`}
                   date={item.created_at}
                   icon={FileText}
                   color="emerald"
                   action={() => handleViewResume(item)}
                   actionLabel="View Report"
                 />
               ))}
             </GridListWrapper>
           )}

           {/* -- JOBS -- */}
           {activeTab === 'jobs' && (
             <GridListWrapper viewMode={viewMode} isEmpty={filteredData.length === 0} emptyText="No job searches found.">
               {filteredData.map(item => (
                 <HistoryCard 
                   key={item._id}
                   viewMode={viewMode}
                   title="Job Recommendations"
                   subtitle={`${item.jobs?.length || 0} roles found`}
                   date={item.created_at}
                   icon={Briefcase}
                   color="amber"
                   footer={
                     <div className="flex -space-x-2 pt-2 overflow-hidden">
                       {item.jobs?.slice(0,4).map((j,i) => (
                         <div key={i} className="h-6 w-6 rounded-full bg-gray-100 border border-white flex items-center justify-center text-[8px] font-bold text-gray-500" title={j.title}>
                           {j.title?.[0]}
                         </div>
                       ))}
                     </div>
                   }
                 />
               ))}
             </GridListWrapper>
           )}

           {/* -- LEARNING -- */}
           {activeTab === 'learning-paths' && (
             <GridListWrapper viewMode={viewMode} isEmpty={filteredData.length === 0} emptyText="No learning paths found.">
               {filteredData.map(lp => (
                 <HistoryCard 
                   key={lp._id}
                   viewMode={viewMode}
                   title={lp.topic || 'Learning Path'}
                   subtitle={`${lp.steps?.length || 0} steps • ${lp.career_path || 'General'}`}
                   date={lp.created_at}
                   icon={GraduationCap}
                   color="purple"
                   action={() => handleViewLearningPath(lp)}
                   onDelete={() => handleDeleteLearningPath(lp._id)}
                   footer={
                     <div className="w-full bg-gray-100 h-1 mt-2 rounded-full overflow-hidden">
                        <div className="bg-purple-500 h-full rounded-full" style={{ width: `${(lp.steps?.filter(s => s.completed).length / lp.steps?.length) * 100 || 0}%` }}></div>
                     </div>
                   }
                 />
               ))}
             </GridListWrapper>
           )}

           {/* -- INTERVIEWS -- */}
           {activeTab === 'mock-interviews' && (
             <GridListWrapper viewMode={viewMode} isEmpty={filteredData.length === 0} emptyText="No interviews found.">
               {filteredData.map(mi => (
                 <HistoryCard 
                   key={mi.interview_id}
                   viewMode={viewMode}
                   title={mi.role}
                   subtitle={`${mi.interviewType} • ${mi.totalQuestions} Qs`}
                   date={mi.created_at}
                   icon={FileCheck2}
                   color="blue"
                   action={() => handleViewMockInterview(mi.interview_id)}
                   footer={
                     mi.status === 'completed' ? (
                       <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase border ${
                         mi.performance === 'Excellent' ? 'bg-green-50 text-green-700 border-green-100' : 
                         mi.performance === 'Good' ? 'bg-blue-50 text-blue-700 border-blue-100' : 'bg-yellow-50 text-yellow-700 border-yellow-100'
                       }`}>
                         {mi.performance} • {mi.totalScore}%
                       </span>
                     ) : (
                       <span className="text-[10px] px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full font-bold uppercase">Incomplete</span>
                     )
                   }
                 />
               ))}
             </GridListWrapper>
           )}
        </div>

      </div>
    </div>
  );
};

// --- Sub-Components ---

const StatCard = ({ title, value, icon: Icon, color }) => {
  const colors = {
    indigo: "bg-indigo-50 text-indigo-600",
    emerald: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
    purple: "bg-purple-50 text-purple-600",
    blue: "bg-blue-50 text-blue-600",
  };
  
  return (
    <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center justify-between group hover:border-gray-200 hover:shadow-md transition-all">
      <div>
        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-0.5">{title}</p>
        <h3 className="text-2xl font-light text-gray-900">{value}</h3>
      </div>
      <div className={`p-2.5 rounded-lg ${colors[color]} group-hover:scale-110 transition-transform`}>
        <Icon size={18} />
      </div>
    </div>
  );
};

const TabButton = ({ active, onClick, label }) => (
  <button 
    onClick={onClick}
    className={`px-4 py-2 text-xs font-bold transition-all whitespace-nowrap rounded-lg ${
      active 
        ? 'bg-purple-600 text-white shadow-md shadow-purple-200' 
        : 'bg-transparent text-gray-500 hover:bg-gray-50 hover:text-gray-900'
    }`}
  >
    {label}
  </button>
);

const GridListWrapper = ({ viewMode, isEmpty, emptyText, children }) => {
  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center py-20 bg-white/50 border border-dashed border-gray-200 rounded-2xl">
        <div className="p-3 bg-gray-50 rounded-full mb-3"><Search size={20} className="text-gray-300"/></div>
        <p className="text-gray-400 text-sm">{emptyText}</p>
      </div>
    );
  }
  
  return (
    <div className={viewMode === 'grid' ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" : "flex flex-col gap-3"}>
      {children}
    </div>
  );
};

const HistoryCard = ({ viewMode, title, subtitle, date, icon: Icon, color, action, actionLabel, onDelete, footer }) => {
  const colors = {
    indigo: "text-indigo-600 bg-indigo-50 border-indigo-100",
    emerald: "text-emerald-600 bg-emerald-50 border-emerald-100",
    amber: "text-amber-600 bg-amber-50 border-amber-100",
    purple: "text-purple-600 bg-purple-50 border-purple-100",
    blue: "text-blue-600 bg-blue-50 border-blue-100",
  };

  // List View
  if (viewMode === 'list') {
    return (
      <div className="group bg-white p-3 pr-4 rounded-xl border border-gray-100 flex items-center justify-between hover:border-purple-200 hover:shadow-lg hover:shadow-purple-50/30 transition-all duration-300">
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <div className={`p-2.5 rounded-lg border ${colors[color]} shrink-0`}>
            <Icon size={18} />
          </div>
          <div className="min-w-0">
            <h4 className="font-bold text-gray-900 text-sm truncate group-hover:text-purple-700 transition-colors">{title}</h4>
            <div className="flex items-center gap-2 text-[10px] text-gray-500 mt-0.5">
              <span className="truncate">{subtitle}</span>
              <span className="w-0.5 h-0.5 bg-gray-300 rounded-full"></span>
              <span className="shrink-0">{new Date(date).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
           {action && (
             <button onClick={action} className="p-2 hover:bg-gray-50 rounded-lg text-gray-500 hover:text-purple-600 transition-colors">
               {actionLabel ? <span className="text-xs font-bold px-2">{actionLabel}</span> : <Eye size={16}/>}
             </button>
           )}
           {onDelete && (
             <button onClick={onDelete} className="p-2 hover:bg-red-50 rounded-lg text-gray-400 hover:text-red-500 transition-colors">
               <Trash2 size={16} />
             </button>
           )}
        </div>
      </div>
    );
  }

  // Grid View
  return (
    <div className="group bg-white p-5 rounded-2xl border border-gray-100 hover:border-purple-200 hover:shadow-xl hover:shadow-purple-50/50 hover:-translate-y-1 transition-all duration-300 flex flex-col relative overflow-hidden">
      
      <div className="flex justify-between items-start mb-4">
         <div className={`p-3 rounded-xl border ${colors[color]}`}>
            <Icon size={20} />
         </div>
         {onDelete && (
           <button onClick={onDelete} className="absolute top-4 right-4 p-1.5 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100">
             <Trash2 size={14} />
           </button>
         )}
      </div>
      
      <h3 className="text-base font-bold text-gray-900 mb-1 line-clamp-1 group-hover:text-purple-700 transition-colors">{title}</h3>
      <p className="text-xs text-gray-500 font-medium mb-4 line-clamp-1">{subtitle}</p>
      
      {footer && <div className="mt-auto mb-3">{footer}</div>}
      
      <div className="mt-auto pt-3 border-t border-gray-50 flex items-center justify-between">
         <div className="flex items-center gap-1.5 text-[10px] text-gray-400 font-medium">
            <Calendar size={10} />
            {new Date(date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
         </div>
         
         {action && (
           <button onClick={action} className="flex items-center gap-1 text-[10px] font-bold text-purple-600 hover:text-purple-800 transition-colors">
             {actionLabel || 'View'} <ChevronRight size={12} />
           </button>
         )}
      </div>
    </div>
  );
};

export default UserHistory;