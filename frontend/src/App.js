import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      fetchUser();
      fetchBots();
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      localStorage.removeItem('token');
      setToken(null);
    }
  };

  const fetchBots = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/bots`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBots(response.data.bots);
    } catch (error) {
      console.error('Error fetching bots:', error);
    }
  };

  const handleAuth = async (authData, isLogin = true) => {
    setLoading(true);
    setError('');
    
    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const response = await axios.post(`${API_URL}${endpoint}`, authData);
      
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(user);
      setCurrentPage('dashboard');
    } catch (error) {
      setError(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setCurrentPage('landing');
  };

  const LandingPage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black text-white">
      {/* Header */}
      <nav className="px-6 py-4 flex justify-between items-center">
        <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          OmniBot
        </div>
        <div className="space-x-4">
          <button
            onClick={() => setCurrentPage('login')}
            className="px-4 py-2 text-blue-400 hover:text-white transition-colors"
          >
            Login
          </button>
          <button
            onClick={() => setCurrentPage('register')}
            className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all"
          >
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          The Future of
          <br />
          Omni-Channel AI
        </h1>
        <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto">
          Connect WhatsApp, Telegram, LINE, and Instagram with powerful AI chatbots. 
          One platform, unlimited possibilities.
        </p>
        
        {/* Hero Image */}
        <div className="mb-12">
          <img 
            src="https://images.unsplash.com/photo-1628939824352-baa1cdddeb6b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwxfHxjaGF0Ym90fGVufDB8fHxibHVlfDE3NTI0NjM3MTR8MA&ixlib=rb-4.1.0&q=85"
            alt="AI Chatbot Technology"
            className="w-full max-w-4xl mx-auto rounded-2xl shadow-2xl"
          />
        </div>

        <div className="flex flex-col md:flex-row gap-4 justify-center">
          <button
            onClick={() => setCurrentPage('register')}
            className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg text-lg font-semibold hover:from-blue-600 hover:to-purple-600 transition-all transform hover:scale-105"
          >
            Start Free Trial
          </button>
          <button
            onClick={() => setCurrentPage('login')}
            className="px-8 py-4 border border-blue-400 rounded-lg text-lg font-semibold hover:bg-blue-400 hover:bg-opacity-20 transition-all"
          >
            Sign In
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Why Choose OmniBot?</h2>
          <p className="text-xl text-gray-300">Everything you need to build intelligent chatbots</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-8 hover:bg-opacity-70 transition-all">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg mb-6 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-4">Multi-Platform Support</h3>
            <p className="text-gray-300">Connect WhatsApp, Telegram, LINE, and Instagram in one unified platform.</p>
          </div>

          {/* Feature 2 */}
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-8 hover:bg-opacity-70 transition-all">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg mb-6 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-4">AI-Powered Responses</h3>
            <p className="text-gray-300">Choose from multiple AI providers: Gemini, OpenAI, Claude, and more.</p>
          </div>

          {/* Feature 3 */}
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-8 hover:bg-opacity-70 transition-all">
            <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-red-500 rounded-lg mb-6 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-4">Easy Setup</h3>
            <p className="text-gray-300">Configure your bots in minutes with our intuitive interface.</p>
          </div>
        </div>
      </div>

      {/* Pricing Section */}
      <div className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
          <p className="text-xl text-gray-300">Choose the plan that fits your needs</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {/* Free Plan */}
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-8 hover:bg-opacity-70 transition-all">
            <h3 className="text-2xl font-bold mb-4">Free</h3>
            <p className="text-4xl font-bold mb-6">$0<span className="text-lg font-normal text-gray-300">/month</span></p>
            <ul className="space-y-3 mb-8">
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                100 messages/month
              </li>
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                1 bot account
              </li>
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                All platforms
              </li>
            </ul>
            <button className="w-full px-6 py-3 border border-blue-400 rounded-lg hover:bg-blue-400 hover:bg-opacity-20 transition-all">
              Get Started
            </button>
          </div>

          {/* Basic Plan */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl p-8 transform scale-105 relative">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-yellow-400 text-black px-4 py-1 rounded-full text-sm font-semibold">
              POPULAR
            </div>
            <h3 className="text-2xl font-bold mb-4 text-white">Basic</h3>
            <p className="text-4xl font-bold mb-6 text-white">$19<span className="text-lg font-normal text-gray-200">/month</span></p>
            <ul className="space-y-3 mb-8 text-white">
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                1,000 messages/month
              </li>
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                5 bot accounts
              </li>
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                Priority support
              </li>
            </ul>
            <button className="w-full px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition-all">
              Choose Basic
            </button>
          </div>

          {/* Premium Plan */}
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-8 hover:bg-opacity-70 transition-all">
            <h3 className="text-2xl font-bold mb-4">Premium</h3>
            <p className="text-4xl font-bold mb-6">$49<span className="text-lg font-normal text-gray-300">/month</span></p>
            <ul className="space-y-3 mb-8">
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                5,000 messages/month
              </li>
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                Unlimited bots
              </li>
              <li className="flex items-center">
                <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                </svg>
                Advanced analytics
              </li>
            </ul>
            <button className="w-full px-6 py-3 border border-purple-400 rounded-lg hover:bg-purple-400 hover:bg-opacity-20 transition-all">
              Choose Premium
            </button>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-6 py-20 text-center">
        <h2 className="text-4xl font-bold mb-4">Ready to Get Started?</h2>
        <p className="text-xl text-gray-300 mb-8">Join thousands of businesses using OmniBot to enhance their customer engagement</p>
        <button
          onClick={() => setCurrentPage('register')}
          className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg text-lg font-semibold hover:from-blue-600 hover:to-purple-600 transition-all transform hover:scale-105"
        >
          Start Your Free Trial
        </button>
      </div>
    </div>
  );

  const AuthPage = ({ isLogin = true }) => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-gray-800 bg-opacity-50 rounded-xl p-8 backdrop-blur-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h1>
          <p className="text-gray-300">
            {isLogin ? 'Sign in to your OmniBot account' : 'Join the future of AI chatbots'}
          </p>
        </div>

        <form onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.target);
          const authData = {
            email: formData.get('email'),
            password: formData.get('password'),
            ...(isLogin ? {} : { full_name: formData.get('fullName') })
          };
          handleAuth(authData, isLogin);
        }}>
          {!isLogin && (
            <div className="mb-4">
              <label className="block text-gray-300 mb-2">Full Name</label>
              <input
                type="text"
                name="fullName"
                required
                className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your full name"
              />
            </div>
          )}

          <div className="mb-4">
            <label className="block text-gray-300 mb-2">Email</label>
            <input
              type="email"
              name="email"
              required
              className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your email"
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-300 mb-2">Password</label>
            <input
              type="password"
              name="password"
              required
              className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-500 bg-opacity-20 border border-red-500 rounded-lg text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg text-white font-semibold hover:from-blue-600 hover:to-purple-600 transition-all disabled:opacity-50"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-300">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
            <button
              onClick={() => setCurrentPage(isLogin ? 'register' : 'login')}
              className="text-blue-400 hover:text-blue-300 transition-colors"
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => setCurrentPage('landing')}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );

  const Dashboard = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black text-white">
      {/* Header */}
      <nav className="px-6 py-4 bg-gray-800 bg-opacity-50 backdrop-blur-sm">
        <div className="flex justify-between items-center">
          <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            OmniBot Dashboard
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-300">Welcome, {user?.full_name}</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-2">Chat Usage</h3>
            <p className="text-3xl font-bold text-blue-400">
              {user?.chat_count || 0}/{user?.chat_limit || 100}
            </p>
            <p className="text-gray-300">Messages this month</p>
          </div>

          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-2">Active Bots</h3>
            <p className="text-3xl font-bold text-purple-400">{bots.length}</p>
            <p className="text-gray-300">Connected platforms</p>
          </div>

          <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-2">Current Plan</h3>
            <p className="text-3xl font-bold text-green-400">{user?.plan || 'Free'}</p>
            <p className="text-gray-300">Subscription status</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <button
            onClick={() => setCurrentPage('create-bot')}
            className="p-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl hover:from-blue-600 hover:to-purple-600 transition-all"
          >
            <div className="text-2xl mb-2">🤖</div>
            <h3 className="font-semibold">Create Bot</h3>
          </button>

          <button
            onClick={() => setCurrentPage('chat-interface')}
            className="p-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all"
          >
            <div className="text-2xl mb-2">💬</div>
            <h3 className="font-semibold">Chat Interface</h3>
          </button>

          <button
            onClick={() => setCurrentPage('settings')}
            className="p-6 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl hover:from-green-600 hover:to-teal-600 transition-all"
          >
            <div className="text-2xl mb-2">⚙️</div>
            <h3 className="font-semibold">Settings</h3>
          </button>

          <button
            onClick={() => setCurrentPage('analytics')}
            className="p-6 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl hover:from-yellow-600 hover:to-orange-600 transition-all"
          >
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-semibold">Analytics</h3>
          </button>
        </div>

        {/* Bots List */}
        <div className="bg-gray-800 bg-opacity-50 rounded-xl p-6">
          <h2 className="text-2xl font-bold mb-6">Your Bots</h2>
          {bots.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold mb-2">No bots yet</h3>
              <p className="text-gray-300 mb-6">Create your first bot to get started</p>
              <button
                onClick={() => setCurrentPage('create-bot')}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all"
              >
                Create Your First Bot
              </button>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {bots.map(bot => (
                <div key={bot.bot_id} className="bg-gray-700 bg-opacity-50 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">{bot.bot_name}</h3>
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">
                        {bot.platform === 'whatsapp' && '📱'}
                        {bot.platform === 'telegram' && '✈️'}
                        {bot.platform === 'line' && '💬'}
                        {bot.platform === 'instagram' && '📸'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs ${bot.is_active ? 'bg-green-500' : 'bg-red-500'}`}>
                        {bot.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-300 mb-4">Platform: {bot.platform}</p>
                  <p className="text-gray-300 mb-4">AI: {bot.ai_provider}</p>
                  <div className="flex space-x-2">
                    <button className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
                      Chat
                    </button>
                    <button className="px-4 py-2 bg-gray-600 rounded-lg hover:bg-gray-700 transition-colors">
                      Settings
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const CreateBotPage = () => {
    const [formData, setFormData] = useState({
      bot_name: '',
      platform: 'whatsapp',
      api_key: '',
      ai_provider: 'gemini',
      ai_model: 'gemini-2.0-flash',
      system_message: 'You are a helpful assistant.',
      auto_reply: true
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      setLoading(true);
      
      try {
        await axios.post(`${API_URL}/api/bots`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        alert('Bot created successfully!');
        setCurrentPage('dashboard');
        fetchBots();
      } catch (error) {
        alert(error.response?.data?.detail || 'Failed to create bot');
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black text-white">
        <nav className="px-6 py-4 bg-gray-800 bg-opacity-50 backdrop-blur-sm">
          <div className="flex justify-between items-center">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className="text-blue-400 hover:text-white transition-colors"
            >
              ← Back to Dashboard
            </button>
            <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Create New Bot
            </div>
            <div></div>
          </div>
        </nav>

        <div className="container mx-auto px-6 py-8">
          <div className="max-w-2xl mx-auto bg-gray-800 bg-opacity-50 rounded-xl p-8">
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label className="block text-gray-300 mb-2">Bot Name</label>
                <input
                  type="text"
                  value={formData.bot_name}
                  onChange={(e) => setFormData({...formData, bot_name: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter bot name"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-300 mb-2">Platform</label>
                <select
                  value={formData.platform}
                  onChange={(e) => setFormData({...formData, platform: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="whatsapp">WhatsApp</option>
                  <option value="telegram">Telegram</option>
                  <option value="line">LINE</option>
                  <option value="instagram">Instagram</option>
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-gray-300 mb-2">API Key</label>
                <input
                  type="password"
                  value={formData.api_key}
                  onChange={(e) => setFormData({...formData, api_key: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter platform API key"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-300 mb-2">AI Provider</label>
                <select
                  value={formData.ai_provider}
                  onChange={(e) => setFormData({...formData, ai_provider: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="gemini">Gemini</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Claude</option>
                  <option value="deepseek">DeepSeek</option>
                  <option value="qwen">Qwen</option>
                  <option value="kimi">Kimi</option>
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-gray-300 mb-2">AI Model</label>
                <input
                  type="text"
                  value={formData.ai_model}
                  onChange={(e) => setFormData({...formData, ai_model: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter AI model name"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-300 mb-2">System Message</label>
                <textarea
                  value={formData.system_message}
                  onChange={(e) => setFormData({...formData, system_message: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 h-32"
                  placeholder="Enter system message for your bot"
                  required
                />
              </div>

              <div className="mb-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.auto_reply}
                    onChange={(e) => setFormData({...formData, auto_reply: e.target.checked})}
                    className="mr-2"
                  />
                  <span className="text-gray-300">Enable auto-reply</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg text-white font-semibold hover:from-blue-600 hover:to-purple-600 transition-all disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Bot'}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // Router
  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage />;
      case 'login':
        return <AuthPage isLogin={true} />;
      case 'register':
        return <AuthPage isLogin={false} />;
      case 'dashboard':
        return <Dashboard />;
      case 'create-bot':
        return <CreateBotPage />;
      default:
        return <LandingPage />;
    }
  };

  return (
    <div className="App">
      {renderCurrentPage()}
    </div>
  );
}

export default App;