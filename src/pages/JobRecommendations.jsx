import React, { useState, useEffect } from 'react';
import { 
  Briefcase, MapPin, DollarSign, Star, 
  ArrowRight, Building2, CheckCircle2, 
  AlertCircle, TrendingUp, Sparkles,
  LayoutGrid, List, Search, Filter,
  ExternalLink, Clock
} from 'lucide-react';
import { apiService } from '../services/api';
// Assuming these exist, otherwise standard divs are used in the fallback
import Loading from '../components/Loading';
import Error from '../components/Error';

// --- Utilities (Preserved) ---
const stripHtml = (html) => {
  if (!html) return '';
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  let text = tmp.textContent || tmp.innerText || '';
  text = text.replace(/\s+/g, ' ').trim();
  if (text.length > 200) {
    text = text.substring(0, 200) + '...';
  }
  return text;
};

const formatIndianLocation = (location) => {
  if (!location) return 'India (Remote)';
  const locationLower = location.toLowerCase();
  const indianCities = ['bangalore', 'mumbai', 'delhi', 'hyderabad', 'pune', 'chennai', 
    'kolkata', 'ahmedabad', 'gurgaon', 'noida', 'bengaluru', 'gurugram', 'india'];
  if (indianCities.some(city => locationLower.includes(city))) return location;
  if (locationLower.includes('remote') || locationLower.includes('work from home')) return 'India (Remote)';
  return 'Bangalore/Mumbai/Hyderabad';
};

const formatIndianSalary = (salary) => {
  if (!salary) return null;
  const salaryStr = String(salary).toLowerCase();
  if (salaryStr.includes('₹') || salaryStr.includes('inr') || salaryStr.includes('lpa') || salaryStr.includes('lakhs')) return salary;
  if (!isNaN(salary) && Number(salary) > 0) {
    if (Number(salary) > 10000) {
      const inrLakhs = Math.round((Number(salary) * 83) / 100000); 
      return `₹${inrLakhs} LPA`;
    }
  }
  const numberMatch = salaryStr.match(/[\d,]+/g);
  if (!numberMatch) return null; 
  if (salaryStr.includes('$') || salaryStr.includes('usd')) {
    const numbers = numberMatch.map(n => parseInt(n.replace(/,/g, '')));
    if (numbers.length >= 2) {
      const minINR = Math.round(numbers[0] * 83 / 100000); 
      const maxINR = Math.round(numbers[1] * 83 / 100000);
      return `₹${minINR}-${maxINR} LPA`;
    } else if (numbers.length === 1) {
      const inrLakhs = Math.round(numbers[0] * 83 / 100000);
      return `₹${inrLakhs} LPA`;
    }
  }
  return null; 
};

// --- Components ---

const BackgroundBlobs = () => (
  <>
    <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob pointer-events-none"></div>
    <div className="absolute top-[20%] left-[-10%] w-[400px] h-[400px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000 pointer-events-none"></div>
    <div className="absolute bottom-[-10%] right-[20%] w-[300px] h-[300px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-4000 pointer-events-none"></div>
  </>
);

