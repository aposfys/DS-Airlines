import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/auth/token', { username: email, password });
      login(response.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-6 text-center text-primary">Login</h2>
        {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Email/Username</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:border-primary"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">Password</label>
            <input
              type="password"
              className="w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:border-primary"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-primary text-white font-bold py-2 px-4 rounded hover:bg-blue-600 transition duration-200"
          >
            Sign In
          </button>
        </form>
        <p className="mt-4 text-center text-sm">
          Don't have an account? <a href="/register" className="text-primary hover:underline">Sign Up</a>
        </p>
      </div>
    </div>
  );
};

export default Login;
