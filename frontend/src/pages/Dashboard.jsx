import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, Briefcase, GraduationCap, 
  Brain, TrendingUp, AlertCircle, BookOpen, 
  CheckCircle2, Clock, MapPin, DollarSign, 
  ChevronRight, Award, User, RefreshCw, Star,
  Sparkles, ArrowUpRight, Building2
} from 'lucide-react';
import { apiService } from '../services/api';

// --- Utilities (Preserved) ---
const formatIndianSalary = (salary) => {
  if (!salary) return 'Not Disclosed';
  const str = String(salary).toLowerCase();
  if (str.includes('₹') || str.includes('lpa')) return salary;
  const matches = str.match(/[\d,]+/g);
  if (!matches) return '₹8-18 LPA';
  if (str.includes('$') || str.includes('usd') || str.includes('k')) {
    const nums = matches.map(n => parseInt(n.replace(/,/g, '')));
    if (nums.length >= 1) {
      const min = Math.round((nums[0] * 1000 * 83) / 100000); 
      const max = nums[1] ? Math.round((nums[1] * 1000 * 83) / 100000) : min + 5;
      return `₹${min}-${max} LPA`;
    }
  }
  return '₹10-25 LPA'; 
};

const formatIndianLocation = (location) => {
  if (!location) return 'Remote';
  const lower = location.toLowerCase();
  const cities = ['bangalore', 'mumbai', 'delhi', 'hyderabad', 'pune', 'chennai', 'gurgaon', 'noida', 'india'];
  if (cities.some(city => lower.includes(city))) return location;
  if (lower.includes('remote')) return 'Remote';
  return 'Bangalore/Mumbai';
};

// --- Styled Components ---

const BackgroundBlobs = () => (
  <>
    <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob pointer-events-none"></div>
    <div className="absolute top-[20%] left-[-10%] w-[400px] h-[400px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000 pointer-events-none"></div>
    <div className="absolute bottom-[-10%] right-[20%] w-[300px] h-[300px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-4000 pointer-events-none"></div>
  </>
);

const SectionCard = ({ title, icon: Icon, children, className = "", action }) => (
  <div className={`bg-white/70 backdrop-blur-md rounded-2xl border border-white shadow-sm shadow-purple-100/50 overflow-hidden flex flex-col h-full hover:shadow-md transition-all duration-300 ${className}`}>
    <div className="px-6 py-4 border-b border-gray-50 flex justify-between items-center">
      <div className="flex items-center gap-2">
        <Icon size={16} className="text-purple-600" />
        <h3 className="font-bold text-gray-800 text-xs uppercase tracking-wider">{title}</h3>
      </div>
      {action}
    </div>
    <div className="p-6 flex-1">
      {children}
    </div>
  </div>
);

const Badge = ({ children, color = "indigo" }) => {
  const colors = {
    indigo: "bg-indigo-50 text-indigo-700 border-indigo-100",
    green: "bg-emerald-50 text-emerald-700 border-emerald-100",
    gray: "bg-gray-50 text-gray-600 border-gray-100",
  };
  return (
    <span className={`px-2.5 py-1 rounded-full text-[10px] font-semibold border ${colors[color] || colors.indigo} inline-flex items-center gap-1`}>
      {children}
    </span>
  );
};

const TimelineItem = ({ title, subtitle, date, description, last }) => (
  <div className="relative pl-6 pb-8 group last:pb-0">
    {!last && <div className="absolute left-[7px] top-2 bottom-0 w-[1px] bg-gray-200 group-hover:bg-purple-200 transition-colors"></div>}
    <div className="absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full bg-white border-2 border-gray-300 group-hover:border-purple-500 shadow-sm transition-colors z-10"></div>
    
    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-1">
      <h4 className="text-sm font-semibold text-gray-900 group-hover:text-purple-700 transition-colors">{title}</h4>
      {date && <span className="text-[10px] font-mono text-gray-400 bg-gray-50 px-2 py-0.5 rounded border border-gray-100 whitespace-nowrap">{date}</span>}
    </div>
    
    {subtitle && (
      <p className="text-xs text-gray-600 font-medium mb-2 flex items-center gap-1">
        <Building2 size={10} className="text-gray-400" /> {subtitle}
      </p>
    )}
    
    {description && (
      <p className="text-xs text-gray-500 leading-relaxed line-clamp-2 pl-1 border-l-2 border-transparent group-hover:border-purple-100 transition-all">
        {description}
      </p>
    )}
  </div>
);

