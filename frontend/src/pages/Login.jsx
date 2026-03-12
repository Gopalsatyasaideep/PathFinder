import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiService } from '../services/api';
import { Mail, Lock, AlertCircle, Sparkles, Chrome, ArrowRight } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await apiService.login(formData.email, formData.password);
      localStorage.setItem('isAuthenticated', 'true');
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Background Blobs Component (Reused for consistency)
  const BackgroundBlobs = () => (
    <>
      <div className="absolute top-[20%] left-[20%] w-[400px] h-[400px] bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob"></div>
      <div className="absolute top-[20%] right-[20%] w-[400px] h-[400px] bg-indigo-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>
      <div className="absolute bottom-[20%] left-[30%] w-[400px] h-[400px] bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-4000"></div>
    </>
  );

  return (
    <div className="flex h-screen w-full bg-white overflow-hidden font-sans text-gray-800 selection:bg-purple-100">
      
      {/* LEFT SIDE - Visual / Brand */}
      <div className="hidden lg:flex w-1/2 relative items-center justify-center bg-gray-50 overflow-hidden">
        <BackgroundBlobs />
        
        <div className="relative z-10 p-12 text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-3xl shadow-xl shadow-purple-100 mb-8 animate-fade-in-up">
             <Sparkles size={40} className="text-purple-600 fill-purple-100" />
          </div>
          
          <h2 className="text-4xl font-light text-gray-900 mb-4 tracking-tight animate-fade-in-up delay-100">
            PathFinder <span className="font-bold">AI</span>
          </h2>
          
          <p className="text-gray-500 text-lg leading-relaxed max-w-md mx-auto animate-fade-in-up delay-200">
            Intelligent career guidance tailored to your unique skills and ambitions.
          </p>

          {/* Decorative Card Stack */}
          <div className="mt-12 relative h-32 w-64 mx-auto animate-fade-in-up delay-300">
             <div className="absolute top-0 left-0 w-full h-20 bg-white rounded-2xl shadow-lg border border-gray-100 transform -rotate-6 z-10 flex items-center px-4 gap-3 opacity-90">
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600"><Sparkles size={16}/></div>
                <div className="h-2 w-24 bg-gray-100 rounded-full"></div>
             </div>
             <div className="absolute top-4 left-4 w-full h-20 bg-white rounded-2xl shadow-lg border border-gray-100 transform rotate-3 z-20 flex items-center px-4 gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center text-purple-600"><Sparkles size={16}/></div>
                <div className="h-2 w-32 bg-gray-100 rounded-full"></div>
             </div>
          </div>
        </div>
      </div>

      {/* RIGHT SIDE - Login Form */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center items-center bg-white px-8 md:px-16 relative z-10">
        
        <div className="w-full max-w-[380px]">
          
          {/* Header */}
          <div className="mb-10">
            <h1 className="text-3xl font-light text-gray-900 mb-2">Welcome <span className="font-medium">back</span></h1>
            <p className="text-gray-500 text-sm">Please enter your details to sign in.</p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 flex items-center gap-3 text-sm animate-shake">
              <AlertCircle size={18} className="shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            
            {/* Email Input */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Email</label>
              <div className="relative group">
                <div className="absolute left-4 top-3.5 text-gray-400 group-focus-within:text-purple-600 transition-colors">
                  <Mail size={20} />
                </div>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="name@company.com"
                  className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-transparent rounded-xl text-gray-900 placeholder-gray-400 text-sm focus:bg-white focus:border-purple-200 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
                  required
                />
              </div>
            </div>

            {/* Password Input */}
            <div className="space-y-2">
              <div className="flex justify-between items-center ml-1">
                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Password</label>
                <Link to="/forgot-password" className="text-xs text-purple-600 hover:text-purple-800 font-medium transition-colors">
                  Forgot Password?
                </Link>
              </div>
              <div className="relative group">
                <div className="absolute left-4 top-3.5 text-gray-400 group-focus-within:text-purple-600 transition-colors">
                  <Lock size={20} />
                </div>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-transparent rounded-xl text-gray-900 placeholder-gray-400 text-sm focus:bg-white focus:border-purple-200 focus:ring-4 focus:ring-purple-50 outline-none transition-all"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gray-900 text-white py-3.5 rounded-xl hover:bg-black hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 font-medium text-sm flex items-center justify-center gap-2 group mt-4"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Sign In <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative flex py-6 items-center">
            <div className="flex-grow border-t border-gray-100"></div>
            <span className="flex-shrink-0 mx-4 text-gray-400 text-[10px] uppercase font-bold tracking-widest">Or continue with</span>
            <div className="flex-grow border-t border-gray-100"></div>
          </div>

          {/* Google Button */}
          <button className="w-full border border-gray-200 bg-white text-gray-600 py-3 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 flex items-center justify-center gap-3 font-medium text-sm">
             <Chrome size={18} />
             Google
          </button>

          {/* Footer */}
          <div className="text-center mt-8">
            <p className="text-gray-500 text-sm">
              Don't have an account?{' '}
              <Link to="/signup" className="text-purple-600 font-semibold hover:text-purple-800 transition-colors">
                Sign up
              </Link>
            </p>
          </div>

        </div>
        
        {/* Footer Copyright */}
        <div className="absolute bottom-6 text-gray-300 text-xs">
          © 2026 PathFinder AI
        </div>
      </div>
    </div>
  );
};

export default Login;