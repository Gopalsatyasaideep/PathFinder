import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from '../api';
import { Mail, Lock, User, AlertCircle, Sparkles, Chrome, ArrowRight } from 'lucide-react';

const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ name: '', email: '', password: '', confirmPassword: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const validateForm = () => {
    if (!formData.name.trim()) { setError('Name is required'); return false; }
    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) { setError('Invalid email'); return false; }
    if (formData.password.length < 8) { setError('Password too short (min 8)'); return false; }
    if (formData.password !== formData.confirmPassword) { setError('Passwords do not match'); return false; }
    return true;
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);

    try {
      // send actual request to backend
      const response = await API.post('/auth/signup', {
        name: formData.name,
        email: formData.email,
        password: formData.password,
      });
      // you might want to store token in localStorage
      localStorage.setItem('access_token', response.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  // Reusable Background Component
  const BackgroundBlobs = () => (
    <>
      <div className="absolute top-[10%] left-[10%] w-[400px] h-[400px] bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob"></div>
      <div className="absolute top-[10%] right-[10%] w-[400px] h-[400px] bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-[10%] left-[20%] w-[400px] h-[400px] bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-4000"></div>
    </>
  );

  return (
    <div className="flex h-screen w-full bg-white overflow-hidden font-sans text-gray-800 selection:bg-purple-100">
      
      {/* LEFT SIDE - Brand Visuals */}
      <div className="hidden lg:flex w-1/2 relative items-center justify-center bg-gray-50 overflow-hidden">
        <BackgroundBlobs />
        
        <div className="relative z-10 p-12 text-center max-w-lg">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-2xl shadow-xl shadow-purple-100 mb-6 animate-fade-in-up">
             <Sparkles size={32} className="text-purple-600 fill-purple-100" />
          </div>
          
          <h2 className="text-3xl font-light text-gray-900 mb-3 tracking-tight animate-fade-in-up delay-100">
            Join <span className="font-bold">PathFinder</span>
          </h2>
          
          <p className="text-gray-500 text-base leading-relaxed animate-fade-in-up delay-200">
            Create an account to unlock personalized career insights, AI mock interviews, and tailored job recommendations.
          </p>
        </div>
      </div>

      {/* RIGHT SIDE - Compact Form */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center items-center bg-white px-6 relative z-10">
        
        <div className="w-full max-w-[340px]"> {/* Reduced max-width for tighter look */}
          
          {/* Header */}
          <div className="mb-6 text-center lg:text-left">
            <h1 className="text-2xl font-semibold text-gray-900 mb-1">Create Account</h1>
            <p className="text-gray-500 text-xs">Sign up to get started.</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-4 p-2.5 bg-red-50 border border-red-100 rounded-lg text-red-600 flex items-center gap-2 text-xs animate-shake">
              <AlertCircle size={14} className="shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-3"> {/* Reduced spacing */}
            
            {/* Name Input */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Full Name</label>
              <div className="relative group">
                <div className="absolute left-3 top-2.5 text-gray-400 group-focus-within:text-purple-600 transition-colors">
                  <User size={16} />
                </div>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="John Doe"
                  className="w-full pl-9 pr-3 py-2.5 bg-gray-50 border border-transparent rounded-lg text-gray-900 placeholder-gray-400 text-sm focus:bg-white focus:border-purple-200 focus:ring-2 focus:ring-purple-50 outline-none transition-all"
                  required
                />
              </div>
            </div>

            {/* Email Input */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Email</label>
              <div className="relative group">
                <div className="absolute left-3 top-2.5 text-gray-400 group-focus-within:text-purple-600 transition-colors">
                  <Mail size={16} />
                </div>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="name@company.com"
                  className="w-full pl-9 pr-3 py-2.5 bg-gray-50 border border-transparent rounded-lg text-gray-900 placeholder-gray-400 text-sm focus:bg-white focus:border-purple-200 focus:ring-2 focus:ring-purple-50 outline-none transition-all"
                  required
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Password</label>
              <div className="relative group">
                <div className="absolute left-3 top-2.5 text-gray-400 group-focus-within:text-purple-600 transition-colors">
                  <Lock size={16} />
                </div>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Min. 8 chars"
                  className="w-full pl-9 pr-3 py-2.5 bg-gray-50 border border-transparent rounded-lg text-gray-900 placeholder-gray-400 text-sm focus:bg-white focus:border-purple-200 focus:ring-2 focus:ring-purple-50 outline-none transition-all"
                  required
                />
              </div>
            </div>

            {/* Confirm Password Input */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Confirm Password</label>
              <div className="relative group">
                <div className="absolute left-3 top-2.5 text-gray-400 group-focus-within:text-purple-600 transition-colors">
                  <Lock size={16} />
                </div>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Re-enter password"
                  className="w-full pl-9 pr-3 py-2.5 bg-gray-50 border border-transparent rounded-lg text-gray-900 placeholder-gray-400 text-sm focus:bg-white focus:border-purple-200 focus:ring-2 focus:ring-purple-50 outline-none transition-all"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gray-900 text-white py-3 rounded-lg hover:bg-black hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 font-medium text-sm flex items-center justify-center gap-2 group mt-4"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Sign Up <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative flex py-4 items-center">
            <div className="flex-grow border-t border-gray-100"></div>
            <span className="flex-shrink-0 mx-3 text-gray-400 text-[10px] uppercase font-bold tracking-widest">Or</span>
            <div className="flex-grow border-t border-gray-100"></div>
          </div>

          {/* Google Button */}
          <button className="w-full border border-gray-200 bg-white text-gray-600 py-2.5 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 flex items-center justify-center gap-2 font-medium text-xs">
             <Chrome size={16} />
             Sign up with Google
          </button>

          {/* Footer */}
          <div className="text-center mt-6">
            <p className="text-gray-500 text-xs">
              Already have an account?{' '}
              <Link to="/login" className="text-purple-600 font-semibold hover:text-purple-800 transition-colors">
                Log in
              </Link>
            </p>
          </div>

        </div>
        
        {/* Footer Copyright */}
        <div className="absolute bottom-4 text-gray-300 text-[10px]">
          © 2026 PathFinder AI
        </div>
      </div>
    </div>
  );
};

export default Signup;