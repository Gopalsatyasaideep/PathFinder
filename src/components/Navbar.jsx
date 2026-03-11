import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LogOut, User, Search, ChevronDown, 
  History, GraduationCap, X, FileText, 
  Sparkles, LayoutDashboard, Briefcase, MessageSquare, 
  Menu
} from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

/**
 * Navbar Component - "Think Tech" Redesign
 * Minimalist text-only branding, Glassmorphism, Pill-shaped nav
 */
const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState({ chats: [], resumes: [], jobs: [] });
  const [searchLoading, setSearchLoading] = useState(false);
  
  const dropdownRef = useRef(null);
  const searchRef = useRef(null);

  // --- Logic (Preserved) ---

  useEffect(() => {
    const checkAuth = () => {
      const authStatus = localStorage.getItem('isAuthenticated') === 'true';
      const userData = localStorage.getItem('user');
      setIsAuthenticated(authStatus);
      if (authStatus && userData) {
        setUser(JSON.parse(userData));
      }
    };
    checkAuth();
  }, [location]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowUserDropdown(false);
      }
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSearch(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (searchQuery.length > 2) {
      performSearch(searchQuery);
    } else {
      setSearchResults({ chats: [], resumes: [], jobs: [] });
    }
  }, [searchQuery]);

  const performSearch = async (query) => {
    setSearchLoading(true);
    try {
      const { apiService } = await import('../services/api');
      
      const [chatsData, resumesData, jobsData] = await Promise.all([
        apiService.getChatHistory().catch(() => ({ chats: [] })),
        apiService.getResumeAnalyses().catch(() => ({ analyses: [] })),
        apiService.getJobRecommendationsHistory().catch(() => ({ recommendations: [] }))
      ]);

      const lowerQuery = query.toLowerCase();
      
      const filteredChats = (chatsData.chats || [])
        .filter(chat => 
          chat.session_name?.toLowerCase().includes(lowerQuery) ||
          chat.messages?.some(m => m.content?.toLowerCase().includes(lowerQuery))
        ).slice(0, 3);

      const filteredResumes = (resumesData.analyses || [])
        .filter(resume => 
          resume.file_name?.toLowerCase().includes(lowerQuery) ||
          resume.resume_data?.name?.toLowerCase().includes(lowerQuery)
        ).slice(0, 3);

      const filteredJobs = (jobsData.recommendations || [])
        .filter(jobRec => 
          jobRec.jobs?.some(job => 
            job.title?.toLowerCase().includes(lowerQuery) ||
            job.company?.toLowerCase().includes(lowerQuery)
          )
        ).slice(0, 3);

      setSearchResults({ chats: filteredChats, resumes: filteredResumes, jobs: filteredJobs });
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    setIsAuthenticated(false);
    setShowUserDropdown(false);
    navigate('/login');
  };

  const handleSearchResultClick = (type, item) => {
    if (type === 'chat') {
      localStorage.setItem('lastActiveChatId', item._id);
      navigate('/chatbot');
    } else if (type === 'resume') {
      navigate('/history');
    } else if (type === 'job') {
      navigate('/jobs');
    }
    setShowSearch(false);
    setSearchQuery('');
  };

  const isActive = (path) => location.pathname === path;

  // --- Configuration ---

  const navLinks = [
    { path: '/', label: 'Home', icon: Sparkles },
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/jobs', label: 'Jobs', icon: Briefcase },
    { path: '/chatbot', label: 'AI Chat', icon: MessageSquare },
    ...(isAuthenticated ? [{ path: '/mock-interview', label: 'Interview', icon: User }] : []),
  ];

  const totalResults = searchResults.chats.length + searchResults.resumes.length + searchResults.jobs.length;

  return (
    <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100/50 shadow-sm transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 md:h-20">
          
          {/* Logo Section */}
          <div className="flex items-center gap-8">
            <Link to="/" className="group">
              {/* Text Only Branding - Clean & Bold */}
              <span className="text-xl font-bold tracking-tight text-gray-900 group-hover:text-purple-600 transition-colors font-sans">
                PathFinder
              </span>
            </Link>

            {/* Desktop Navigation (Pill Shape) */}
            <div className="hidden md:flex items-center gap-1 bg-gray-100/50 p-1 rounded-full border border-gray-100">
              {navLinks.map((link) => {
                const active = isActive(link.path);
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${
                      active
                        ? 'bg-white text-purple-600 shadow-sm shadow-gray-200'
                        : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200/50'
                    }`}
                  >
                    {active && <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse"></span>}
                    {link.label}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-3">
            
            {/* Search Trigger */}
            {isAuthenticated && (
              <div className="relative" ref={searchRef}>
                <button
                  onClick={() => setShowSearch(!showSearch)}
                  className={`p-2.5 rounded-full transition-all duration-200 ${
                    showSearch ? 'bg-purple-100 text-purple-600' : 'text-gray-500 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Search size={20} />
                </button>

                {/* Floating Search Panel */}
                {showSearch && (
                  <div className="absolute right-0 top-full mt-4 w-80 md:w-96 bg-white/90 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/50 ring-1 ring-black/5 overflow-hidden animate-fade-in-up origin-top-right">
                    <div className="p-3 border-b border-gray-100 bg-gray-50/50">
                      <div className="relative">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-purple-500" />
                        <input
                          type="text"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          placeholder="Type to search..."
                          className="w-full pl-9 pr-8 py-2.5 bg-white border border-gray-200 rounded-xl text-sm outline-none focus:border-purple-300 focus:ring-4 focus:ring-purple-50/50 transition-all placeholder:text-gray-400"
                          autoFocus
                        />
                        {searchQuery && (
                          <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                            <X size={14} />
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="max-h-[60vh] overflow-y-auto p-2 custom-scrollbar">
                      {searchLoading ? (
                        <div className="py-8 text-center">
                          <div className="animate-spin w-5 h-5 border-2 border-purple-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                          <span className="text-xs text-gray-400">Searching...</span>
                        </div>
                      ) : totalResults > 0 ? (
                        <div className="space-y-4">
                          {/* Group: Chats */}
                          {searchResults.chats.length > 0 && (
                            <div>
                              <h4 className="px-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Recent Chats</h4>
                              {searchResults.chats.map(chat => (
                                <button key={chat._id} onClick={() => handleSearchResultClick('chat', chat)} className="w-full text-left p-2.5 hover:bg-purple-50 rounded-xl transition-colors flex items-center gap-3 group">
                                  <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg group-hover:bg-indigo-100 transition-colors">
                                    <MessageSquare size={14} />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-sm font-medium text-gray-900 truncate">{chat.session_name || 'Conversation'}</p>
                                    <p className="text-xs text-gray-500 truncate">{new Date(chat.updated_at).toLocaleDateString()}</p>
                                  </div>
                                </button>
                              ))}
                            </div>
                          )}
                          {/* Group: Jobs */}
                          {searchResults.jobs.length > 0 && (
                            <div>
                              <h4 className="px-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Jobs</h4>
                              {searchResults.jobs.map(rec => (
                                <button key={rec._id} onClick={() => handleSearchResultClick('job', rec)} className="w-full text-left p-2.5 hover:bg-purple-50 rounded-xl transition-colors flex items-center gap-3 group">
                                  <div className="p-2 bg-emerald-50 text-emerald-600 rounded-lg group-hover:bg-emerald-100 transition-colors">
                                    <Briefcase size={14} />
                                  </div>
                                  <div className="min-w-0">
                                    <p className="text-sm font-medium text-gray-900 truncate">{rec.jobs?.[0]?.title || 'Recommendations'}</p>
                                    <p className="text-xs text-gray-500 truncate">{rec.jobs?.length} Matches</p>
                                  </div>
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      ) : searchQuery.length > 2 ? (
                        <div className="py-8 text-center text-gray-400 text-sm">No results found.</div>
                      ) : (
                        <div className="py-8 text-center text-gray-400 text-sm">Start typing to search...</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* User Profile */}
            {isAuthenticated && user ? (
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setShowUserDropdown(!showUserDropdown)}
                  className={`flex items-center gap-2 pl-1 pr-3 py-1 rounded-full border transition-all duration-200 ${
                    showUserDropdown 
                      ? 'bg-purple-50 border-purple-200 ring-2 ring-purple-100' 
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                    {user.name?.charAt(0).toUpperCase()}
                  </div>
                  <ChevronDown size={14} className={`text-gray-400 transition-transform ${showUserDropdown ? 'rotate-180' : ''}`} />
                </button>

                {/* User Dropdown */}
                {showUserDropdown && (
                  <div className="absolute right-0 top-full mt-3 w-64 bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl shadow-purple-500/10 border border-white/50 ring-1 ring-black/5 overflow-hidden animate-fade-in-up origin-top-right">
                    <div className="p-4 border-b border-gray-100">
                      <p className="text-sm font-semibold text-gray-900">{user.name}</p>
                      <p className="text-xs text-gray-500 truncate">{user.email}</p>
                    </div>
                    
                    <div className="p-2 space-y-0.5">
                      <Link to="/history" onClick={() => setShowUserDropdown(false)} className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-xl transition-colors">
                        <History size={16} /> History
                      </Link>
                      <Link to="/learning-path" onClick={() => setShowUserDropdown(false)} className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-xl transition-colors">
                        <GraduationCap size={16} /> Learning Path
                      </Link>
                      <Link to="/mock-interview/history" onClick={() => setShowUserDropdown(false)} className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-xl transition-colors">
                        <FileText size={16} /> Interviews
                      </Link>
                    </div>

                    <div className="p-2 border-t border-gray-100">
                      <button onClick={handleLogout} className="flex items-center gap-3 w-full px-3 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 rounded-xl transition-colors">
                        <LogOut size={16} /> Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="bg-gray-900 text-white text-sm font-medium px-5 py-2.5 rounded-xl hover:bg-black hover:shadow-lg transition-all transform hover:-translate-y-0.5"
              >
                Log In
              </Link>
            )}

            {/* Mobile Menu Toggle (Visible only on small screens) */}
            <button className="md:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg">
               <Menu size={24} />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;