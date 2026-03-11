import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import {
  ArrowLeft,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  TrendingUp,
  FileText,
  Target,
  Lightbulb,
  AlertCircle,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

/**
 * Mock Interview Detail Page - "Think Tech" Redesign
 */
const MockInterviewHistoryDetail = () => {
  const { interviewId } = useParams();
  const navigate = useNavigate();
  const [interview, setInterview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedQuestions, setExpandedQuestions] = useState(new Set());

  // --- Logic (Preserved) ---

  useEffect(() => {
    fetchInterviewDetail();
  }, [interviewId]);

  const fetchInterviewDetail = async () => {
    try {
      setLoading(true);
      const data = await apiService.getInterviewDetail(interviewId);
      setInterview(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching interview detail:', err);
      setError('Failed to load interview details');
    } finally {
      setLoading(false);
    }
  };

  const toggleQuestion = (questionId) => {
    setExpandedQuestions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getScoreColor = (score) => {
    if (score >= 9) return 'text-green-600';
    if (score >= 7) return 'text-purple-600';
    if (score >= 5) return 'text-yellow-600';
    return 'text-red-500';
  };

  // --- Visual Components ---

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
          <h2 className="text-2xl font-light text-gray-900 mb-2">Loading Report</h2>
          <p className="text-gray-500 text-sm">Retrieving your interview analysis...</p>
        </div>
      </div>
    );
  }

  if (error || !interview) {
    return (
      <div className="min-h-screen bg-white relative overflow-hidden flex items-center justify-center p-4 font-sans">
        <BackgroundBlobs />
        <div className="relative z-10 bg-white/80 backdrop-blur-xl border border-red-100 rounded-2xl p-10 text-center max-w-md w-full shadow-xl">
          <div className="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
             <AlertCircle size={32} className="text-red-500" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Unavailable</h3>
          <p className="text-gray-500 mb-8">{error || 'Interview details could not be found.'}</p>
          <button
            onClick={() => navigate('/mock-interview/history')}
            className="w-full px-6 py-3 bg-gray-900 text-white rounded-xl text-sm font-medium hover:bg-black transition-colors"
          >
            Return to History
          </button>
        </div>
      </div>
    );
  }

  const isCompleted = interview.status === 'completed';

  return (
    <div className="min-h-screen bg-white relative font-sans text-gray-800 selection:bg-purple-100">
      <BackgroundBlobs />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        
        {/* Navigation */}
        <button
          onClick={() => navigate('/mock-interview/history')}
          className="group mb-8 flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-purple-600 transition-colors"
        >
          <div className="p-1 rounded-full bg-gray-50 group-hover:bg-purple-50 transition-colors">
             <ArrowLeft size={16} />
          </div>
          Back to History
        </button>

        {/* --- HEADER CARD --- */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl border border-white shadow-xl shadow-purple-100/50 p-8 mb-8">
          <div className="flex flex-col md:flex-row justify-between items-start gap-6">
            
            <div className="flex-1">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-purple-50 border border-purple-100 rounded-full mb-4">
                 <FileText size={12} className="text-purple-600" />
                 <span className="text-[10px] font-bold text-purple-700 uppercase tracking-wider">
                    {interview.interviewType} Interview
                 </span>
              </div>
              
              <h1 className="text-3xl md:text-4xl font-light text-gray-900 mb-4 leading-tight">
                {interview.role}
              </h1>
              
              <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-100">
                  <Calendar size={14} /> {formatDate(interview.created_at)}
                </span>
                <span className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-100">
                  <Clock size={14} /> {interview.questions.length} Questions
                </span>
              </div>
            </div>

            {/* Score Display */}
            {isCompleted && interview.totalScore !== null && (
              <div className="flex flex-col items-center md:items-end min-w-[120px]">
                <div className="relative w-32 h-32 flex items-center justify-center">
                   {/* Decorative Ring */}
                   <svg className="absolute inset-0 w-full h-full -rotate-90">
                      <circle cx="50%" cy="50%" r="48%" fill="none" stroke="#f3f4f6" strokeWidth="8" />
                      <circle cx="50%" cy="50%" r="48%" fill="none" stroke="url(#gradient)" strokeWidth="8" 
                        strokeDasharray={`${2 * Math.PI * 48}`} 
                        strokeDashoffset={`${2 * Math.PI * 48 * (1 - interview.totalScore / 100)}`} 
                        strokeLinecap="round"
                      />
                      <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#9333ea" />
                          <stop offset="100%" stopColor="#4f46e5" />
                        </linearGradient>
                      </defs>
                   </svg>
                   <div className="text-center">
                      <span className="text-4xl font-light text-gray-900 tracking-tighter block">{interview.totalScore}</span>
                      <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Score</span>
                   </div>
                </div>
                <div className="mt-2 px-3 py-1 bg-gray-100 rounded-full text-xs font-bold text-gray-600 uppercase tracking-wider">
                   {interview.performance}
                </div>
              </div>
            )}
          </div>

          {/* Job Description (Collapsible style visually) */}
          <div className="mt-8 pt-6 border-t border-gray-100">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Context</h3>
            <p className="text-gray-600 text-sm leading-relaxed whitespace-pre-line max-w-3xl">
               {interview.jobDescription}
            </p>
          </div>
        </div>

        {/* --- FEEDBACK SECTION --- */}
        {isCompleted && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
            
            {/* Left Column: Strengths & Weaknesses */}
            <div className="space-y-6">
               {/* Strengths */}
               <div className="bg-white rounded-2xl p-6 border border-green-100 shadow-sm">
                  <h3 className="text-sm font-bold text-green-700 uppercase tracking-wide mb-4 flex items-center gap-2">
                     <CheckCircle size={16} /> Key Strengths
                  </h3>
                  <ul className="space-y-3">
                    {interview.keyStrengths?.map((strength, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-3">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-400 mt-2 shrink-0"></span>
                        <span className="leading-relaxed">{strength}</span>
                      </li>
                    ))}
                  </ul>
               </div>

               {/* Improvements */}
               <div className="bg-white rounded-2xl p-6 border border-amber-100 shadow-sm">
                  <h3 className="text-sm font-bold text-amber-600 uppercase tracking-wide mb-4 flex items-center gap-2">
                     <TrendingUp size={16} /> Areas to Improve
                  </h3>
                  <ul className="space-y-3">
                    {interview.areasToImprove?.map((area, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-3">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-2 shrink-0"></span>
                        <span className="leading-relaxed">{area}</span>
                      </li>
                    ))}
                  </ul>
               </div>
            </div>

            {/* Right Column: Detailed Feedback & Next Steps */}
            <div className="space-y-6">
               <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-6 border border-white shadow-sm h-full flex flex-col">
                  <div className="mb-6">
                     <h3 className="text-sm font-bold text-indigo-900 uppercase tracking-wide mb-3 flex items-center gap-2">
                        <Sparkles size={16} className="text-purple-500" /> AI Feedback
                     </h3>
                     <p className="text-sm text-gray-600 leading-7">
                        {interview.detailedFeedback}
                     </p>
                  </div>

                  {interview.nextSteps?.length > 0 && (
                    <div className="mt-auto pt-6 border-t border-gray-100">
                       <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                          <Target size={14} /> Recommended Steps
                       </h3>
                       <ul className="space-y-2">
                          {interview.nextSteps.map((step, idx) => (
                            <li key={idx} className="text-sm text-indigo-900 font-medium flex items-center gap-2">
                               <span className="font-mono text-purple-400 text-xs">0{idx + 1}.</span>
                               {step}
                            </li>
                          ))}
                       </ul>
                    </div>
                  )}
               </div>
            </div>
          </div>
        )}

        {/* --- QUESTIONS BREAKDOWN --- */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-6 px-2">
             <div className="w-1 h-6 bg-purple-500 rounded-full"></div>
             <h2 className="text-xl font-light text-gray-900">
               {isCompleted ? 'Analysis Breakdown' : 'Interview Questions'}
             </h2>
          </div>

          <div className="space-y-4">
            {interview.questions.map((question, idx) => {
              const answer = interview.answers?.find((a) => a.questionId === question.id);
              const isExpanded = expandedQuestions.has(question.id);

              return (
                <div 
                  key={question.id}
                  className={`bg-white rounded-2xl border transition-all duration-300 overflow-hidden ${
                    isExpanded ? 'border-purple-200 shadow-lg shadow-purple-50/50' : 'border-gray-100 hover:border-gray-200 hover:shadow-sm'
                  }`}
                >
                  <div className="p-6">
                    {/* Question Header */}
                    <div className="flex justify-between items-start gap-4">
                       <div className="flex gap-4">
                          <span className="flex-shrink-0 w-8 h-8 rounded-lg bg-gray-50 text-gray-500 font-mono text-sm flex items-center justify-center border border-gray-100">
                             {idx + 1}
                          </span>
                          <div>
                             <h3 className="text-base font-medium text-gray-900 mb-2">{question.question}</h3>
                             <div className="flex gap-2 text-xs">
                                <span className="px-2 py-1 bg-gray-50 text-gray-500 rounded border border-gray-100">{question.type}</span>
                                <span className="px-2 py-1 bg-gray-50 text-gray-500 rounded border border-gray-100">{question.difficulty}</span>
                             </div>
                          </div>
                       </div>

                       {answer && (
                          <div className="flex flex-col items-end gap-1">
                             <div className="flex items-center gap-2">
                                <span className={`text-xl font-light ${getScoreColor(answer.score)}`}>{answer.score}</span>
                                <span className="text-xs text-gray-400 font-medium">/10</span>
                             </div>
                             {isCompleted && (
                               <button 
                                 onClick={() => toggleQuestion(question.id)}
                                 className="text-gray-400 hover:text-purple-600 transition-colors p-1"
                               >
                                  {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                               </button>
                             )}
                          </div>
                       )}
                    </div>

                    {/* Expandable Details */}
                    {isExpanded && isCompleted && answer && (
                      <div className="mt-6 pt-6 border-t border-gray-50 animate-fade-in">
                         
                         <div className="grid md:grid-cols-2 gap-8">
                            {/* User Response */}
                            <div>
                               <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Your Answer</h4>
                               <p className="text-sm text-gray-600 leading-relaxed bg-gray-50/50 p-4 rounded-xl border border-gray-100">
                                  {answer.answer}
                               </p>
                            </div>

                            {/* AI Feedback Loop */}
                            <div className="space-y-6">
                               <div>
                                  <h4 className="text-xs font-bold text-purple-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                                     <Lightbulb size={12} /> Analysis
                                  </h4>
                                  <p className="text-sm text-gray-600 leading-relaxed">
                                     {answer.feedback}
                                  </p>
                               </div>

                               {answer.correctAnswer && (
                                 <div className="bg-green-50/50 rounded-xl p-4 border border-green-100">
                                    <h4 className="text-xs font-bold text-green-700 uppercase tracking-wider mb-2">Ideal Response</h4>
                                    <p className="text-sm text-green-800/80 leading-relaxed">{answer.correctAnswer}</p>
                                 </div>
                               )}
                            </div>
                         </div>

                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex justify-center gap-4 pt-8 border-t border-gray-100">
           <button
             onClick={() => navigate('/mock-interview')}
             className="px-8 py-3 bg-gray-900 text-white rounded-xl text-sm font-medium hover:bg-black hover:shadow-lg transition-all transform hover:-translate-y-0.5"
           >
             Start New Session
           </button>
        </div>

      </div>
    </div>
  );
};

export default MockInterviewHistoryDetail;