// --- Main Component ---

const Dashboard = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const storedData = localStorage.getItem('resumeData');
      const storedInsights = localStorage.getItem('resumeInsights');
      const storedJobs = localStorage.getItem('jobRecommendations');
      
      if (storedData) {
        const parsedData = JSON.parse(storedData);
        const insights = storedInsights ? JSON.parse(storedInsights) : {};
        const jobs = storedJobs ? JSON.parse(storedJobs) : [];
        
        setData({
          name: parsedData.name || 'Candidate',
          extractedSkills: parsedData.skills || [],
          education: parsedData.education || [],
          experience: parsedData.experience || [],
          insights: insights,
          recommendedJobs: jobs,
        });
        setLoading(false);
        return;
      }
      
      const response = await apiService.getDashboardData();
      setData(response);
    } catch (err) {
      setError('No resume data found. Please upload a resume first.');
    } finally {
      setLoading(false);
    }
  };

  const EmptyState = ({ icon: Icon, text }) => (
    <div className="h-full flex flex-col items-center justify-center py-10 opacity-60">
      <div className="p-4 bg-gray-50 rounded-full mb-3 border border-gray-100">
         <Icon size={20} className="text-gray-400" />
      </div>
      <p className="text-xs font-medium text-gray-400">{text}</p>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-white relative overflow-hidden flex flex-col items-center justify-center font-sans">
        <BackgroundBlobs />
        <div className="relative z-10 text-center">
          <div className="w-16 h-16 border-4 border-purple-100 border-t-purple-600 rounded-full animate-spin mx-auto mb-6"></div>
          <h2 className="text-2xl font-light text-gray-900 mb-2">Loading Dashboard</h2>
          <p className="text-gray-500 text-sm">Synchronizing your career profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
     return (
        <div className="min-h-screen bg-white flex items-center justify-center p-4">
           <div className="text-center">
              <p className="text-red-500 mb-4">{error}</p>
              <button onClick={() => navigate('/resume-upload')} className="text-purple-600 underline">Upload Resume</button>
           </div>
        </div>
     )
  }

  const dashboardData = data || {};
  const insights = dashboardData.insights || {};
  const safeStr = (val, key) => (typeof val === 'string' ? val : (val?.[key] || ''));

  return (
    <div className="min-h-screen bg-white relative font-sans text-gray-800 selection:bg-purple-100 overflow-x-hidden">
      <BackgroundBlobs />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 pb-6 border-b border-gray-100">
          <div>
             <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-50 border border-green-100 rounded-full mb-3">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                <span className="text-[10px] font-bold text-green-700 uppercase tracking-wider">Analysis Active</span>
             </div>
             <h1 className="text-3xl md:text-4xl font-light text-gray-900 mb-1">
               Career <span className="font-medium">Dashboard</span>
             </h1>
             <p className="text-gray-500 text-sm">
               Welcome back, <span className="font-medium text-gray-900">{dashboardData.name}</span>.
             </p>
          </div>
          <button 
            onClick={fetchDashboardData}
            className="flex items-center gap-2 px-4 py-2 bg-white/80 border border-gray-200 text-gray-600 text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-white hover:border-purple-300 hover:text-purple-600 transition-all shadow-sm"
          >
            <RefreshCw size={14} /> Sync Data
          </button>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* LEFT COLUMN (3 cols) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* 1. ATS Score Card */}
            <SectionCard title="ATS Compatibility" icon={TrendingUp} className="min-h-[300px]">
              {dashboardData.recommendedJobs?.length > 0 ? (
                (() => {
                  const jobsWithATS = dashboardData.recommendedJobs.filter(j => j.ats_score);
                  if (!jobsWithATS.length) return <EmptyState icon={TrendingUp} text="No ATS data available." />;
                  
                  const avgScore = Math.round(jobsWithATS.reduce((s, j) => s + (j.ats_score.overall_score || 0), 0) / jobsWithATS.length);
                  
                  return (
                    <div className="flex flex-col items-center justify-center h-full py-4">
                       <div className="relative w-40 h-40 flex items-center justify-center mb-6">
                          {/* SVG Ring */}
                          <svg className="absolute inset-0 w-full h-full -rotate-90">
                             <circle cx="50%" cy="50%" r="70" fill="none" stroke="#f3f4f6" strokeWidth="12" />
                             <circle cx="50%" cy="50%" r="70" fill="none" stroke="url(#gradient)" strokeWidth="12" 
                               strokeDasharray={`${2 * Math.PI * 70}`} 
                               strokeDashoffset={`${2 * Math.PI * 70 * (1 - avgScore / 100)}`} 
                               strokeLinecap="round"
                             />
                             <defs>
                               <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                 <stop offset="0%" stopColor="#9333ea" />
                                 <stop offset="100%" stopColor="#4f46e5" />
                               </linearGradient>
                             </defs>
                          </svg>
                          <div className="text-center z-10">
                             <span className="text-4xl font-light text-gray-900 tracking-tighter">{avgScore}</span>
                             <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider mt-1">Avg Score</span>
                          </div>
                       </div>
                       
                       <div className="w-full grid grid-cols-2 gap-3">
                          <div className="p-3 bg-gray-50/50 rounded-xl text-center border border-gray-100">
                             <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">Status</div>
                             <div className="text-sm font-bold text-gray-800">
                               {avgScore >= 75 ? 'Excellent' : avgScore >= 50 ? 'Fair' : 'Needs Work'}
                             </div>
                          </div>
                          <div className="p-3 bg-gray-50/50 rounded-xl text-center border border-gray-100">
                             <div className="text-[10px] text-gray-400 font-bold uppercase mb-1">Analyzed</div>
                             <div className="text-sm font-bold text-gray-800">{jobsWithATS.length} Jobs</div>
                          </div>
                       </div>
                    </div>
                  );
                })()
              ) : (
                <EmptyState icon={TrendingUp} text="Upload resume to see scores." />
              )}
            </SectionCard>

            {/* 2. Skills Cloud */}
            <SectionCard title="Detected Skills" icon={Award}>
               {dashboardData.extractedSkills?.length > 0 ? (
                 <div className="h-full flex flex-col">
                    <div className="flex flex-wrap gap-2 content-start mb-4">
                      {dashboardData.extractedSkills.slice(0, 15).map((skill, i) => (
                         <Badge key={i} color="gray">
                           {typeof skill === 'string' ? skill : skill.name}
                         </Badge>
                      ))}
                      {dashboardData.extractedSkills.length > 15 && (
                         <span className="text-xs text-purple-600 font-medium py-1 px-1 cursor-pointer hover:underline">
                            +{dashboardData.extractedSkills.length - 15} more
                         </span>
                      )}
                    </div>
                    <div className="mt-auto pt-4 border-t border-gray-50 flex justify-between items-center text-xs text-gray-400">
                       <span>Keyword Match</span>
                       <span className="font-bold text-gray-900">{dashboardData.extractedSkills.length} Found</span>
                    </div>
                 </div>
               ) : (
                 <EmptyState icon={Award} text="No skills detected." />
               )}
            </SectionCard>
          </div>

          {/* MIDDLE COLUMN (5 cols) - Recommendations & Insights */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* 3. Job Recommendations */}
            <div className="space-y-4">
              <div className="flex justify-between items-end px-1">
                 <div>
                    <h3 className="text-lg font-light text-gray-900">Recommended <span className="font-medium">Roles</span></h3>
                    <p className="text-xs text-gray-500">Based on your skills profile</p>
                 </div>
                 {dashboardData.recommendedJobs?.length > 3 && (
                   <button onClick={() => navigate('/jobs')} className="text-xs font-bold text-purple-600 flex items-center gap-1 hover:underline">
                      View All <ArrowUpRight size={14} />
                   </button>
                 )}
              </div>

              {dashboardData.recommendedJobs?.length > 0 ? (
                 <div className="space-y-3">
                    {dashboardData.recommendedJobs.slice(0, 3).map((job, i) => {
                       const title = safeStr(job, 'title') || safeStr(job, 'job_title') || job;
                       const company = typeof job === 'object' ? (job.company || job.organization) : '';
                       const score = typeof job === 'object' ? (job.match_score || 0) : 0;
                       
                       return (
                          <div key={i} className="group bg-white rounded-xl border border-gray-100 p-4 hover:border-purple-200 hover:shadow-lg hover:shadow-purple-50 hover:-translate-y-1 transition-all duration-300 cursor-pointer">
                             <div className="flex justify-between items-start mb-2">
                                <div>
                                   <h4 className="font-bold text-gray-800 text-sm line-clamp-1 group-hover:text-purple-700">{title}</h4>
                                   <p className="text-xs text-gray-500">{company}</p>
                                </div>
                                {score > 0 && (
                                   <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${score >= 80 ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'}`}>
                                      {score}%
                                   </span>
                                )}
                             </div>
                             <div className="flex gap-3 text-[10px] text-gray-400 mt-3">
                                <span className="flex items-center gap-1"><MapPin size={10} /> {formatIndianLocation(job.location)}</span>
                                <span className="flex items-center gap-1"><DollarSign size={10} /> {formatIndianSalary(job.salary)}</span>
                             </div>
                          </div>
                       )
                    })}
                 </div>
              ) : (
                 <div className="bg-white/50 border border-dashed border-gray-300 rounded-xl p-8 text-center">
                    <p className="text-gray-400 text-xs">No job matches found yet.</p>
                 </div>
              )}
            </div>

            {/* 4. AI Insights */}
            <SectionCard title="AI Career Insights" icon={Brain}>
               {insights && Object.keys(insights).length > 0 ? (
                 <div className="space-y-6">
                    {insights.improvements?.length > 0 && (
                      <div>
                        <h4 className="text-[10px] font-bold text-red-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                           <AlertCircle size={12} /> Critical Fixes
                        </h4>
                        <ul className="space-y-2">
                           {insights.improvements.slice(0, 2).map((imp, i) => (
                              <li key={i} className="text-xs text-gray-600 bg-red-50/50 p-3 rounded-lg border border-red-50 leading-relaxed">
                                 {imp}
                              </li>
                           ))}
                        </ul>
                      </div>
                    )}
                    {insights.strengths?.length > 0 && (
                       <div>
                         <h4 className="text-[10px] font-bold text-green-600 uppercase tracking-wider mb-3 flex items-center gap-2">
                            <Sparkles size={12} /> Top Strengths
                         </h4>
                         <div className="flex flex-wrap gap-2">
                           {insights.strengths.slice(0, 4).map((s, i) => (
                              <Badge key={i} color="green">{s}</Badge>
                           ))}
                         </div>
                       </div>
                    )}
                 </div>
               ) : (
                 <EmptyState icon={Brain} text="No insights generated." />
               )}
            </SectionCard>

          </div>

          {/* RIGHT COLUMN (3 cols) - Timeline */}
          <div className="lg:col-span-3 space-y-6">
             <SectionCard title="Experience" icon={Briefcase}>
                {dashboardData.experience?.length > 0 ? (
                   <div className="pt-2">
                      {dashboardData.experience.slice(0, 3).map((exp, i) => (
                         <TimelineItem 
                            key={i}
                            title={safeStr(exp, 'role') || safeStr(exp, 'position') || exp}
                            subtitle={typeof exp === 'object' ? exp.company : ''}
                            date={typeof exp === 'object' ? exp.duration : ''}
                            last={i === Math.min(dashboardData.experience.length, 3) - 1}
                         />
                      ))}
                   </div>
                ) : (
                   <EmptyState icon={Briefcase} text="No experience listed." />
                )}
             </SectionCard>

             <SectionCard title="Education" icon={GraduationCap}>
                {dashboardData.education?.length > 0 ? (
                   <div className="pt-2">
                      {dashboardData.education.slice(0, 2).map((edu, i) => (
                         <TimelineItem 
                            key={i}
                            title={safeStr(edu, 'degree') || safeStr(edu, 'qualification') || edu}
                            subtitle={typeof edu === 'object' ? (edu.institution || edu.school) : ''}
                            date={typeof edu === 'object' ? (edu.year || edu.graduation_year) : ''}
                            last={i === Math.min(dashboardData.education.length, 2) - 1}
                         />
                      ))}
                   </div>
                ) : (
                   <EmptyState icon={GraduationCap} text="No education listed." />
                )}
             </SectionCard>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Dashboard;