import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, FileText, MessageSquare, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';

/**
 * Mock Interview Setup Page - "Think Tech" Minimalist Redesign
 */
const MockInterview = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    interviewType: '',
    role: '',
    jobDescription: '',
    experienceLevel: 'mid',
  });

  const [errors, setErrors] = useState({});

  const interviewTypes = [
    { value: 'technical', label: 'Technical', icon: '💻' },
    { value: 'behavioral', label: 'Behavioral', icon: '🗣️' },
    { value: 'case-study', label: 'Case Study', icon: '📊' },
    { value: 'hr', label: 'HR Round', icon: '👔' },
    { value: 'mixed', label: 'Mixed', icon: '🎯' },
  ];

  const experienceLevels = [
    { value: 'entry', label: 'Entry Level (0-2y)' },
    { value: 'mid', label: 'Mid Level (3-5y)' },
    { value: 'senior', label: 'Senior Level (6+y)' },
  ];

  const validateForm = () => {
    const newErrors = {};
    if (!formData.interviewType) newErrors.interviewType = 'Required';
    if (!formData.role.trim()) newErrors.role = 'Required';
    if (!formData.jobDescription.trim() || formData.jobDescription.length < 50) {
      newErrors.jobDescription = 'Min 50 chars required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      const response = await apiService.generateInterviewQuestions(formData);
      sessionStorage.setItem('mockInterviewData', JSON.stringify({
        ...formData,
        questions: response.questions,
        interviewId: response.interview_id,
      }));
      navigate('/mock-interview/start');
    } catch (error) {
      console.error('Error generating questions:', error);
      alert('Failed to generate interview questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: '' }));
  };

  return (
    <div className="min-h-screen bg-white relative overflow-hidden font-sans text-gray-800 selection:bg-purple-100">
      
      {/* Background Decor - Matching the "Think Tech" blurry circles */}
      <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-purple-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
      <div className="absolute top-[20%] left-[-10%] w-[400px] h-[400px] bg-indigo-50 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-[-10%] right-[20%] w-[300px] h-[300px] bg-pink-50 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>

      <div className="max-w-6xl mx-auto px-6 py-12 relative z-10">
        
        {/* Minimal Header */}
        <div className="mb-16">
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-purple-600 text-white text-xs font-bold px-2 py-1 rounded-sm uppercase tracking-wider">New</span>
            <span className="text-purple-600 text-xs font-semibold uppercase tracking-widest">AI Interviewer</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-light tracking-tight text-gray-900 mb-4">
            Configure your <span className="font-medium">practice session</span>
          </h1>
          <p className="text-gray-500 max-w-xl text-sm leading-relaxed">
            Customize your mock interview experience. Our AI will generate tailored questions based on your specific role and job description.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          
          {/* Main Form Area */}
          <div className="lg:col-span-8">
            <form onSubmit={handleSubmit} className="space-y-10">
              
              {/* Section 1: Type & Level */}
              <div className="space-y-6">
                <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">01. Configuration</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {/* Interview Type */}
                  <div className="space-y-3">
                    <label className="text-sm font-medium text-gray-700">Interview Type</label>
                    <div className="grid grid-cols-2 gap-3">
                      {interviewTypes.map((type) => (
                        <button
                          key={type.value}
                          type="button"
                          onClick={() => handleInputChange('interviewType', type.value)}
                          className={`p-3 text-left border transition-all duration-200 rounded-md flex items-center gap-2 group ${
                            formData.interviewType === type.value
                              ? 'border-purple-600 bg-purple-50'
                              : 'border-gray-200 hover:border-purple-300 bg-white'
                          }`}
                        >
                          <span className="text-lg opacity-80">{type.icon}</span>
                          <span className={`text-xs font-medium ${formData.interviewType === type.value ? 'text-purple-700' : 'text-gray-600'}`}>
                            {type.label}
                          </span>
                        </button>
                      ))}
                    </div>
                    {errors.interviewType && <p className="text-xs text-red-500 mt-1">{errors.interviewType}</p>}
                  </div>

                  {/* Experience Level */}
                  <div className="space-y-3">
                    <label className="text-sm font-medium text-gray-700">Experience Level</label>
                    <div className="flex flex-col gap-2">
                      {experienceLevels.map((level) => (
                        <label 
                          key={level.value}
                          className={`flex items-center p-3 border rounded-md cursor-pointer transition-all ${
                            formData.experienceLevel === level.value 
                            ? 'border-purple-600 bg-purple-50' 
                            : 'border-gray-200 hover:border-gray-300 bg-white'
                          }`}
                        >
                          <input
                            type="radio"
                            name="experience"
                            value={level.value}
                            checked={formData.experienceLevel === level.value}
                            onChange={(e) => handleInputChange('experienceLevel', e.target.value)}
                            className="w-4 h-4 text-purple-600 border-gray-300 focus:ring-purple-500"
                          />
                          <span className="ml-3 text-xs font-medium text-gray-700">{level.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Section 2: Details */}
              <div className="space-y-6">
                 <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">02. Role Details</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Target Role</label>
                    <div className="relative">
                      <Briefcase size={16} className="absolute left-3 top-3.5 text-gray-400" />
                      <input
                        type="text"
                        value={formData.role}
                        onChange={(e) => handleInputChange('role', e.target.value)}
                        placeholder="e.g. Senior Frontend Developer"
                        className={`w-full pl-10 pr-4 py-3 bg-gray-50 border rounded-md text-sm focus:bg-white focus:ring-1 focus:ring-purple-500 transition-colors outline-none ${
                          errors.role ? 'border-red-300' : 'border-transparent'
                        }`}
                      />
                    </div>
                    {errors.role && <p className="text-xs text-red-500 mt-1">{errors.role}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Job Description <span className="text-gray-400 font-normal ml-1">(Paste relevant parts)</span>
                    </label>
                    <div className="relative">
                      <FileText size={16} className="absolute left-3 top-3.5 text-gray-400" />
                      <textarea
                        value={formData.jobDescription}
                        onChange={(e) => handleInputChange('jobDescription', e.target.value)}
                        placeholder="Paste the requirements and responsibilities here..."
                        rows={6}
                        className={`w-full pl-10 pr-4 py-3 bg-gray-50 border rounded-md text-sm focus:bg-white focus:ring-1 focus:ring-purple-500 transition-colors outline-none resize-none ${
                          errors.jobDescription ? 'border-red-300' : 'border-transparent'
                        }`}
                      />
                    </div>
                    <div className="flex justify-between items-center mt-1">
                       {errors.jobDescription ? (
                         <p className="text-xs text-red-500">{errors.jobDescription}</p>
                       ) : (
                         <span></span>
                       )}
                       <span className={`text-xs ${formData.jobDescription.length < 50 ? 'text-gray-400' : 'text-purple-600'}`}>
                        {formData.jobDescription.length} chars
                       </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action */}
              <div className="pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-purple-600 text-white text-sm font-medium uppercase tracking-wide py-4 px-8 rounded-sm hover:bg-purple-700 transition-all duration-300 shadow-lg shadow-purple-200 disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      Start Interview
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Info Sidebar - Mimicking the "clean product shot" feel */}
          <div className="lg:col-span-4 mt-8 lg:mt-0">
            <div className="bg-white/60 backdrop-blur-sm border border-white p-6 rounded-2xl shadow-sm sticky top-8">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4 text-purple-600">
                <MessageSquare size={24} />
              </div>
              <h4 className="text-lg font-medium text-gray-900 mb-2">Session Preview</h4>
              <p className="text-sm text-gray-500 mb-6">
                Based on your inputs, we will structure a professional interview environment.
              </p>

              <div className="space-y-4">
                <div className="flex gap-3 items-start">
                   <div className="mt-1"><CheckCircle2 size={16} className="text-purple-500" /></div>
                   <div>
                     <p className="text-sm font-medium text-gray-800">AI Analysis</p>
                     <p className="text-xs text-gray-500">Real-time feedback on your answers.</p>
                   </div>
                </div>
                <div className="flex gap-3 items-start">
                   <div className="mt-1"><CheckCircle2 size={16} className="text-purple-500" /></div>
                   <div>
                     <p className="text-sm font-medium text-gray-800">Role Specific</p>
                     <p className="text-xs text-gray-500">Questions tailored to {formData.role || 'your role'}.</p>
                   </div>
                </div>
                <div className="flex gap-3 items-start">
                   <div className="mt-1"><CheckCircle2 size={16} className="text-purple-500" /></div>
                   <div>
                     <p className="text-sm font-medium text-gray-800">Voice Enabled</p>
                     <p className="text-xs text-gray-500">Text-to-speech for realistic simulation.</p>
                   </div>
                </div>
              </div>

              {/* Decorative price-tag style element from image */}
              <div className="mt-8 pt-6 border-t border-gray-100">
                <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Estimated Duration</p>
                <p className="text-2xl font-light text-gray-900">~20 <span className="text-sm text-gray-500">mins</span></p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default MockInterview;