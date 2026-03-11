import React, { useState, useEffect, useRef } from 'react';
import { apiService } from '../services/api'; 
import { 
  ArrowUp, User, Bot, Plus, Settings, Download, 
  X, Moon, Sun, Sparkles, Clock, Image as ImageIcon,
  Mic
} from 'lucide-react';

const Chatbot = () => {
  // --- State ---
  const [messages, setMessages] = useState([]); 
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showTimestamps, setShowTimestamps] = useState(true);
  
  // --- Refs ---
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // --- Effects ---
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    loadRecentChat();
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      saveChatToBackend();
    }
  }, [messages]);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    if (window.innerWidth > 768) {
      textareaRef.current?.focus();
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  // --- Logic ---
  const loadRecentChat = async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.id) {
        const chatHistory = await apiService.getChatHistory(user.id);
        if (chatHistory && chatHistory.length > 0) {
          const recentChat = chatHistory[0];
          if (recentChat.messages && recentChat.messages.length > 0) {
            setMessages(recentChat.messages);
            setCurrentChatId(recentChat._id);
          }
        }
      }
    } catch (err) {
      console.error('Error loading chat history:', err);
    }
  };

  const saveChatToBackend = async () => {
    try {
      if (currentChatId) {
        await apiService.updateChatHistory(currentChatId, messages);
      } else {
        const response = await apiService.saveChatHistory(messages);
        if (response && response.chat_id) {
          setCurrentChatId(response.chat_id);
        }
      }
    } catch (err) {
      console.error('Error saving chat:', err);
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setCurrentChatId(null);
    setInputMessage('');
    textareaRef.current?.focus();
  };

  const exportChat = () => {
    const chatText = messages.map(m => 
      `${m.role === 'user' ? 'You' : 'AI'}: ${m.content}`
    ).join('\n\n');
    
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
  };

  const handleInputResize = (e) => {
    setInputMessage(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 150)}px`;
  };

  const handleSend = async (e) => {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userContent = inputMessage.trim();
    const userMessage = {
      role: 'user',
      content: userContent,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    if (textareaRef.current) textareaRef.current.style.height = 'auto';

    try {
      const response = await apiService.chat(userContent, messages);
      const answerText = response.answer || response.message || response.content || "I couldn't process that request.";
      
      const aiMessage = {
        role: 'assistant',
        content: answerText,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: "I apologize, I'm having trouble connecting right now.",
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // --- Visuals ---
  const BackgroundBlobs = () => (
    <>
      <div className={`fixed top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl animate-blob pointer-events-none ${darkMode ? 'opacity-10' : 'opacity-60'}`}></div>
      <div className={`fixed top-[20%] left-[-10%] w-[400px] h-[400px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000 pointer-events-none ${darkMode ? 'opacity-10' : 'opacity-60'}`}></div>
      <div className={`fixed bottom-[-10%] right-[20%] w-[300px] h-[300px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000 pointer-events-none ${darkMode ? 'opacity-10' : 'opacity-60'}`}></div>
    </>
  );

  return (
    <div className={`fixed inset-0 flex flex-col font-sans overflow-hidden transition-colors duration-300 ${darkMode ? 'bg-gray-950 text-white' : 'bg-white text-gray-900'}`}>
      
      <BackgroundBlobs />
      
      <style>{`
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        textarea:focus { box-shadow: none; }
      `}</style>
      
      {/* --- HEADER --- */}
      <div className={`flex-none relative z-20 flex items-center justify-between px-6 py-4 border-b transition-colors ${darkMode ? 'bg-gray-950/80 border-gray-800' : 'bg-white/80 border-gray-100'} backdrop-blur-md`}>
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center shadow-sm shadow-purple-500/20 ${darkMode ? 'bg-indigo-600' : 'bg-black'}`}>
            <Sparkles size={16} className="text-white" />
          </div>
          <div>
            <span className="font-semibold text-sm tracking-tight block leading-none">PathFinder AI</span>
            <span className={`text-[10px] uppercase tracking-wider font-bold ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>Beta</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button 
            onClick={startNewChat}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              darkMode 
                ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' 
                : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            <Plus size={14} />
            <span className="hidden sm:inline">New Chat</span>
          </button>
          
          <button
            onClick={() => setShowSettings(true)}
            className={`p-2 rounded-lg transition-all ${darkMode ? 'hover:bg-gray-800 text-gray-400' : 'hover:bg-gray-100 text-gray-400 hover:text-gray-600'}`}
          >
            <Settings size={18} />
          </button>
        </div>
      </div>

      {/* --- SETTINGS MODAL --- */}
      {showSettings && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowSettings(false)}></div>
          <div className={`relative rounded-2xl shadow-2xl max-w-sm w-full p-6 border transition-all transform scale-100 ${darkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-white'}`}>
            <div className="flex justify-between items-center mb-6">
              <h2 className={`text-lg font-light ${darkMode ? 'text-white' : 'text-gray-900'}`}>Preferences</h2>
              <button onClick={() => setShowSettings(false)} className="text-gray-400 hover:text-gray-600"><X size={18}/></button>
            </div>
            
            <div className="space-y-1">
              <div className={`flex items-center justify-between p-3 rounded-xl ${darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-50'} transition-colors`}>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${darkMode ? 'bg-gray-800 text-purple-400' : 'bg-purple-50 text-purple-600'}`}>
                    {darkMode ? <Moon size={16} /> : <Sun size={16} />}
                  </div>
                  <span className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>Dark Mode</span>
                </div>
                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className={`w-10 h-6 rounded-full transition-all ${darkMode ? 'bg-indigo-600' : 'bg-gray-200'} relative`}
                >
                  <div className={`w-4 h-4 rounded-full bg-white absolute top-1 left-1 transition-transform shadow-sm ${darkMode ? 'translate-x-4' : 'translate-x-0'}`} />
                </button>
              </div>
              
              <div className={`flex items-center justify-between p-3 rounded-xl ${darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-50'} transition-colors`}>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${darkMode ? 'bg-gray-800 text-indigo-400' : 'bg-indigo-50 text-indigo-600'}`}>
                    <Clock size={16} />
                  </div>
                  <span className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'}`}>Timestamps</span>
                </div>
                <button
                  onClick={() => setShowTimestamps(!showTimestamps)}
                  className={`w-10 h-6 rounded-full transition-all ${showTimestamps ? 'bg-indigo-600' : 'bg-gray-200'} relative`}
                >
                  <div className={`w-4 h-4 rounded-full bg-white absolute top-1 left-1 transition-transform shadow-sm ${showTimestamps ? 'translate-x-4' : 'translate-x-0'}`} />
                </button>
              </div>

              {messages.length > 0 && (
                <div className="pt-4 mt-2 border-t border-gray-100 dark:border-gray-800">
                  <button
                    onClick={() => { exportChat(); setShowSettings(false); }}
                    className={`w-full px-4 py-3 rounded-xl text-sm font-medium transition-all flex items-center justify-center gap-2 ${
                      darkMode ? 'bg-gray-800 hover:bg-gray-700 text-white' : 'bg-gray-900 hover:bg-black text-white shadow-lg shadow-gray-200'
                    }`}
                  >
                    <Download size={16} />
                    Export Conversation
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* --- MAIN CHAT AREA --- */}
      <main className="flex-1 flex flex-col w-full max-w-4xl mx-auto overflow-hidden relative z-10">
        
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto px-4 py-6 no-scrollbar min-h-0 scroll-smooth">
          
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center pb-20 px-6 fade-in">
              <div className={`w-20 h-20 rounded-2xl flex items-center justify-center mb-8 border ${
                darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-white shadow-xl shadow-purple-100'
              }`}>
                 <Bot size={40} className="text-indigo-500" />
              </div>
              <h1 className={`text-3xl md:text-4xl font-light mb-4 text-center ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                How can I <span className="font-medium">help?</span>
              </h1>
              
              {/* Quick Actions */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full mt-8">
                 {['Explain quantum computing', 'Debug a React component', 'Draft a cold email', 'Suggest a project idea'].map((suggestion, i) => (
                    <button 
                      key={i}
                      onClick={() => { setInputMessage(suggestion); textareaRef.current?.focus(); }}
                      className={`text-xs px-4 py-3 rounded-xl border text-left transition-all ${
                        darkMode 
                        ? 'border-gray-800 bg-gray-900/50 hover:bg-gray-800 text-gray-300' 
                        : 'border-white bg-white/60 hover:bg-white text-gray-600 shadow-sm hover:shadow-md'
                      }`}
                    >
                      {suggestion}
                    </button>
                 ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col space-y-6 pb-4">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
                  
                  {msg.role === 'assistant' && (
                    <div className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center mt-1 border ${
                      darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-100 shadow-sm'
                    }`}>
                      <Sparkles size={14} className="text-indigo-500" />
                    </div>
                  )}

                  <div className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-sm ${
                    msg.role === 'user' 
                      ? `${darkMode ? 'bg-indigo-600 text-white' : 'bg-gray-900 text-white'} rounded-tr-sm` 
                      : `${darkMode ? 'bg-gray-800/80 border border-gray-700 text-gray-200' : 'bg-white/80 border border-white text-gray-800 shadow-purple-50'} rounded-tl-sm backdrop-blur-sm`
                  }`}>
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                    
                    {showTimestamps && (
                      <div className={`text-[10px] mt-2 flex items-center justify-end gap-1 opacity-50 ${
                        msg.role === 'user' ? 'text-white' : (darkMode ? 'text-gray-400' : 'text-gray-500')
                      }`}>
                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center mt-1 ${
                      darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'
                    }`}>
                      <User size={14} />
                    </div>
                  )}
                </div>
              ))}
              
              {loading && (
                <div className="flex gap-4 animate-pulse">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center mt-1 border ${
                      darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-100 shadow-sm'
                    }`}>
                      <Sparkles size={14} className="text-indigo-500" />
                  </div>
                  <div className={`flex space-x-1 items-center h-10 px-4 rounded-2xl rounded-tl-sm border ${
                    darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-white shadow-sm'
                  }`}>
                    <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"></div>
                    <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce delay-75"></div>
                    <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce delay-150"></div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} className="h-2" />
            </div>
          )}
        </div>

        {/* --- INPUT AREA --- */}
        {/* FIX: Reduced padding from pb-6 to pb-3 to remove excess space */}
        <div className={`flex-none w-full pb-3 pt-2 px-4 z-20`}>
          <div className={`rounded-2xl border shadow-xl relative max-w-3xl mx-auto flex items-end p-2 transition-all duration-300 ${
            darkMode 
              ? 'bg-gray-900 border-gray-800 shadow-black/40 focus-within:border-gray-700' 
              : 'bg-white/90 border-white shadow-purple-100/50 backdrop-blur-xl focus-within:border-indigo-100 focus-within:ring-4 focus-within:ring-indigo-50/50'
          }`}>
            
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={handleInputResize}
              onKeyDown={handleKeyDown}
              placeholder="Type your message..."
              className={`w-full bg-transparent resize-none outline-none text-sm px-4 py-3 min-h-[48px] max-h-[160px] no-scrollbar self-center ${
                darkMode ? 'text-white placeholder-gray-600' : 'text-gray-800 placeholder-gray-400'
              }`}
              rows={1}
            />

            {/* Action Buttons inside Input */}
            <div className="flex items-center gap-1 mb-1 mr-1">
               {!inputMessage.trim() && (
                  <div className="flex items-center gap-1 mr-1">
                     <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-gray-800 text-gray-500' : 'hover:bg-gray-100 text-gray-400'}`}>
                        <ImageIcon size={18} />
                     </button>
                     <button className={`p-2 rounded-lg transition-colors ${darkMode ? 'hover:bg-gray-800 text-gray-500' : 'hover:bg-gray-100 text-gray-400'}`}>
                        <Mic size={18} />
                     </button>
                  </div>
               )}

               <button 
                 onClick={handleSend}
                 disabled={!inputMessage.trim() || loading}
                 className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-300 ${
                   inputMessage.trim() 
                     ? `${darkMode ? 'bg-indigo-600 hover:bg-indigo-500' : 'bg-gray-900 hover:bg-black'} text-white shadow-md transform hover:scale-105 active:scale-95` 
                     : `${darkMode ? 'bg-gray-800 text-gray-600' : 'bg-gray-100 text-gray-300'} cursor-not-allowed`
                 }`}
               >
                 <ArrowUp size={18} strokeWidth={2.5} />
               </button>
            </div>

          </div>
          <p className={`text-[10px] text-center mt-2 ${darkMode ? 'text-gray-600' : 'text-gray-400'}`}>
            AI can make mistakes. Please verify important information.
          </p>
        </div>

      </main>
    </div>
  );
};

export default Chatbot;