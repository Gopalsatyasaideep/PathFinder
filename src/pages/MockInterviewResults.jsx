import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Trophy, 
  TrendingUp, 
  Target, 
  CheckCircle2, 
  AlertCircle,
  Home,
  RotateCcw,
  Loader2,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Award,
  BarChart3,
  History
} from 'lucide-react';
import { apiService } from '../services/api';

/**
 * Mock Interview Results Page - "Think Tech" Redesign
 */
const MockInterviewResults = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [evaluation, setEvaluation] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [expandedQuestions, setExpandedQuestions] = useState({});
  const [animateScore, setAnimateScore] = useState(false);

  // --- Logic (Unchanged) ---

  useEffect(() => {
    loadAndEvaluate();
  }, []);

  const loadAndEvaluate = async () => {
    try {
      const answersData = sessionStorage.getItem('mockInterviewAnswers');
      if (!answersData) {
        // For development testing without data, you might want to mock this
        // alert('No interview data found.');
        // navigate('/mock-interview');
        // return;
        
        // Mock data for preview purposes if real data is missing (optional)
        // remove this block in production
         alert('No interview data found. Redirecting...');
         navigate('/mock-interview');
         return;
      }

      const parsedAnswers = JSON.parse(answersData);
      const result = await apiService.evaluateMockInterview(parsedAnswers);
      setEvaluation(result);
      setQuestions(result.questions || []);
      
      setTimeout(() => setAnimateScore(true), 100);
      
    } catch (error) {
      console.error('Error evaluating interview:', error);
      alert('Failed to evaluate your interview. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleQuestionExpansion = (questionId) => {
    setExpandedQuestions(prev => ({
      ...prev,
      [questionId]: !prev[questionId]
    }));
  };

  const getScoreColor = (score) => {
    if (score >= 9) return 'text-green-600';
    if (score >= 7) return 'text-purple-600';
    if (score >= 5) return 'text-yellow-600';
    return 'text-red-500';
  };

  const handleRetry = () => {
    sessionStorage.removeItem('mockInterviewData');
    sessionStorage.removeItem('mockInterviewAnswers');
    navigate('/mock-interview');
  };

  // --- Render Components ---

  const BackgroundBlobs = () => (
    <>
      <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob pointer-events-none"></div>
      <div className="absolute top-[20%] left-[-10%] w-[400px] h-[400px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[20%] w-[300px] h-[300px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-60 animate-blob animation-delay-4000 pointer-events-none"></div>
    </>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-white relative overflow-hidden flex flex-col items-center justify-center font-sans">
        <BackgroundBlobs />
        <div className="relative z-10 text-center">
          <div className="w-16 h-16 border-4 border-purple-100 border-t-purple-600 rounded-full animate-spin mx-auto mb-6"></div>
          <h2 className="text-2xl font-light text-gray-900 mb-2">Analyzing Performance</h2>
          <p className="text-gray-500 text-sm">Our AI is reviewing your answers...</p>
        </div>
      </div>
    );
  }

  if (!evaluation) {
    return (
      <div className="min-h-screen bg-white relative overflow-hidden flex items-center justify-center">
        <BackgroundBlobs />
        <div className="relative z-10 text-center p-8 bg-white/80 backdrop-blur-xl rounded-2xl border border-red-100 shadow-xl max-w-md mx-auto">
          <div className="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-4 text-red-500">
            <AlertCircle size={24} />
          </div>
          <h2 className="text-xl font-medium text-gray-900 mb-2">Evaluation Failed</h2>
          <p className="text-gray-500 text-sm mb-6">We couldn't generate your results. Please try again.</p>
          <button
            onClick={() => navigate('/mock-interview')}
            className="w-full px-6 py-3 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-black transition-colors"
          >
            Start New Session
          </button>
        </div>
      </div>
    );
  }

  const { overallEvaluation, questionEvaluations } = evaluation;

  return (
    <div className="min-h-screen bg-white relative font-sans text-gray-800 selection:bg-purple-100">
      <BackgroundBlobs />
      
      {/* Top Navigation / Header */}
      <nav className="sticky top-0 z-20 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
           <div className="flex items-center gap-2">
             <div className="bg-purple-600 text-white p-1 rounded">
               <Award size={16} />
             </div>
             <span className="font-semibold text-gray-900 tracking-tight">Report Card</span>
           </div>
           <div className="flex gap-3">
              <button 
                onClick={() => navigate('/dashboard')}
                className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors"
              >
                Dashboard
              </button>
           </div>
        </div>
      </nav>

      <main className="relative z-10 max-w-6xl mx-auto px-6 py-10">
        
        {/* Header Section */}
        <div className="mb-10 text-center md:text-left md:flex justify-between items-end">
          <div>
            <h1 className="text-3xl md:text-4xl font-light text-gray-900 mb-2">
              Performance <span className="font-medium">Summary</span>
            </h1>
            <p className="text-gray-500 max-w-xl">
              AI-generated insights based on your recent interview session.
            </p>
          </div>
          <div className="mt-4 md:mt-0 flex gap-3">
             <button
                onClick={handleRetry}
                className="px-5 py-2.5 bg-white border border-gray-200 text-gray-700 font-medium rounded-lg hover:border-purple-300 hover:text-purple-600 transition-all text-sm flex items-center gap-2 shadow-sm"
              >
                <RotateCcw size={16} />
                Retry
              </button>
          </div>
        </div>

        {/* --- High Level Metrics Grid --- */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
          
          {/* 1. Score Card */}
          <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm shadow-purple-50 flex flex-col items-center justify-center relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <Trophy size={100} className="text-purple-600" />
            </div>
            
            <div className="relative w-48 h-48 mb-4">
               {/* SVG Circular Progress */}
               <svg className="transform -rotate-90 w-full h-full">
                 <circle
                   cx="96" cy="96" r="88"
                   stroke="#f3f4f6" strokeWidth="8" fill="none"
                 />
                 <circle
                   cx="96" cy="96" r="88"
                   stroke="url(#gradient)" strokeWidth="8" fill="none"
                   strokeDasharray={`${2 * Math.PI * 88}`}
                   strokeDashoffset={`${2 * Math.PI * 88 * (1 - (animateScore ? overallEvaluation.totalScore / 100 : 0))}`}
                   strokeLinecap="round"
                   className="transition-all duration-1000 ease-out"
                 />
                 <defs>
                   <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                     <stop offset="0%" stopColor="#9333ea" />
                     <stop offset="100%" stopColor="#4f46e5" />
                   </linearGradient>
                 </defs>
               </svg>
               <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-5xl font-light text-gray-900 tracking-tighter">
                    {animateScore ? overallEvaluation.totalScore : 0}
                  </span>
                  <span className="text-xs uppercase tracking-widest text-gray-400 mt-1">Total Score</span>
               </div>
            </div>
            
            <div className="px-4 py-1.5 bg-purple-50 text-purple-700 rounded-full text-xs font-bold uppercase tracking-wider">
               {overallEvaluation.performance}
            </div>
          </div>

          {/* 2. Feedback Summary */}
          <div className="lg:col-span-2 bg-white/60 backdrop-blur-sm rounded-2xl p-8 border border-gray-100 shadow-sm flex flex-col">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wide mb-4 flex items-center gap-2">
              <Sparkles size={16} className="text-purple-500" />
              AI Feedback
            </h3>
            <p className="text-gray-600 leading-relaxed text-sm md:text-base flex-1">
              {overallEvaluation.detailedFeedback}
            </p>
            
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
               <div>
                  <h4 className="text-xs font-bold text-green-600 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <CheckCircle2 size={14} /> Key Strengths
                  </h4>
                  <ul className="space-y-2">
                    {overallEvaluation.keyStrengths.slice(0, 3).map((strength, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-400 mt-1.5 shrink-0"></span>
                        {strength}
                      </li>
                    ))}
                  </ul>
               </div>
               <div>
                  <h4 className="text-xs font-bold text-orange-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <TrendingUp size={14} /> Focus Areas
                  </h4>
                  <ul className="space-y-2">
                    {overallEvaluation.areasToImprove.slice(0, 3).map((area, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-orange-400 mt-1.5 shrink-0"></span>
                        {area}
                      </li>
                    ))}
                  </ul>
               </div>
            </div>
          </div>
        </div>

        {/* --- Next Steps (Thin Banner) --- */}
        <div className="mb-12 bg-indigo-50/50 border border-indigo-100 rounded-xl p-6">
           <h3 className="text-sm font-bold text-indigo-900 uppercase tracking-wide mb-3 flex items-center gap-2">
              <Target size={16} /> Recommended Actions
           </h3>
           <div className="flex flex-wrap gap-x-8 gap-y-2">
              {overallEvaluation.nextSteps.map((step, idx) => (
                <div key={idx} className="text-sm text-indigo-800/80 flex items-center gap-2">
                  <span className="font-mono text-indigo-400 font-bold">{idx + 1}.</span>
                  {step}
                </div>
              ))}
           </div>
        </div>

        {/* --- Detailed Question Breakdown --- */}
        <div>
           <div className="flex items-center gap-3 mb-6">
              <BarChart3 size={20} className="text-gray-400" />
              <h2 className="text-xl font-light text-gray-900">Question <span className="font-medium">Analysis</span></h2>
           </div>

           <div className="space-y-4">
             {questionEvaluations.map((qEval) => {
               // Find the matching question
               const question = questions.find(q => q.id === qEval.questionId);
               
               return (
               <div 
                 key={qEval.questionId}
                 className={`bg-white rounded-xl border transition-all duration-300 overflow-hidden ${
                   expandedQuestions[qEval.questionId] 
                     ? 'border-purple-200 shadow-lg shadow-purple-50 ring-1 ring-purple-100' 
                     : 'border-gray-100 hover:border-gray-200 hover:shadow-sm'
                 }`}
               >
                 {/* Question Header (Clickable) */}
                 <button
                   onClick={() => toggleQuestionExpansion(qEval.questionId)}
                   className="w-full px-6 py-5 flex items-start md:items-center justify-between gap-4 text-left"
                 >
                   <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                          Question {qEval.questionId}
                        </span>
                        {question && (
                          <>
                            <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                               question.type === 'technical' ? 'bg-blue-50 text-blue-600' :
                               question.type === 'behavioral' ? 'bg-green-50 text-green-600' :
                               question.type === 'case-study' ? 'bg-purple-50 text-purple-600' :
                               'bg-gray-50 text-gray-600'
                            }`}>
                              {question.type}
                            </span>
                            <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                               question.difficulty === 'easy' ? 'bg-green-50 text-green-600' :
                               question.difficulty === 'medium' ? 'bg-yellow-50 text-yellow-600' :
                               'bg-red-50 text-red-600'
                            }`}>
                              {question.difficulty}
                            </span>
                          </>
                        )}
                        {qEval.isCorrect !== undefined && (
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                             qEval.isCorrect ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
                          }`}>
                            {qEval.isCorrect ? 'Correct' : 'Needs Work'}
                          </span>
                        )}
                      </div>
                      <h3 className="text-sm font-medium text-gray-900">
                         {question ? question.question : 'Question details unavailable'}
                      </h3>
                   </div>

                   <div className="flex items-center gap-6">
                      <div className="text-right">
                         <span className={`text-2xl font-light ${getScoreColor(qEval.score)}`}>
                           {qEval.score}
                         </span>
                         <span className="text-xs text-gray-400 font-medium">/10</span>
                      </div>
                      <div className={`p-1 rounded-full transition-transform duration-300 ${expandedQuestions[qEval.questionId] ? 'rotate-180 bg-gray-100' : ''}`}>
                         <ChevronDown size={18} className="text-gray-400" />
                      </div>
                   </div>
                 </button>

                 {/* Expanded Content */}
                 <div 
                   className={`grid transition-[grid-template-rows] duration-300 ease-out ${
                     expandedQuestions[qEval.questionId] ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'
                   }`}
                 >
                   <div className="overflow-hidden">
                     <div className="px-6 pb-6 pt-2 border-t border-gray-50 bg-gray-50/30">
                        
                        {/* Display Question Details */}
                        {question && (
                          <div className="mb-6 bg-purple-50/50 border border-purple-100 rounded-lg p-4">
                             <h4 className="text-xs font-bold text-purple-700 uppercase tracking-wider mb-3 flex items-center gap-2">
                                <Target size={12} /> Question Details
                             </h4>
                             <p className="text-sm text-purple-900 mb-3 font-medium">{question.question}</p>
                             {question.expectedPoints && question.expectedPoints.length > 0 && (
                               <div>
                                 <p className="text-xs text-purple-700 font-semibold mb-1">Expected Key Points:</p>
                                 <ul className="space-y-1">
                                   {question.expectedPoints.map((point, idx) => (
                                     <li key={idx} className="text-xs text-purple-800/80 flex items-start gap-2">
                                       <span className="w-1 h-1 rounded-full bg-purple-400 mt-1.5 shrink-0"></span>
                                       {point}
                                     </li>
                                   ))}
                                 </ul>
                               </div>
                             )}
                          </div>
                        )}
                        
                        <div className="mb-6">
                           <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2">AI Feedback</h4>
                           <p className="text-sm text-gray-600 leading-relaxed">{qEval.feedback}</p>
                        </div>

                        {qEval.correctAnswer && (
                          <div className="mb-6 bg-blue-50/50 border border-blue-100 rounded-lg p-4">
                             <h4 className="text-xs font-bold text-blue-700 uppercase tracking-wider mb-2 flex items-center gap-2">
                                <AlertCircle size={12} /> Expected Answer / Key Points
                             </h4>
                             <p className="text-sm text-blue-900/80">{qEval.correctAnswer}</p>
                          </div>
                        )}

                        <div className="grid md:grid-cols-2 gap-6">
                           <div>
                              <h4 className="text-xs font-bold text-green-600 uppercase tracking-wider mb-2">Strengths</h4>
                              <ul className="space-y-1">
                                 {qEval.strengths.map((s, i) => (
                                   <li key={i} className="text-sm text-gray-500 flex items-start gap-2">
                                     <CheckCircle2 size={14} className="text-green-500 mt-0.5 shrink-0" />
                                     {s}
                                   </li>
                                 ))}
                              </ul>
                           </div>
                           <div>
                              <h4 className="text-xs font-bold text-orange-500 uppercase tracking-wider mb-2">Improvements</h4>
                              <ul className="space-y-1">
                                 {qEval.improvements.map((s, i) => (
                                   <li key={i} className="text-sm text-gray-500 flex items-start gap-2">
                                     <TrendingUp size={14} className="text-orange-400 mt-0.5 shrink-0" />
                                     {s}
                                   </li>
                                 ))}
                              </ul>
                           </div>
                        </div>

                     </div>
                   </div>
                 </div>
               </div>
               );
             })}
           </div>
        </div>

        <div className="mt-12 text-center space-y-4">
           <p className="text-gray-400 text-sm">Review complete. Practice makes perfect.</p>
           <div className="flex items-center justify-center gap-4">
             <button
               onClick={() => navigate('/mock-interview')}
               className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
             >
               <RotateCcw size={18} />
               Start New Interview
             </button>
             <button
               onClick={() => navigate('/mock-interview/history')}
               className="px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
             >
               <History size={18} />
               View History
             </button>
             <button
               onClick={() => navigate('/dashboard')}
               className="px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
             >
               <Home size={18} />
               Dashboard
             </button>
           </div>
        </div>

      </main>
    </div>
  );
};

export default MockInterviewResults;