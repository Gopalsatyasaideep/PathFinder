import { Link } from 'react-router-dom';
import { FileText, Target, Briefcase, Map, Bot, ArrowRight, Sparkles, UploadCloud } from 'lucide-react';

/**
 * Landing Page - "Think Tech" Redesign
 * Minimalist, spacious, and modern aesthetic with abstract purple accents.
 */
const Landing = () => {
  const features = [
    {
      title: 'Resume Analysis',
      description: 'Smart parsing to extract skills, experience, and qualifications from your resume.',
      icon: FileText,
      linkText: 'Analyze Now',
      path: '/upload'
    },
    {
      title: 'Skill Gap Detection',
      description: 'Compare your skills against target roles to identify what you need to learn.',
      icon: Target,
      linkText: 'Check Skills',
      path: '/dashboard'
    },
    {
      title: 'Real Job Search',
      description: 'Live job postings from top platforms, matched to your resume and skills.',
      icon: Briefcase,
      linkText: 'Search Jobs',
      path: '/jobs'
    },
    {
      title: 'Learning Path Guidance',
      description: 'Personalized learning roadmaps with courses and resources to advance your career.',
      icon: Map,
      linkText: 'View Paths',
      path: '/learning-path'
    },
    {
      title: 'AI Career Assistant',
      description: 'Context-aware chatbot that remembers your conversation and provides career guidance.',
      icon: Bot,
      linkText: 'Chat Now',
      path: '/chatbot'
    },
  ];

  // Background Component
  const BackgroundBlobs = () => (
    <>
      <div className="absolute top-[-10%] right-[-5%] w-[600px] h-[600px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob pointer-events-none"></div>
      <div className="absolute top-[20%] left-[-10%] w-[500px] h-[500px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[20%] w-[400px] h-[400px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-4000 pointer-events-none"></div>
    </>
  );

  return (
    <div className="min-h-screen bg-white font-sans relative overflow-hidden text-gray-800 selection:bg-purple-100">
      <BackgroundBlobs />
      
      {/* --- HERO SECTION --- */}
      <div className="relative z-10 pt-24 pb-16 px-4 sm:px-6 lg:px-8 text-center max-w-5xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 border border-purple-100 rounded-full mb-6 animate-fade-in-down">
           <Sparkles size={14} className="text-purple-600 fill-purple-200" />
           <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider">AI Powered Career Growth</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-light tracking-tight text-gray-900 mb-6 leading-tight animate-fade-in-up">
          Intelligent <span className="font-medium bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-indigo-600">Career Guidance</span>
        </h1>
        
        <p className="text-lg md:text-xl text-gray-500 max-w-2xl mx-auto font-light leading-relaxed mb-10 animate-fade-in-up delay-100">
          Unlock your potential with real-time job matching, resume analysis, and personalized learning paths powered by advanced AI.
        </p>

        <div className="flex justify-center gap-4 animate-fade-in-up delay-200">
           <Link 
             to="/upload" 
             className="px-8 py-4 bg-gray-900 text-white rounded-xl font-medium text-sm hover:bg-black hover:shadow-xl hover:-translate-y-1 transition-all flex items-center gap-2"
           >
             <UploadCloud size={18} />
             Upload Resume
           </Link>
           <Link 
             to="/jobs" 
             className="px-8 py-4 bg-white border border-gray-200 text-gray-600 rounded-xl font-medium text-sm hover:border-purple-200 hover:text-purple-600 hover:shadow-lg hover:-translate-y-1 transition-all flex items-center gap-2"
           >
             Explore Jobs
           </Link>
        </div>
      </div>

      {/* --- FEATURES GRID --- */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {features.map((feature, index) => (
            <Link 
              key={index}
              to={feature.path}
              className="group bg-white/60 backdrop-blur-md rounded-3xl p-8 border border-white shadow-sm hover:shadow-xl hover:shadow-purple-50/50 hover:border-purple-100 transition-all duration-300 flex flex-col items-start"
            >
              <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-sm border border-gray-50 group-hover:scale-110 transition-transform duration-300">
                <feature.icon size={28} className="text-purple-600 opacity-80" strokeWidth={1.5} />
              </div>

              <h3 className="text-xl font-semibold text-gray-900 mb-3 group-hover:text-purple-700 transition-colors">
                {feature.title}
              </h3>
              
              <p className="text-gray-500 text-sm leading-relaxed mb-6 flex-1">
                {feature.description}
              </p>
              
              <div className="flex items-center text-sm font-bold text-gray-400 group-hover:text-purple-600 transition-colors uppercase tracking-wide text-[10px]">
                {feature.linkText}
                <ArrowRight size={14} className="ml-2 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}

          {/* CTA Card */}
          <div className="bg-gradient-to-br from-gray-900 to-indigo-900 rounded-3xl p-8 flex flex-col justify-center items-center text-center shadow-2xl shadow-indigo-200 text-white relative overflow-hidden group">
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
            <div className="absolute -top-10 -right-10 w-32 h-32 bg-purple-500 rounded-full blur-3xl opacity-30 group-hover:opacity-50 transition-opacity"></div>
            
            <h3 className="text-2xl font-light mb-4 relative z-10">Ready to <span className="font-bold">Start?</span></h3>
            <p className="text-gray-300 text-sm mb-8 max-w-xs mx-auto relative z-10 leading-relaxed">
              Upload your resume to get real job recommendations from The Muse, RemoteOK, and more.
            </p>
            <Link
              to="/upload"
              className="px-6 py-3 bg-white text-gray-900 font-bold text-xs uppercase tracking-widest rounded-lg hover:bg-gray-100 transition-colors w-full sm:w-auto relative z-10 flex items-center justify-center gap-2"
            >
              Get Started <ArrowRight size={14} />
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Landing;