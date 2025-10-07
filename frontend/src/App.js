import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Components imports
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Alert, AlertDescription } from './components/ui/alert';
import { Progress } from './components/ui/progress';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserInfo();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { access_token, user: newUser } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(newUser);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Landing Page Component
const LandingPage = () => {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [showAuth, setShowAuth] = useState(false);

  const handleLeadMagnetSignup = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await axios.post(`${API}/lead-magnet/signup`, {
        email,
        first_name: firstName,
        lead_magnet_type: 'ai_prompts_guide',
        source: 'website'
      });
      
      setShowSuccess(true);
      setEmail('');
      setFirstName('');
    } catch (error) {
      console.error('Lead magnet signup failed:', error);
      alert('Signup failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const initiatePayment = async () => {
    try {
      const response = await axios.post(`${API}/payments/create-checkout`);
      window.location.href = response.data.checkout_url;
    } catch (error) {
      console.error('Payment initiation failed:', error);
      alert('Payment setup failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50">
      {/* Header */}
      <header className="border-b border-orange-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-amber-500 rounded-lg"></div>
            <span className="text-xl font-bold text-gray-900">BizPromptAI</span>
          </div>
          <Button 
            data-testid="get-started-btn"
            onClick={() => setShowAuth(true)} 
            className="bg-orange-500 hover:bg-orange-600 text-white"
          >
            Get Started
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Save 2+ Hours Daily with 
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-amber-600"> AI Automation</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            47 battle-tested AI prompts that automate your most time-consuming business tasks. 
            Used by 1000+ professionals to reclaim their productivity.
          </p>
          
          {!showSuccess ? (
            <Card className="max-w-md mx-auto bg-white/90 backdrop-blur border-orange-200 shadow-xl">
              <CardHeader>
                <CardTitle className="text-orange-600">Get 5 FREE AI Prompts</CardTitle>
                <CardDescription>
                  Start saving time today with our most popular prompts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleLeadMagnetSignup} className="space-y-4">
                  <Input
                    data-testid="lead-email-input"
                    type="email"
                    placeholder="Your email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="border-orange-200 focus:border-orange-400"
                  />
                  <Input
                    data-testid="lead-name-input"
                    type="text"
                    placeholder="First name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="border-orange-200 focus:border-orange-400"
                  />
                  <Button 
                    data-testid="lead-submit-btn"
                    type="submit" 
                    className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? 'Sending...' : 'Get Free Prompts'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          ) : (
            <Alert className="max-w-md mx-auto bg-green-50 border-green-200">
              <AlertDescription className="text-green-800">
                ✅ Success! Check your email for the free AI prompts guide.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            What's Included in the Complete Toolkit
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <Card className="border-orange-200 hover:shadow-lg transition-all">
              <CardHeader>
                <CardTitle className="text-orange-600 flex items-center">
                  📧 Email Automation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Cold outreach, follow-ups, and professional communication templates that get responses.</p>
                <Badge className="mt-2 bg-orange-100 text-orange-700">Saves 25+ min per email</Badge>
              </CardContent>
            </Card>
            
            <Card className="border-orange-200 hover:shadow-lg transition-all">
              <CardHeader>
                <CardTitle className="text-orange-600 flex items-center">
                  🔍 Research & Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">Competitor analysis, market research, and strategic insights in minutes instead of hours.</p>
                <Badge className="mt-2 bg-orange-100 text-orange-700">Saves 2+ hours per report</Badge>
              </CardContent>
            </Card>
            
            <Card className="border-orange-200 hover:shadow-lg transition-all">
              <CardHeader>
                <CardTitle className="text-orange-600 flex items-center">
                  📝 Content Creation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">LinkedIn posts, meeting agendas, and project reports that impress stakeholders.</p>
                <Badge className="mt-2 bg-orange-100 text-orange-700">Saves 30+ min per piece</Badge>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="bg-gradient-to-br from-orange-100 to-amber-100 py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-12 text-gray-900">
            Limited Time: Early Access Offer
          </h2>
          <Card className="max-w-md mx-auto bg-white shadow-xl border-2 border-orange-300">
            <CardHeader className="bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-t-lg">
              <CardTitle className="text-2xl">AI Automation Toolkit</CardTitle>
              <CardDescription className="text-orange-100">
                Complete 47-prompt library + bonuses
              </CardDescription>
            </CardHeader>
            <CardContent className="p-8">
              <div className="text-center mb-6">
                <span className="text-4xl font-bold text-orange-600">$37</span>
                <span className="text-lg text-gray-500 line-through ml-2">$47</span>
                <p className="text-sm text-gray-600 mt-1">First 25 customers only</p>
              </div>
              
              <div className="space-y-3 text-left mb-6">
                <div className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  <span className="text-gray-700">47 Professional AI Prompts</span>
                </div>
                <div className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  <span className="text-gray-700">5 Bonus Prompts (Immediate Access)</span>
                </div>
                <div className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  <span className="text-gray-700">Private Feedback Group</span>
                </div>
                <div className="flex items-center">
                  <span className="text-green-500 mr-2">✓</span>
                  <span className="text-gray-700">Lifetime Updates</span>
                </div>
              </div>
              
              <Button 
                data-testid="purchase-btn"
                onClick={initiatePayment}
                className="w-full bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white text-lg py-3"
              >
                Get Early Access Now
              </Button>
              
              <p className="text-xs text-gray-500 mt-4 text-center">
                30-day money-back guarantee
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Auth Modal */}
      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </div>
  );
};

// Auth Modal Component
const AuthModal = ({ onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    const result = isLogin 
      ? await login(formData.email, formData.password)
      : await register(formData);

    if (result.success) {
      onClose();
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    setIsSubmitting(false);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4 bg-white">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>{isLogin ? 'Sign In' : 'Create Account'}</CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>×</Button>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <>
                <Input
                  placeholder="First Name"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                />
                <Input
                  placeholder="Last Name"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                />
              </>
            )}
            <Input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              required
            />
            
            {error && (
              <Alert className="bg-red-50 border-red-200">
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}
            
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
            </Button>
          </form>
          
          <div className="mt-4 text-center">
            <Button variant="ghost" onClick={() => setIsLogin(!isLogin)}>
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { user, logout } = useAuth();
  const [prompts, setPrompts] = useState([]);
  const [surveys, setSurveys] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [promptsRes, surveysRes] = await Promise.all([
        axios.get(`${API}/prompts`),
        axios.get(`${API}/surveys`)
      ]);
      
      setPrompts(promptsRes.data);
      setSurveys(surveysRes.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-amber-500 rounded-lg"></div>
              <span className="text-xl font-bold text-gray-900">BizPromptAI</span>
            </Link>
            <Badge className={`${user?.role === 'admin' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
              {user?.role === 'admin' ? 'Admin' : user?.subscription_status || 'Free'}
            </Badge>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">Welcome, {user?.first_name || user?.email}</span>
            <Button variant="ghost" onClick={handleLogout}>Logout</Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <Tabs defaultValue={user?.role === 'admin' ? 'admin' : 'library'} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="library">Prompt Library</TabsTrigger>
            <TabsTrigger value="surveys">Surveys</TabsTrigger>
            {user?.role === 'admin' && <TabsTrigger value="admin">Admin Panel</TabsTrigger>}
            <TabsTrigger value="profile">Profile</TabsTrigger>
          </TabsList>
          
          <TabsContent value="library" className="mt-8">
            <PromptLibrary prompts={prompts} userSubscription={user?.subscription_status} />
          </TabsContent>
          
          <TabsContent value="surveys" className="mt-8">
            <SurveySection surveys={surveys} />
          </TabsContent>
          
          {user?.role === 'admin' && (
            <TabsContent value="admin" className="mt-8">
              <AdminPanel />
            </TabsContent>
          )}
          
          <TabsContent value="profile" className="mt-8">
            <ProfileSection user={user} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// Prompt Library Component
const PromptLibrary = ({ prompts, userSubscription }) => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPrompt, setSelectedPrompt] = useState(null);

  const categories = ['all', ...new Set(prompts.map(p => p.category))];
  const filteredPrompts = selectedCategory === 'all' 
    ? prompts 
    : prompts.filter(p => p.category === selectedCategory);

  const canAccessPrompt = (prompt) => {
    if (!prompt.is_premium) return true;
    return userSubscription === 'paid' || userSubscription === 'trial';
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">AI Prompt Library</h2>
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Select category" />
          </SelectTrigger>
          <SelectContent>
            {categories.map(cat => (
              <SelectItem key={cat} value={cat}>
                {cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPrompts.map(prompt => (
          <Card 
            key={prompt.id} 
            className={`cursor-pointer transition-all hover:shadow-lg ${
              !canAccessPrompt(prompt) ? 'opacity-60' : ''
            }`}
            onClick={() => canAccessPrompt(prompt) && setSelectedPrompt(prompt)}
          >
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{prompt.title}</CardTitle>
                {prompt.is_premium && (
                  <Badge className="bg-amber-100 text-amber-700">Premium</Badge>
                )}
              </div>
              <CardDescription>{prompt.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between items-center text-sm text-gray-600">
                <span className="capitalize">{prompt.category}</span>
                <span>Saves {prompt.time_saved_minutes} min</span>
              </div>
              {!canAccessPrompt(prompt) && (
                <div className="mt-2 p-2 bg-amber-50 rounded text-sm text-amber-700">
                  🔒 Premium subscription required
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Prompt Detail Modal */}
      {selectedPrompt && (
        <Dialog open={!!selectedPrompt} onOpenChange={() => setSelectedPrompt(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{selectedPrompt.title}</DialogTitle>
              <DialogDescription>{selectedPrompt.description}</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label className="font-semibold">Prompt Template:</Label>
                <Textarea 
                  value={selectedPrompt.prompt_text} 
                  readOnly 
                  className="mt-2 h-32 bg-gray-50"
                />
              </div>
              <div className="flex gap-4 text-sm text-gray-600">
                <span>Category: {selectedPrompt.category}</span>
                <span>Time Saved: {selectedPrompt.time_saved_minutes} minutes</span>
                <span>Level: {selectedPrompt.difficulty_level}</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedPrompt.tags.map(tag => (
                  <Badge key={tag} variant="secondary">{tag}</Badge>
                ))}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

// Survey Section Component
const SurveySection = ({ surveys }) => {
  const [selectedSurvey, setSelectedSurvey] = useState(null);
  const [responses, setResponses] = useState({});
  const [userEmail, setUserEmail] = useState('');

  const handleSubmitSurvey = async () => {
    if (!selectedSurvey || !userEmail) return;

    try {
      await axios.post(`${API}/surveys/${selectedSurvey.id}/responses`, responses, {
        params: { user_email: userEmail }
      });
      
      alert('Survey submitted successfully!');
      setSelectedSurvey(null);
      setResponses({});
      setUserEmail('');
    } catch (error) {
      console.error('Survey submission failed:', error);
      alert('Failed to submit survey. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Available Surveys</h2>
      
      <div className="grid md:grid-cols-2 gap-6">
        {surveys.map(survey => (
          <Card key={survey.id} className="cursor-pointer hover:shadow-lg transition-all">
            <CardHeader>
              <CardTitle>{survey.title}</CardTitle>
              <CardDescription>{survey.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => setSelectedSurvey(survey)}
                className="w-full"
              >
                Take Survey
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Survey Modal */}
      {selectedSurvey && (
        <Dialog open={!!selectedSurvey} onOpenChange={() => setSelectedSurvey(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{selectedSurvey.title}</DialogTitle>
              <DialogDescription>{selectedSurvey.description}</DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <Label>Your Email</Label>
                <Input 
                  type="email"
                  value={userEmail}
                  onChange={(e) => setUserEmail(e.target.value)}
                  placeholder="Enter your email"
                />
              </div>
              
              {selectedSurvey.questions.map(question => (
                <div key={question.id}>
                  <Label className="font-semibold">{question.question}</Label>
                  {question.type === 'multiple_choice' ? (
                    <Select onValueChange={(value) => setResponses({...responses, [question.id]: value})}>
                      <SelectTrigger className="mt-2">
                        <SelectValue placeholder="Select an option" />
                      </SelectTrigger>
                      <SelectContent>
                        {question.options.map(option => (
                          <SelectItem key={option} value={option}>{option}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : question.type === 'text' ? (
                    <Textarea 
                      className="mt-2"
                      placeholder="Enter your response"
                      onChange={(e) => setResponses({...responses, [question.id]: e.target.value})}
                    />
                  ) : (
                    <Input 
                      type="number"
                      className="mt-2"
                      placeholder="Enter number"
                      onChange={(e) => setResponses({...responses, [question.id]: e.target.value})}
                    />
                  )}
                </div>
              ))}
              
              <Button onClick={handleSubmitSurvey} className="w-full">
                Submit Survey
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

// Admin Panel Component
const AdminPanel = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [users, setUsers] = useState([]);
  const [surveyResponses, setSurveyResponses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const [dashboardRes, usersRes, responsesRes] = await Promise.all([
        axios.get(`${API}/admin/dashboard`),
        axios.get(`${API}/admin/users`),
        axios.get(`${API}/admin/survey-responses`)
      ]);
      
      setDashboardData(dashboardRes.data);
      setUsers(usersRes.data);
      setSurveyResponses(responsesRes.data);
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading admin data...</div>;
  }

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-900">Admin Dashboard</h2>
      
      {/* Metrics Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600">Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.users?.total || 0}</div>
            <p className="text-sm text-gray-600">
              {dashboardData?.users?.recent_signups || 0} this week
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600">Paid Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{dashboardData?.users?.paid || 0}</div>
            <p className="text-sm text-gray-600">
              {dashboardData?.users?.conversion_rate?.toFixed(1) || 0}% conversion
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600">Total Leads</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.leads?.total || 0}</div>
            <p className="text-sm text-gray-600">
              {dashboardData?.leads?.recent || 0} this week
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-sm text-gray-600">Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              ${dashboardData?.revenue?.total?.toFixed(0) || 0}
            </div>
            <Progress 
              value={(dashboardData?.revenue?.total / dashboardData?.revenue?.monthly_target) * 100 || 0} 
              className="mt-2"
            />
          </CardContent>
        </Card>
      </div>
      
      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Users</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Email</th>
                  <th className="text-left p-2">Name</th>
                  <th className="text-left p-2">Role</th>
                  <th className="text-left p-2">Subscription</th>
                  <th className="text-left p-2">Joined</th>
                </tr>
              </thead>
              <tbody>
                {users.slice(0, 10).map(user => (
                  <tr key={user.id} className="border-b">
                    <td className="p-2">{user.email}</td>
                    <td className="p-2">{user.first_name} {user.last_name}</td>
                    <td className="p-2">
                      <Badge className={user.role === 'admin' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}>
                        {user.role}
                      </Badge>
                    </td>
                    <td className="p-2">
                      <Badge className={user.subscription_status === 'paid' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}>
                        {user.subscription_status}
                      </Badge>
                    </td>
                    <td className="p-2">{new Date(user.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      
      {/* Survey Responses */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Survey Responses ({surveyResponses.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {surveyResponses.slice(0, 5).map(response => (
              <div key={response.id} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{response.user_email}</p>
                    <p className="text-sm text-gray-600">
                      {new Date(response.submitted_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="mt-2 text-sm">
                  {Object.entries(response.responses).map(([key, value]) => (
                    <p key={key} className="text-gray-700">
                      <strong>{key}:</strong> {value}
                    </p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Profile Section Component
const ProfileSection = ({ user }) => {
  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Profile</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Email</Label>
            <Input value={user?.email || ''} disabled />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>First Name</Label>
              <Input value={user?.first_name || ''} disabled />
            </div>
            <div>
              <Label>Last Name</Label>
              <Input value={user?.last_name || ''} disabled />
            </div>
          </div>
          <div>
            <Label>Subscription Status</Label>
            <div className="mt-2">
              <Badge className={user?.subscription_status === 'paid' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}>
                {user?.subscription_status || 'free'}
              </Badge>
            </div>
          </div>
          <div>
            <Label>Member Since</Label>
            <p className="text-sm text-gray-600 mt-1">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </CardContent>
      </Card>
      
      {user?.subscription_status !== 'paid' && (
        <Card className="border-orange-200">
          <CardHeader>
            <CardTitle className="text-orange-600">Upgrade to Premium</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Get access to all 47 premium AI prompts and save 12+ hours per week.
            </p>
            <Button 
              onClick={async () => {
                try {
                  const response = await axios.post(`${API}/payments/create-checkout`);
                  window.location.href = response.data.checkout_url;
                } catch (error) {
                  alert('Payment setup failed. Please try again.');
                }
              }}
              className="bg-orange-500 hover:bg-orange-600"
            >
              Upgrade for $37
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Payment Success/Cancel Pages
const PaymentSuccess = () => {
  const [status, setStatus] = useState('checking');
  const navigate = useNavigate();
  
  useEffect(() => {
    const sessionId = new URLSearchParams(window.location.search).get('session_id');
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, []);

  const checkPaymentStatus = async (sessionId) => {
    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      if (response.data.payment_status === 'paid') {
        setStatus('success');
        // Refresh user data
        setTimeout(() => navigate('/dashboard'), 3000);
      } else {
        setStatus('pending');
        // Poll again in 2 seconds
        setTimeout(() => checkPaymentStatus(sessionId), 2000);
      }
    } catch (error) {
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="max-w-md mx-4">
        <CardContent className="text-center p-8">
          {status === 'checking' && (
            <>
              <div className="w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin mx-auto mb-4"></div>
              <h2 className="text-xl font-semibold mb-2">Processing Payment</h2>
              <p className="text-gray-600">Please wait while we confirm your payment...</p>
            </>
          )}
          
          {status === 'success' && (
            <>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">✅</span>
              </div>
              <h2 className="text-xl font-semibold mb-2 text-green-600">Payment Successful!</h2>
              <p className="text-gray-600 mb-4">Thank you for your purchase. You now have access to all premium prompts.</p>
              <Button onClick={() => navigate('/dashboard')} className="bg-green-500 hover:bg-green-600">
                Go to Dashboard
              </Button>
            </>
          )}
          
          {status === 'error' && (
            <>
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">❌</span>
              </div>
              <h2 className="text-xl font-semibold mb-2 text-red-600">Payment Failed</h2>
              <p className="text-gray-600 mb-4">There was an issue processing your payment. Please try again.</p>
              <Button onClick={() => navigate('/')} variant="outline">
                Back to Home
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

const PaymentCancel = () => {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="max-w-md mx-4">
        <CardContent className="text-center p-8">
          <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">⚠️</span>
          </div>
          <h2 className="text-xl font-semibold mb-2 text-yellow-600">Payment Cancelled</h2>
          <p className="text-gray-600 mb-4">
            Your payment was cancelled. No charges were made to your account.
          </p>
          <div className="space-y-2">
            <Button onClick={() => navigate('/dashboard')} className="w-full">
              Go to Dashboard
            </Button>
            <Button onClick={() => navigate('/')} variant="outline" className="w-full">
              Back to Home
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-orange-200 border-t-orange-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/success" element={<PaymentSuccess />} />
            <Route path="/cancel" element={<PaymentCancel />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;