const JobRecommendations = () => {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredJobs(jobs);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = jobs.filter(job => 
        job.title?.toLowerCase().includes(query) ||
        job.company?.toLowerCase().includes(query) ||
        job.location?.toLowerCase().includes(query) ||
        job.description?.toLowerCase().includes(query) ||
        job.skills?.some(skill => 
          (typeof skill === 'string' ? skill : skill.name)?.toLowerCase().includes(query)
        )
      );
      setFilteredJobs(filtered);
    }
  }, [searchQuery, jobs]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const storedJobs = localStorage.getItem('jobRecommendations');
      if (storedJobs) {
        const parsedJobs = JSON.parse(storedJobs);
        if (Array.isArray(parsedJobs) && parsedJobs.length > 0) {
          setJobs(parsedJobs);
          setLoading(false);
          return;
        }
      }
      
      const response = await apiService.getJobs();
      const jobsData = Array.isArray(response) ? response : (response.recommended_jobs || response.jobs || []);
      
      if (jobsData.length > 0) {
        await apiService.saveJobRecommendations(jobsData);
      }
      
      setJobs(jobsData);
      setFilteredJobs(jobsData);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || 'Failed to load job recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white relative overflow-hidden flex flex-col items-center justify-center font-sans">
        <BackgroundBlobs />
        <div className="relative z-10 text-center">
          <div className="w-16 h-16 border-4 border-purple-100 border-t-purple-600 rounded-full animate-spin mx-auto mb-6"></div>
          <h2 className="text-2xl font-light text-gray-900 mb-2">Curating Opportunities</h2>
          <p className="text-gray-500 text-sm">AI is matching jobs to your profile...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
     return (
        <div className="min-h-screen bg-white flex items-center justify-center p-4">
           <div className="text-center">
              <p className="text-red-500 mb-4">{error}</p>
              <button onClick={fetchJobs} className="text-purple-600 underline">Retry</button>
           </div>
        </div>
     );
  }

  return (
    <div className="min-h-screen bg-white relative font-sans text-gray-800 selection:bg-purple-100">
      <BackgroundBlobs />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 pb-6 border-b border-gray-100">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 border border-purple-100 rounded-full mb-3">
              <Sparkles size={12} className="text-purple-600 fill-purple-200" />
              <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider">AI Recommended</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-light text-gray-900 mb-1">
              Job <span className="font-medium">Marketplace</span>
            </h1>
            <p className="text-gray-500 text-sm max-w-2xl">
              Curated roles matched to your unique skill profile.
            </p>
          </div>
          
          <div className="flex items-center gap-4">
             <div className="hidden md:block text-right">
                <span className="block text-2xl font-light text-gray-900">{filteredJobs.length}</span>
                <span className="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Matches Found</span>
             </div>
             <div className="h-8 w-[1px] bg-gray-200 hidden md:block"></div>
             <div className="flex bg-gray-100 p-1 rounded-lg">
                <button 
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-all ${viewMode === 'grid' ? 'bg-white text-purple-600 shadow-sm' : 'text-gray-400 hover:text-gray-600'}`}
                >
                  <LayoutGrid size={18} />
                </button>
                <button 
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-all ${viewMode === 'list' ? 'bg-white text-purple-600 shadow-sm' : 'text-gray-400 hover:text-gray-600'}`}
                >
                  <List size={18} />
                </button>
             </div>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-gray-200 p-2 mb-8 sticky top-4 z-20 flex gap-2">
           <div className="relative flex-1">
             <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
             <input
               type="text"
               placeholder="Search by title, company, or skill..."
               value={searchQuery}
               onChange={(e) => setSearchQuery(e.target.value)}
               className="w-full pl-12 pr-4 py-3 bg-transparent rounded-xl focus:outline-none focus:bg-gray-50 transition-colors text-sm"
             />
             {searchQuery && (
               <button
                 onClick={() => setSearchQuery('')}
                 className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs uppercase font-bold"
               >
                 Clear
               </button>
             )}
           </div>
           <button className="hidden md:flex items-center gap-2 px-6 py-2 bg-gray-50 text-gray-600 rounded-xl hover:bg-gray-100 transition-colors text-sm font-medium border border-transparent hover:border-gray-200">
              <Filter size={16} />
              <span>Filters</span>
           </button>
        </div>

        {/* Content Grid */}
        {filteredJobs.length === 0 ? (
          searchQuery ? (
            <div className="flex flex-col items-center justify-center py-20 bg-white/50 rounded-2xl border border-dashed border-gray-200">
              <div className="bg-gray-50 p-4 rounded-full mb-4">
                <Search size={24} className="text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900">No matches found</h3>
              <p className="text-gray-500 text-sm mt-1">Try adjusting your search terms.</p>
              <button 
                onClick={() => setSearchQuery('')}
                className="mt-6 px-6 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 transition-colors"
              >
                Clear Search
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-20 bg-white/50 rounded-2xl border border-dashed border-gray-200">
               <Briefcase size={32} className="text-gray-300 mb-4" />
               <p className="text-gray-500">No recommendations available yet.</p>
            </div>
          )
        ) : (
          <div className={viewMode === 'grid' ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" : "flex flex-col gap-4"}>
            {filteredJobs.map((job, index) => (
              <JobCard key={index} job={job} viewMode={viewMode} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const JobCard = ({ job, viewMode }) => {
  // Safe Data Extraction
  const jobTitle = typeof job === 'string' ? job : (job.job_title || job.title || 'Unknown Position');
  const company = job.company || job.company_type || 'Confidential Company';
  const rawLocation = job.location || job.remote_option || '';
  const location = formatIndianLocation(rawLocation);
  const rawSalary = job.salary_range || job.salary || job.salary_max;
  const salaryRange = rawSalary ? formatIndianSalary(rawSalary) : null;
  const rawDescription = job.reason || job.description || job.summary || '';
  const description = stripHtml(rawDescription);
  const applyUrl = job.url || '';
  const jobSource = job.source || 'Database';
  const postedDate = job.posted_date || job.created_at || '';
  const jobType = job.job_type || 'Full-time';
  const matchPercentage = job.match_score || job.matchPercentage || job.match || 0;
  const matchedSkills = job.matched_skills || job.skills || [];

  const handleApply = () => {
    if (applyUrl) {
      window.open(applyUrl, '_blank', 'noopener,noreferrer');
    }
  };

  // --- LIST VIEW ---
  if (viewMode === 'list') {
    return (
      <div className="group bg-white rounded-xl p-5 border border-gray-100 hover:border-purple-200 hover:shadow-lg hover:shadow-purple-50 transition-all duration-300 flex flex-col md:flex-row gap-6 items-start md:items-center">
         
         {/* Logo / Icon Placeholder */}
         <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-gray-50 rounded-lg flex items-center justify-center border border-gray-100 text-gray-400 group-hover:bg-purple-50 group-hover:text-purple-600 transition-colors">
               <Building2 size={24} />
            </div>
         </div>

         {/* Main Info */}
         <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
               <h3 className="text-base font-bold text-gray-900 truncate group-hover:text-purple-600 transition-colors cursor-pointer" onClick={handleApply}>
                 {jobTitle}
               </h3>
               {jobSource !== 'Database' && (
                 <span className="flex-shrink-0 w-2 h-2 rounded-full bg-green-500" title="Live Job"></span>
               )}
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-gray-500">
               <span className="font-medium text-gray-700">{company}</span>
               {location && (
                 <span className="flex items-center gap-1"><MapPin size={12} /> {location}</span>
               )}
               {salaryRange && (
                 <span className="flex items-center gap-1 text-emerald-600 font-medium bg-emerald-50 px-1.5 py-0.5 rounded">
                   <DollarSign size={10} /> {salaryRange}
                 </span>
               )}
               <span className="flex items-center gap-1"><Clock size={12} /> {jobType}</span>
            </div>
         </div>

         {/* Match & Action */}
         <div className="flex items-center gap-6 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 border-gray-50 pt-4 md:pt-0">
            {matchPercentage > 0 && (
               <div className="text-right">
                  <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-0.5">Match</div>
                  <div className={`text-lg font-light ${matchPercentage >= 80 ? 'text-green-600' : 'text-indigo-600'}`}>
                    {matchPercentage}%
                  </div>
               </div>
            )}
            <button 
              onClick={handleApply}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                applyUrl 
                ? 'bg-gray-900 text-white hover:bg-black shadow-sm' 
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              Apply
            </button>
         </div>
      </div>
    );
  }

  // --- GRID VIEW ---
  return (
    <div className="group bg-white rounded-2xl border border-gray-100 hover:border-purple-200 hover:shadow-xl hover:shadow-purple-50/50 hover:-translate-y-1 transition-all duration-300 flex flex-col h-full relative overflow-hidden">
      
      {/* Header */}
      <div className="p-6 pb-4">
        <div className="flex justify-between items-start mb-4">
           <div className="w-10 h-10 bg-gray-50 rounded-lg flex items-center justify-center border border-gray-100 text-gray-400 group-hover:bg-purple-50 group-hover:text-purple-600 transition-colors">
              <Building2 size={20} />
           </div>
           {matchPercentage > 0 && (
              <span className={`text-[10px] font-bold px-2 py-1 rounded-full border ${
                 matchPercentage >= 80 
                 ? 'bg-green-50 text-green-700 border-green-100' 
                 : 'bg-indigo-50 text-indigo-700 border-indigo-100'
              }`}>
                 {matchPercentage}% Match
              </span>
           )}
        </div>
        
        <h3 className="text-lg font-bold text-gray-900 leading-tight mb-1 line-clamp-2 group-hover:text-purple-600 transition-colors">
          {jobTitle}
        </h3>
        <p className="text-sm text-gray-500 font-medium mb-4">{company}</p>
        
        <div className="flex flex-wrap gap-2 text-xs">
           {location && (
             <span className="inline-flex items-center gap-1 text-gray-500 bg-gray-50 px-2 py-1 rounded border border-gray-100">
               <MapPin size={10} /> {location}
             </span>
           )}
           {salaryRange && (
             <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-1 rounded border border-emerald-100 font-medium">
               <DollarSign size={10} /> {salaryRange}
             </span>
           )}
        </div>
      </div>

      {/* Description Preview */}
      <div className="px-6 py-2 flex-1">
         {description && (
           <p className="text-xs text-gray-500 leading-relaxed line-clamp-3">
             {description}
           </p>
         )}
      </div>

      {/* Footer */}
      <div className="p-6 pt-4 mt-auto border-t border-gray-50">
         {matchedSkills.length > 0 && (
            <div className="mb-4">
               <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Matching Skills</p>
               <div className="flex flex-wrap gap-1">
                  {matchedSkills.slice(0, 3).map((skill, i) => (
                    <span key={i} className="px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-[10px] font-medium">
                      {typeof skill === 'string' ? skill : skill.name}
                    </span>
                  ))}
                  {matchedSkills.length > 3 && (
                     <span className="px-1.5 py-0.5 text-gray-400 text-[10px] font-medium">+{matchedSkills.length - 3}</span>
                  )}
               </div>
            </div>
         )}
         
         <button 
           onClick={handleApply}
           className={`w-full py-3 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 transition-all ${
             applyUrl 
             ? 'bg-gray-900 text-white hover:bg-black shadow-lg shadow-gray-200' 
             : 'bg-gray-100 text-gray-400 cursor-not-allowed'
           }`}
         >
           {applyUrl ? (
             <>Apply Now <ArrowRight size={14} /></>
           ) : (
             'No Link Available'
           )}
         </button>
      </div>

    </div>
  );
};

export default JobRecommendations;