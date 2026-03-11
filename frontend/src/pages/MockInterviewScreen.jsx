import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Volume2, 
  VolumeX, 
  ArrowRight, 
  ArrowLeft, 
  Check, 
  Clock,
  Maximize2,
  Minimize2,
  Lightbulb,
  CheckCircle2
} from 'lucide-react';

/**
 * Mock Interview Screen - Fullscreen "No Scroll" App Layout
 */
const MockInterviewScreen = () => {
  const navigate = useNavigate();
  const [interviewData, setInterviewData] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [questionStartTimes, setQuestionStartTimes] = useState({});
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [isReading, setIsReading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  
  const speechSynthesis = window.speechSynthesis;
  const timerRef = useRef(null);
  const containerRef = useRef(null);

  // --- Logic (Unchanged) ---

  useEffect(() => {
    const data = sessionStorage.getItem('mockInterviewData');
    if (!data) {
      // For dev/testing purposes if no data exists, you might want to comment this out or mock it
      // alert('No interview data found. Please start a new interview.');
      // navigate('/mock-interview');
      return;
    }
    
    const parsedData = JSON.parse(data);
    setInterviewData(parsedData);
    
    const times = {};
    parsedData.questions.forEach((_, idx) => {
      times[idx] = Date.now();
    });
    setQuestionStartTimes(times);
  }, [navigate]);

  useEffect(() => {
    if (hasStarted) {
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [hasStarted]);

  useEffect(() => {
    if (hasStarted && voiceEnabled && interviewData) {
      const currentQuestion = interviewData.questions[currentQuestionIndex];
      if (currentQuestion) {
        readQuestion(currentQuestion.question);
      }
    }
  }, [currentQuestionIndex, voiceEnabled, hasStarted, interviewData]);

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const readQuestion = (text) => {
    speechSynthesis.cancel();
    if (!voiceEnabled) return;
    
    setIsReading(true);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.onend = () => setIsReading(false);
    utterance.onerror = () => setIsReading(false);
    speechSynthesis.speak(utterance);
  };

  const toggleVoice = () => {
    if (voiceEnabled) speechSynthesis.cancel();
    setVoiceEnabled(!voiceEnabled);
  };

  const toggleFullscreen = async () => {
    if (!document.fullscreenElement) {
      await containerRef.current?.requestFullscreen();
    } else {
      await document.exitFullscreen();
    }
  };

  const handleStart = () => {
    setHasStarted(true);
    setQuestionStartTimes(prev => ({ ...prev, [0]: Date.now() }));
  };

  const handleAnswerChange = (value) => {
    setAnswers(prev => ({ ...prev, [currentQuestionIndex]: value }));
  };

  const goToNextQuestion = () => {
    if (currentQuestionIndex < interviewData.questions.length - 1) {
      speechSynthesis.cancel();
      setCurrentQuestionIndex(prev => prev + 1);
      setQuestionStartTimes(prev => ({ ...prev, [currentQuestionIndex + 1]: Date.now() }));
    }
  };

  const goToPreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      speechSynthesis.cancel();
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    speechSynthesis.cancel();
    const unansweredCount = interviewData.questions.length - Object.keys(answers).filter(key => answers[key]?.trim()).length;
    
    if (unansweredCount > 0) {
      const confirm = window.confirm(`You have ${unansweredCount} unanswered question(s). Submit anyway?`);
      if (!confirm) return;
    }

    const answersWithTime = interviewData.questions.map((question, idx) => {
      const timeSpent = idx === currentQuestionIndex 
        ? Math.floor((Date.now() - questionStartTimes[idx]) / 1000)
        : 0;
      
      return {
        questionId: question.id,
        answer: answers[idx] || '',
        timeSpent: timeSpent
      };
    });

    sessionStorage.setItem('mockInterviewAnswers', JSON.stringify({
      interview_id: interviewData.interviewId,
      interviewType: interviewData.interviewType,
      role: interviewData.role,
      answers: answersWithTime,
      totalTime: elapsedTime
    }));

    navigate('/mock-interview/results');
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // --- Render ---

  if (!interviewData) {
    return <div className="h-screen flex items-center justify-center">Loading...</div>;
  }

  const BackgroundBlobs = () => (
    <>
      <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob pointer-events-none"></div>
      <div className="absolute top-[20%] left-[-10%] w-[400px] h-[400px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[20%] w-[300px] h-[300px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000 pointer-events-none"></div>
    </>
  );

  // START SCREEN (Simple Centered)
  if (!hasStarted) {
    return (
      <div className="h-screen w-screen bg-white relative overflow-hidden flex items-center justify-center font-sans text-gray-800">
        <BackgroundBlobs />
        <div className="max-w-xl w-full relative z-10 px-6">
          <div className="bg-white/80 backdrop-blur-xl border border-white/50 shadow-2xl rounded-2xl p-10 text-center">
            <h1 className="text-3xl font-light text-gray-900 mb-2">Ready?</h1>
            <p className="text-gray-500 mb-8">{interviewData.role} • {interviewData.interviewType}</p>
            
            <div className="grid grid-cols-3 gap-4 mb-8 text-center">
               <div className="p-3 bg-purple-50 rounded-lg">
                 <h3 className="text-lg font-bold text-purple-600">{interviewData.questions.length}</h3>
                 <p className="text-xs text-gray-500 uppercase">Questions</p>
               </div>
               <div className="p-3 bg-purple-50 rounded-lg">
                 <h3 className="text-lg font-bold text-purple-600">~{interviewData.estimatedDuration}</h3>
                 <p className="text-xs text-gray-500 uppercase">Minutes</p>
               </div>
               <div className="p-3 bg-purple-50 rounded-lg">
                 <h3 className="text-lg font-bold text-purple-600">AI</h3>
                 <p className="text-xs text-gray-500 uppercase">Review</p>
               </div>
            </div>

            <button
              onClick={handleStart}
              className="w-full bg-purple-600 text-white font-medium py-3.5 rounded-lg hover:bg-purple-700 transition-all shadow-lg shadow-purple-200 flex items-center justify-center gap-2"
            >
              Start Interview
              <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = interviewData.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / interviewData.questions.length) * 100;

  // MAIN INTERVIEW SCREEN (No Page Scroll)
  return (
    <div 
      ref={containerRef}
      className={`h-screen w-full relative overflow-hidden flex flex-col font-sans text-gray-800 selection:bg-purple-100 ${isFullscreen ? 'bg-white' : 'bg-white'}`}
    >
      <BackgroundBlobs />

      {/* 1. Header (Fixed Height) */}
      <header className="flex-none h-16 bg-white/80 backdrop-blur-md border-b border-gray-100 z-20">
        <div className="max-w-7xl mx-auto px-4 md:px-6 h-full flex items-center justify-between">
          
          <div className="flex items-center gap-4">
             {/* Progress Bar (Compact) */}
             <div className="flex flex-col w-32 md:w-48">
                <div className="flex justify-between text-[10px] uppercase font-bold text-gray-400 mb-1">
                  <span>Progress</span>
                  <span>{currentQuestionIndex + 1}/{interviewData.questions.length}</span>
                </div>
                <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-purple-600 transition-all duration-500 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
             </div>
          </div>

          {/* Center Timer */}
          <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
             <div className="flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-full border border-gray-200 shadow-sm">
                <Clock size={14} className="text-purple-600" />
                <span className="text-sm font-mono font-medium text-gray-700">{formatTime(elapsedTime)}</span>
             </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleVoice}
              className={`p-2 rounded-lg transition-all ${
                voiceEnabled ? 'text-purple-600 bg-purple-50' : 'text-gray-400 hover:bg-gray-50'
              }`}
            >
              {voiceEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
            </button>
            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-lg"
            >
              {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
            </button>
          </div>
        </div>
      </header>

      {/* 2. Main Body (Flex Grow + Overflow Hidden) */}
      <main className="flex-1 flex flex-col relative z-10 overflow-hidden">
        <div className="w-full max-w-5xl mx-auto h-full flex flex-col px-6 py-6 md:py-8">
          
          {/* Question Section (Flex None - Takes natural height) */}
          <div className="flex-none mb-6 animate-fade-in-down">
             <div className="flex items-center gap-2 mb-4">
                <span className="bg-purple-100 text-purple-700 text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">
                  Question {currentQuestionIndex + 1}
                </span>
                <span className="text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider border border-gray-200 text-gray-500">
                  {currentQuestion.difficulty}
                </span>
             </div>

             <h2 className="text-2xl md:text-3xl font-light text-gray-900 leading-tight">
               {currentQuestion.question}
               {voiceEnabled && (
                  <button 
                    onClick={() => readQuestion(currentQuestion.question)}
                    className={`ml-2 inline-block align-baseline text-purple-400 hover:text-purple-600 transition-colors ${isReading ? 'animate-pulse' : ''}`}
                  >
                    <Volume2 size={20} />
                  </button>
               )}
             </h2>

             {/* Hints (Collapsible or Small) */}
             {currentQuestion.expectedPoints && currentQuestion.expectedPoints.length > 0 && (
               <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
                 <Lightbulb size={12} className="text-yellow-500" />
                 <span>Tips: {currentQuestion.expectedPoints.slice(0, 3).join(', ')}...</span>
               </div>
             )}
          </div>

          {/* Answer Section (Flex 1 - Fills remaining space) */}
          <div className="flex-1 flex flex-col min-h-0 bg-gray-50 rounded-2xl border border-gray-200 relative focus-within:ring-2 focus-within:ring-purple-100 focus-within:border-purple-300 transition-all">
             {/* Textarea Label */}
             <div className="flex-none px-4 py-3 border-b border-gray-100 flex justify-between items-center bg-white rounded-t-2xl">
                <label className="text-xs font-bold uppercase tracking-wider text-gray-400">Your Answer</label>
                {answers[currentQuestionIndex]?.trim() && (
                    <span className="text-xs text-green-600 font-medium flex items-center gap-1">
                      <CheckCircle2 size={12} /> Saved
                    </span>
                )}
             </div>
             
             {/* Actual Textarea (Scrolls internally) */}
             <textarea
               value={answers[currentQuestionIndex] || ''}
               onChange={(e) => handleAnswerChange(e.target.value)}
               placeholder="Type your detailed answer here..."
               className="flex-1 w-full p-4 bg-transparent border-none outline-none resize-none text-gray-700 text-base leading-relaxed"
               autoFocus
               spellCheck="false"
             />

             {/* Character Count */}
             <div className="flex-none px-4 py-2 text-right">
                <span className="text-[10px] text-gray-400 font-mono">
                   {answers[currentQuestionIndex]?.length || 0} chars
                </span>
             </div>
          </div>

          {/* Footer Navigation (Flex None - Fixed at bottom of container) */}
          <div className="flex-none pt-6 mt-2 flex items-center justify-between">
            <button
              onClick={goToPreviousQuestion}
              disabled={currentQuestionIndex === 0}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ArrowLeft size={16} />
              Previous
            </button>

            {currentQuestionIndex === interviewData.questions.length - 1 ? (
              <button
                onClick={handleSubmit}
                className="bg-gray-900 text-white px-8 py-3 rounded-lg text-sm font-medium hover:bg-black transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2"
              >
                Submit Interview
                <Check size={16} />
              </button>
            ) : (
              <button
                onClick={goToNextQuestion}
                className="bg-purple-600 text-white px-8 py-3 rounded-lg text-sm font-medium hover:bg-purple-700 transition-all shadow-lg shadow-purple-200 hover:shadow-xl transform hover:-translate-y-0.5 flex items-center gap-2"
              >
                Next Question
                <ArrowRight size={16} />
              </button>
            )}
          </div>

        </div>
      </main>
    </div>
  );
};

export default MockInterviewScreen;