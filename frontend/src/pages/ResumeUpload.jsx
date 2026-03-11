import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import Error from '../components/Error'; // Assuming you have this component
import { UploadCloud, FileText, CheckCircle, X, Loader2 } from 'lucide-react';

/**
 * Resume Upload Page
 * Handles file upload with AI-powered analysis
 */
const ResumeUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [targetRole, setTargetRole] = useState('');
  const [analysisProgress, setAnalysisProgress] = useState('');
  const navigate = useNavigate();

  // Allowed file types
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  const maxSize = 5 * 1024 * 1024; // 5MB

  const validateFile = (file) => {
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Please upload a PDF or DOCX file');
    }
    if (file.size > maxSize) {
      throw new Error('File size must be less than 5MB');
    }
    return true;
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      try {
        validateFile(selectedFile);
        setFile(selectedFile);
        setError(null);
      } catch (err) {
        setError(err.message);
        setFile(null);
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      try {
        validateFile(droppedFile);
        setFile(droppedFile);
        setError(null);
      } catch (err) {
        setError(err.message);
        setFile(null);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      // 1. Upload & Extraction Phase
      setAnalysisProgress('📄 Uploading and extracting resume data...');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 2. Analysis Phase
      setAnalysisProgress('🤖 Analyzing skills and experience with AI...');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 3. Job Fetching Phase
      setAnalysisProgress('🌐 Fetching real jobs from 12+ APIs (Remotive, Jobicy, IndianAPI, RemoteOK, DevITjobs...)');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 4. Job Scoring Phase
      setAnalysisProgress('📊 Scoring jobs with ATS algorithm (this may take 1-2 minutes)...');
      
      // API Call - this will take time but we wait for it!
      console.log('🚀 Starting backend analysis...');
      const startTime = Date.now();
      // Don't hardcode target role - let backend auto-detect from resume
      const response = await apiService.smartAnalysis(formData, targetRole || null);
      const duration = Math.round((Date.now() - startTime) / 1000);
      
      console.log(`✅ Backend completed in ${duration} seconds`);
      console.log('📊 Response:', response);
      console.log('📊 Jobs found:', response?.job_recommendations?.length || 0);
      console.log('🎯 Detected role:', response?.target_role || 'Unknown');
      
      // 5. Finalizing Phase
      setAnalysisProgress('✨ Preparing your career dashboard...');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Validate response
      if (!response || !response.resume) {
        throw new Error('Invalid response from server - missing resume data');
      }
      
      if (!response.job_recommendations || response.job_recommendations.length === 0) {
        console.warn('⚠️ No jobs in response');
      }
      
      // Store resume data
      localStorage.setItem('resumeData', JSON.stringify(response.resume || {}));
      
      // Store enhanced job recommendations - ALL OF THEM!
      const enhancedJobs = (response.job_recommendations || []).map(job => ({
        ...job,
        job_title: job.title || job.job_title,
        title: job.title || job.job_title,
        company_name: job.company || job.company_name,
        location: job.location || 'Remote',
        employment_type: job.job_type || job.employment_type || 'Full-time',
        skills_matched: job.matched_skills || job.skills_matched || [],
        required_skills: job.required_skills || [],
        match_score: job.match_score || job.compatibility_score || 0,
        ats_score: job.ats_score || job.match_score || 0,
        remote_option: job.remote_option || 'Remote',
        url: job.url || '',
        source: job.source || 'Web',
      }));
      
      console.log(`✅ Storing ${enhancedJobs.length} jobs to localStorage`);
      
      localStorage.setItem('jobRecommendations', JSON.stringify(enhancedJobs));
      localStorage.setItem('resumeInsights', JSON.stringify(response.insights || {}));
      localStorage.setItem('analysisComplete', 'true');
      localStorage.setItem('targetRole', targetRole || 'Software Engineer');
      localStorage.setItem('analysisTimestamp', new Date().toISOString());
      
      setAnalysisProgress(`✅ Complete! Found ${enhancedJobs.length} jobs. Redirecting to dashboard...`);
      
      // Save to backend history
      try {
        await apiService.saveResumeAnalysis(
          response.resume || {},
          {
            job_recommendations: response.job_recommendations || [],
            insights: response.insights || {},
            target_role: targetRole || 'Software Engineer',
            timestamp: new Date().toISOString()
          },
          file.name
        );
        console.log('✅ Saved to backend history');
      } catch (historyErr) {
        console.warn('⚠️ Failed to save history:', historyErr);
        // Continue anyway
      }
      
      // Navigate to dashboard
      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);

    } catch (err) {
      console.error('❌ Upload error:', err);
      console.error('❌ Error response:', err.response?.data);
      console.error('❌ Error status:', err.response?.status);
      console.error('❌ Error message:', err.message);
      
      setAnalysisProgress('');
      let errorMessage = 'Failed to analyze resume. Please try again.';
      
      // Better error handling - be specific
      if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
        errorMessage = '⏱️ Request timed out. The analysis is still running on the server. Please wait 30 seconds and check your Dashboard.';
        // Auto-redirect after showing error
        setTimeout(() => {
          console.log('Redirecting to dashboard after timeout...');
          navigate('/dashboard');
        }, 5000);
      } else if (err.response?.status === 504 || err.response?.status === 502) {
        errorMessage = '⏱️ Server is still processing your resume. Check the Dashboard in a moment for results.';
      } else if (err.response?.status === 413) {
        errorMessage = '📄 File is too large. Please upload a smaller resume (max 5MB).';
      } else if (err.response?.status === 422) {
        errorMessage = '📄 Invalid file format. Please upload a PDF or DOCX file.';
      } else if (err.response?.data?.detail) {
         const detail = err.response.data.detail;
         errorMessage = typeof detail === 'string' ? detail : JSON.stringify(detail);
      } else if (err.message && err.message !== 'Network Error') {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50/50 py-16 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-2xl mx-auto">
        
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 sm:p-10">
          
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Upload Resume</h1>
            <p className="text-gray-500 text-sm">Upload your CV to get AI-powered career insights.</p>
          </div>

          <div className="space-y-6">
            
            {/* Drag & Drop Zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-xl p-10 text-center transition-all duration-200 ease-in-out ${
                dragActive
                  ? 'border-blue-500 bg-blue-50/50 scale-[1.02]'
                  : 'border-gray-200 hover:border-blue-400 hover:bg-gray-50/30'
              }`}
            >
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                disabled={uploading}
              />
              
              <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
                <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4 transition-transform group-hover:scale-110">
                  <UploadCloud size={32} />
                </div>
                <p className="text-gray-900 font-medium mb-1">
                  {file ? 'Change file' : 'Click to upload or drag and drop'}
                </p>
                <p className="text-xs text-gray-400 uppercase tracking-wide">
                  PDF or DOCX (Max 5MB)
                </p>
              </label>
            </div>

            {/* Selected File State */}
            {file && (
              <div className="bg-gray-50 rounded-xl p-4 flex items-center justify-between border border-gray-100 animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200 shadow-sm text-blue-600">
                    <FileText size={20} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900 truncate max-w-[200px]">{file.name}</p>
                    <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
                
                {!uploading && (
                  <button
                    onClick={() => setFile(null)}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <X size={18} />
                  </button>
                )}
              </div>
            )}

            {/* Optional Target Role */}
            <div>
              <label htmlFor="target-role" className="block text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                Target Role (Optional)
              </label>
              <input
                id="target-role"
                type="text"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                placeholder="e.g. Full Stack Developer"
                disabled={uploading}
                className="w-full px-4 py-3 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all placeholder-gray-400"
              />
            </div>

            {/* Progress Bar */}
            {analysisProgress && (
              <div className="bg-blue-50/80 border border-blue-100 rounded-lg p-4 flex items-center gap-3">
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                <span className="text-sm font-medium text-blue-700">{analysisProgress}</span>
              </div>
            )}

            {/* Error Message */}
            {error && (
               <div className="bg-red-50 border border-red-100 rounded-lg p-4 text-sm text-red-600 flex items-center gap-2">
                 <div className="w-1.5 h-1.5 bg-red-500 rounded-full" />
                 {typeof error === 'string' ? error : String(error)}
               </div>
            )}

            {/* Submit Button */}
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className={`w-full py-3.5 px-6 rounded-lg font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2 ${
                !file || uploading
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-900 text-white hover:bg-black hover:shadow-lg transform active:scale-[0.99]'
              }`}
            >
              {uploading ? 'Processing...' : 'Analyze Resume'}
              {!uploading && <CheckCircle size={16} />}
            </button>
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeUpload;