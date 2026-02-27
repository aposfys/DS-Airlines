import React, { useState } from 'react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

const Register = () => {
  const [formData, setFormData] = useState({
    fullname: '',
    username: '',
    email: '',
    password: '',
    passport_num: '',
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/auth/register', formData);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-primary">Sign Up</h2>
        {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
        <form onSubmit={handleSubmit}>
          {Object.keys(formData).map((key) => (
            <div className="mb-4" key={key}>
              <label className="block text-gray-700 text-sm font-bold mb-2 capitalize">{key.replace('_', ' ')}</label>
              <input
                type={key === 'password' ? 'password' : 'text'}
                name={key}
                value={formData[key]}
                onChange={handleChange}
                className="w-full px-3 py-2 border rounded shadow-sm focus:outline-none focus:border-primary"
                required
              />
            </div>
          ))}
          <button
            type="submit"
            className="w-full bg-secondary text-white font-bold py-2 px-4 rounded hover:bg-green-600 transition duration-200"
          >
            Register
          </button>
        </form>
        <p className="mt-4 text-center text-sm">
          Already have an account? <a href="/login" className="text-primary hover:underline">Log In</a>
        </p>
      </div>
    </div>
  );
};

export default Register;
