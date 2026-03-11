import axios from 'axios';

// Base API URL - update this with your backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // If FormData, remove Content-Type to let axios set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Upload resume - basic parsing only
  uploadResume: async (formData) => {
    const response = await api.post('/upload-resume', formData, {
      timeout: 30000,
    });
    return response.data;
  },

  // Smart Analysis - Complete AI-powered analysis with NVIDIA
  smartAnalysis: async (formData, targetRole = null) => {
    // Only add target role if explicitly provided, otherwise let backend auto-detect
    if (targetRole) {
      formData.append('target_role', targetRole);
    }
    formData.append('num_jobs', '15'); // Fetch 15 jobs for better results
    
    const response = await api.post('/upload-resume/smart-analysis', formData, {
      timeout: 300000, // 5 minutes - enough time for fetching and scoring all jobs
      onUploadProgress: (progressEvent) => {
        console.log('Upload progress:', Math.round((progressEvent.loaded * 100) / progressEvent.total) + '%');
      },
    });
    console.log('✅ Backend analysis complete:', response.data);
    return response.data;
  },

  // Analyze resume with jobs and ATS scores
  analyzeResumeWithJobs: async (formData, targetRole = null, includeATS = true) => {
    if (targetRole) formData.append('target_role', targetRole);
    formData.append('include_ats_scores', includeATS);
    
    const response = await api.post('/upload-resume/analyze-with-jobs', formData, {
      timeout: 60000,
    });
    return response.data;
  },

  // Get dashboard data (from localStorage or API)
  getDashboardData: async () => {
    // Try localStorage first
    const storedData = localStorage.getItem('resumeData');
    if (storedData) {
      const parsed = JSON.parse(storedData);
      return {
        name: parsed.name,
        extractedSkills: parsed.skills || [],
        education: parsed.education || [],
        experience: parsed.experience || [],
        skillGaps: [],
        recommendedJobs: [],
        learningPath: []
      };
    }
    // Fallback to API if available
    try {
      const response = await api.get('/dashboard-data');
      return response.data;
    } catch {
      return {
        extractedSkills: [],
        skillGaps: [],
        recommendedJobs: [],
        learningPath: []
      };
    }
  },

  // Get job recommendations - REAL JOBS from web search
  getJobs: async () => {
    try {
      // Get resume data from localStorage
      const storedData = localStorage.getItem('resumeData');
      const resumeData = storedData ? JSON.parse(storedData) : {};
      const skills = resumeData.skills || [];
      const targetRole = resumeData.targetRole || 'Software Engineer';
      
      if (skills.length === 0) {
        // Return empty if no skills
        return [];
      }
      
      // FETCH REAL JOBS from 12+ web APIs (Remotive, Jobicy, IndianAPI, RemoteOK, DevITjobs, etc.)
      const response = await api.get('/web-jobs/recommended', {
        params: { 
          target_role: targetRole,
          skills: skills.join(','),
          location: 'India',  // Changed to India for better local job results
          experience_level: resumeData.experienceLevel || 'Mid-level',
          top_n: 20,
          prioritize_india: true,  // Prioritize India-based jobs
        },
      });
      
      // Extract web jobs (real postings with apply links)
      const realJobs = response.data.recommendations?.web_jobs || [];
      const aiJobs = response.data.recommendations?.recommended_jobs || [];
      
      // Prioritize real web jobs
      const allJobs = [...realJobs, ...aiJobs];
      
      // Transform to match frontend expectations
      return allJobs.map(job => ({
        title: job.title || job.job_title || 'Job Title',
        company: job.company || 'Company',
        location: job.location || 'Remote',
        salary: job.salary || job.salary_range || job.salary_max || null, // All salary fields
        salary_range: job.salary_range || job.salary || job.salary_max || null,
        match_score: job.match_score || job.matchPercentage || 0,
        matchPercentage: job.match_score || job.matchPercentage || 0,
        skills: job.matched_skills || job.skills || [],
        matched_skills: job.matched_skills || job.skills || [],
        missing_skills: job.missing_skills || [],
        missingSkills: job.missing_skills || [],
        description: job.description || job.reason || '',
        url: job.url || '', // REAL APPLY LINK
        source: job.source || 'Web',
        posted_date: job.posted_date || job.created_at || '',
        job_type: job.job_type || 'Full-time',
      }));
    } catch (err) {
      console.error('Error fetching jobs:', err);
      // Fallback to AI recommendations if web search fails
      try {
        const response = await api.post('/job-recommendations', resumeData, {
          params: { 
            skills: skills.join(','),
          },
        });
        const jobs = response.data.recommended_jobs || [];
        return jobs.map(job => ({
          title: job.job_title || job.title || 'Job Title',
          matchPercentage: job.match_score || job.matchPercentage || 0,
          skills: job.matched_skills || job.skills || [],
          missingSkills: job.missing_skills || [],
          description: job.reason || job.description || '',
        }));
      } catch {
        return [];
      }
    }
  },

  // Get learning path
  getLearningPath: async (domain) => {
    try {
      if (!domain) {
        return [];
      }
      
      // Get missing skills from localStorage or use domain as target role
      const storedData = localStorage.getItem('resumeData');
      const resumeData = storedData ? JSON.parse(storedData) : {};
      const skills = resumeData.skills || [];
      
      // Use some default skills if none available
      const missingSkills = skills.length > 0 ? skills.slice(0, 5).join(',') : 'Python,SQL,AWS,Docker,React';
      
      const response = await api.get('/learning-path', {
        params: { 
          missing_skills: missingSkills,
          target_role: domain || 'Software Developer',
        },
        headers: {
          'Content-Type': 'application/json',
        },
      });
      // Transform to match frontend expectations
      const path = response.data.learning_path || [];
      return path.map(step => ({
        title: step.skill || step.title || 'Skill',
        description: step.outcome || step.description || '',
        resources: step.resources || [],
        phase: step.phase || 'Foundation',
        difficulty: step.difficulty || 'Intermediate',
      }));
    } catch (err) {
      console.error('Error fetching learning path:', err);
      // Return empty array on error
      return [];
    }
  },

  // Chat with AI
  chat: async (message, chatHistory = []) => {
    try {
      if (!message || !message.trim()) {
        return {
          answer: 'Please provide a question.',
          message: 'Please provide a question.',
          sources: [],
        };
      }
      
      // Get context from localStorage
      const storedData = localStorage.getItem('resumeData');
      const resumeJson = storedData ? JSON.parse(storedData) : null;
      
      // Get skill gap and job recommendations from localStorage
      const skillGapData = localStorage.getItem('skillGapReport');
      const skillGapReport = skillGapData ? JSON.parse(skillGapData) : null;
      
      const jobsData = localStorage.getItem('recommendedJobs');
      const jobRecommendations = jobsData ? JSON.parse(jobsData) : null;
      
      const response = await api.post('/chat', { 
        question: message,
        chat_history: chatHistory,
        resume_json: resumeJson,
        skill_gap_report: skillGapReport,
        job_recommendations: jobRecommendations,
      });
      // Transform response - handle both 'answer' and 'message' fields
      const answer = response.data.answer || response.data.message || response.data.response || 'I apologize, but I couldn\'t process your request.';
      return {
        answer: answer,
        message: answer,
        response: answer,
        sources: response.data.sources || [],
        confidence: response.data.confidence,
      };
    } catch (err) {
      console.error('Error in chat:', err);
      return {
        answer: 'I apologize, but I\'m having trouble connecting right now. Please try again later.',
        message: 'I apologize, but I\'m having trouble connecting right now. Please try again later.',
        sources: [],
      };
    }
  },

  // ===== USER HISTORY ENDPOINTS =====
  
  // Save chat history
  saveChatHistory: async (messages, sessionName = null) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) {
        console.warn('No user ID found, skipping chat save');
        return null;
      }
      
      const response = await api.post('/user-history/chat/save', {
        messages,
        session_name: sessionName,
        user_id: userId
      });
      return response.data;
    } catch (err) {
      console.error('Error saving chat history:', err);
      return null;
    }
  },

  // Get chat history list
  getChatHistory: async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return { chats: [] };
      
      const response = await api.get(`/user-history/chat/list?user_id=${userId}`);
      return response.data;
    } catch (err) {
      console.error('Error fetching chat history:', err);
      return { chats: [] };
    }
  },

  // Get specific chat by ID
  getChatById: async (chatId) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return null;
      
      const response = await api.get(`/user-history/chat/${chatId}?user_id=${userId}`);
      return response.data;
    } catch (err) {
      console.error('Error fetching chat:', err);
      return null;
    }
  },

  // Update chat history
  updateChatHistory: async (chatId, messages) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return null;
      
      const response = await api.put(`/user-history/chat/${chatId}`, {
        messages,
        user_id: userId
      });
      return response.data;
    } catch (err) {
      console.error('Error updating chat:', err);
      return null;
    }
  },

  // Delete chat
  deleteChat: async (chatId) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return null;
      
      const response = await api.delete(`/user-history/chat/${chatId}?user_id=${userId}`);
      return response.data;
    } catch (err) {
      console.error('Error deleting chat:', err);
      return null;
    }
  },

  // Save resume analysis
  saveResumeAnalysis: async (resumeData, analysisResults, fileName = null) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) {
        console.warn('No user ID found, skipping analysis save');
        return null;
      }
      
      const response = await api.post('/user-history/resume/save', {
        resume_data: resumeData,
        analysis_results: analysisResults,
        file_name: fileName,
        user_id: userId
      });
      return response.data;
    } catch (err) {
      console.error('Error saving resume analysis:', err);
      return null;
    }
  },

  // Get resume analyses list
  getResumeAnalyses: async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return { analyses: [] };
      
      const response = await api.get(`/user-history/resume/list?user_id=${userId}`);
      return response.data;
    } catch (err) {
      console.error('Error fetching resume analyses:', err);
      return { analyses: [] };
    }
  },

  // Save job recommendations
  saveJobRecommendations: async (jobs, resumeId = null) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) {
        console.warn('No user ID found, skipping job save');
        return null;
      }
      
      const response = await api.post('/user-history/jobs/save', {
        jobs,
        resume_id: resumeId,
        user_id: userId
      });
      return response.data;
    } catch (err) {
      console.error('Error saving job recommendations:', err);
      return null;
    }
  },

  // Get job recommendations list
  getJobRecommendationsHistory: async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return { recommendations: [] };
      
      const response = await api.get(`/user-history/jobs/list?user_id=${userId}`);
      return response.data;
    } catch (err) {
      console.error('Error fetching job recommendations:', err);
      return { recommendations: [] };
    }
  },

  // Get user history summary
  getUserHistorySummary: async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return { summary: {} };
      
      const response = await api.get(`/user-history/summary?user_id=${userId}`);
      return response.data;
    } catch (err) {
      console.error('Error fetching user summary:', err);
      return { summary: {} };
    }
  },

  // Auth endpoints
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', {
        email,
        password
      });
      
      const { access_token, user } = response.data;
      
      // Store token and user data
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return response.data;
    } catch (err) {
      console.error('Login error:', err);
      throw err;
    }
  },

  signup: async (name, email, password) => {
    try {
      const response = await api.post('/auth/signup', {
        name,
        email,
        password
      });
      
      const { access_token, user } = response.data;
      
      // Store token and user data
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return response.data;
    } catch (err) {
      console.error('Signup error:', err);
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  // ===== LEARNING PATH ENDPOINTS =====
  
  // Generate personalized learning path with AI
  generatePersonalizedLearningPath: async (data) => {
    try {
      const response = await api.post('/user-history/learning-path/generate', data);
      return response.data;
    } catch (err) {
      console.error('Error generating learning path:', err);
      throw err;
    }
  },

  // Save learning path
  saveLearningPath: async (pathData) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) {
        console.warn('No user ID found, skipping save');
        return null;
      }
      
      const response = await api.post('/user-history/learning-path/save', {
        ...pathData,
        user_id: userId
      });
      return response.data;
    } catch (err) {
      console.error('Error saving learning path:', err);
      return null;
    }
  },

  // Get saved learning paths
  getSavedLearningPaths: async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return { paths: [] };
      
      const response = await api.get(`/user-history/learning-path/list?user_id=${userId}`);
      return response.data;
    } catch (err) {
      console.error('Error fetching learning paths:', err);
      return { paths: [] };
    }
  },

  // Delete learning path
  deleteLearningPath: async (pathId) => {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = user.id;
      
      if (!userId) return null;
      
      const response = await api.delete(`/user-history/learning-path/${pathId}?user_id=${userId}`);
      return response.data;
    } catch (err) {
      console.error('Error deleting learning path:', err);
      return null;
    }
  },

  // Mock Interview - Generate questions
  generateInterviewQuestions: async (formData) => {
    try {
      const response = await api.post('/api/mock-interview/generate-questions', formData, {
        timeout: 120000, // 2 minutes for AI generation (NVIDIA can be slow)
      });
      return response.data;
    } catch (err) {
      console.error('Error generating interview questions:', err);
      throw err;
    }
  },

  // Mock Interview - Evaluate answers
  evaluateMockInterview: async (evaluationData) => {
    try {
      const response = await api.post('/api/mock-interview/evaluate-answers', evaluationData, {
        timeout: 120000, // 2 minutes for AI evaluation
      });
      return response.data;
    } catch (err) {
      console.error('Error evaluating interview:', err);
      throw err;
    }
  },

  // Mock Interview - Get history
  getInterviewHistory: async (page = 1, perPage = 10) => {
    try {
      const response = await api.get('/api/mock-interview/history', {
        params: { page, per_page: perPage }
      });
      return response.data;
    } catch (err) {
      console.error('Error fetching interview history:', err);
      throw err;
    }
  },

  // Mock Interview - Get detail
  getInterviewDetail: async (interviewId) => {
    try {
      const response = await api.get(`/api/mock-interview/detail/${interviewId}`);
      return response.data;
    } catch (err) {
      console.error('Error fetching interview detail:', err);
      throw err;
    }
  },
};

export default api;
