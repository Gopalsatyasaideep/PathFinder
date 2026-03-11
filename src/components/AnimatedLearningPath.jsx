import { useState, useEffect } from 'react';
import { 
  BookOpen, Trophy, Lightbulb, CheckCircle2, Clock, ExternalLink, 
  Target, Play, Award, Brain, Code, Zap, Star, TrendingUp,
  ChevronRight, ChevronDown, Sparkles, Rocket
} from 'lucide-react';

/**
 * Animated Learning Path Component with Visual Avatars and Step-by-Step Progression
 */
const AnimatedLearningPath = ({ learningPath, targetRole, onNewPath }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [expandedSteps, setExpandedSteps] = useState([0]);
  const [showCelebration, setShowCelebration] = useState(false);

  // Auto-scroll to active step
  useEffect(() => {
    const element = document.getElementById(`step-${activeStep}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [activeStep]);

  // Avatar images from online sources (ui-avatars.com for diverse characters)
  const getAvatarForStep = (index, total) => {
    const avatars = [
      `https://api.dicebear.com/7.x/avataaars/svg?seed=beginner&backgroundColor=b6e3f4&size=120`,
      `https://api.dicebear.com/7.x/avataaars/svg?seed=learning&backgroundColor=c0aede&size=120`,
      `https://api.dicebear.com/7.x/avataaars/svg?seed=intermediate&backgroundColor=ffd5dc&size=120`,
      `https://api.dicebear.com/7.x/avataaars/svg?seed=advanced&backgroundColor=d1f4e0&size=120`,
      `https://api.dicebear.com/7.x/avataaars/svg?seed=expert&backgroundColor=ffe8b6&size=120`,
      `https://api.dicebear.com/7.x/avataaars/svg?seed=master&backgroundColor=ffc9c9&size=120`,
    ];
    
    const segment = Math.floor((index / total) * avatars.length);
    return avatars[Math.min(segment, avatars.length - 1)];
  };

  const getProgressPercentage = () => {
    return ((completedSteps.length / learningPath.length) * 100).toFixed(0);
  };

  const markAsCompleted = (stepIndex) => {
    if (!completedSteps.includes(stepIndex)) {
      setCompletedSteps([...completedSteps, stepIndex]);
      
      // Show celebration if all steps completed
      if (completedSteps.length + 1 === learningPath.length) {
        setShowCelebration(true);
        setTimeout(() => setShowCelebration(false), 5000);
      }
    }
  };

  const toggleStepExpansion = (stepIndex) => {
    if (expandedSteps.includes(stepIndex)) {
      setExpandedSteps(expandedSteps.filter(i => i !== stepIndex));
    } else {
      setExpandedSteps([...expandedSteps, stepIndex]);
    }
  };

  const goToNextStep = () => {
    if (activeStep < learningPath.length - 1) {
      setActiveStep(activeStep + 1);
      if (!expandedSteps.includes(activeStep + 1)) {
        setExpandedSteps([...expandedSteps, activeStep + 1]);
      }
    }
  };

  const goToPreviousStep = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      
      {/* Celebration Animation */}
      {showCelebration && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-3xl p-12 text-center shadow-2xl transform animate-bounce-in max-w-md mx-4">
            <div className="text-6xl mb-4">🎉</div>
            <Trophy className="w-20 h-20 text-yellow-500 mx-auto mb-4 animate-spin-slow" />
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Congratulations!</h2>
            <p className="text-gray-600 text-lg">
              You've completed your learning path! You're one step closer to becoming a {targetRole}!
            </p>
            <button
              onClick={() => setShowCelebration(false)}
              className="mt-6 px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-full hover:scale-105 transition-transform"
            >
              Continue Journey
            </button>
          </div>
        </div>
      )}

      {/* Header Section */}
      <div className="sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Rocket className="text-indigo-600 animate-pulse" size={32} />
                <Sparkles className="absolute -top-1 -right-1 text-yellow-400" size={16} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Your Learning Journey</h1>
                <p className="text-sm text-gray-600">Goal: {targetRole}</p>
              </div>
            </div>
            <button
              onClick={onNewPath}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors text-sm"
            >
              New Path
            </button>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700">Overall Progress</span>
              <span className="text-sm font-bold text-indigo-600">{getProgressPercentage()}%</span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 transition-all duration-700 ease-out relative"
                style={{ width: `${getProgressPercentage()}%` }}
              >
                <div className="absolute inset-0 bg-white/30 animate-shimmer"></div>
              </div>
            </div>
            <div className="flex items-center justify-between mt-1 text-xs text-gray-500">
              <span>{completedSteps.length} of {learningPath.length} steps completed</span>
              <span>{learningPath.length - completedSteps.length} remaining</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Learning Path Steps */}
        <div className="space-y-6">
          {learningPath.map((step, index) => {
            const stepData = typeof step === 'string' 
              ? { title: step, description: '', resources: [] }
              : step;

            const isActive = activeStep === index;
            const isCompleted = completedSteps.includes(index);
            const isExpanded = expandedSteps.includes(index);
            const isLocked = index > activeStep && !isCompleted;

            return (
              <div 
                key={index}
                id={`step-${index}`}
                className={`relative transition-all duration-500 ${
                  isActive ? 'scale-105' : 'scale-100'
                }`}
              >
                {/* Connecting Line */}
                {index !== learningPath.length - 1 && (
                  <div className="absolute left-16 top-32 bottom-0 w-1 bg-gradient-to-b from-indigo-400 via-purple-400 to-pink-400 ml-0.5 animate-glow"></div>
                )}

                {/* Step Card */}
                <div 
                  className={`relative bg-white rounded-2xl border-2 transition-all duration-300 ${
                    isActive 
                      ? 'border-indigo-500 shadow-2xl shadow-indigo-200' 
                      : isCompleted
                      ? 'border-green-400 shadow-lg'
                      : isLocked
                      ? 'border-gray-200 opacity-60'
                      : 'border-gray-300 shadow-md hover:shadow-lg'
                  }`}
                >
                  {/* Step Header */}
                  <div className="flex items-start gap-6 p-6">
                    
                    {/* Avatar Circle */}
                    <div className="relative flex-shrink-0">
                      <div className={`w-32 h-32 rounded-full border-4 overflow-hidden transition-all duration-300 ${
                        isActive 
                          ? 'border-indigo-500 shadow-xl animate-float' 
                          : isCompleted
                          ? 'border-green-500'
                          : 'border-gray-300'
                      }`}>
                        <img 
                          src={getAvatarForStep(index, learningPath.length)} 
                          alt={`Step ${index + 1} avatar`}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      
                      {/* Step Number Badge */}
                      <div className={`absolute -bottom-2 -right-2 w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow-lg ${
                        isCompleted
                          ? 'bg-gradient-to-br from-green-500 to-emerald-600'
                          : isActive
                          ? 'bg-gradient-to-br from-indigo-600 to-purple-600 animate-pulse'
                          : 'bg-gradient-to-br from-gray-400 to-gray-500'
                      }`}>
                        {isCompleted ? <CheckCircle2 size={20} /> : index + 1}
                      </div>

                      {/* Active Pulse Effect */}
                      {isActive && (
                        <div className="absolute inset-0 rounded-full border-4 border-indigo-400 animate-ping-slow"></div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      
                      {/* Title Row */}
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            {isActive && <Zap className="text-yellow-500 animate-bounce" size={20} />}
                            {isCompleted && <Award className="text-green-500" size={20} />}
                            {!isActive && !isCompleted && <Brain className="text-gray-400" size={20} />}
                            <h3 className={`text-2xl font-bold ${
                              isActive ? 'text-indigo-600' : isCompleted ? 'text-green-600' : 'text-gray-900'
                            }`}>
                              {stepData.title || stepData.skill || `Step ${index + 1}`}
                            </h3>
                          </div>

                          {/* Phase Badge */}
                          {stepData.phase && (
                            <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${
                              isActive 
                                ? 'bg-indigo-100 text-indigo-700' 
                                : isCompleted
                                ? 'bg-green-100 text-green-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}>
                              <Star size={12} />
                              {stepData.phase}
                            </span>
                          )}
                        </div>

                        {/* Expand/Collapse Button */}
                        <button
                          onClick={() => toggleStepExpansion(index)}
                          disabled={isLocked}
                          className={`p-2 rounded-full transition-all ${
                            isLocked 
                              ? 'bg-gray-100 cursor-not-allowed' 
                              : 'bg-gray-100 hover:bg-indigo-100'
                          }`}
                        >
                          {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                        </button>
                      </div>

                      {/* Quick Info */}
                      <div className="flex flex-wrap gap-4 mb-3">
                        {stepData.duration && (
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <Clock size={16} className="text-indigo-500" />
                            <span className="font-medium">{stepData.duration}</span>
                          </div>
                        )}
                        {stepData.difficulty && (
                          <div className="flex items-center gap-2 text-sm">
                            <Target size={16} className="text-orange-500" />
                            <span className="font-medium text-gray-700">{stepData.difficulty}</span>
                          </div>
                        )}
                        {isCompleted && (
                          <div className="flex items-center gap-2 text-sm text-green-600 font-semibold">
                            <CheckCircle2 size={16} />
                            <span>Completed!</span>
                          </div>
                        )}
                      </div>

                      {/* Short Description (Always Visible) */}
                      {stepData.description && (
                        <p className="text-gray-600 text-sm leading-relaxed line-clamp-2">
                          {stepData.description}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="px-6 pb-6 space-y-6 animate-slideDown">
                      
                      {/* Full Description */}
                      {stepData.description && (
                        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-5 border border-indigo-100">
                          <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                            <BookOpen size={18} className="text-indigo-600" />
                            What You'll Learn
                          </h4>
                          <p className="text-gray-700 leading-relaxed">
                            {stepData.description}
                          </p>
                        </div>
                      )}

                      {/* Outcome */}
                      {stepData.outcome && stepData.outcome !== stepData.description && (
                        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-5 border border-green-100">
                          <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                            <TrendingUp size={18} className="text-green-600" />
                            Expected Outcome
                          </h4>
                          <p className="text-gray-700 leading-relaxed">
                            {stepData.outcome}
                          </p>
                        </div>
                      )}

                      {/* Resources */}
                      {stepData.resources && stepData.resources.length > 0 && (
                        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-5 border border-yellow-100">
                          <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                            <Code size={18} className="text-orange-600" />
                            Learning Resources ({stepData.resources.length})
                          </h4>
                          <div className="grid gap-3">
                            {stepData.resources.map((resource, resIndex) => {
                              const resourceData = typeof resource === 'string' 
                                ? { title: resource, url: '#' }
                                : resource;
                              
                              return (
                                <a
                                  key={resIndex}
                                  href={resourceData.url || resourceData.link || '#'}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-3 p-3 bg-white rounded-lg hover:bg-orange-50 border border-transparent hover:border-orange-200 transition-all group"
                                >
                                  <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                                    <Play size={14} className="text-orange-600" />
                                  </div>
                                  <span className="text-gray-700 font-medium flex-1 group-hover:text-orange-700">
                                    {resourceData.title || resourceData.name || resource}
                                  </span>
                                  <ExternalLink size={16} className="text-gray-400 group-hover:text-orange-600 transition-colors" />
                                </a>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Action Buttons */}
                      <div className="flex gap-3 pt-4 border-t border-gray-200">
                        {!isCompleted && (
                          <button
                            onClick={() => markAsCompleted(index)}
                            disabled={isLocked}
                            className={`flex-1 py-3 px-6 rounded-xl font-bold transition-all ${
                              isLocked
                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                : 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-lg hover:scale-105 active:scale-95'
                            }`}
                          >
                            <CheckCircle2 size={18} className="inline mr-2" />
                            Mark as Completed
                          </button>
                        )}
                        {index < learningPath.length - 1 && (
                          <button
                            onClick={goToNextStep}
                            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl hover:shadow-lg hover:scale-105 active:scale-95 transition-all"
                          >
                            Next Step
                            <ChevronRight size={18} className="inline ml-2" />
                          </button>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Lock Overlay */}
                  {isLocked && (
                    <div className="absolute inset-0 bg-white/60 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                      <div className="text-center">
                        <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-2">
                          <span className="text-3xl">🔒</span>
                        </div>
                        <p className="text-gray-600 font-semibold">Complete previous steps to unlock</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Success Tips */}
        <div className="mt-12 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Lightbulb size={32} className="text-yellow-300" />
            <h3 className="text-2xl font-bold">Pro Tips for Success</h3>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <span>📚</span>
              </div>
              <div>
                <h4 className="font-bold mb-1">Learn by Doing</h4>
                <p className="text-sm text-indigo-100">Build projects after each step to solidify your knowledge</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <span>⏰</span>
              </div>
              <div>
                <h4 className="font-bold mb-1">Stay Consistent</h4>
                <p className="text-sm text-indigo-100">Dedicate time daily, even if it's just 30 minutes</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <span>🤝</span>
              </div>
              <div>
                <h4 className="font-bold mb-1">Join Communities</h4>
                <p className="text-sm text-indigo-100">Connect with others on Discord, Reddit, or LinkedIn</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <span>🎯</span>
              </div>
              <div>
                <h4 className="font-bold mb-1">Track Progress</h4>
                <p className="text-sm text-indigo-100">Celebrate small wins and adjust your pace as needed</p>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Floating Navigation */}
      {learningPath.length > 1 && (
        <div className="fixed bottom-8 right-8 flex gap-3 z-30">
          {activeStep > 0 && (
            <button
              onClick={goToPreviousStep}
              className="w-14 h-14 bg-white shadow-xl rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-transform border-2 border-gray-200"
              title="Previous Step"
            >
              <ChevronRight size={24} className="text-gray-700 rotate-180" />
            </button>
          )}
          {activeStep < learningPath.length - 1 && (
            <button
              onClick={goToNextStep}
              className="w-14 h-14 bg-gradient-to-r from-indigo-600 to-purple-600 shadow-xl rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-transform text-white"
              title="Next Step"
            >
              <ChevronRight size={24} />
            </button>
          )}
        </div>
      )}

    </div>
  );
};

export default AnimatedLearningPath;
