import { useState, useEffect, useCallback, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen, Trophy, Lightbulb, CheckCircle2, Clock, ExternalLink,
  Target, Play, Award, Brain, Code, Zap, Star, TrendingUp,
  ChevronRight, ChevronLeft, Sparkles, Rocket, ArrowLeft,
  GraduationCap, Users, Coffee, Timer, SkipForward, Pause,
  Wrench, Layers, MessageCircle, Hammer, Tag, CheckSquare
} from 'lucide-react';

/* ─────────── Helpers ─────────── */
const AVATAR_SEEDS = ['mentor', 'coach', 'guide', 'sage', 'wizard', 'guru', 'sensei', 'professor'];
const AVATAR_BG = ['b6e3f4', 'c0aede', 'ffd5dc', 'd1f4e0', 'ffe8b6', 'ffc9c9', 'c4f0f4', 'e8d5f5'];
const PHASE_COLORS = [
  { bg: 'from-blue-500 to-indigo-600', light: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', ring: 'ring-blue-400', accent: '#6366f1' },
  { bg: 'from-purple-500 to-violet-600', light: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', ring: 'ring-purple-400', accent: '#8b5cf6' },
  { bg: 'from-pink-500 to-rose-600', light: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200', ring: 'ring-pink-400', accent: '#ec4899' },
  { bg: 'from-amber-500 to-orange-600', light: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', ring: 'ring-amber-400', accent: '#f59e0b' },
  { bg: 'from-emerald-500 to-teal-600', light: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', ring: 'ring-emerald-400', accent: '#10b981' },
  { bg: 'from-cyan-500 to-sky-600', light: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-200', ring: 'ring-cyan-400', accent: '#06b6d4' },
  { bg: 'from-red-500 to-rose-600', light: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', ring: 'ring-red-400', accent: '#ef4444' },
  { bg: 'from-indigo-500 to-blue-600', light: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200', ring: 'ring-indigo-400', accent: '#4f46e5' },
];

const getAvatar = (idx) =>
  `https://api.dicebear.com/7.x/avataaars/svg?seed=${AVATAR_SEEDS[idx % AVATAR_SEEDS.length]}&backgroundColor=${AVATAR_BG[idx % AVATAR_BG.length]}&size=160`;

const getColor = (idx) => PHASE_COLORS[idx % PHASE_COLORS.length];

/* ─────────── Particles ─────────── */
const Particles = () => {
  const particles = Array.from({ length: 16 }, (_, i) => ({
    id: i, x: Math.random() * 100, y: Math.random() * 100,
    size: Math.random() * 6 + 2, delay: Math.random() * 5, duration: Math.random() * 5 + 5,
  }));
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {particles.map((p) => (
        <motion.div key={p.id} className="absolute rounded-full bg-gradient-to-br from-purple-400/20 to-indigo-400/20"
          style={{ left: `${p.x}%`, top: `${p.y}%`, width: p.size, height: p.size }}
          animate={{ y: [0, -30, 0], opacity: [0.2, 0.6, 0.2], scale: [1, 1.5, 1] }}
          transition={{ duration: p.duration, delay: p.delay, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}
    </div>
  );
};

/* ─────────── Typewriter Text ─────────── */
const TypewriterText = ({ text, speed = 25, onComplete }) => {
  const [displayed, setDisplayed] = useState('');
  const indexRef = useRef(0);

  useEffect(() => {
    setDisplayed('');
    indexRef.current = 0;
    const iv = setInterval(() => {
      if (indexRef.current < text.length) {
        setDisplayed(text.slice(0, indexRef.current + 1));
        indexRef.current++;
      } else {
        clearInterval(iv);
        onComplete?.();
      }
    }, speed);
    return () => clearInterval(iv);
  }, [text, speed]);

  return <span>{displayed}<span className="animate-pulse">|</span></span>;
};

/* ─────────── Character Speech Bubble (AI dialogue) ─────────── */
const CharacterSpeechBubble = ({ dialogue, delay = 0, useTypewriter = true }) => (
  <motion.div
    initial={{ opacity: 0, y: 15, scale: 0.95 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    transition={{ delay, type: 'spring', stiffness: 200, damping: 20 }}
    className="relative bg-white rounded-2xl rounded-bl-md shadow-xl shadow-purple-100/50 border border-purple-100 px-6 py-4 max-w-xl"
  >
    <div className="absolute -bottom-2 left-6 w-4 h-4 bg-white border-b border-r border-purple-100 rotate-45" />
    <div className="flex items-start gap-2">
      <MessageCircle size={16} className="text-purple-400 mt-0.5 flex-shrink-0" />
      <p className="text-gray-700 text-sm leading-relaxed">
        {useTypewriter ? <TypewriterText text={dialogue} speed={20} /> : dialogue}
      </p>
    </div>
  </motion.div>
);

/* ─────────── Floating Character Avatar ─────────── */
const FloatingCharacter = ({ phaseIndex, isActive, position = 'inline' }) => {
  const posClass = position === 'fixed'
    ? 'fixed bottom-24 right-6 z-40'
    : 'relative';

  return (
    <motion.div className={posClass}
      animate={isActive ? { y: [0, -8, 0] } : {}}
      transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
    >
      <div className={`w-20 h-20 md:w-24 md:h-24 rounded-full border-4 overflow-hidden shadow-xl transition-all duration-500 ${isActive ? 'border-purple-500 shadow-purple-200/60' : 'border-gray-200'
        }`}>
        <img src={getAvatar(phaseIndex)} alt="AI Guide" className="w-full h-full object-cover" />
      </div>
      {isActive && (
        <motion.div
          className="absolute -top-1 -right-1 w-6 h-6 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-full flex items-center justify-center shadow-lg"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <Sparkles size={12} className="text-white" />
        </motion.div>
      )}
    </motion.div>
  );
};

/* ─────────── Key Concept Tag ─────────── */
const ConceptTag = ({ concept, index, color }) => (
  <motion.span
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay: 0.4 + index * 0.08, type: 'spring' }}
    className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-semibold ${color.light} ${color.text} border ${color.border}`}
  >
    <Tag size={10} />
    {concept}
  </motion.span>
);

/* ─────────── Project Card ─────────── */
const ProjectCard = ({ project, index, color }) => {
  const p = typeof project === 'string' ? { name: project, description: '' } : project;
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.5 + index * 0.15, type: 'spring' }}
      className={`p-4 ${color.light} rounded-xl border ${color.border} group hover:shadow-md transition-all`}
    >
      <div className="flex items-center gap-2 mb-2">
        <Hammer size={16} className={color.text} />
        <h5 className="font-bold text-gray-800 text-sm">{p.name}</h5>
      </div>
      {p.description && (
        <p className="text-gray-600 text-xs leading-relaxed">{p.description}</p>
      )}
    </motion.div>
  );
};

/* ─────────── Resource Link ─────────── */
const ResourceLink = ({ resource, index, color }) => {
  const r = typeof resource === 'string' ? { title: resource, url: '#' } : resource;
  return (
    <motion.a
      href={r.url || r.link || '#'}
      target="_blank"
      rel="noopener noreferrer"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.3 + index * 0.1, type: 'spring', stiffness: 200 }}
      className={`flex items-center gap-3 p-3 ${color.light} rounded-xl border ${color.border} hover:shadow-md transition-all group cursor-pointer`}
    >
      <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${color.bg} flex items-center justify-center flex-shrink-0 shadow-sm`}>
        <Play size={14} className="text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <span className="text-gray-700 text-sm font-medium block truncate group-hover:text-gray-900 transition-colors">
          {r.title || r.name || resource}
        </span>
        {r.type && <span className="text-xs text-gray-400 capitalize">{r.type}</span>}
      </div>
      <ExternalLink size={14} className="text-gray-300 group-hover:text-gray-500 transition-colors flex-shrink-0" />
    </motion.a>
  );
};

/* ─────────── Timeline Dot ─────────── */
const TimelineDot = ({ index, isActive, isVisited, onClick, title, color }) => (
  <button onClick={onClick} className="group flex items-center gap-3 w-full text-left py-1" title={title}>
    <div className="relative flex flex-col items-center">
      <motion.div
        className={`w-4 h-4 rounded-full border-2 transition-all duration-300 ${isActive ? `bg-gradient-to-br ${color.bg} border-transparent shadow-lg`
            : isVisited ? 'bg-purple-200 border-purple-300' : 'bg-gray-100 border-gray-300'
          }`}
        animate={isActive ? { scale: [1, 1.3, 1] } : {}}
        transition={{ duration: 2, repeat: Infinity }}
      />
      {isActive && (
        <motion.div className={`absolute inset-0 rounded-full ${color.ring} ring-2 ring-offset-2`}
          animate={{ opacity: [0.5, 0, 0.5] }} transition={{ duration: 2, repeat: Infinity }}
        />
      )}
    </div>
    <span className={`text-xs font-medium truncate max-w-[120px] transition-colors ${isActive ? color.text : isVisited ? 'text-gray-600' : 'text-gray-400'
      }`}>{title}</span>
    {isVisited && !isActive && <CheckSquare size={12} className="text-green-400 ml-auto" />}
  </button>
);

/* ─────────── Celebration Overlay ─────────── */
const CelebrationOverlay = ({ targetRole, onClose }) => (
  <motion.div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
    initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    {Array.from({ length: 30 }).map((_, i) => (
      <motion.div key={i} className="absolute w-3 h-3 rounded-full"
        style={{
          backgroundColor: ['#7c3aed', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#ef4444'][i % 6],
          left: `${Math.random() * 100}%`, top: `${Math.random() * 40}%`,
        }}
        initial={{ y: -100, opacity: 1 }}
        animate={{ y: 800, opacity: 0, rotate: Math.random() * 720 - 360 }}
        transition={{ duration: Math.random() * 2 + 1.5, delay: Math.random() * 0.5 }}
      />
    ))}
    <motion.div className="bg-white rounded-3xl p-10 text-center shadow-2xl max-w-md mx-4 relative z-10"
      initial={{ scale: 0.5, y: 50 }} animate={{ scale: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 200, damping: 15 }}>
      <motion.div className="text-7xl mb-4" animate={{ rotate: [0, -10, 10, -10, 0] }} transition={{ duration: 0.5, delay: 0.3 }}>🎓</motion.div>
      <Trophy className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
      <h2 className="text-3xl font-bold text-gray-900 mb-2">You Made It!</h2>
      <p className="text-gray-600 text-lg mb-6">
        You've explored the complete roadmap to becoming a <strong className="text-purple-700">{targetRole}</strong>!
      </p>
      <button onClick={onClose}
        className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-full hover:scale-105 transition-transform shadow-lg">
        Let's Go! 🚀
      </button>
    </motion.div>
  </motion.div>
);

/* ═══════════ MAIN COMPONENT ═══════════ */
const LearningPathResults = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { learningPath: rawPath, targetRole, learningGoal, currentSkills, timeCommitment } = location.state || {};

  const [currentPhase, setCurrentPhase] = useState(-1);
  const [visitedPhases, setVisitedPhases] = useState(new Set());
  const [showCelebration, setShowCelebration] = useState(false);
  const [autoPlay, setAutoPlay] = useState(false);
  const autoPlayRef = useRef(null);

  // Normalize path data
  const learningPath = (Array.isArray(rawPath) ? rawPath : []).map((step) =>
    typeof step === 'string' ? { title: step, description: '', resources: [], character_dialogue: '' } : step
  );

  // Redirect if no data
  useEffect(() => {
    if (!rawPath || !targetRole) {
      navigate('/learning-path', { replace: true });
    }
  }, [rawPath, targetRole, navigate]);

  // Mark visited
  useEffect(() => {
    if (currentPhase >= 0) {
      setVisitedPhases((prev) => new Set(prev).add(currentPhase));
    }
  }, [currentPhase]);

  // Auto-play
  useEffect(() => {
    if (autoPlay && currentPhase < learningPath.length - 1) {
      autoPlayRef.current = setTimeout(() => setCurrentPhase((p) => p + 1), 10000);
    }
    return () => clearTimeout(autoPlayRef.current);
  }, [autoPlay, currentPhase, learningPath.length]);

  const goNext = useCallback(() => {
    if (currentPhase < learningPath.length - 1) {
      setCurrentPhase((p) => p + 1);
    } else if (currentPhase === learningPath.length - 1) {
      setShowCelebration(true);
      setAutoPlay(false);
    }
  }, [currentPhase, learningPath.length]);

  const goPrev = useCallback(() => setCurrentPhase((p) => Math.max(-1, p - 1)), []);
  const goToPhase = useCallback((idx) => { setCurrentPhase(idx); setAutoPlay(false); }, []);

  if (!rawPath || !targetRole) return null;

  const color = currentPhase >= 0 ? getColor(currentPhase) : PHASE_COLORS[0];
  const step = currentPhase >= 0 ? learningPath[currentPhase] : null;

  // Get character dialogue — prefer AI-generated, fallback to generic
  const getDialogue = (s, idx) => {
    if (s?.character_dialogue) return s.character_dialogue;
    const title = s?.title || `Phase ${idx + 1}`;
    if (idx === 0) return `Let's start with the foundation — ${title}. This is where your journey begins! Every expert started here, and so will you.`;
    if (idx === learningPath.length - 1) return `Final phase! ${title} — You're almost there! 🎉 This is where everything comes together into your portfolio masterpiece.`;
    return `Next up: ${title}. You're making great progress! 💪 Keep up the momentum — consistency is the key to mastery.`;
  };

  return (
    <div className="h-screen w-full bg-gradient-to-br from-slate-50 via-white to-purple-50 flex overflow-hidden">
      <Particles />

      {/* ─── Left Timeline Sidebar ─── */}
      <aside className="hidden lg:flex w-72 flex-col bg-white/70 backdrop-blur-xl border-r border-gray-100 z-20">
        <div className="p-5 border-b border-gray-50">
          <button onClick={() => navigate('/learning-path')}
            className="flex items-center gap-2 text-gray-500 hover:text-purple-600 transition-colors text-sm mb-4 group">
            <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> Back to Form
          </button>
          <div className="flex items-center gap-2 mb-1">
            <GraduationCap size={18} className="text-purple-600" />
            <span className="font-bold text-gray-900 text-sm">Learning Journey</span>
          </div>
          <p className="text-xs text-gray-400 truncate">{targetRole}</p>
        </div>

        {/* Intro */}
        <div className="px-5 pt-5 pb-2">
          <TimelineDot index={-1} isActive={currentPhase === -1} isVisited={true}
            onClick={() => goToPhase(-1)} title="Introduction" color={PHASE_COLORS[0]} />
        </div>

        {/* Phase dots */}
        <div className="flex-1 overflow-y-auto px-5 space-y-0.5 pb-4">
          {learningPath.map((s, i) => (
            <div key={i} className="relative">
              {i < learningPath.length - 1 && (
                <div className={`absolute left-[7px] top-6 w-0.5 h-5 ${visitedPhases.has(i) ? 'bg-purple-200' : 'bg-gray-100'}`} />
              )}
              <TimelineDot index={i} isActive={currentPhase === i} isVisited={visitedPhases.has(i)}
                onClick={() => goToPhase(i)} title={s.title || s.skill || `Phase ${i + 1}`} color={getColor(i)} />
            </div>
          ))}
        </div>

        {/* Progress */}
        <div className="p-5 border-t border-gray-50">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>Progress</span>
            <span className="font-bold text-purple-600">{Math.max(0, currentPhase + 1)} / {learningPath.length}</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full"
              animate={{ width: `${((currentPhase + 1) / learningPath.length) * 100}%` }}
              transition={{ duration: 0.5 }} />
          </div>
        </div>
      </aside>

      {/* ─── Main Content ─── */}
      <main className="flex-1 flex flex-col relative z-10 overflow-hidden">
        {/* Top Bar */}
        <div className="flex items-center justify-between px-6 py-3 bg-white/60 backdrop-blur-md border-b border-gray-100">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/learning-path')} className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors">
              <ArrowLeft size={18} />
            </button>
            <div>
              <h1 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Rocket size={18} className="text-purple-600" /> {targetRole}
              </h1>
              <p className="text-xs text-gray-400 truncate max-w-sm">{learningGoal}</p>
            </div>
          </div>
          <button onClick={() => setAutoPlay(!autoPlay)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${autoPlay ? 'bg-purple-100 text-purple-700 ring-2 ring-purple-200' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}>
            {autoPlay ? <Pause size={12} /> : <Play size={12} />}
            {autoPlay ? 'Pause' : 'Auto-Play'}
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-6 py-10 min-h-full">
            <AnimatePresence mode="wait">

              {/* ─── INTRO SCREEN ─── */}
              {currentPhase === -1 && (
                <motion.div key="intro" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, x: -50 }}
                  transition={{ duration: 0.4 }} className="flex flex-col items-center text-center">
                  <motion.div initial={{ scale: 0, rotate: -180 }} animate={{ scale: 1, rotate: 0 }}
                    transition={{ type: 'spring', stiffness: 150, damping: 15, delay: 0.2 }} className="mb-8">
                    <div className="w-32 h-32 md:w-40 md:h-40 rounded-full border-4 border-purple-400 overflow-hidden shadow-2xl shadow-purple-200/60 animate-float">
                      <img src={getAvatar(0)} alt="AI Guide" className="w-full h-full object-cover" />
                    </div>
                  </motion.div>

                  <div className="space-y-4 mb-10 max-w-lg">
                    {[
                      `Hey there! 👋 I'm your AI Learning Guide.`,
                      `I've analyzed the best path to become a **${targetRole}**.`,
                      `Let me walk you through each phase step by step!`,
                    ].map((line, i) => (
                      <motion.div key={i} initial={{ opacity: 0, y: 15, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ delay: 0.5 + i * 0.4, type: 'spring', stiffness: 200, damping: 20 }}
                        className="relative bg-white rounded-2xl rounded-bl-md shadow-xl shadow-purple-100/50 border border-purple-100 px-6 py-4 max-w-lg">
                        <p className="text-gray-700 text-sm leading-relaxed"
                          dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.*?)\*\*/g, '<strong class="text-purple-700">$1</strong>') }} />
                      </motion.div>
                    ))}
                  </div>

                  <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 2 }}
                    className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-2xl mb-10">
                    {[
                      { icon: Target, label: 'Role', value: targetRole, c: 'text-blue-600 bg-blue-50' },
                      { icon: BookOpen, label: 'Phases', value: `${learningPath.length} Steps`, c: 'text-purple-600 bg-purple-50' },
                      { icon: Clock, label: 'Weekly', value: `${timeCommitment || '5-10'}h`, c: 'text-amber-600 bg-amber-50' },
                      { icon: CheckCircle2, label: 'Skills', value: currentSkills ? currentSkills.split(',').length : '0', c: 'text-green-600 bg-green-50' },
                    ].map(({ icon: Icon, label, value, c }, i) => (
                      <motion.div key={label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 2.2 + i * 0.1 }} className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
                        <div className={`w-8 h-8 rounded-lg ${c} flex items-center justify-center mb-2`}><Icon size={16} /></div>
                        <p className="text-xs text-gray-400">{label}</p>
                        <p className="text-sm font-bold text-gray-800 truncate">{value}</p>
                      </motion.div>
                    ))}
                  </motion.div>

                  <motion.button initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 2.8, type: 'spring' }} onClick={goNext}
                    className="px-10 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-2xl shadow-xl shadow-purple-200/50 hover:shadow-2xl hover:scale-105 active:scale-95 transition-all flex items-center gap-3 text-lg">
                    Begin Your Journey <ChevronRight size={22} />
                  </motion.button>
                </motion.div>
              )}

              {/* ─── PHASE SCREEN ─── */}
              {currentPhase >= 0 && step && (
                <motion.div key={`phase-${currentPhase}`}
                  initial={{ opacity: 0, x: 60 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -60 }}
                  transition={{ duration: 0.4 }}>

                  {/* Character + AI Dialogue */}
                  <div className="flex items-start gap-5 mb-8">
                    <FloatingCharacter phaseIndex={currentPhase} isActive={true} />
                    <div className="flex-1 pt-2">
                      <CharacterSpeechBubble dialogue={getDialogue(step, currentPhase)} useTypewriter={true} />
                    </div>
                  </div>

                  {/* Phase Header */}
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mb-6">
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`px-3 py-1 rounded-full text-xs font-bold text-white bg-gradient-to-r ${color.bg} shadow-sm`}>
                        Phase {currentPhase + 1} of {learningPath.length}
                      </div>
                      {step.phase && (
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${color.light} ${color.text}`}>
                          <Star size={10} className="inline mr-1" />{step.phase}
                        </span>
                      )}
                      {step.difficulty && (
                        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-600">
                          <Zap size={10} className="inline mr-1" />{step.difficulty}
                        </span>
                      )}
                    </div>
                    <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                      {step.title || step.skill || `Phase ${currentPhase + 1}`}
                    </h2>
                    {step.duration && (
                      <div className="flex items-center gap-1.5 text-sm text-gray-500 mt-2">
                        <Timer size={14} className="text-indigo-500" />
                        <span className="font-medium">{step.duration}</span>
                      </div>
                    )}
                  </motion.div>

                  {/* Key Concepts */}
                  {step.key_concepts && step.key_concepts.length > 0 && (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} className="mb-6">
                      <div className="flex flex-wrap gap-2">
                        {step.key_concepts.map((concept, i) => (
                          <ConceptTag key={i} concept={concept} index={i} color={color} />
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Content Grid */}
                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    {step.description && (
                      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                        className={`${color.light} rounded-2xl p-6 border ${color.border}`}>
                        <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                          <BookOpen size={18} className={color.text} /> What You'll Learn
                        </h4>
                        <p className="text-gray-700 leading-relaxed text-sm">{step.description}</p>
                      </motion.div>
                    )}
                    {step.outcome && (
                      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
                        className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl p-6 border border-emerald-200">
                        <h4 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                          <TrendingUp size={18} className="text-emerald-600" /> Expected Outcome
                        </h4>
                        <p className="text-gray-700 leading-relaxed text-sm">{step.outcome}</p>
                      </motion.div>
                    )}
                  </div>

                  {/* Projects */}
                  {step.projects && step.projects.length > 0 && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }} className="mb-6">
                      <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Hammer size={18} className={color.text} /> Hands-On Projects
                        <span className={`text-xs font-normal px-2 py-0.5 rounded-full ${color.light} ${color.text}`}>{step.projects.length}</span>
                      </h4>
                      <div className="grid md:grid-cols-2 gap-4">
                        {step.projects.map((project, i) => (
                          <ProjectCard key={i} project={project} index={i} color={color} />
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Resources */}
                  {step.resources && step.resources.length > 0 && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="mb-6">
                      <h4 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Code size={18} className={color.text} /> Learning Resources
                        <span className={`text-xs font-normal px-2 py-0.5 rounded-full ${color.light} ${color.text}`}>{step.resources.length}</span>
                      </h4>
                      <div className="grid gap-3">
                        {step.resources.map((resource, i) => (
                          <ResourceLink key={i} resource={resource} index={i} color={color} />
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Pro Tip */}
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}
                    className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-5 flex items-start gap-4 mb-6">
                    <div className="w-10 h-10 bg-yellow-400/20 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Lightbulb size={20} className="text-yellow-400" />
                    </div>
                    <div>
                      <h5 className="text-white font-bold text-sm mb-1">Pro Tip</h5>
                      <p className="text-gray-300 text-xs leading-relaxed">
                        {currentPhase === 0
                          ? "Don't rush the fundamentals. A strong foundation will make everything else easier."
                          : currentPhase === learningPath.length - 1
                            ? "Build a portfolio project using everything you've learned — this is what employers will look at!"
                            : "Practice daily, even for just 30 minutes. Consistency beats intensity every single time."}
                      </p>
                    </div>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* ─── Bottom Nav ─── */}
        <div className="border-t border-gray-100 bg-white/80 backdrop-blur-md px-6 py-4 flex items-center justify-between relative z-20">
          <button onClick={goPrev} disabled={currentPhase <= -1}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all disabled:opacity-30 disabled:cursor-not-allowed bg-gray-100 text-gray-700 hover:bg-gray-200">
            <ChevronLeft size={16} /> Previous
          </button>
          <div className="lg:hidden flex items-center gap-1.5">
            {learningPath.map((_, i) => (
              <div key={i} className={`w-2 h-2 rounded-full transition-all ${i === currentPhase ? 'bg-purple-600 w-6' : i < currentPhase ? 'bg-purple-300' : 'bg-gray-200'
                }`} />
            ))}
          </div>
          <button onClick={goNext}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-bold text-sm transition-all shadow-lg hover:scale-105 active:scale-95 text-white bg-gradient-to-r ${currentPhase === learningPath.length - 1
                ? 'from-yellow-500 to-amber-600 shadow-amber-200/50'
                : 'from-purple-600 to-indigo-600 shadow-purple-200/50'
              }`}>
            {currentPhase === learningPath.length - 1 ? (<>Complete <Trophy size={16} /></>)
              : currentPhase === -1 ? (<>Start <Rocket size={16} /></>)
                : (<>Next Phase <ChevronRight size={16} /></>)}
          </button>
        </div>
      </main>

      {/* Celebration */}
      <AnimatePresence>
        {showCelebration && <CelebrationOverlay targetRole={targetRole} onClose={() => setShowCelebration(false)} />}
      </AnimatePresence>
    </div>
  );
};

export default LearningPathResults;
